"""
Intelligence Routes — competitor analysis, email list builder, YouTube Shorts automator.
All endpoints require authentication.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ai_services.auth_utils import require_auth
from ai_services.competitor_analyzer import CompetitorAnalyzer
from ai_services.email_list_builder import EmailListBuilder
from ai_services.youtube_shorts_automator import YouTubeShortsAutomator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

# --- dependency instances ---

def _competitor() -> CompetitorAnalyzer:
    return CompetitorAnalyzer()

def _email() -> EmailListBuilder:
    return EmailListBuilder()

def _shorts() -> YouTubeShortsAutomator:
    return YouTubeShortsAutomator()


# ── Competitor Analyzer ───────────────────────────────────────────────────────

class AnalyzeCompetitorRequest(BaseModel):
    competitor_name: str
    competitor_url: Optional[str] = None

class MarketGapsRequest(BaseModel):
    niche: str

class SentimentRequest(BaseModel):
    competitor_name: str
    source: str = "reviews"

class IntelligenceRequest(BaseModel):
    niche: str


@router.post("/competitor/analyze")
async def analyze_competitor(
    body: AnalyzeCompetitorRequest,
    _auth: dict = Depends(require_auth),
):
    """Analyze a specific competitor using AI."""
    try:
        return await _competitor().analyze_competitor(body.competitor_name, body.competitor_url)
    except Exception as e:
        logger.error("analyze_competitor route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitor/market-gaps")
async def find_market_gaps(
    body: MarketGapsRequest,
    _auth: dict = Depends(require_auth),
):
    """Find underserved market gaps in a niche."""
    try:
        return await _competitor().find_market_gaps(body.niche)
    except Exception as e:
        logger.error("find_market_gaps route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitor/sentiment")
async def analyze_sentiment(
    body: SentimentRequest,
    _auth: dict = Depends(require_auth),
):
    """Analyze customer sentiment for a competitor."""
    try:
        return await _competitor().analyze_customer_sentiment(body.competitor_name, body.source)
    except Exception as e:
        logger.error("analyze_sentiment route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitor/underpriced-markets")
async def underpriced_markets(_auth: dict = Depends(require_auth)):
    """Find underpriced market segments for digital products."""
    try:
        return await _competitor().find_underpriced_markets()
    except Exception as e:
        logger.error("underpriced_markets route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitor/landscape")
async def competitive_landscape(
    body: IntelligenceRequest,
    _auth: dict = Depends(require_auth),
):
    """Get full competitive landscape for a niche."""
    try:
        return await _competitor().get_competitive_intelligence(body.niche)
    except Exception as e:
        logger.error("competitive_landscape route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Email List Builder ────────────────────────────────────────────────────────

class CreateListRequest(BaseModel):
    product: Dict[str, Any]

class GenerateSequenceRequest(BaseModel):
    product: Dict[str, Any]
    days: int = 30

class AddSubscriberRequest(BaseModel):
    email: str
    list_id: str
    metadata: Optional[Dict[str, Any]] = None

class ActivateSequenceRequest(BaseModel):
    list_id: str
    emails: List[Dict[str, Any]]


@router.post("/email/create-list")
async def create_email_list(
    body: CreateListRequest,
    _auth: dict = Depends(require_auth),
):
    """Create a Mailchimp audience for a product."""
    try:
        return await _email().create_email_list(body.product)
    except Exception as e:
        logger.error("create_email_list route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/generate-sequence")
async def generate_email_sequence(
    body: GenerateSequenceRequest,
    _auth: dict = Depends(require_auth),
):
    """Generate an AI-written 30-day email sequence for a product."""
    try:
        return await _email().generate_email_sequence(body.product, body.days)
    except Exception as e:
        logger.error("generate_email_sequence route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/subscribe")
async def add_subscriber(
    body: AddSubscriberRequest,
    _auth: dict = Depends(require_auth),
):
    """Add a subscriber to a Mailchimp audience."""
    try:
        return await _email().add_subscriber(body.email, body.list_id, body.metadata)
    except Exception as e:
        logger.error("add_subscriber route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/activate-sequence")
async def activate_email_sequence(
    body: ActivateSequenceRequest,
    _auth: dict = Depends(require_auth),
):
    """Create a Mailchimp campaign and activate the email sequence."""
    try:
        return await _email().send_email_sequence(body.list_id, body.emails)
    except Exception as e:
        logger.error("activate_email_sequence route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/email/metrics/{list_id}")
async def email_metrics(
    list_id: str,
    _auth: dict = Depends(require_auth),
):
    """Get real Mailchimp audience metrics for a list."""
    try:
        return await _email().get_email_metrics(list_id)
    except Exception as e:
        logger.error("email_metrics route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── YouTube Shorts Automator ──────────────────────────────────────────────────

class GenerateShortsRequest(BaseModel):
    product: Dict[str, Any]
    count: int = 30

class UploadShortRequest(BaseModel):
    script: Dict[str, Any]
    video_path: Optional[str] = None

class ScheduleUploadsRequest(BaseModel):
    scripts: List[Dict[str, Any]]


@router.post("/shorts/generate-scripts")
async def generate_shorts_scripts(
    body: GenerateShortsRequest,
    _auth: dict = Depends(require_auth),
):
    """Generate AI YouTube Shorts scripts for a product (30-day plan)."""
    try:
        return await _shorts().generate_shorts_script(body.product, body.count)
    except Exception as e:
        logger.error("generate_shorts_scripts route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shorts/upload")
async def upload_short(
    body: UploadShortRequest,
    _auth: dict = Depends(require_auth),
):
    """Upload a Short to YouTube (requires YouTube OAuth credentials in env)."""
    try:
        return await _shorts().upload_short(body.script, body.video_path)
    except Exception as e:
        logger.error("upload_short route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shorts/schedule")
async def schedule_uploads(
    body: ScheduleUploadsRequest,
    _auth: dict = Depends(require_auth),
):
    """Generate a daily upload schedule manifest for a set of scripts."""
    try:
        return await _shorts().schedule_daily_upload(body.scripts)
    except Exception as e:
        logger.error("schedule_uploads route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shorts/analytics/{video_id}")
async def shorts_analytics(
    video_id: str,
    _auth: dict = Depends(require_auth),
):
    """Get analytics for an uploaded Short."""
    try:
        return await _shorts().get_shorts_analytics(video_id)
    except Exception as e:
        logger.error("shorts_analytics route error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
