"""
Quality Control & Production Cycle Routes
Exposes endpoints for running QC checks, viewing cycle history,
and manually triggering a generation cycle.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

from ai_services.product_quality_engine import run_qc, THRESHOLDS
from ai_services.product_cycle_scheduler import get_cycle_scheduler
from ai_services.agent_orchestrator import get_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quality", tags=["quality-control"])


def _get_database(request: Request):
    return getattr(request.app.state, "db", None)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class QCRequest(BaseModel):
    product_id: Optional[str] = None
    product: Optional[Dict[str, Any]] = None  # inline product data


class BulkQCRequest(BaseModel):
    limit: Optional[int] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/check")
async def run_quality_check(request: QCRequest, http_request: Request):
    """
    Run a quality check against a product.
    Pass either product_id (fetches from DB) or inline product data.
    Returns a full QC report with score, grade, and actionable fixes.
    """
    db = _get_database(http_request)
    product = request.product

    if not product and request.product_id:
        if not db:
            raise HTTPException(status_code=503, detail="Database unavailable")
        product = await db["products"].find_one({"id": request.product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if "_id" in product:
            del product["_id"]

    if not product:
        raise HTTPException(status_code=400, detail="Provide product_id or inline product data")

    report = run_qc(product)

    # Persist report to DB if we have a product id
    if db and (product_id := product.get("id")):
        await db["products"].update_one(
            {"id": product_id},
            {"$set": {
                "qc_report": report,
                "qc_score": report["overall_score"],
                "qc_grade": report["grade"],
                "qc_passed": report["passed"],
                "qc_ready": report["ready_for_sale"],
            }}
        )

    return report


@router.get("/standards")
async def get_quality_standards():
    """
    Return the current quality thresholds so the UI can display them.
    """
    return {
        "thresholds": THRESHOLDS,
        "scoring": {
            "pass_score": THRESHOLDS["pass_score"],
            "sale_score": THRESHOLDS["sale_score"],
            "grades": {
                "A+": "95-100",
                "A": "90-94",
                "B+": "85-89",
                "B": "80-84",
                "C": "75-79",
                "D": "65-74",
                "F": "0-64",
            },
        },
        "required_checks": [
            "Title (4-15 words, no filler)",
            "Description (300+ characters, no placeholders)",
            "Pricing ($9-$997)",
            "Content Depth (min chapters/lessons for type)",
            "Uniqueness (45%+ unique word ratio)",
            "Value Proposition (3+ benefit signals)",
            "Target Audience (defined)",
            "Keywords (5+ search tags)",
            "Sales Assets (cover image required)",
            "Monetization Fitness (conversion language)",
            "Compliance (no unqualified income/medical claims)",
        ],
    }


@router.get("/products")
async def list_products_with_qc(http_request: Request, status: Optional[str] = None):
    """
    List all products with their QC scores.
    Filter by status: approved | rejected | pending
    """
    db = _get_database(http_request)
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    query: Dict[str, Any] = {}
    if status:
        query["status"] = status

    cursor = db["products"].find(query).sort("generated_at", -1).limit(200)
    products = []
    async for p in cursor:
        if "_id" in p:
            del p["_id"]
        products.append({
            "id": p.get("id"),
            "title": p.get("title"),
            "product_type": p.get("product_type"),
            "price": p.get("price"),
            "status": p.get("status", "pending"),
            "qc_score": p.get("qc_score"),
            "qc_grade": p.get("qc_grade"),
            "qc_passed": p.get("qc_passed"),
            "qc_ready": p.get("qc_ready"),
            "generated_at": p.get("generated_at"),
            "cycle_id": p.get("cycle_id"),
            "qc_report": p.get("qc_report"),
        })

    return products


@router.post("/review-all")
async def review_all_products(request: BulkQCRequest, http_request: Request):
    """
    Run the strict QC engine across the current catalog and classify each product.
    Approved and published products remain sellable; weak items are rejected,
    duplicates are flagged, and failing published items are retired.
    """
    db = _get_database(http_request)
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    orchestrator = get_orchestrator(db)
    limit = max(int(request.limit or 0), 0)
    cursor = db["products"].find({}, {"_id": 0}).sort("created_at", -1)
    if limit:
        cursor = cursor.limit(limit)

    summary = {
        "processed": 0,
        "approved": 0,
        "published": 0,
        "rejected": 0,
        "duplicate": 0,
        "retired": 0,
        "store_ready": 0,
        "average_score": 0.0,
        "examples": [],
    }
    total_score = 0.0

    async for product in cursor:
        try:
            report = run_qc(product)
            score = float(report.get("overall_score") or 0)
            grade = report.get("grade") or "F"
            content_signature = product.get("content_signature") or orchestrator._content_signature(product)
            duplicate_of = await orchestrator._find_duplicate_product({**product, "content_signature": content_signature})
            blocking_issues = list(report.get("blocking_issues") or [])
            improvements = list(report.get("improvements") or [])

            if duplicate_of:
                blocking_issues.append("Duplicate Content")
                improvements.append(f"Rewrite the product so it is materially different from product {duplicate_of}.")
                score = min(score, 35.0)
                grade = "F"

            report["blocking_issues"] = list(dict.fromkeys(blocking_issues))
            report["improvements"] = list(dict.fromkeys(improvements))
            report["overall_score"] = round(score, 1)
            report["grade"] = grade
            report["passed"] = bool(report.get("passed")) and not duplicate_of
            report["ready_for_sale"] = bool(report.get("ready_for_sale")) and not duplicate_of

            current_status = str(product.get("status") or "").lower()
            if report.get("ready_for_sale"):
                status = "published" if current_status == "published" else "approved"
            elif duplicate_of:
                status = "duplicate"
            elif current_status == "published":
                status = "retired"
            else:
                status = "rejected"

            launch_score = orchestrator._calculate_launch_score(product, qc_score=score)
            store_ready = bool(report.get("ready_for_sale"))

            await db["products"].update_one(
                {"id": product["id"]},
                {"$set": {
                    "status": status,
                    "qc_score": score,
                    "qc_grade": grade,
                    "qc_report": report,
                    "qc_passed": bool(report.get("passed")),
                    "qc_ready": store_ready,
                    "qc_checked_at": datetime.now(timezone.utc).isoformat(),
                    "content_signature": content_signature,
                    "duplicate_of": duplicate_of,
                    "launch_score": launch_score,
                    "featured_candidate": store_ready and not report.get("blocking_issues") and score >= orchestrator.auto_feature_min_score,
                    "campaign_priority": "auto" if store_ready and score >= orchestrator.auto_feature_min_score else ("blocked" if report.get("blocking_issues") else "review"),
                    "store_ready": store_ready,
                    "store_ready_at": datetime.now(timezone.utc).isoformat() if store_ready else None,
                    "qc_error_reason": None,
                    "qc_error_at": None,
                }}
            )

            summary["processed"] += 1
            total_score += score
            summary[status] = summary.get(status, 0) + 1
            if store_ready:
                summary["store_ready"] += 1

            if len(summary["examples"]) < 12:
                summary["examples"].append({
                    "id": product.get("id"),
                    "title": product.get("title"),
                    "status": status,
                    "qc_score": round(score, 1),
                    "qc_grade": grade,
                    "duplicate_of": duplicate_of,
                })
        except Exception as exc:
            await db["products"].update_one(
                {"id": product.get("id")},
                {"$set": {
                    "status": "qc_error",
                    "qc_score": 0.0,
                    "qc_grade": "ERROR",
                    "qc_report": None,
                    "qc_passed": False,
                    "qc_ready": False,
                    "qc_error_reason": str(exc),
                    "qc_error_at": datetime.now(timezone.utc).isoformat(),
                    "launch_score": 0.0,
                    "featured_candidate": False,
                    "campaign_priority": "blocked",
                    "store_ready": False,
                    "store_ready_at": None,
                }}
            )
            summary["processed"] += 1

    if summary["processed"]:
        summary["average_score"] = round(total_score / summary["processed"], 1)

    return summary


# ---------------------------------------------------------------------------
# Cycle management
# ---------------------------------------------------------------------------

@router.get("/cycle/status")
async def get_cycle_status(http_request: Request):
    """
    Return status of the automated product generation cycle.
    """
    db = _get_database(http_request)
    scheduler = get_cycle_scheduler(db)
    return scheduler.status


@router.post("/cycle/trigger")
async def trigger_cycle_now(background_tasks: BackgroundTasks, http_request: Request):
    """
    Manually trigger a product generation cycle immediately.
    The cycle runs in the background — returns immediately.
    """
    db = _get_database(http_request)
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    scheduler = get_cycle_scheduler(db)
    background_tasks.add_task(scheduler._run_cycle)

    return {
        "message": f"Product generation cycle started — generating minimum {10} products",
        "interval_hours": 2,
    }


@router.get("/cycle/history")
async def get_cycle_history(http_request: Request, limit: int = 20):
    """
    Return history of completed generation cycles.
    """
    db = _get_database(http_request)
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    cursor = db["product_cycles"].find({}).sort("started_at", -1).limit(limit)
    cycles = []
    async for c in cursor:
        if "_id" in c:
            del c["_id"]
        # Convert datetime objects for JSON serialization
        for key in ("started_at", "completed_at"):
            if isinstance(c.get(key), datetime):
                c[key] = c[key].isoformat()
        cycles.append(c)

    return cycles
