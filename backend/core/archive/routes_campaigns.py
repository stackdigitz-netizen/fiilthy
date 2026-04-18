"""
Video & Campaign Routes - Endpoints for video generation and campaign management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

from ai_services.video_campaign_manager import get_campaign_manager, VideoCampaignManager
from ai_services.real_video_generator import get_real_video_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


# Models
class VideoGenerationRequest(BaseModel):
    product_id: str
    product_title: str
    product_description: str
    price: float
    target_audience: Optional[Dict[str, Any]] = None


class CampaignRequest(BaseModel):
    product_id: str
    product_title: str
    product_description: str
    price: float
    budget: float = 100.0
    target_audience: Optional[Dict[str, Any]] = None
    schedule_start_days_ahead: int = 1
    duration_days: int = 14


class ScheduleRequest(BaseModel):
    campaign_id: str
    start_date_offset_days: int = 1
    videos_per_day: int = 1


class PostRequest(BaseModel):
    video_id: str
    campaign_id: str
    caption: str
    hashtags: List[str]


# Endpoints

@router.post("/generate-product-campaign")
async def generate_product_campaign(
    request: CampaignRequest,
    background_tasks: BackgroundTasks,
    db = None
):
    """
    Generate complete video campaign for a product
    Creates:
    - 10 TikTok videos (optimized for platform)
    - 10 Instagram videos (optimized for platform)
    - Campaign configuration with scheduling
    """
    try:
        manager = get_campaign_manager(db)
        
        schedule_start = datetime.now(timezone.utc) + timedelta(
            days=request.schedule_start_days_ahead
        )
        schedule_end = schedule_start + timedelta(days=request.duration_days)
        
        result = await manager.create_product_campaign(
            product_id=request.product_id,
            product_title=request.product_title,
            product_description=request.product_description,
            price=request.price,
            target_audience=request.target_audience,
            budget=request.budget,
            schedule_start=schedule_start,
            schedule_end=schedule_end
        )
        
        if result["success"]:
            # Schedule campaign in background
            background_tasks.add_task(
                schedule_campaign_videos,
                manager,
                result["campaign_id"],
                schedule_start
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Campaign generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/{campaign_id}")
async def schedule_campaign(
    campaign_id: str,
    request: ScheduleRequest,
    db = None
):
    """
    Schedule campaign videos for automatic posting
    """
    try:
        manager = get_campaign_manager(db)
        
        start_date = datetime.now(timezone.utc) + timedelta(
            days=request.start_date_offset_days
        )
        
        result = await manager.schedule_campaign(
            campaign_id=campaign_id,
            start_date=start_date,
            videos_per_day=request.videos_per_day
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Schedule failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post-tiktok")
async def post_to_tiktok(
    request: PostRequest,
    background_tasks: BackgroundTasks,
    db = None
):
    """
    Post video to TikTok
    """
    try:
        manager = get_campaign_manager(db)
        
        result = await manager.post_to_tiktok(
            video_id=request.video_id,
            caption=request.caption,
            hashtags=request.hashtags
        )
        
        # Log posting activity
        if result["success"]:
            background_tasks.add_task(
                log_campaign_activity,
                request.campaign_id,
                "tiktok_post",
                request.video_id
            )
        
        return result
    
    except Exception as e:
        logger.error(f"TikTok posting failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post-instagram")
async def post_to_instagram(
    request: PostRequest,
    video_type: str = "reel",
    background_tasks: BackgroundTasks = None,
    db = None
):
    """
    Post video to Instagram
    """
    try:
        manager = get_campaign_manager(db)
        
        result = await manager.post_to_instagram(
            video_id=request.video_id,
            caption=request.caption,
            hashtags=request.hashtags,
            video_type=video_type
        )
        
        # Log posting activity
        if result["success"] and background_tasks:
            background_tasks.add_task(
                log_campaign_activity,
                request.campaign_id,
                "instagram_post",
                request.video_id
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Instagram posting failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, db = None):
    """
    Get campaign details
    """
    try:
        if db:
            campaigns_collection = db["campaigns"]
            campaign = await campaigns_collection.find_one({"id": campaign_id})
            if campaign:
                # Remove MongoDB's _id field
                campaign.pop("_id", None)
                return {"success": True, "campaign": campaign}
        
        return {"success": False, "error": "Campaign not found"}
    
    except Exception as e:
        logger.error(f"Error fetching campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/schedule")
async def get_campaign_schedule(campaign_id: str, db = None):
    """
    Get campaign posting schedule
    """
    try:
        if db:
            schedules_collection = db["campaign_schedules"]
            schedule = await schedules_collection.find_one({"campaign_id": campaign_id})
            if schedule:
                schedule.pop("_id", None)
                return {"success": True, "schedule": schedule}
        
        return {"success": False, "error": "Schedule not found"}
    
    except Exception as e:
        logger.error(f"Error fetching schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/activate")
async def activate_campaign(campaign_id: str, db = None):
    """
    Activate campaign for posting
    """
    try:
        if db:
            campaigns_collection = db["campaigns"]
            await campaigns_collection.update_one(
                {"id": campaign_id},
                {"$set": {"status": "active", "activated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "status": "activated"
            }
        
        return {"success": False, "error": "Campaign not found"}
    
    except Exception as e:
        logger.error(f"Error activating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Background tasks

async def schedule_campaign_videos(
    manager: VideoCampaignManager,
    campaign_id: str,
    start_date: datetime
):
    """Background task to schedule campaign videos"""
    try:
        await manager.schedule_campaign(campaign_id, start_date)
        logger.info(f"Campaign {campaign_id} scheduled successfully")
    except Exception as e:
        logger.error(f"Failed to schedule campaign {campaign_id}: {str(e)}")


async def log_campaign_activity(
    campaign_id: str,
    activity_type: str,
    video_id: str,
    db = None
):
    """Log campaign activity for analytics"""
    try:
        if db:
            activity_log = {
                "campaign_id": campaign_id,
                "activity_type": activity_type,
                "video_id": video_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logs_collection = db["campaign_logs"]
            await logs_collection.insert_one(activity_log)
    except Exception as e:
        logger.error(f"Failed to log activity: {str(e)}")
