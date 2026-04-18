#!/usr/bin/env python3
"""
Generate a complete Ad Campaign Pack for every provided product.

Sources, in priority order:
1. --input JSON file
2. --api-url local/remote API
3. Direct MongoDB connection using repo config
4. Built-in sample products

Outputs:
- JSON export with a structured campaign pack for every product
- Markdown export with the same campaign packs in a readable format
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "ceo" / "backend"
EXPORT_DIR = ROOT_DIR / "exports" / "ad_campaign_packs"

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - defensive fallback
    load_dotenv = None

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:  # pragma: no cover - defensive fallback
    MongoClient = None
    PyMongoError = Exception

try:
    import certifi
except ImportError:  # pragma: no cover - defensive fallback
    certifi = None

try:
    from config.keys_manager import keys_manager
except Exception:  # pragma: no cover - local CLI should still work without key manager
    keys_manager = None


FALLBACK_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "flagship-ai-offer-engine",
        "title": "AI Offer Engine for Solo Operators",
        "subtitle": "Create a high-converting offer, even if you've never sold anything before.",
        "description": "Turn one skill into a premium digital offer, a fast checkout flow, and an AI-assisted sales engine you can run without a team.",
        "benefits": [
            "Turn an idea into something people will pay for",
            "Create offers that actually convert",
            "Launch faster without guessing",
        ],
        "includes": [
            "High-ticket offer design worksheet",
            "AI prompts for positioning and sales copy",
            "7-day launch sprint plan",
            "Delivery and fulfillment checklist",
            "Upsell and retention framework",
        ],
        "perfect_for": ["Solo operators", "Service providers", "Experts packaging knowledge"],
        "cta": "Start Building Your Offer Today",
        "price": 79.0,
        "originalPrice": 149.0,
        "type": "blueprint",
        "product_type": "ebook",
        "tags": ["AI", "Offers", "Sales", "Solo Operator"],
        "status": "published",
        "rating": 4.9,
        "reviews": 0,
        "downloads": 0,
    },
    {
        "id": "fiilthy-002",
        "title": "Digital Product Launch Playbook",
        "subtitle": "Launch profitable digital products in 7 days with AI.",
        "description": "Launch profitable digital products in 7 days with AI. The exact playbook used to generate $50K+ in launches.",
        "benefits": [
            "Launch products that actually sell",
            "Use AI to speed up your process",
            "Follow a proven 7-day framework",
            "Generate revenue faster",
        ],
        "includes": [
            "127-point launch checklist",
            "5-part email funnel sequences",
            "40+ social media templates",
            "Pricing and positioning guide",
            "Competitor research framework",
        ],
        "perfect_for": ["Creators", "Operators", "Founders with product ideas"],
        "cta": "Launch Your First Product Today",
        "price": 49.0,
        "originalPrice": 99.0,
        "type": "template",
        "product_type": "template",
        "tags": ["Digital Products", "Launch", "Marketing"],
        "status": "published",
        "rating": 4.8,
        "reviews": 32,
        "downloads": 920,
    },
    {
        "id": "fiilthy-003",
        "title": "TikTok Affiliate Money Machine",
        "subtitle": "Earn $1K-$5K per month with TikTok affiliate marketing.",
        "description": "Earn $1K-$5K per month with TikTok affiliate marketing. No face, no followers, no experience needed.",
        "benefits": [
            "Make money on TikTok without being on camera",
            "Use proven affiliate formats",
            "Start with simple scripts and repeatable workflows",
        ],
        "includes": [
            "30 done-for-you video scripts",
            "Affiliate niche finder tool",
            "Analytics tracker template",
            "1,000 viral hashtag database",
            "Niche selection masterclass",
        ],
        "perfect_for": ["Side hustlers", "Beginners", "People avoiding on-camera content"],
        "cta": "Start Making Money on TikTok",
        "price": 37.0,
        "originalPrice": 77.0,
        "type": "course",
        "product_type": "course",
        "tags": ["TikTok", "Affiliate", "Social Media"],
        "status": "published",
        "rating": 4.7,
        "reviews": 89,
        "downloads": 2100,
    },
    {
        "id": "fiilthy-004",
        "title": "ChatGPT Business Command Pack",
        "subtitle": "500+ battle-tested prompts for entrepreneurs.",
        "description": "500+ battle-tested ChatGPT prompts for entrepreneurs. Create content, ads, emails, and sales copy in seconds.",
        "benefits": [
            "Save hours on copy and content creation",
            "Generate stronger ads and emails faster",
            "Scale output without hiring more people",
        ],
        "includes": [
            "500+ categorised prompts",
            "Prompt engineering guide",
            "Email marketing swipe file",
            "Social media caption pack",
            "Sales page template library",
        ],
        "perfect_for": ["Entrepreneurs", "Marketers", "Agencies", "Creators"],
        "cta": "Get Professional Copy Instantly",
        "price": 27.0,
        "originalPrice": 57.0,
        "type": "tool",
        "product_type": "template",
        "tags": ["ChatGPT", "AI", "Prompts", "Business"],
        "status": "published",
        "rating": 4.9,
        "reviews": 156,
        "downloads": 4200,
    },
]


def load_env() -> None:
    if load_dotenv is None:
        return
    load_dotenv(ROOT_DIR / ".env")
    load_dotenv(BACKEND_DIR / ".env")


def clean_env_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def resolve_mongo_url() -> Optional[str]:
    candidates = []
    if keys_manager is not None:
        try:
            candidates.append(clean_env_value(keys_manager.get_key("mongodb_url")))
        except Exception:
            pass
    candidates.extend([
        clean_env_value(os.environ.get("MONGO_URI")),
        clean_env_value(os.environ.get("MONGO_URL")),
    ])

    for candidate in candidates:
        if not candidate:
            continue
        lowered = candidate.lower()
        if "atlas-sql-" in lowered or ".query.mongodb.net" in lowered:
            continue
        return candidate
    return None


def resolve_db_name() -> str:
    return (
        clean_env_value(os.environ.get("DB_NAME"))
        or clean_env_value(os.environ.get("MONGO_DB_NAME"))
        or "ceo_ai"
    )


def normalize_list(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        if not value.strip():
            return []
        return [part.strip() for part in re.split(r"[,\n|]", value) if part.strip()]
    return [str(value).strip()]


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "product"


def compact_text(*parts: Optional[str]) -> str:
    text = " ".join(part.strip() for part in parts if part and part.strip())
    return re.sub(r"\s+", " ", text).strip()


def normalize_product(product: Dict[str, Any]) -> Dict[str, Any]:
    title = compact_text(str(product.get("title") or product.get("name") or "Untitled Product"))
    description = compact_text(
        str(product.get("description") or ""),
        str(product.get("subtitle") or ""),
    )
    normalized = {
        "id": str(product.get("id") or slugify(title)),
        "title": title,
        "subtitle": compact_text(str(product.get("subtitle") or "")),
        "description": description,
        "benefits": normalize_list(product.get("benefits")),
        "includes": normalize_list(product.get("includes") or product.get("features")),
        "perfect_for": normalize_list(product.get("perfect_for") or product.get("ideal_customer")),
        "cta": compact_text(str(product.get("cta") or "Tap the link and get instant access")),
        "price": safe_float(product.get("price"), 29.0),
        "original_price": safe_float(product.get("originalPrice") or product.get("original_price"), 0.0),
        "type": compact_text(str(product.get("type") or product.get("product_type") or "digital product")),
        "product_type": compact_text(str(product.get("product_type") or product.get("type") or "digital product")),
        "tags": normalize_list(product.get("tags") or product.get("keywords")),
        "status": compact_text(str(product.get("status") or "draft")),
        "rating": safe_float(product.get("rating"), 0.0),
        "reviews": safe_int(product.get("reviews"), 0),
        "downloads": safe_int(product.get("downloads"), 0),
        "revenue": safe_float(product.get("revenue"), 0.0),
    }
    if not normalized["benefits"] and normalized["description"]:
        normalized["benefits"] = [normalized["description"]]
    return normalized


def load_products_from_json(path: Path) -> Tuple[List[Dict[str, Any]], str]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        raw_products = payload.get("products") or payload.get("items") or payload.get("data") or []
    else:
        raw_products = payload
    return [normalize_product(item) for item in raw_products], f"json:{path.name}"


def load_products_from_api(api_url: str, limit: Optional[int]) -> Tuple[List[Dict[str, Any]], str]:
    normalized_base = api_url.rstrip("/")
    if not normalized_base.endswith("/api/products"):
        if normalized_base.endswith("/api"):
            normalized_base = f"{normalized_base}/products"
        else:
            normalized_base = f"{normalized_base}/api/products"

    query_limit = limit or 5000
    url = f"{normalized_base}?limit={query_limit}"
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return [normalize_product(item) for item in payload], f"api:{url}"


def load_products_from_mongo(limit: Optional[int]) -> Tuple[List[Dict[str, Any]], str]:
    if MongoClient is None:
        raise RuntimeError("pymongo is not installed in the active environment")

    mongo_url = resolve_mongo_url()
    if not mongo_url:
        raise RuntimeError("MongoDB URL is not configured")

    client_kwargs: Dict[str, Any] = {
        "serverSelectionTimeoutMS": 5000,
        "connectTimeoutMS": 10000,
    }
    if (mongo_url.startswith("mongodb+srv://") or "tls=true" in mongo_url.lower()) and certifi is not None:
        client_kwargs["tlsCAFile"] = certifi.where()

    client = MongoClient(mongo_url, **client_kwargs)
    db_name = resolve_db_name()
    try:
        collection = client[db_name].products
        cursor = collection.find({}, {"_id": 0}).sort("created_at", -1)
        if limit:
            cursor = cursor.limit(limit)
        return [normalize_product(item) for item in cursor], f"mongo:{db_name}.products"
    except PyMongoError as error:
        raise RuntimeError(f"MongoDB query failed: {error}") from error
    finally:
        client.close()


def dedupe_products(products: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_ids = set()
    unique_products = []
    for product in products:
        product_id = product.get("id") or slugify(product.get("title", "product"))
        if product_id in seen_ids:
            continue
        seen_ids.add(product_id)
        unique_products.append(product)
    return unique_products


def detect_primary_angle(product: Dict[str, Any]) -> str:
    text = compact_text(
        product.get("title", ""),
        product.get("subtitle", ""),
        product.get("description", ""),
        " ".join(product.get("tags", [])),
        " ".join(product.get("benefits", [])),
    ).lower()

    angle_map = {
        "income": ["income", "money", "sales", "revenue", "passive", "affiliate", "profit"],
        "speed": ["launch", "fast", "7-day", "checklist", "playbook", "framework"],
        "authority": ["chatgpt", "prompts", "copy", "marketing", "command", "business"],
        "freedom": ["solo", "operators", "clients", "service", "freelance", "autopilot"],
        "simplicity": ["template", "guide", "system", "toolkit", "easy", "simple"],
    }

    for angle, keywords in angle_map.items():
        if any(keyword in text for keyword in keywords):
            return angle
    return "transformation"


def detect_emotional_trigger(product: Dict[str, Any]) -> str:
    angle = detect_primary_angle(product)
    trigger_map = {
        "income": "financial desire",
        "speed": "impatience",
        "authority": "status and competence",
        "freedom": "escape and autonomy",
        "simplicity": "relief and clarity",
        "transformation": "identity upgrade",
    }
    return trigger_map.get(angle, "identity upgrade")


def build_hook(product: Dict[str, Any], variant: int = 0) -> str:
    title = product["title"]
    price = product["price"]
    angle = detect_primary_angle(product)

    hook_variants = {
        "income": [
            [
                f"This {title} can pay for itself faster than your next bad ad spend.",
                f"If you want more sales without more chaos, watch this before you skip {title}.",
                f"What if {title} turned your next idea into $10K+ without the usual struggle?",
            ],
            [
                f"Most people waste money on ads. {title} turns attention into revenue.",
                f"If your sales are inconsistent, {title} is the missing piece you need.",
                f"This is what you buy when you want predictable income from digital products.",
            ],
            [
                f"Stop leaving money on the table. {title} shows you how to capture it all.",
                f"If you want to monetize faster than your competitors, {title} is your edge.",
                f"This {title} blueprint has generated more launches than most people ever attempt.",
            ],
        ],
        "speed": [
            [
                f"You do not need 30 days. {title} was built for speed.",
                f"If your last launch dragged on forever, {title} fixes that in one move.",
                f"This is the 7-day system that turns ideas into launched products.",
            ],
            [
                f"Most launches fail because they take too long. {title} changes that.",
                f"If you want to ship before you lose momentum, {title} is your framework.",
                f"This {title} cuts your launch timeline in half without cutting corners.",
            ],
            [
                f"Stop overthinking. {title} gives you the exact steps to launch fast.",
                f"If your products stay in draft forever, {title} gets them out the door.",
                f"This is the speed system that turns 'someday' projects into 'today' launches.",
            ],
        ],
        "authority": [
            [
                f"Most people are using AI wrong. {title} turns it into money.",
                f"This is the shortcut marketers wish they had before buying another course.",
                f"If you want to look like a pro without years of experience, {title} delivers.",
            ],
            [
                f"Stop sounding like everyone else. {title} gives you the positioning edge.",
                f"If your marketing feels generic, {title} makes you stand out instantly.",
                f"This {title} turns amateur copy into authority-level messaging.",
            ],
            [
                f"Most creators stay invisible. {title} gives you the leverage to be seen.",
                f"If you want to command higher prices, {title} shows you how to position.",
                f"This is what separates the amateurs from the authority figures in your niche.",
            ],
        ],
        "freedom": [
            [
                f"Still trading hours for cash? {title} is the exit ramp.",
                f"This is what you buy when you are done selling your time all day.",
                f"If you want freedom without the feast-or-famine cycle, {title} is your path.",
            ],
            [
                f"Most businesses trap you in the daily grind. {title} sets you free.",
                f"If you want to work less and earn more, {title} automates the process.",
                f"This {title} turns your skills into scalable assets that work 24/7.",
            ],
            [
                f"Stop being the bottleneck. {title} scales you beyond your own time.",
                f"If you want to build something bigger than yourself, {title} is the blueprint.",
                f"This is the freedom framework that turns solo operators into business owners.",
            ],
        ],
        "simplicity": [
            [
                f"If your business feels messy, {title} is the clean system you were missing.",
                f"This is the easiest way to stop guessing and start shipping a real offer.",
                f"Most people overcomplicate success. {title} makes it simple again.",
            ],
            [
                f"Stop drowning in complexity. {title} gives you the clear path forward.",
                f"If your workflow feels overwhelming, {title} organizes everything for you.",
                f"This {title} turns chaos into a systematic process you can actually follow.",
            ],
            [
                f"Most systems are too complicated. {title} is designed for real people.",
                f"If you want results without the headache, {title} delivers simplicity.",
                f"This is the clean framework that removes overwhelm and adds clarity.",
            ],
        ],
        "transformation": [
            [
                f"The people winning online move faster, and {title} shows you how.",
                f"If your current workflow feels small, {title} is the upgrade.",
                f"This {title} transforms stuck operators into confident marketers.",
            ],
            [
                f"Most people stay in their comfort zone. {title} pushes you to the next level.",
                f"If you want to evolve from beginner to expert, {title} is your guide.",
                f"This {title} turns ordinary efforts into extraordinary results.",
            ],
            [
                f"Stop playing small. {title} gives you the tools to think bigger.",
                f"If you want to level up your entire approach, {title} transforms everything.",
                f"This is the upgrade that turns good operators into great ones.",
            ],
        ],
    }

    selected_hooks = hook_variants.get(angle, hook_variants["transformation"])[variant % 3]
    selected = selected_hooks[variant % len(selected_hooks)]

    if price > 0 and price <= 39:
        return f"{selected} And it costs less than one weak impulse buy."
    return selected


def build_target_audience(product: Dict[str, Any]) -> Dict[str, Any]:
    perfect_for = product.get("perfect_for") or []
    tags = product.get("tags") or []
    audience_core = perfect_for[:3] if perfect_for else ["digital product buyers", "operators", "growth-focused creators"]
    pain_points = []
    angle = detect_primary_angle(product)
    if angle == "income":
        pain_points = ["wants extra revenue", "needs a faster monetization path", "is tired of inconsistent sales"]
    elif angle == "speed":
        pain_points = ["overthinks launches", "moves too slowly", "needs a step-by-step system"]
    elif angle == "authority":
        pain_points = ["struggles with copy and positioning", "wants sharper marketing assets", "needs leverage without hiring"]
    elif angle == "freedom":
        pain_points = ["trades time for money", "wants autonomy", "needs an offer that scales"]
    else:
        pain_points = ["feels stuck", "needs clearer execution", "wants a faster path to results"]

    return {
        "primary_segments": audience_core,
        "mindset": "already interested in buying or promoting digital offers, but needs a stronger reason to act now",
        "pain_points": pain_points,
        "interest_signals": tags[:5],
    }


def build_sales_angle(product: Dict[str, Any]) -> Dict[str, str]:
    price = product["price"]
    title = product["title"]
    angle = detect_primary_angle(product)

    if price <= 29:
        monetization = "Low-friction direct sale with an impulse-buy frame, then upsell into a higher-ticket toolkit or bundle."
    elif price <= 79:
        monetization = "Core-offer direct sale with urgency, plus an order bump or bundle stack to increase average order value."
    else:
        monetization = "Premium transformation pitch positioned as a faster path to revenue, speed, or authority than doing it manually."

    angle_line_map = {
        "income": f"Sell {title} as the fastest route from attention to revenue.",
        "speed": f"Sell {title} as the shortcut that removes launch delay and indecision.",
        "authority": f"Sell {title} as the tool that makes the buyer look sharper, faster, and more professional.",
        "freedom": f"Sell {title} as the move that gets the buyer out of time-for-money work.",
        "simplicity": f"Sell {title} as the clean system that reduces overwhelm and increases execution speed.",
        "transformation": f"Sell {title} as the identity upgrade from stuck operator to confident marketer.",
    }

    return {
        "sales_angle": angle_line_map.get(angle, angle_line_map["transformation"]),
        "monetization_method": monetization,
        "call_to_action": product.get("cta") or "Tap the link and buy now",
    }


def build_proof_line(product: Dict[str, Any]) -> str:
    reviews = product.get("reviews", 0)
    downloads = product.get("downloads", 0)
    rating = product.get("rating", 0.0)
    includes = product.get("includes", [])
    if reviews and downloads:
        return f"Buyers already pushed this to {downloads}+ downloads with a {rating:.1f} rating and strong repeat intent."
    if reviews:
        return f"This already has {reviews}+ buyer signals, which means the angle is market-ready."
    if includes:
        return f"You are not buying a vague idea. You get {includes[0]} plus a full action stack behind it."
    return "This is built like a real offer, not another generic digital download."


def build_visual_plan(product: Dict[str, Any], hook: str, variant: int = 0) -> List[Dict[str, str]]:
    title = product["title"]
    proof = build_proof_line(product)
    benefit = (product.get("benefits") or product.get("includes") or [product.get("description")])[0]
    cta = product.get("cta") or "Tap the link and buy now"

    visual_variants = [
        # Variant A: Problem-Solution-Proof
        [
            {
                "time": "0-3s",
                "visual": "Bold kinetic text over fast punch-in product mockups and mobile-first UI overlays.",
                "on_screen_text": hook,
                "voiceover": hook,
            },
            {
                "time": "3-8s",
                "visual": "Show the pain: overwhelmed tabs, slow launches, weak sales dashboards, or creator frustration depending on the offer.",
                "on_screen_text": "Most people stay stuck here",
                "voiceover": f"Most people stay stuck because they keep doing the slow version of this instead of using {title}.",
            },
            {
                "time": "8-16s",
                "visual": "Reveal the product with fast cuts through modules, benefits, templates, or the most tangible deliverables.",
                "on_screen_text": benefit,
                "voiceover": f"{title} gives you {benefit.lower()} so you can move faster and sell with more confidence.",
            },
            {
                "time": "16-23s",
                "visual": "Stack proof with ratings, downloads, screenshots, revenue-style overlays, and feature callouts.",
                "on_screen_text": "Proof beats hype",
                "voiceover": proof,
            },
            {
                "time": "23-30s",
                "visual": "Strong CTA card, gold accent button, product cover, and a final motion freeze frame.",
                "on_screen_text": cta,
                "voiceover": f"If you want the shortcut, {cta.lower()}.",
            },
        ],
        # Variant B: Story-Transformation-CTA
        [
            {
                "time": "0-3s",
                "visual": "Quick cuts of frustrated creators, failed launches, and missed opportunities with bold text overlay.",
                "on_screen_text": hook,
                "voiceover": hook,
            },
            {
                "time": "3-10s",
                "visual": "Show the transformation journey: before (chaos) to after (organized, profitable) with smooth transitions.",
                "on_screen_text": "From stuck to unstoppable",
                "voiceover": f"I built {title} because I was tired of seeing good ideas fail. This system turns potential into profit.",
            },
            {
                "time": "10-18s",
                "visual": "Demonstrate key features with real UI walkthroughs, templates opening, and results showing.",
                "on_screen_text": "See it in action",
                "voiceover": f"You get {benefit.lower()} plus everything you need to implement it immediately.",
            },
            {
                "time": "18-25s",
                "visual": "Social proof montage: testimonials, download numbers, success screenshots, and revenue graphics.",
                "on_screen_text": "Real results from real people",
                "voiceover": f"This isn't theory. {proof.lower()}.",
            },
            {
                "time": "25-30s",
                "visual": "Urgent CTA with countdown timer, limited spots graphic, and compelling offer stack.",
                "on_screen_text": f"{cta} - Limited time",
                "voiceover": f"Don't wait for another month to pass. {cta.lower()} and start your transformation today.",
            },
        ],
        # Variant C: Authority-Shortcut-Command
        [
            {
                "time": "0-3s",
                "visual": "Expert positioning shots, authority symbols, and commanding text that demands attention.",
                "on_screen_text": hook,
                "voiceover": hook,
            },
            {
                "time": "3-9s",
                "visual": "Expose common mistakes and wrong approaches with red X graphics and frustrated reactions.",
                "on_screen_text": "Stop doing this wrong",
                "voiceover": f"Most people waste time on ineffective strategies. {title} gives you the proven shortcut.",
            },
            {
                "time": "9-17s",
                "visual": "Commanding reveal of the system with step-by-step graphics, checklists, and framework breakdowns.",
                "on_screen_text": "The exact system that works",
                "voiceover": f"This is {title} - the complete system for {benefit.lower()} without the guesswork.",
            },
            {
                "time": "17-24s",
                "visual": "Authority-building proof: case studies, expert endorsements, and competitive advantages.",
                "on_screen_text": "Why this works when others don't",
                "voiceover": f"{proof}. This is why {title} delivers results others promise but can't.",
            },
            {
                "time": "24-30s",
                "visual": "Commanding CTA with authority positioning, scarcity elements, and premium offer presentation.",
                "on_screen_text": f"Command your success - {cta}",
                "voiceover": f"If you want to lead instead of follow, {cta.lower()}. This is for serious operators only.",
            },
        ],
    ]

    return visual_variants[variant % len(visual_variants)]


def build_script(product: Dict[str, Any], hook: str, variant: int = 0) -> List[Dict[str, str]]:
    title = product["title"]
    description = product["description"]
    benefit = (product.get("benefits") or product.get("includes") or [description])[0]
    proof = build_proof_line(product)
    cta = product.get("cta") or "Tap the link and buy now"

    script_variants = [
        # Variant A: Problem-Solution-Proof
        [
            {
                "time": "0-3s",
                "label": "Hook",
                "line": hook,
            },
            {
                "time": "3-8s",
                "label": "Pain",
                "line": f"If you are still doing this the slow way, you are losing time, momentum, and sales every single week.",
            },
            {
                "time": "8-16s",
                "label": "Solution",
                "line": f"{title} is built to fix that fast. You get {benefit.lower()} without guessing your way through it.",
            },
            {
                "time": "16-23s",
                "label": "Proof",
                "line": proof,
            },
            {
                "time": "23-30s",
                "label": "CTA",
                "line": f"This is the move if you want the cleaner path. {cta}.",
            },
        ],
        # Variant B: Story-Transformation-CTA
        [
            {
                "time": "0-3s",
                "label": "Hook",
                "line": hook,
            },
            {
                "time": "3-10s",
                "label": "Story",
                "line": f"I built {title} because I saw too many good ideas fail from slow execution and poor positioning.",
            },
            {
                "time": "10-18s",
                "label": "Transformation",
                "line": f"This system gives you {benefit.lower()} plus the exact framework to implement it without getting stuck.",
            },
            {
                "time": "18-25s",
                "label": "Social Proof",
                "line": f"The results speak for themselves. {proof.lower()}.",
            },
            {
                "time": "25-30s",
                "label": "Urgent CTA",
                "line": f"Your next launch doesn't have to be another disappointment. {cta} and get the transformation you need.",
            },
        ],
        # Variant C: Authority-Shortcut-Command
        [
            {
                "time": "0-3s",
                "label": "Hook",
                "line": hook,
            },
            {
                "time": "3-9s",
                "label": "Expose Wrong Way",
                "line": f"Most people waste months on ineffective strategies and amateur positioning. It's costing them sales and credibility.",
            },
            {
                "time": "9-17s",
                "label": "Authority Solution",
                "line": f"{title} is the proven system that gives you {benefit.lower()} with professional positioning and execution.",
            },
            {
                "time": "17-24s",
                "label": "Competitive Edge",
                "line": f"This is why {title} works when others don't. {proof}.",
            },
            {
                "time": "24-30s",
                "label": "Commanding CTA",
                "line": f"If you want to be the authority in your space instead of just another seller, {cta}. This is for serious operators.",
            },
        ],
    ]

    return script_variants[variant % len(script_variants)]


def build_caption(product: Dict[str, Any], hook: str, variant: int = 0) -> str:
    title = product["title"]
    benefit = (product.get("benefits") or product.get("includes") or [product["description"]])[0]
    cta = product.get("cta") or "Tap the link"

    caption_variants = [
        # Variant A: Direct and confrontational
        f"{hook} {title} is for people who are done wasting time and want {benefit.lower()}. "
        f"If you want the fast version instead of the frustrating version, {cta.lower()}. Comment 'PACK' if you want the breakdown.",

        # Variant B: Story-driven and relatable
        f"{hook} I built {title} because I was tired of seeing good ideas fail. "
        f"If you want {benefit.lower()} without the struggle, {cta.lower()}. "
        f"Tag a friend who needs this transformation. Link in bio.",

        # Variant C: Authority and commanding
        f"{hook} Most people are doing this wrong. {title} gives you the proven system for {benefit.lower()}. "
        f"If you want to be the authority instead of just another seller, {cta.lower()}. "
        f"This is for serious operators only. Comment 'AUTHORITY' below.",
    ]

    return caption_variants[variant % len(caption_variants)]


def build_hashtags(product: Dict[str, Any]) -> List[str]:
    base_tags = [
        "#DigitalProducts",
        "#OnlineBusiness",
        "#Marketing",
        "#Entrepreneur",
        "#MakeMoneyOnline",
    ]
    derived = []
    for raw_tag in product.get("tags", [])[:5]:
        token = re.sub(r"[^A-Za-z0-9]", "", raw_tag.title().replace(" ", ""))
        if token:
            derived.append(f"#{token}")
    for word in product.get("title", "").split():
        cleaned = re.sub(r"[^A-Za-z0-9]", "", word.title())
        if cleaned and len(cleaned) > 3:
            derived.append(f"#{cleaned}")
    hashtags = []
    for tag in base_tags + derived:
        if tag not in hashtags:
            hashtags.append(tag)
    return hashtags[:8]


def build_campaign_packs(product: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate 3 different viral video ad variants (A/B/C testing) for a product."""
    target_audience = build_target_audience(product)
    sales_angle = build_sales_angle(product)
    hashtags = build_hashtags(product)
    trigger = detect_emotional_trigger(product)
    duration_seconds = 28

    variants = []
    variant_names = ["A", "B", "C"]
    variant_descriptions = [
        "Problem-Solution-Proof direct response",
        "Story-Transformation emotional journey",
        "Authority-Shortcut commanding positioning"
    ]

    for i, (variant_name, variant_desc) in enumerate(zip(variant_names, variant_descriptions)):
        hook = build_hook(product, i)
        visual_plan = build_visual_plan(product, hook, i)
        script = build_script(product, hook, i)
        caption = build_caption(product, hook, i)

        variants.append({
            "product_id": product["id"],
            "product_title": product["title"],
            "status": product.get("status"),
            "variant": variant_name,
            "variant_description": variant_desc,
            "ad_campaign_pack": {
                "campaign_name": f"{product['title']} Conversion Push - Variant {variant_name}",
                "objective": "Drive direct-response clicks and purchases from short-form social traffic.",
                "primary_emotional_trigger": trigger,
                "viral_short_form_video_ad": {
                    "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"],
                    "duration_seconds": duration_seconds,
                    "creative_direction": "High-energy direct-response creative with fast cuts, proof overlays, and motion-heavy text designed to stop scroll and convert.",
                    "editing_notes": "Use large subtitles, hard cuts every 1-2 seconds, screenshot proof, motion zooms, and a final CTA freeze-frame.",
                    "scene_breakdown": visual_plan,
                },
                "hook_first_3_seconds": hook,
                "full_ad_script": script,
                "engagement_caption": caption,
                "viral_hashtags": hashtags,
                "target_audience": target_audience,
                "sales_angle": sales_angle["sales_angle"],
                "monetization_method": sales_angle["monetization_method"],
                "call_to_action": sales_angle["call_to_action"],
                "posting_strategy": {
                    "frequency": "3-5 posts per week per variant",
                    "best_times": ["Morning rush (7-9am)", "Lunch break (12-2pm)", "Evening wind-down (7-9pm)"],
                    "testing_approach": f"Run all 3 variants simultaneously for 7 days, then optimize winner for next 14 days",
                    "engagement_focus": "Respond to comments within 5 minutes, ask questions to boost algorithm",
                },
            },
        })

    return variants


def render_markdown(campaigns: List[Dict[str, Any]], source_label: str) -> str:
    # Group campaigns by product
    product_groups = {}
    for campaign in campaigns:
        product_id = campaign["product_id"]
        if product_id not in product_groups:
            product_groups[product_id] = {
                "title": campaign["product_title"],
                "status": campaign.get("status"),
                "variants": []
            }
        product_groups[product_id]["variants"].append(campaign)

    lines = [
        "# Ad Campaign Packs",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Source: {source_label}",
        f"Products: {len(product_groups)}",
        f"Total Variants: {len(campaigns)}",
        "",
    ]

    for product_id, product_data in product_groups.items():
        lines.extend([
            f"## {product_data['title']}",
            "",
            f"- Product ID: {product_id}",
            f"- Status: {product_data.get('status') or 'unknown'}",
            f"- Variants: {len(product_data['variants'])} (A/B/C testing)",
            "",
        ])

        for campaign in product_data["variants"]:
            pack = campaign["ad_campaign_pack"]
            lines.extend([
                f"### Variant {campaign['variant']}: {campaign['variant_description']}",
                "",
                f"- Campaign Name: {pack['campaign_name']}",
                f"- Objective: {pack['objective']}",
                f"- Emotional Trigger: {pack['primary_emotional_trigger']}",
                "",
                "#### Viral Short-Form Video Ad",
                "",
                f"- Platforms: {', '.join(pack['viral_short_form_video_ad']['platforms'])}",
                f"- Duration: {pack['viral_short_form_video_ad']['duration_seconds']} seconds",
                f"- Creative Direction: {pack['viral_short_form_video_ad']['creative_direction']}",
                f"- Editing Notes: {pack['viral_short_form_video_ad']['editing_notes']}",
                "",
                "##### Scene Breakdown",
                "",
            ])
            for scene in pack["viral_short_form_video_ad"]["scene_breakdown"]:
                lines.extend([
                    f"- {scene['time']}: {scene['visual']}",
                    f"  On-screen text: {scene['on_screen_text']}",
                    f"  Voiceover: {scene['voiceover']}",
                ])

            lines.extend([
                "",
                "#### Hook (First 3 Seconds)",
                "",
                pack["hook_first_3_seconds"],
                "",
                "#### Full Ad Script",
                "",
            ])
            for beat in pack["full_ad_script"]:
                lines.append(f"- {beat['time']} {beat['label']}: {beat['line']}")

            lines.extend([
                "",
                "#### Engagement Caption",
                "",
                pack["engagement_caption"],
                "",
                "#### Viral Hashtags",
                "",
                f"{', '.join(pack['viral_hashtags'])}",
                "",
                "#### Target Audience",
                "",
                f"- Primary Segments: {', '.join(pack['target_audience']['primary_segments'])}",
                f"- Mindset: {pack['target_audience']['mindset']}",
                f"- Pain Points: {', '.join(pack['target_audience']['pain_points'])}",
                f"- Interest Signals: {', '.join(pack['target_audience']['interest_signals'])}",
                "",
                "#### Sales Angle",
                "",
                pack["sales_angle"],
                "",
                "#### Monetization Method",
                "",
                pack["monetization_method"],
                "",
                "#### Call to Action",
                "",
                pack["call_to_action"],
                "",
                "#### Posting Strategy",
                "",
                f"- Frequency: {pack['posting_strategy']['frequency']}",
                f"- Best Times: {', '.join(pack['posting_strategy']['best_times'])}",
                f"- Testing Approach: {pack['posting_strategy']['testing_approach']}",
                f"- Engagement Focus: {pack['posting_strategy']['engagement_focus']}",
                "",
            ])

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Ad Campaign Packs for products")
    parser.add_argument("--input", type=Path, help="Path to a JSON file containing products")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000", help="Base API URL or /api/products endpoint")
    parser.add_argument("--source", choices=["auto", "json", "api", "mongo", "fallback"], default="auto")
    parser.add_argument("--limit", type=int, default=None, help="Optional product limit")
    parser.add_argument("--output-stem", default=None, help="Custom output filename stem")
    return parser.parse_args()


def load_products(args: argparse.Namespace) -> Tuple[List[Dict[str, Any]], str]:
    if args.source == "json":
        if not args.input:
            raise ValueError("--input is required when --source json is used")
        return load_products_from_json(args.input)

    if args.source == "api":
        return load_products_from_api(args.api_url, args.limit)

    if args.source == "mongo":
        return load_products_from_mongo(args.limit)

    if args.source == "fallback":
        return [normalize_product(product) for product in FALLBACK_PRODUCTS], "fallback:sample-products"

    if args.input:
        try:
            return load_products_from_json(args.input)
        except Exception:
            pass

    try:
        return load_products_from_api(args.api_url, args.limit)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        pass

    try:
        return load_products_from_mongo(args.limit)
    except Exception:
        pass

    return [normalize_product(product) for product in FALLBACK_PRODUCTS], "fallback:sample-products"


def main() -> int:
    load_env()
    args = parse_args()
    products, source_label = load_products(args)
    products = dedupe_products(products)

    if args.limit:
        products = products[: args.limit]

    campaigns = []
    for product in products:
        campaigns.extend(build_campaign_packs(product))

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    output_stem = args.output_stem or f"ad_campaign_packs_{timestamp}"
    json_path = EXPORT_DIR / f"{output_stem}.json"
    md_path = EXPORT_DIR / f"{output_stem}.md"

    json_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source_label,
        "product_count": len(campaigns),
        "campaigns": campaigns,
    }

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(json_payload, handle, indent=2, ensure_ascii=True)

    with md_path.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(campaigns, source_label))

    print(f"Generated {len(campaigns)} Ad Campaign Packs")
    print(f"Source: {source_label}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())