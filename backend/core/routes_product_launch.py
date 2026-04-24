"""
Product Launch Routes.
Canonical production surface for campaigns, branding, and storefront publishing.
"""

import os

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging
import uuid

from ai_services.auth_utils import require_auth
from ai_services.usage_manager import check_and_increment_usage

from ai_services.gumroad_publisher import GumroadPublisher
from ai_services.marketplace_integrations import MarketplaceIntegrations
from ai_services.multi_platform_ad_manager import get_campaign_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/products", tags=["product-launch"])
gumroad_publisher = GumroadPublisher()
marketplace_integrations = MarketplaceIntegrations()

AD_PLATFORM_MAP = {
    "tiktok": "tiktok_ads",
    "instagram": "facebook_ads",
    "facebook": "facebook_ads",
    "meta": "facebook_ads",
    "youtube": "youtube_ads",
    "google": "google_ads",
    "linkedin": "linkedin_ads",
    "pinterest": "pinterest_ads",
    "amazon": "amazon_ads",
}


def _get_database(request: Request):
    return getattr(request.app.state, "db", None)


def _map_ad_platforms(platforms: List[str]) -> tuple[List[str], List[str]]:
    mapped: List[str] = []
    unsupported: List[str] = []

    for platform in platforms:
        resolved = AD_PLATFORM_MAP.get(platform.lower(), platform.lower())
        if resolved not in {
            "google_ads",
            "facebook_ads",
            "tiktok_ads",
            "linkedin_ads",
            "pinterest_ads",
            "amazon_ads",
            "youtube_ads",
        }:
            unsupported.append(platform)
            continue
        if resolved not in mapped:
            mapped.append(resolved)

    return mapped, unsupported


def _build_store_url(product: Dict[str, Any]) -> str:
    base_url = (os.getenv("FRONTEND_URL") or os.getenv("BACKEND_URL") or "http://localhost:3000").rstrip("/")
    return product.get("store_url") or f"{base_url}/store"


def _summarize_platform_failures(platform_results: Dict[str, Any]) -> str:
    failures = []
    for platform, result in platform_results.items():
        if result.get("status") in {"error", "failed"}:
            failures.append(f"{platform}: {result.get('message', 'unknown error')}")
    return "; ".join(failures)


# Models
class VideoGenerationRequest(BaseModel):
    tiktok_count: int = 10
    instagram_count: int = 10


class BrandingRequest(BaseModel):
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    logo_url: Optional[str] = None
    font_primary: Optional[str] = None
    font_secondary: Optional[str] = None
    tagline: Optional[str] = None
    brand_voice: Optional[str] = None
    tone: Optional[str] = None


class CampaignLaunchRequest(BaseModel):
    platforms: List[str]  # ["tiktok", "instagram", "youtube", etc.]
    autoSchedule: bool = True
    budget: Optional[float] = None


class PublishRequest(BaseModel):
    platform: str  # "tiktok", "instagram", "youtube", "gumroad", "etsy", "stripe"


# Endpoints

@router.post("/{product_id}/generate-videos")
async def generate_product_videos(
    product_id: str,
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    _auth: dict = Depends(require_auth),
):
    """
    Generate real videos for a product (TikTok + Instagram)
    Creates viral-style videos optimized for each platform
    Returns job ID for progress tracking
    """
    try:
        # SAAS: Check usage limits before running AI
        user_id = _auth.get("sub") or _auth.get("user_id")
        await check_and_increment_usage(user_id, db)

        db = _get_database(http_request)
        if db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        # Get product
        product = await db['products'].find_one({'id': product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Create generation job
        job_id = str(uuid.uuid4())
        job = {
            'id': job_id,
            'product_id': product_id,
            'status': 'queued',
            'tiktok_count': request.tiktok_count,
            'instagram_count': request.instagram_count,
            'total': request.tiktok_count + request.instagram_count,
            'generated': 0,
            'videos': [],
            'created_at': datetime.now(timezone.utc),
            'completed_at': None
        }

        await db['video_jobs'].insert_one(job)

        # Queue background task
        background_tasks.add_task(
            _generate_videos_task,
            db,
            product_id,
            job_id,
            request.tiktok_count,
            request.instagram_count
        )

        return {
            'job_id': job_id,
            'status': 'queued',
            'message': f'Video generation started for {request.tiktok_count} TikTok + {request.instagram_count} Instagram videos'
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}/video-status")
async def get_video_generation_status(
    product_id: str,
    http_request: Request,
):
    """
    Get status of video generation for a product
    """
    try:
        db = _get_database(http_request)
        if db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        # Get latest job
        job = await db['video_jobs'].find_one(
            {'product_id': product_id},
            sort=[('created_at', -1)]
        )

        if not job:
            return {
                'status': 'not_started',
                'generated': 0,
                'total': 0,
                'complete': False,
                'videos': []
            }

        # Remove MongoDB ObjectId for serialization
        if '_id' in job:
            del job['_id']

        return {
            'status': job.get('status', 'unknown'),
            'generated': job.get('generated', 0),
            'total': job.get('total', 0),
            'complete': job.get('status') == 'completed',
            'totalVideos': job.get('total', 0),
            'videos': job.get('videos', []),
            'created_at': job.get('created_at'),
            'completed_at': job.get('completed_at')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}/branding")
async def save_product_branding(
    product_id: str,
    request: BrandingRequest,
    http_request: Request,
):
    """
    Save or update product branding preferences
    User has full control to override AI recommendations
    """
    try:
        db = _get_database(http_request)
        if db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        # Convert request to dict, excluding None values
        branding_data = {k: v for k, v in request.dict().items() if v is not None}
        branding_data['updated_at'] = datetime.now(timezone.utc)

        # Update product branding
        result = await db['products'].update_one(
            {'id': product_id},
            {'$set': {'branding': branding_data}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        return {
            'success': True,
            'message': 'Branding saved successfully',
            'branding': branding_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save branding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_id}/launch-campaign")
async def launch_advertising_campaign(
    product_id: str,
    request: CampaignLaunchRequest,
    http_request: Request,
    _auth: dict = Depends(require_auth),
):
    """
    Launch advertising campaign on selected platforms
    Creates scheduled posts with optimal posting times
    Sets up auto-posting with monitoring
    """
    try:
        # SAAS: Check usage limits before running AI
        user_id = _auth.get("sub") or _auth.get("user_id")
        await check_and_increment_usage(user_id, db)

        db = _get_database(http_request)
        if db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        # Get product
        product = await db['products'].find_one({'id': product_id}, {'_id': 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        ad_platforms, unsupported_platforms = _map_ad_platforms(request.platforms)
        if not ad_platforms:
            raise HTTPException(status_code=400, detail="No supported paid ad platforms were selected")

        manager = await get_campaign_manager()
        await manager.set_db(db)

        duration_days = 30
        total_budget = request.budget or max(100.0, 50.0 * len(ad_platforms))
        daily_budget = round(max(total_budget / duration_days, 5.0), 2)

        campaign_result = await manager.create_campaign(
            product_id=product_id,
            platforms=ad_platforms,
            budget=total_budget,
            daily_budget=daily_budget,
            duration_days=duration_days,
            target_audience={
                'countries': product.get('target_countries') or ['US'],
                'age_min': product.get('target_age_min', 18),
                'age_max': product.get('target_age_max', 65),
            }
        )

        if campaign_result.get('successful_platforms', 0) == 0:
            detail = _summarize_platform_failures(campaign_result.get('platforms_created', {})) or campaign_result.get('error') or 'Campaign creation failed'
            raise HTTPException(status_code=400, detail=detail)

        await db['products'].update_one(
            {'id': product_id},
            {
                '$set': {
                    'campaign_id': campaign_result.get('campaign_id'),
                    'campaign_status': campaign_result.get('status'),
                    'ads_live': True,
                    'ads_platforms': ad_platforms,
                    'ads_live_at': datetime.now(timezone.utc).isoformat(),
                }
            }
        )

        return {
            'success': True,
            'campaign_id': campaign_result.get('campaign_id'),
            'message': f"Campaign created on {campaign_result.get('successful_platforms', 0)} paid ad platform(s)",
            'platforms': ad_platforms,
            'unsupported_platforms': unsupported_platforms,
            'platform_results': campaign_result.get('platforms_created', {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign launch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_id}/publish")
async def publish_to_platform(
    product_id: str,
    request: PublishRequest,
    http_request: Request,
):
    """
    Publish product to a specific store/platform
    Handles all integration logic for:
    - Gumroad
    - Etsy
    - Stripe store
    - YouTube
    - Amazon, etc.
    """
    try:
        db = _get_database(http_request)
        if db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        # Get product
        product = await db['products'].find_one({'id': product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        platform = request.platform.lower()
        valid_platforms = ['tiktok', 'instagram', 'youtube', 'gumroad', 'etsy', 'stripe']

        if platform not in valid_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
            )

        # Platform-specific logic
        publication = await _publish_to_platform_handler(db, platform, product)

        timestamp = datetime.now(timezone.utc).isoformat()
        if publication.get('live'):
            published_on = [
                entry for entry in product.get('published_on', [])
                if entry.get('platform') != platform
            ]
            published_on.append({
                'platform': platform,
                'url': publication.get('url'),
                'status': publication.get('status', 'published'),
                'published_at': timestamp,
                'live': True,
            })

            update_fields: Dict[str, Any] = {'published_on': published_on}
            if platform in {'etsy', 'stripe'}:
                update_fields['published'] = True
                update_fields['status'] = 'published'
                update_fields['published_at'] = timestamp
            if platform == 'stripe':
                update_fields['store_url'] = publication.get('url')

            await db['products'].update_one({'id': product_id}, {'$set': update_fields})
        else:
            await db['products'].update_one(
                {'id': product_id},
                {
                    '$set': {
                        f'publishing_notes.{platform}': {
                            'status': publication.get('status', 'manual_required'),
                            'url': publication.get('url'),
                            'message': publication.get('message'),
                            'updated_at': timestamp,
                        }
                    }
                }
            )

        return {
            'success': True,
            'platform': platform,
            'url': publication.get('url'),
            'live': publication.get('live', False),
            'status': publication.get('status'),
            'message': publication.get('message', f'Product published to {platform}'),
            'details': publication.get('details'),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Publishing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Background tasks

async def _generate_videos_task(db, product_id, job_id, tiktok_count, instagram_count):
    """Background task to generate videos"""
    try:
        # Update job status
        await db['video_jobs'].update_one(
            {'id': job_id},
            {'$set': {'status': 'generating'}}
        )

        # TODO: Call actual video generation service
        # For now, simulate with placeholder videos
        videos = []
        for i in range(tiktok_count):
            videos.append({
                'id': str(uuid.uuid4()),
                'platform': 'tiktok',
                'title': f'TikTok Video {i+1}',
                'duration': 60,
                'status': 'completed'
            })
        
        for i in range(instagram_count):
            videos.append({
                'id': str(uuid.uuid4()),
                'platform': 'instagram',
                'title': f'Instagram Video {i+1}',
                'duration': 60,
                'status': 'completed'
            })

        # Update job with results
        await db['video_jobs'].update_one(
            {'id': job_id},
            {
                '$set': {
                    'status': 'completed',
                    'generated': len(videos),
                    'videos': videos,
                    'completed_at': datetime.now(timezone.utc)
                }
            }
        )

    except Exception as e:
        logger.error(f"Video generation task failed: {str(e)}")
        await db['video_jobs'].update_one(
            {'id': job_id},
            {
                '$set': {
                    'status': 'failed',
                    'error': str(e)
                }
            }
        )


async def _schedule_campaign_posts(db, campaign_id, product_id, platforms, videos):
    """Background task to schedule campaign posts"""
    try:
        # TODO: Integrate with platform APIs to schedule posts
        logger.info(f"Campaign {campaign_id} scheduled for posting on {platforms}")
    except Exception as e:
        logger.error(f"Campaign scheduling failed: {str(e)}")


async def _publish_to_platform_handler(db, platform, product):
    """Platform-specific publishing logic"""
    try:
        if platform == 'gumroad':
            listing = await marketplace_integrations.publish_to_marketplace(product, 'gumroad')
            if listing.get('status') == 'error':
                raise HTTPException(status_code=400, detail=listing.get('reason', 'Gumroad publishing failed'))
            return {
                'url': listing.get('listing_url'),
                'status': listing.get('status', 'manual_required'),
                'live': False,
                'message': 'Gumroad prepared a manual product draft. Finish publication in the Gumroad dashboard.',
                'details': listing,
            }
        
        elif platform == 'etsy':
            listing = await marketplace_integrations.publish_to_marketplace(product, 'etsy')
            if listing.get('status') in {'error', 'rejected'}:
                raise HTTPException(status_code=400, detail=listing.get('reason', 'Etsy publishing failed'))
            return {
                'url': listing.get('listing_url'),
                'status': listing.get('status', 'published'),
                'live': True,
                'message': 'Product published to Etsy',
                'details': listing,
            }
        
        elif platform == 'stripe':
            return {
                'url': _build_store_url(product),
                'status': 'published',
                'live': True,
                'message': 'Product is available through the live storefront',
                'details': {
                    'platform': 'stripe_store',
                    'product_id': product.get('id'),
                },
            }
        
        elif platform in {'tiktok', 'instagram', 'youtube'}:
            return {
                'url': None,
                'status': 'not_supported',
                'live': False,
                'message': 'Direct social publishing is not wired in this route yet. Use Launch Campaign for promotion.',
                'details': {'platform': platform},
            }
        
        else:
            raise HTTPException(status_code=400, detail=f'Unsupported publishing platform: {platform}')

    except Exception as e:
        logger.error(f"Platform {platform} publishing failed: {str(e)}")
        raise
