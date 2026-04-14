"""
Quality Control & Production Cycle Routes
Exposes endpoints for running QC checks, viewing cycle history,
and manually triggering a generation cycle.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

from ai_services.product_quality_engine import run_qc, THRESHOLDS
from ai_services.product_cycle_scheduler import get_cycle_scheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quality", tags=["quality-control"])


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class QCRequest(BaseModel):
    product_id: Optional[str] = None
    product: Optional[Dict[str, Any]] = None  # inline product data


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/check")
async def run_quality_check(request: QCRequest, db=None):
    """
    Run a quality check against a product.
    Pass either product_id (fetches from DB) or inline product data.
    Returns a full QC report with score, grade, and actionable fixes.
    """
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
async def list_products_with_qc(status: Optional[str] = None, db=None):
    """
    List all products with their QC scores.
    Filter by status: approved | rejected | pending
    """
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


# ---------------------------------------------------------------------------
# Cycle management
# ---------------------------------------------------------------------------

@router.get("/cycle/status")
async def get_cycle_status(db=None):
    """
    Return status of the automated product generation cycle.
    """
    scheduler = get_cycle_scheduler(db)
    return scheduler.status


@router.post("/cycle/trigger")
async def trigger_cycle_now(background_tasks: BackgroundTasks, db=None):
    """
    Manually trigger a product generation cycle immediately.
    The cycle runs in the background — returns immediately.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    scheduler = get_cycle_scheduler(db)
    background_tasks.add_task(scheduler._run_cycle)

    return {
        "message": f"Product generation cycle started — generating minimum {10} products",
        "interval_hours": 2,
    }


@router.get("/cycle/history")
async def get_cycle_history(limit: int = 20, db=None):
    """
    Return history of completed generation cycles.
    """
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
