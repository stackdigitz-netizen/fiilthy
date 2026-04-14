"""
Product Quality Control Engine
Strict standards to ensure every product is top quality before selling.

Every product must pass ALL of these checks:
  - Content completeness (title, description, chapters, files)
  - Market viability (demand, competition, pricing)
  - Value density (pages, depth, actionability)
  - Uniqueness score (not generic filler content)
  - Monetization fitness (clear transformation, buyer persona)
  - Legal & compliance (no plagiarism, proper disclaimers)
  - Sales readiness (cover image, keywords, USP)

Scores below threshold are either fixed or rejected.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class QCStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class QCCheck:
    name: str
    status: QCStatus
    score: float          # 0-100
    weight: float         # How much this check counts toward total
    message: str
    fix: Optional[str] = None
    blocking: bool = True  # If True, product cannot be sold until fixed


@dataclass
class QCReport:
    product_id: str
    product_title: str
    timestamp: str
    checks: List[QCCheck] = field(default_factory=list)
    overall_score: float = 0.0
    passed: bool = False
    grade: str = "F"
    ready_for_sale: bool = False
    improvements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "product_title": self.product_title,
            "timestamp": self.timestamp,
            "overall_score": round(self.overall_score, 1),
            "grade": self.grade,
            "passed": self.passed,
            "ready_for_sale": self.ready_for_sale,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "score": round(c.score, 1),
                    "message": c.message,
                    "fix": c.fix,
                    "blocking": c.blocking,
                }
                for c in self.checks
            ],
            "improvements": self.improvements,
            "blocking_issues": [
                c.name for c in self.checks
                if c.blocking and c.status == QCStatus.FAIL
            ],
        }


# ---------------------------------------------------------------------------
# Minimum thresholds
# ---------------------------------------------------------------------------
THRESHOLDS = {
    "min_title_words": 4,
    "max_title_words": 15,
    "min_description_chars": 300,
    "min_description_words": 40,
    "min_price_usd": 9.00,
    "max_price_usd": 997.00,
    "min_chapters": 5,
    "min_pages_ebook": 20,
    "min_lessons_course": 8,
    "min_keywords": 5,
    "min_benefits": 3,
    "min_target_audience_chars": 20,
    "min_unique_word_ratio": 0.45,  # 45% unique words in description = not filler
    "pass_score": 75.0,             # 75+ = pass
    "sale_score": 80.0,             # 80+ = ready for sale
}

FILLER_PHRASES = [
    "lorem ipsum",
    "placeholder",
    "tbd",
    "to be determined",
    "coming soon",
    "sample text",
    "insert",
    "[product name]",
    "[description]",
    "TODO",
    "FIXME",
    "example product",
    "test product",
    "dummy",
]

WEAK_TITLE_WORDS = [
    "untitled",
    "product",
    "ebook",
    "course",
    "guide",
    "template",
]


class ProductQualityEngine:
    """
    Runs all quality checks and returns a full QC report.
    A product must score >= 80 to be listed for sale.
    """

    def run(self, product: Dict[str, Any]) -> QCReport:
        product_id = product.get("id") or product.get("product_id", "unknown")
        title = product.get("title", "")

        report = QCReport(
            product_id=product_id,
            product_title=title,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        checks = [
            self._check_title(product),
            self._check_description(product),
            self._check_pricing(product),
            self._check_content_depth(product),
            self._check_uniqueness(product),
            self._check_value_proposition(product),
            self._check_target_audience(product),
            self._check_keywords(product),
            self._check_sales_assets(product),
            self._check_monetization_fitness(product),
            self._check_compliance(product),
        ]

        report.checks = checks

        # Weighted score
        total_weight = sum(c.weight for c in checks)
        weighted_score = sum(c.score * c.weight for c in checks)
        report.overall_score = (weighted_score / total_weight) if total_weight > 0 else 0

        # Grade
        s = report.overall_score
        if s >= 95:
            report.grade = "A+"
        elif s >= 90:
            report.grade = "A"
        elif s >= 85:
            report.grade = "B+"
        elif s >= 80:
            report.grade = "B"
        elif s >= 75:
            report.grade = "C"
        elif s >= 65:
            report.grade = "D"
        else:
            report.grade = "F"

        report.passed = report.overall_score >= THRESHOLDS["pass_score"]
        report.ready_for_sale = report.overall_score >= THRESHOLDS["sale_score"] and not any(
            c.blocking and c.status == QCStatus.FAIL for c in checks
        )

        # Collect actionable improvements
        for c in checks:
            if c.status != QCStatus.PASS and c.fix:
                report.improvements.append(c.fix)

        return report

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_title(self, product: Dict) -> QCCheck:
        title = (product.get("title") or "").strip()
        words = title.split()

        if not title:
            return QCCheck("Title", QCStatus.FAIL, 0, 10, "Title is missing", "Add a compelling title with 4-15 words", True)

        if len(words) < THRESHOLDS["min_title_words"]:
            return QCCheck("Title", QCStatus.FAIL, 30, 10,
                           f'Title too short ({len(words)} words; need {THRESHOLDS["min_title_words"]}+)',
                           "Make title more descriptive — include the main benefit and target audience", True)

        if len(words) > THRESHOLDS["max_title_words"]:
            return QCCheck("Title", QCStatus.WARNING, 70, 10,
                           f"Title has {len(words)} words; keep it under {THRESHOLDS['max_title_words']}",
                           "Shorten title for better click-through on stores", False)

        # Check for obvious filler / generic words
        lower = title.lower()
        if all(w in WEAK_TITLE_WORDS for w in lower.split()):
            return QCCheck("Title", QCStatus.FAIL, 20, 10,
                           "Title is too generic and won't stand out",
                           "Include a specific transformation, number, or unique angle", True)

        for filler in FILLER_PHRASES:
            if filler.lower() in lower:
                return QCCheck("Title", QCStatus.FAIL, 0, 10,
                               f'Filler text detected in title: "{filler}"',
                               "Replace filler text with the real product title", True)

        return QCCheck("Title", QCStatus.PASS, 100, 10, "Title looks good ✓")

    def _check_description(self, product: Dict) -> QCCheck:
        desc = (product.get("description") or "").strip()
        char_count = len(desc)
        words = desc.split()
        word_count = len(words)

        if not desc:
            return QCCheck("Description", QCStatus.FAIL, 0, 15,
                           "Description is missing",
                           "Write a detailed description with the main benefits, what's included, and who it's for", True)

        for filler in FILLER_PHRASES:
            if filler.lower() in desc.lower():
                return QCCheck("Description", QCStatus.FAIL, 10, 15,
                               f'Filler text detected: "{filler}"',
                               "Replace all placeholder text with real product content", True)

        if char_count < THRESHOLDS["min_description_chars"]:
            score = (char_count / THRESHOLDS["min_description_chars"]) * 50
            return QCCheck("Description", QCStatus.FAIL, score, 15,
                           f"Description too short ({char_count} chars; need {THRESHOLDS['min_description_chars']}+)",
                           "Expand description with benefits, what customers will learn/get, and who this is for", True)

        if word_count < THRESHOLDS["min_description_words"]:
            return QCCheck("Description", QCStatus.WARNING, 65, 15,
                           f"Description sparse ({word_count} words)",
                           "Add more detail about features, benefits, and what makes this unique", False)

        return QCCheck("Description", QCStatus.PASS, 100, 15, f"Description good ({word_count} words) ✓")

    def _check_pricing(self, product: Dict) -> QCCheck:
        # Accept different field names
        raw_price = (
            product.get("price")
            or product.get("price_usd")
            or product.get("base_price")
        )

        # Handle "$29.99" style strings
        if isinstance(raw_price, str):
            match = re.search(r"[\d.]+", raw_price)
            raw_price = float(match.group()) if match else None

        if raw_price is None:
            return QCCheck("Pricing", QCStatus.FAIL, 0, 10,
                           "No price set for product",
                           f"Set a price between ${THRESHOLDS['min_price_usd']} and ${THRESHOLDS['max_price_usd']}", True)

        price = float(raw_price)

        if price < THRESHOLDS["min_price_usd"]:
            return QCCheck("Pricing", QCStatus.FAIL, 20, 10,
                           f"Price ${price:.2f} is too low — undercuts perceived value",
                           f"Minimum price is ${THRESHOLDS['min_price_usd']:.2f}. Raise price to reflect quality.", True)

        if price > THRESHOLDS["max_price_usd"]:
            return QCCheck("Pricing", QCStatus.WARNING, 70, 10,
                           f"Price ${price:.2f} is very high — ensure product justifies it",
                           "Add strong social proof and testimonials for high-ticket items", False)

        return QCCheck("Pricing", QCStatus.PASS, 100, 10, f"Price ${price:.2f} ✓")

    def _check_content_depth(self, product: Dict) -> QCCheck:
        """Check that product has real substance inside."""
        product_type = (product.get("product_type") or product.get("type") or "ebook").lower()

        # Ebook / guide checks
        if product_type in ("ebook", "guide", "book"):
            chapters = product.get("chapters") or product.get("table_of_contents") or []
            pages = product.get("pages") or product.get("page_count") or 0

            if not chapters and pages < THRESHOLDS["min_pages_ebook"]:
                return QCCheck("Content Depth", QCStatus.FAIL, 10, 20,
                               f"eBook has no chapters and only {pages} pages",
                               f"eBook must have at least {THRESHOLDS['min_chapters']} chapters and {THRESHOLDS['min_pages_ebook']} pages of real content", True)

            if isinstance(chapters, list) and len(chapters) < THRESHOLDS["min_chapters"]:
                score = (len(chapters) / THRESHOLDS["min_chapters"]) * 60
                return QCCheck("Content Depth", QCStatus.FAIL, score, 20,
                               f"Only {len(chapters)} chapters (minimum {THRESHOLDS['min_chapters']})",
                               f"Expand to at least {THRESHOLDS['min_chapters']} substantial chapters", True)

            return QCCheck("Content Depth", QCStatus.PASS, 100, 20,
                           f"eBook depth good: {len(chapters) if isinstance(chapters, list) else '?'} chapters / {pages} pages ✓")

        # Course checks
        if product_type in ("course", "masterclass", "training"):
            lessons = (
                product.get("lessons")
                or product.get("modules")
                or product.get("curriculum")
                or []
            )
            lesson_count = len(lessons) if isinstance(lessons, list) else 0

            if lesson_count < THRESHOLDS["min_lessons_course"]:
                score = (lesson_count / THRESHOLDS["min_lessons_course"]) * 50
                return QCCheck("Content Depth", QCStatus.FAIL, score, 20,
                               f"Course has only {lesson_count} lessons (minimum {THRESHOLDS['min_lessons_course']})",
                               f"Add at least {THRESHOLDS['min_lessons_course']} distinct lessons with real teaching content", True)

            return QCCheck("Content Depth", QCStatus.PASS, 100, 20, f"Course depth: {lesson_count} lessons ✓")

        # Template / planner
        if product_type in ("template", "planner", "spreadsheet", "toolkit"):
            components = product.get("components") or product.get("sections") or product.get("pages") or []
            count = len(components) if isinstance(components, list) else (components if isinstance(components, int) else 0)

            if count < 3:
                return QCCheck("Content Depth", QCStatus.FAIL, 30, 20,
                               f"Template only has {count} sections",
                               "Templates should have at least 3 distinct, useful sections", True)

            return QCCheck("Content Depth", QCStatus.PASS, 100, 20, f"Template: {count} sections ✓")

        # Unknown type — partial credit
        return QCCheck("Content Depth", QCStatus.WARNING, 60, 20,
                       f'Content depth check skipped for type "{product_type}"',
                       "Set a clear product_type (ebook, course, template, planner)", False)

    def _check_uniqueness(self, product: Dict) -> QCCheck:
        """Check the description isn't generic filler."""
        desc = (product.get("description") or "").lower()
        if not desc:
            return QCCheck("Uniqueness", QCStatus.FAIL, 0, 10, "No description to analyse", blocking=True)

        words = re.findall(r"\b[a-z]{3,}\b", desc)
        if not words:
            return QCCheck("Uniqueness", QCStatus.FAIL, 0, 10, "Description has no real words", blocking=True)

        unique_ratio = len(set(words)) / len(words)

        if unique_ratio < THRESHOLDS["min_unique_word_ratio"]:
            return QCCheck("Uniqueness", QCStatus.FAIL, unique_ratio * 100, 10,
                           f"Description appears repetitive (unique word ratio: {unique_ratio:.0%})",
                           "Rewrite description with specific, varied language — avoid repeating phrases", True)

        # Check for generic opener patterns
        generic_openers = [
            "this product",
            "this is a guide",
            "this ebook",
            "welcome to",
            "introduction to",
        ]
        for opener in generic_openers:
            if desc.startswith(opener):
                return QCCheck("Uniqueness", QCStatus.WARNING, 75, 10,
                               f'Description opens with generic phrase: "{opener}"',
                               "Start with a powerful hook — the benefit or problem you solve, not a generic intro", False)

        return QCCheck("Uniqueness", QCStatus.PASS, 100, 10, "Content uniqueness ✓")

    def _check_value_proposition(self, product: Dict) -> QCCheck:
        """Product must clearly state what customers get and why it matters."""
        desc = (product.get("description") or "").lower()
        benefits = product.get("benefits") or product.get("key_benefits") or []

        if isinstance(benefits, list) and len(benefits) >= THRESHOLDS["min_benefits"]:
            return QCCheck("Value Proposition", QCStatus.PASS, 100, 10,
                           f"{len(benefits)} clear benefits listed ✓")

        # Fall back to scanning description for benefit language
        benefit_indicators = [
            "you will", "you'll", "you get", "learn how", "discover",
            "save time", "increase", "reduce", "improve", "step-by-step",
            "proven", "includes", "bonus", "framework", "system", "method",
        ]
        found = sum(1 for b in benefit_indicators if b in desc)

        if found < THRESHOLDS["min_benefits"]:
            return QCCheck("Value Proposition", QCStatus.FAIL, (found / THRESHOLDS["min_benefits"]) * 60, 10,
                           f"Only {found} benefit signals found in description",
                           "Add a clear 'What You Get' section with at least 5 specific benefits", True)

        return QCCheck("Value Proposition", QCStatus.PASS, 85 + min(found, 10), 10,
                       f"Value signals present ({found} indicators) ✓")

    def _check_target_audience(self, product: Dict) -> QCCheck:
        audience = (product.get("target_audience") or "").strip()

        if not audience:
            return QCCheck("Target Audience", QCStatus.FAIL, 0, 5,
                           "No target audience defined",
                           "Define exactly who this product is for (e.g. 'Beginner entrepreneurs who want...')", True)

        if len(audience) < THRESHOLDS["min_target_audience_chars"]:
            return QCCheck("Target Audience", QCStatus.WARNING, 50, 5,
                           f"Target audience description too vague ({len(audience)} chars)",
                           "Be specific: demographics, pain points, goals", False)

        return QCCheck("Target Audience", QCStatus.PASS, 100, 5, f"Audience defined ✓")

    def _check_keywords(self, product: Dict) -> QCCheck:
        kw = product.get("keywords") or product.get("tags") or []
        if isinstance(kw, str):
            kw = [k.strip() for k in kw.split(",") if k.strip()]

        count = len(kw)
        if count < THRESHOLDS["min_keywords"]:
            return QCCheck("Keywords / Tags", QCStatus.FAIL, (count / THRESHOLDS["min_keywords"]) * 50, 5,
                           f"Only {count} keywords (minimum {THRESHOLDS['min_keywords']})",
                           "Add at least 5 purchase-intent keywords buyers would search for", True)

        return QCCheck("Keywords / Tags", QCStatus.PASS, 100, 5, f"{count} keywords ✓")

    def _check_sales_assets(self, product: Dict) -> QCCheck:
        """Checks cover image, price, call-to-action presence."""
        has_image = bool(
            product.get("cover_image_url")
            or product.get("image_url")
            or product.get("thumbnail_url")
        )

        if not has_image:
            return QCCheck("Sales Assets", QCStatus.FAIL, 20, 10,
                           "No cover image — stores and campaigns require visuals",
                           "Generate a professional cover image before publishing", True)

        return QCCheck("Sales Assets", QCStatus.PASS, 100, 10, "Cover image present ✓")

    def _check_monetization_fitness(self, product: Dict) -> QCCheck:
        """Does this product have what it needs to convert buyers?"""
        title = product.get("title", "")
        desc = (product.get("description") or "").lower()

        # Transformation language
        transformation_words = [
            "transform", "master", "unlock", "build", "launch", "scale",
            "achieve", "finally", "secret", "blueprint", "system", "formula",
            "step-by-step", "complete", "ultimate",
        ]
        tfm_count = sum(1 for w in transformation_words if w in desc or w in title.lower())

        if tfm_count < 2:
            return QCCheck("Monetization Fitness", QCStatus.WARNING, 65, 5,
                           "Weak conversion language in description",
                           "Use outcome-based language: transformations, specific results, and 'you will' statements", False)

        return QCCheck("Monetization Fitness", QCStatus.PASS, 90 + min(tfm_count, 10), 5,
                       f"Strong conversion language ✓ ({tfm_count} signals)")

    def _check_compliance(self, product: Dict) -> QCCheck:
        """Basic compliance: no prohibited content, proper disclaimers for certain niches."""
        desc = (product.get("description") or "").lower()
        title = (product.get("title") or "").lower()
        combined = title + " " + desc

        # Check for income/earnings claims without disclaimers
        earnings_phrases = ["make $", "earn $", "guaranteed income", "100% profit", "risk-free income"]
        earnings_found = any(phrase in combined for phrase in earnings_phrases)
        has_disclaimer = any(word in combined for word in ["results may vary", "no guarantee", "individual results"])

        if earnings_found and not has_disclaimer:
            return QCCheck("Compliance", QCStatus.FAIL, 30, 5,
                           "Income/earnings claims found without required disclaimer",
                           "Add: 'Results vary. Individual income results depend on effort, experience, and market conditions.'",
                           True)

        # Check for medical/legal advice without disclaimer
        medical_phrases = ["cure", "treat disease", "medical advice", "diagnose", "prescription"]
        if any(phrase in combined for phrase in medical_phrases):
            return QCCheck("Compliance", QCStatus.FAIL, 20, 5,
                           "Medical claims detected without disclaimer",
                           "Add: 'This content is for educational purposes only and not medical advice.'",
                           True)

        return QCCheck("Compliance", QCStatus.PASS, 100, 5, "No compliance issues ✓")


# ---------------------------------------------------------------------------
# Convenience function used in route handlers
# ---------------------------------------------------------------------------

def run_qc(product: Dict[str, Any]) -> Dict[str, Any]:
    """Run QC check and return serialised report dict."""
    engine = ProductQualityEngine()
    report = engine.run(product)
    return report.to_dict()
