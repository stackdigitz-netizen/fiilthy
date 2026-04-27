"""
API Routes for Scheduling, Quality Control, and Content Management
Integrated endpoints for the complete production system
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import logging

# Import service modules
from ai_services.post_scheduler import PostScheduler
from ai_services.quality_control import run_qc_check, ContentQualityControl
from ai_services.real_video_generator import get_real_video_generator
from ai_services.opportunity_hunter import OpportunityHunter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v5", tags=["Production Factory"])

# Initialize services
scheduler = None
opportunity_hunter = None


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ScheduleRequest(BaseModel):
    product_id: str
    content_items: List[Dict[str, Any]]
    platforms: List[str]  # e.g., ["tiktok", "instagram", "youtube"]
    start_date: Optional[datetime] = None
    spacing_minutes: int = 60
    schedule_times: Optional[List[str]] = None


class ContentPost(BaseModel):
    text: str
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    is_video: bool = False
    video_duration_seconds: Optional[int] = None


class VideoGenerationRequest(BaseModel):
    product_id: str
    video_style: str = "promotional"  # promotional, educational, social_proof
    count: int = 1
    run_qc: bool = True


class QCCheckRequest(BaseModel):
    content_type: str  # product, video, post
    data: Dict[str, Any]


# ============================================================================
# SCHEDULING ENDPOINTS
# ============================================================================

@router.post("/schedule/create")
async def create_schedule(request: ScheduleRequest, background_tasks: BackgroundTasks):
    """
    Schedule posts across platforms
    
    Takes content items and creates optimal posting schedule
    """
    try:
        if scheduler is None:
            raise HTTPException(status_code=500, detail="Scheduler not initialized")
        
        result = await scheduler.schedule_posts(
            product_id=request.product_id,
            content_items=request.content_items,
            platforms=request.platforms,
            start_date=request.start_date,
            spacing_minutes=request.spacing_minutes,
            schedule_times=request.schedule_times
        )
        
        if result["success"]:
            logger.info(f"✅ Scheduled {result['total_scheduled']} posts")
        
        return result
    
    except Exception as e:
        logger.error(f"Schedule creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule/{schedule_id}")
async def get_schedule(schedule_id: str):
    """Get schedule details and status"""
    try:
        result = await scheduler.get_schedule(schedule_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule/upcoming")
async def get_upcoming_posts(limit: int = Query(20, ge=1, le=100)):
    """Get next posts to be published (next 7 days)"""
    try:
        result = await scheduler.get_upcoming_posts(limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/{schedule_id}/pause")
async def pause_schedule(schedule_id: str):
    """Pause all posts in schedule"""
    try:
        result = await scheduler.pause_schedule(schedule_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/{schedule_id}/resume")
async def resume_schedule(schedule_id: str):
    """Resume paused schedule"""
    try:
        result = await scheduler.resume_schedule(schedule_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/{post_id}/reschedule")
async def reschedule_post(post_id: str, new_time: datetime):
    """Reschedule a single post"""
    try:
        result = await scheduler.reschedule_post(post_id, new_time)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# QUALITY CONTROL ENDPOINTS
# ============================================================================

@router.post("/qc/check")
async def run_qc(request: QCCheckRequest):
    """
    Run quality control check on content
    
    content_type: 'product', 'video', or 'post'
    Returns quality score, issues, and recommendations
    """
    try:
        result = await run_qc_check(request.content_type, request.data)
        
        logger.info(
            f"QC Check: {request.content_type} | "
            f"Score: {result['quality_score']:.0f}/100 | "
            f"Publishable: {result['is_publishable']}"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"QC check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qc/product-validation")
async def validate_product(product: Dict[str, Any]):
    """Quick product validation"""
    try:
        passed, issues = ContentQualityControl.validate_product(product)
        
        issue_list = [i.to_dict() for i in issues]
        
        return {
            "passed": passed,
            "can_publish": passed,
            "issue_count": len(issue_list),
            "issues": issue_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qc/video-validation")
async def validate_video(video_data: Dict[str, Any]):
    """Quick video validation"""
    try:
        passed, issues = ContentQualityControl.validate_video(video_data)
        issue_list = [i.to_dict() for i in issues]
        
        return {
            "passed": passed,
            "can_publish": passed,
            "issue_count": len(issue_list),
            "issues": issue_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qc/post-validation")
async def validate_post(post_data: Dict[str, Any]):
    """Quick post validation"""
    try:
        passed, issues = ContentQualityControl.validate_post(post_data)
        issue_list = [i.to_dict() for i in issues]
        
        return {
            "passed": passed,
            "can_publish": passed,
            "issue_count": len(issue_list),
            "issues": issue_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VIDEO GENERATION ENDPOINTS
# ============================================================================

@router.post("/videos/generate-real")
async def generate_real_videos(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate videos using real APIs
    Uses ElevenLabs, Pexels, Pixabay
    """
    try:
        generator = await get_real_video_generator()
        
        # Get product data from DB (assume route context has db)
        # For now, create a mock product
        product = {
            "id": request.product_id,
            "title": f"Product {request.product_id}",
            "description": "Amazing product",
            "price": 29.99
        }
        
        if request.count == 1:
            result = await generator.generate_with_api(
                product,
                request.video_style
            )
        else:
            result = await generator.generate_series(product, request.count)
        
        # Run QC if requested
        if request.run_qc and result.get("success"):
            for video in (result.get("videos", []) if "videos" in result else [result]):
                qc_result = await run_qc_check("video", video.get("metadata", {}))
                video["qc_result"] = qc_result
        
        return result
    
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# OPPORTUNITY HUNTER ENDPOINTS
# ============================================================================

@router.post("/opportunities/hunt")
async def hunt_for_opportunities():
    """Hunt for new opportunities"""
    try:
        if opportunity_hunter is None:
            raise HTTPException(status_code=500, detail="Opportunity hunter not initialized")
        
        result = await opportunity_hunter.hunt_opportunities()
        
        logger.info(f"🎯 Found {result['opportunities_found']} opportunities")
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunities/list")
async def list_opportunities(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """List all discovered opportunities"""
    try:
        if opportunity_hunter is None:
            raise HTTPException(status_code=500, detail="Opportunity hunter not initialized")
        
        opportunities = await opportunity_hunter.get_all_opportunities(status, limit)
        
        return {
            "success": True,
            "total": len(opportunities),
            "opportunities": opportunities
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/opportunities/{opportunity_id}/team")
async def create_team_for_opportunity(opportunity_id: str, background_tasks: BackgroundTasks):
    """Create specialized agent team for opportunity"""
    try:
        if opportunity_hunter is None:
            raise HTTPException(status_code=500, detail="Opportunity hunter not initialized")
        
        result = await opportunity_hunter.create_agent_team(opportunity_id)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INITIALIZATION
# ============================================================================

async def init_services(db=None):
    """Initialize services with database connection"""
    global scheduler, opportunity_hunter
    
    scheduler = PostScheduler(db)
    opportunity_hunter = OpportunityHunter(db)
    
    logger.info("✅ Production factory services initialized")
