"""
Agent Empire — REST API Routes.
Canonical production surface for agent control, approvals, and activity feeds.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import logging

from ai_services.auth_utils import require_auth

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


def _db():
    try:
        from server import db as server_db
        return server_db
    except Exception:
        return None


def _normalize(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _configured_operator_emails() -> set[str]:
    configured: set[str] = set()
    for env_name in ("OWNER_EMAIL", "OWNER_EMAILS", "ADMIN_EMAIL", "ADMIN_EMAILS"):
        raw_value = _normalize(os.environ.get(env_name))
        if not raw_value:
            continue
        configured.update(email.strip().lower() for email in raw_value.split(",") if email.strip())
    return configured


async def require_operator_access(_auth: dict = Depends(require_auth)) -> dict:
    if _auth.get("is_admin"):
        return _auth

    role_value = _normalize(_auth.get("role"))
    if role_value and role_value.lower() in {"admin", "owner"}:
        return _auth

    normalized_email = _normalize(_auth.get("email"))
    normalized_email = normalized_email.lower() if normalized_email else None
    if normalized_email and normalized_email in _configured_operator_emails():
        return _auth

    database = _db()
    if database is not None:
        try:
            user_id = _auth.get("sub") or _auth.get("user_id")
            user_doc = None
            if user_id:
                user_doc = await database["users"].find_one({"id": user_id}, {"_id": 0, "is_admin": 1})
            if not user_doc and normalized_email:
                user_doc = await database["users"].find_one({"email": normalized_email}, {"_id": 0, "is_admin": 1})
            if user_doc and user_doc.get("is_admin"):
                return _auth
        except Exception as exc:
            logger.debug(f"Operator auth lookup failed: {exc}")

    raise HTTPException(status_code=403, detail="Operator access required")


# ─── Status & Metrics ─────────────────────────────────────────

@router.get("/status")
async def get_status(_auth: dict = Depends(require_auth)):
    o = _orch()
    return {
        "divisions": await o.get_all_status(),
        "metrics": await o.get_metrics(),
    }


@router.get("/metrics")
async def get_metrics(_auth: dict = Depends(require_auth)):
    return await _orch().get_metrics()


@router.get("/activity")
async def get_activity(limit: int = 60, _auth: dict = Depends(require_auth)):
    return {"activity": await _orch().get_recent_activity(limit)}


@router.get("/pipeline")
async def get_pipeline(limit: int = 6, _auth: dict = Depends(require_auth)):
    o = _orch()
    return {"products": await o.get_top_products(limit)}


# ─── Division Control ─────────────────────────────────────────

@router.post("/start-all")
async def start_all(_auth: dict = Depends(require_operator_access)):
    o = _orch()
    await o.start_all()
    return {"success": True, "message": "All 6 divisions online"}


@router.post("/stop-all")
async def stop_all(_auth: dict = Depends(require_operator_access)):
    o = _orch()
    from ai_services.agent_orchestrator import DIVISIONS
    for div_id in DIVISIONS:
        await o.stop_division(div_id)
    return {"success": True, "message": "All divisions paused"}


@router.post("/{division}/start")
async def start_division(division: str, _auth: dict = Depends(require_operator_access)):
    o = _orch()
    await o.start_division(division)
    return {"success": True, "division": division, "status": "running"}


@router.post("/{division}/stop")
async def stop_division(division: str, _auth: dict = Depends(require_operator_access)):
    o = _orch()
    await o.stop_division(division)
    return {"success": True, "division": division, "status": "paused"}


# ─── Approval Queue ───────────────────────────────────────────

@router.get("/approvals")
async def get_approvals(_auth: dict = Depends(require_auth)):
    return {"approvals": await _orch().get_pending_approvals()}


@router.post("/approvals/{campaign_id}/approve")
async def approve(campaign_id: str, _auth: dict = Depends(require_operator_access)):
    return await _orch().approve_campaign(campaign_id)


@router.post("/approvals/{campaign_id}/reject")
async def reject(campaign_id: str, reason: Optional[str] = "", _auth: dict = Depends(require_operator_access)):
    return await _orch().reject_campaign(campaign_id, reason or "")
