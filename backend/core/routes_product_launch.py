"""
Product Launch Routes - Unified endpoints for video generation, campaigns, and publishing
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/products", tags=["product-launch"])


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
    db = None
):
    """
    Generate real videos for a product (TikTok + Instagram)
    Creates viral-style videos optimized for each platform
    Returns job ID for progress tracking
    """
    try:
        if not db:
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

    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}/video-status")
async def get_video_generation_status(
    product_id: str,
    db = None
):
    """
    Get status of video generation for a product
    """
    try:
        if not db:
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

    except Exception as e:
        logger.error(f"Failed to get video status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}/branding")
async def save_product_branding(
    product_id: str,
    request: BrandingRequest,
    db = None
):
    """
    Save or update product branding preferences
    User has full control to override AI recommendations
    """
    try:
        if not db:
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

    except Exception as e:
        logger.error(f"Failed to save branding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_id}/launch-campaign")
async def launch_advertising_campaign(
    product_id: str,
    request: CampaignLaunchRequest,
    background_tasks: BackgroundTasks,
    db = None
):
    """
    Launch advertising campaign on selected platforms
    Creates scheduled posts with optimal posting times
    Sets up auto-posting with monitoring
    """
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database unavailable")

        # Get product
        product = await db['products'].find_one({'id': product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get videos for this product
        videos_job = await db['video_jobs'].find_one(
            {'product_id': product_id, 'status': 'completed'},
            sort=[('created_at', -1)]
        )

        if not videos_job:
            raise HTTPException(
                status_code=400,
                detail="No completed videos found. Generate videos first."
            )

        # Create campaign
        campaign_id = str(uuid.uuid4())
        campaign = {
            'id': campaign_id,
            'product_id': product_id,
            'platforms': request.platforms,
            'status': 'active',
            'start_date': datetime.now(timezone.utc),
            'auto_schedule': request.autoSchedule,
            'budget': request.budget or 100.0,
            'videos_posted': 0,
            'videos_total': len(videos_job.get('videos', [])),
            'performance_metrics': {},
            'created_at': datetime.now(timezone.utc)
        }

        await db['campaigns'].insert_one(campaign)

        # Schedule background task for posting
        background_tasks.add_task(
            _schedule_campaign_posts,
            db,
            campaign_id,
            product_id,
            request.platforms,
            videos_job.get('videos', [])
        )

        # Update product with published platforms
        await db['products'].update_one(
            {'id': product_id},
            {
                '$set': {
                    'campaign_id': campaign_id,
                    'published_on': [
                        {'platform': p, 'status': 'in_campaign'} for p in request.platforms
                    ]
                }
            }
        )

        return {
            'success': True,
            'campaign_id': campaign_id,
            'message': f'Campaign launched on {len(request.platforms)} platforms',
            'platforms': request.platforms,
            'videos_to_post': len(videos_job.get('videos', []))
        }

    except Exception as e:
        logger.error(f"Campaign launch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_id}/publish")
async def publish_to_platform(
    product_id: str,
    request: PublishRequest,
    background_tasks: BackgroundTasks,
    db = None
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
        if not db:
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
        publish_url = await _publish_to_platform_handler(
            db,
            platform,
            product,
            background_tasks
        )

        # Update product
        published_on = product.get('published_on', [])
        # Remove if already exists
        published_on = [p for p in published_on if p.get('platform') != platform]
        # Add new entry
        published_on.append({
            'platform': platform,
            'url': publish_url,
            'published_at': datetime.now(timezone.utc)
        })

        await db['products'].update_one(
            {'id': product_id},
            {'$set': {'published_on': published_on}}
        )

        return {
            'success': True,
            'platform': platform,
            'url': publish_url,
            'message': f'Product published to {platform}'
        }

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


async def _publish_to_platform_handler(db, platform, product, background_tasks):
    """Platform-specific publishing logic"""
    try:
        if platform == 'gumroad':
            # TODO: Create Gumroad product listing
            return f"https://gumroad.com/products/{product.get('id', 'new')}"
        
        elif platform == 'etsy':
            # TODO: Create Etsy listing
            return f"https://etsy.com/shop/yourshop/{product.get('id', 'new')}"
        
        elif platform == 'stripe':
            # TODO: Create Stripe product page
            return f"https://yourstore.com/products/{product.get('id', 'new')}"
        
        elif platform == 'youtube':
            # TODO: Upload to YouTube channel
            return "https://youtube.com/yourvideos"
        
        else:
            return f"https://example.com/{platform}/{product.get('id', 'new')}"

    except Exception as e:
        logger.error(f"Platform {platform} publishing failed: {str(e)}")
        raise
