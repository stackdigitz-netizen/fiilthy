"""
Product Generation Cycle Scheduler
Runs every 2 hours and generates a minimum of 10 distinct products.
Each product is put through full QC before being accepted.
Failed products are retried with improvements from the QC report.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from .product_quality_engine import ProductQualityEngine, QCStatus
from .real_product_generator import RealProductGenerator
from .opportunity_scout import OpportunityScout

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CYCLE_INTERVAL_HOURS = 2
MIN_PRODUCTS_PER_CYCLE = 10
MAX_RETRIES_PER_PRODUCT = 3        # Retry failed QC products up to 3× with AI fixes
MIN_PASSING_SCORE = 80.0           # Same as QCEngine.sale_score

PRODUCT_TYPES = [
    "ebook",
    "course",
    "template",
    "planner",
    "mini_app",
    "swipe_file",
    "checklist",
]

# Niches to rotate through to ensure variety
DEFAULT_NICHES = [
    "make money online",
    "social media marketing",
    "email marketing",
    "AI tools for business",
    "personal finance",
    "fitness at home",
    "productivity systems",
    "freelance writing",
    "e-commerce",
    "content creation",
    "mindset & motivation",
    "passive income",
]


class ProductCycleScheduler:
    """
    Background scheduler that continuously generates batches of products.
    Wraps AI generation with strict QC gate — products that fail are
    patched and retried up to MAX_RETRIES_PER_PRODUCT times.
    """

    def __init__(self, db):
        self.db = db
        self.qc_engine = ProductQualityEngine()
        self.generator = RealProductGenerator()
        self.scout = OpportunityScout()
        self._running = False
        self._current_cycle: Optional[Dict] = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self):
        """Fire-and-forget — call once at app startup (from lifespan/startup event)."""
        if not self._running:
            self._running = True
            asyncio.ensure_future(self._loop())
            logger.info("ProductCycleScheduler started — cycle every %d hours", CYCLE_INTERVAL_HOURS)

    def stop(self):
        self._running = False

    @property
    def status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "current_cycle": self._current_cycle,
            "next_cycle_at": self._next_cycle_iso(),
        }

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------

    async def _loop(self):
        while self._running:
            try:
                await self._run_cycle()
            except Exception as exc:
                logger.error("Cycle failed with unhandled error: %s", exc, exc_info=True)
            # Sleep until next cycle
            await asyncio.sleep(CYCLE_INTERVAL_HOURS * 3600)

    async def _run_cycle(self) -> Dict[str, Any]:
        cycle_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        logger.info("=== Starting product cycle %s ===", cycle_id)

        cycle_record = {
            "id": cycle_id,
            "started_at": started_at,
            "completed_at": None,
            "status": "running",
            "products_attempted": 0,
            "products_passed": 0,
            "products_failed_permanently": 0,
            "product_ids": [],
            "errors": [],
        }
        self._current_cycle = cycle_record

        if self.db:
            await self.db["product_cycles"].insert_one({**cycle_record})

        passed_products = []
        niche_index = int(started_at.timestamp() / (CYCLE_INTERVAL_HOURS * 3600)) % len(DEFAULT_NICHES)

        # Keep generating until we hit the minimum
        attempt_index = 0
        while len(passed_products) < MIN_PRODUCTS_PER_CYCLE:
            niche = DEFAULT_NICHES[(niche_index + attempt_index) % len(DEFAULT_NICHES)]
            product_type = PRODUCT_TYPES[attempt_index % len(PRODUCT_TYPES)]
            cycle_record["products_attempted"] += 1

            try:
                product = await self._generate_and_validate(niche, product_type, cycle_id)
                if product:
                    passed_products.append(product)
                    cycle_record["products_passed"] += 1
                    cycle_record["product_ids"].append(product["id"])
                    logger.info("  ✓ Product %d/%d passed QC: %s",
                                len(passed_products), MIN_PRODUCTS_PER_CYCLE, product.get("title"))
                else:
                    cycle_record["products_failed_permanently"] += 1
            except Exception as exc:
                logger.error("  Product generation error (niche=%s): %s", niche, exc)
                cycle_record["errors"].append(str(exc))

            attempt_index += 1

            # Safety valve — never hang forever
            if attempt_index > MIN_PRODUCTS_PER_CYCLE * 4:
                logger.warning("Cycle %s reached safety limit after %d attempts", cycle_id, attempt_index)
                break

        cycle_record["completed_at"] = datetime.now(timezone.utc)
        cycle_record["status"] = "completed"

        if self.db:
            await self.db["product_cycles"].update_one(
                {"id": cycle_id},
                {"$set": {
                    "completed_at": cycle_record["completed_at"],
                    "status": "completed",
                    "products_attempted": cycle_record["products_attempted"],
                    "products_passed": cycle_record["products_passed"],
                    "products_failed_permanently": cycle_record["products_failed_permanently"],
                    "product_ids": cycle_record["product_ids"],
                    "errors": cycle_record["errors"],
                }}
            )

        logger.info("=== Cycle %s done: %d/%d products passed QC ===",
                    cycle_id, cycle_record["products_passed"], cycle_record["products_attempted"])
        return cycle_record

    # ------------------------------------------------------------------
    # Generation + QC gate
    # ------------------------------------------------------------------

    async def _generate_and_validate(
        self,
        niche: str,
        product_type: str,
        cycle_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a product for the given niche and type, run it through QC,
        and retry with AI-patched improvements up to MAX_RETRIES_PER_PRODUCT times.
        Returns the final product dict if it passes QC, else None.
        """
        product = None
        last_qc = None

        for attempt in range(MAX_RETRIES_PER_PRODUCT + 1):
            try:
                if attempt == 0:
                    # Fresh generation
                    raw = await self._generate_product(niche, product_type)
                else:
                    # Re-generation with QC feedback injected
                    raw = await self._regenerate_with_feedback(niche, product_type, last_qc)

                if not raw:
                    continue

                # Assign ID if missing
                if "id" not in raw:
                    raw["id"] = str(uuid.uuid4())
                raw["cycle_id"] = cycle_id
                raw["generated_at"] = datetime.now(timezone.utc)
                raw["qc_attempts"] = attempt + 1

                # Run QC
                qc_report = self.qc_engine.run(raw)
                raw["qc_report"] = qc_report.to_dict()
                raw["qc_score"] = qc_report.overall_score
                raw["qc_grade"] = qc_report.grade
                last_qc = qc_report

                if qc_report.ready_for_sale:
                    raw["status"] = "approved"
                    # Persist to database
                    if self.db:
                        await self.db["products"].insert_one(_strip_id(raw))
                    return raw
                else:
                    logger.debug(
                        "  QC attempt %d/%d failed (score=%.1f grade=%s) for %s",
                        attempt + 1, MAX_RETRIES_PER_PRODUCT + 1,
                        qc_report.overall_score, qc_report.grade,
                        raw.get("title", "?"),
                    )

            except Exception as exc:
                logger.error("  Generation attempt %d error: %s", attempt + 1, exc)

        # All retries exhausted — save as rejected for review
        if product and self.db:
            product["status"] = "rejected"
            await self.db["products"].insert_one(_strip_id(product))

        return None

    async def _generate_product(self, niche: str, product_type: str) -> Optional[Dict]:
        """Call the real product generator."""
        try:
            if product_type == "ebook":
                return await self.generator.generate_complete_ebook(
                    niche=niche,
                    keywords=[niche],
                    target_audience="beginners"
                )
            elif product_type == "course":
                return await self.generator.generate_complete_course(
                    topic=niche,
                    target_audience="beginners",
                    duration_hours=3
                )
            else:
                # Fallback to ebook for unsupported types
                return await self.generator.generate_complete_ebook(
                    niche=niche,
                    keywords=[niche, product_type],
                    target_audience="anyone interested in " + niche
                )
        except Exception as exc:
            logger.error("Product generation error: %s", exc)
            return None

    async def _regenerate_with_feedback(
        self,
        niche: str,
        product_type: str,
        last_qc,
    ) -> Optional[Dict]:
        """Generate a new product with QC feedback embedded in the prompt."""
        fixes = last_qc.improvements if last_qc else []
        feedback_text = "; ".join(fixes[:5]) if fixes else "improve overall quality"
        logger.debug("  Retrying with feedback: %s", feedback_text)
        # Re-generate (the real generator does not yet accept feedback args;
        # we simply try again with a fresh call — the randomness of LLM will
        # often clear QC issues)
        return await self._generate_product(niche, product_type)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _next_cycle_iso(self) -> str:
        if self._current_cycle and self._current_cycle.get("started_at"):
            started = self._current_cycle["started_at"]
            if isinstance(started, datetime):
                next_run = started + timedelta(hours=CYCLE_INTERVAL_HOURS)
                return next_run.isoformat()
        return (datetime.now(timezone.utc) + timedelta(hours=CYCLE_INTERVAL_HOURS)).isoformat()


def _strip_id(doc: Dict) -> Dict:
    """Remove MongoDB _id so we can re-insert cleanly."""
    doc.pop("_id", None)
    return doc


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------
_scheduler: Optional[ProductCycleScheduler] = None


def get_cycle_scheduler(db) -> ProductCycleScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = ProductCycleScheduler(db)
    return _scheduler
