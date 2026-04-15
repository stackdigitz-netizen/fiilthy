"""
Agent Empire — REST API Routes
Exposes all 6 division controls + approval queue + activity feed
"""
from fastapi import APIRouter
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _orch():
    """Get orchestrator from server context"""
    try:
        from server import db
        from ai_services.agent_orchestrator import get_orchestrator
        return get_orchestrator(db)
    except Exception:
        from ai_services.agent_orchestrator import get_orchestrator
        return get_orchestrator()


# ─── Status & Metrics ─────────────────────────────────────────

@router.get("/status")
async def get_status():
    o = _orch()
    return {
        "divisions": await o.get_all_status(),
        "metrics": await o.get_metrics(),
    }


@router.get("/metrics")
async def get_metrics():
    return await _orch().get_metrics()


@router.get("/activity")
async def get_activity(limit: int = 60):
    return {"activity": await _orch().get_recent_activity(limit)}


@router.get("/pipeline")
async def get_pipeline(limit: int = 6):
    o = _orch()
    return {"products": await o.get_top_products(limit)}


# ─── Division Control ─────────────────────────────────────────

@router.post("/start-all")
async def start_all():
    o = _orch()
    await o.start_all()
    return {"success": True, "message": "All 6 divisions online"}


@router.post("/stop-all")
async def stop_all():
    o = _orch()
    from ai_services.agent_orchestrator import DIVISIONS
    for div_id in DIVISIONS:
        await o.stop_division(div_id)
    return {"success": True, "message": "All divisions paused"}


@router.post("/{division}/start")
async def start_division(division: str):
    o = _orch()
    await o.start_division(division)
    return {"success": True, "division": division, "status": "running"}


@router.post("/{division}/stop")
async def stop_division(division: str):
    o = _orch()
    await o.stop_division(division)
    return {"success": True, "division": division, "status": "paused"}


# ─── Approval Queue ───────────────────────────────────────────

@router.get("/approvals")
async def get_approvals():
    return {"approvals": await _orch().get_pending_approvals()}


@router.post("/approvals/{campaign_id}/approve")
async def approve(campaign_id: str):
    return await _orch().approve_campaign(campaign_id)


@router.post("/approvals/{campaign_id}/reject")
async def reject(campaign_id: str, reason: Optional[str] = ""):
    return await _orch().reject_campaign(campaign_id, reason or "")
