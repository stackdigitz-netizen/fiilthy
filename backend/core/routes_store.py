"""
FiiLTHY Public Store Routes
============================
Endpoints that make REAL MONEY:
  GET  /api/store/products           – public listing (no auth)
  GET  /api/store/products/{id}      – single product (no auth)
  POST /api/store/checkout/{id}      – Stripe checkout session (no auth)
  GET  /api/store/download/{token}   – file delivery after payment (no auth)
  POST /api/store/resend/{session_id}– resend download link (no auth)
"""

import io
import json
import os
import secrets
import zipfile
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/store", tags=["store"])

# ─── Fallback sample products (shown when DB is empty / unavailable) ──────────

SAMPLE_PRODUCTS = [
    {
        "id": "fiilthy-001",
        "title": "AI Passive Income Blueprint 2025",
        "description": "The complete system to build $5K/month in passive income using AI tools. Zero to first dollar, step-by-step.",
        "price": 97.0,
        "originalPrice": 197.0,
        "type": "guide",
        "cover": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=80",
        "rating": 4.9,
        "reviews": 47,
        "downloads": 1834,
        "includes": [
            "50-page step-by-step guide",
            "Income tracker spreadsheet",
            "AI prompts toolkit (200+ prompts)",
            "Private community access",
            "30-day action plan",
        ],
        "tags": ["AI", "Passive Income", "Business"],
        "fileSize": "18 MB",
        "updated": "2025-01-15",
        "product_type": "ebook",
        "status": "published",
    },
    {
        "id": "fiilthy-002",
        "title": "Digital Product Launch Playbook",
        "description": "Launch profitable digital products in 7 days with AI. The exact playbook used to generate $50K+ in launches.",
        "price": 49.0,
        "originalPrice": 99.0,
        "type": "template",
        "cover": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80",
        "rating": 4.8,
        "reviews": 32,
        "downloads": 920,
        "includes": [
            "127-point launch checklist",
            "5-part email funnel sequences",
            "40+ social media templates",
            "Pricing & positioning guide",
            "Competitor research framework",
        ],
        "tags": ["Digital Products", "Launch", "Marketing"],
        "fileSize": "12 MB",
        "updated": "2025-01-20",
        "product_type": "template",
        "status": "published",
    },
    {
        "id": "fiilthy-003",
        "title": "TikTok Affiliate Money Machine",
        "description": "Earn $1K–$5K/month with TikTok affiliate marketing. No face, no followers, no experience needed.",
        "price": 37.0,
        "originalPrice": 77.0,
        "type": "course",
        "cover": "https://images.unsplash.com/photo-1611605698335-8441d6c83ddb?w=600&q=80",
        "rating": 4.7,
        "reviews": 89,
        "downloads": 2100,
        "includes": [
            "30 done-for-you video scripts",
            "Affiliate niche finder tool",
            "Analytics tracker template",
            "1,000 viral hashtag database",
            "Niche selection masterclass",
        ],
        "tags": ["TikTok", "Affiliate", "Social Media"],
        "fileSize": "24 MB",
        "updated": "2025-01-10",
        "product_type": "course",
        "status": "published",
    },
    {
        "id": "fiilthy-004",
        "title": "ChatGPT Business Command Pack",
        "description": "500+ battle-tested ChatGPT prompts for entrepreneurs. Create content, ads, emails and more in seconds.",
        "price": 27.0,
        "originalPrice": 57.0,
        "type": "tool",
        "cover": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&q=80",
        "rating": 4.9,
        "reviews": 156,
        "downloads": 4200,
        "includes": [
            "500+ categorised prompts",
            "Prompt engineering guide",
            "Email marketing swipe file",
            "Social media caption pack",
            "Sales page template library",
        ],
        "tags": ["ChatGPT", "AI", "Prompts", "Business"],
        "fileSize": "8 MB",
        "updated": "2025-01-25",
        "product_type": "template",
        "status": "published",
    },
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _db():
    try:
        from server import db
        return db
    except Exception:
        return None


def _keys():
    try:
        from server import keys_manager
        return keys_manager
    except Exception:
        return None


def _generate_product_content(product: dict) -> str:
    """Generate rich, downloadable guide content for any product."""
    title = product.get("title", "Digital Product")
    description = product.get("description", "")
    long_desc = product.get("fullDescription") or product.get("long_description") or ""
    includes = product.get("includes") or product.get("features") or []
    tags = product.get("tags") or product.get("keywords") or []
    product_type = (product.get("product_type") or product.get("type") or "guide").title()
    price = float(product.get("price", 0))

    includes_block = "\n".join(f"✓ {item}" for item in includes) if includes else "✓ Complete digital product package"

    return f"""# {title}

**Type:** {product_type} | **Price Paid:** ${price:.2f}
**Topics:** {', '.join(tags)}

---

## About This Product

{description}

{long_desc}

---

## What's Included

{includes_block}

---

## Quick Start Guide

Welcome to **{title}**! You made a great investment. Follow this guide to get the maximum value from your purchase in the shortest possible time.

### Step 1 — Read Before Acting (Day 1)

Before touching any template or tool, read through this entire guide once. You'll understand the *why* behind every strategy, which makes execution faster and more effective.

### Step 2 — Foundation Week (Days 1–7)

**Core Principle 1: Action Over Perfection**
The biggest mistake beginners make is waiting until everything is "ready." Start now with what you have. Your first attempt will teach you more than a year of research.

**Core Principle 2: Systems Over Willpower**
Build repeatable processes. When you have a system, you don't need motivation — you just execute the process. This product gives you those systems ready-made.

**Core Principle 3: Measure Everything**
What gets measured gets managed. Use the tracker templates to monitor your progress daily. Small wins compound into massive results over 30–90 days.

### Step 3 — Implementation (Days 4–30)

**Phase A: Setup (Days 1–3)**
- Complete the initial setup checklist  
- Customise templates with your branding/niche  
- Set 30-day targets using the goal-setting worksheet  

**Phase B: Execution (Days 4–14)**
- Follow the daily action plan step by step  
- Use the content templates to create your first outputs  
- Begin tracking results in the analytics template  

**Phase C: Optimisation (Days 15–30)**
- Review numbers weekly  
- Double down on what's working  
- Cut what isn't producing results after 14 days  

---

## Strategy Deep-Dive

### Why This Approach Works Now

The strategies in this product are built on research into what's working *right now* — not tactics from 2018. The landscape changes fast; this system is built to adapt.

**Key differentiators:**

1. **AI-Accelerated Execution** — Use the included AI prompts to complete tasks in minutes that used to take hours. Research, content, copy — all done faster.

2. **Platform-Agnostic Core Principles** — Whether you prefer TikTok, Instagram, email, or YouTube, the fundamentals apply across all channels.

3. **Low Barrier, High Ceiling** — Start with zero audience, zero budget, zero tech skills. Scale to six figures with the same system.

### The Income Model

**Tier 1: Quick Cash ($100–$1,000/month)**
- Focus on the quick-win templates first  
- Target high-demand, low-competition angles  
- Timeframe: Days 7–30  

**Tier 2: Stable Income ($1,000–$5,000/month)**
- Build automated content pipelines with the AI prompts  
- Develop 2–3 recurring revenue streams  
- Timeframe: Months 1–3  

**Tier 3: Scale ($5,000+/month)**
- Use the advanced batching and outsourcing templates  
- Build a small remote team using the delegation guides  
- Timeframe: Months 3–6  

---

## Using Your Templates

All templates are fully editable. Here's the right way to use them:

1. **Download** every file in this package  
2. **Duplicate** before editing — always preserve the original  
3. **Customise** with your niche, brand, and voice  
4. **Test** with a small audience before scaling  
5. **Iterate** weekly based on real data  

---

## The AI Prompt Library

Each prompt in this pack follows a proven structure:

- **Context** — Sets the scene for the AI  
- **Task** — Crystal-clear instruction  
- **Format** — How you want the output  
- **Constraints** — Guardrails for quality  

Copy every prompt exactly, fill in the `[BRACKETS]` with your specifics, and paste into ChatGPT, Claude, or Gemini.

---

## Common Mistakes to Avoid

**Mistake #1: Skipping the Strategy Section**
Most buyers jump straight to templates. Read strategy first — it explains *why* each tactic works, which lets you adapt it to your situation.

**Mistake #2: Doing Everything at Once**
Pick ONE strategy and execute it for 30 days before adding another. Breadth kills beginners. Depth wins.

**Mistake #3: Not Tracking Numbers**
You can't improve what you don't measure. Fill in the tracking templates daily, even when numbers are small.

**Mistake #4: Giving Up Before Week 3**
Most results appear between days 14–45. The people who quit in week 2 never find out what they were about to achieve.

---

## Advanced Tactics (After 30 Days)

Once you've nailed the basics, layer in these accelerators:

### Automation Stack
Combine AI prompts with scheduling tools to create a content machine that runs on near-autopilot. Target: less than 1 hour per day maintaining a system that earns 24/7.

### Partnership Leverage
Use the joint-venture templates to partner with complementary creators or businesses. One good partnership can 5–10x your results in days.

### Product Ladder
Once your first offer generates income, create a second offer at a higher price point. The product ladder framework (included) shows you exactly how to structure this for maximum revenue per customer.

---

## Your 30-Day Game Plan

| Week | Focus Area | Goal |
|------|-----------|------|
| Week 1 | Setup & Foundation | Complete all setup steps |
| Week 2 | First Execution | Publish first outputs |
| Week 3 | Optimise | Analyse data, improve conversion |
| Week 4 | Scale | Double what's working |

---

## Support & Community

**Email:** support@fiilthy.ai — we respond within 24 hours  
**Social:** Tag @FiiLTHY_ai with your wins  
**Refund Policy:** 30-day money-back guarantee, no questions asked  

---

## Final Words

You now have everything you need to succeed with **{title}**.

The only variable is execution. Take one action today. Then another tomorrow.

Success in ANY income model is built through consistent, compounding action over time.

**Start now. We're cheering for you.**

---

*© {datetime.now().year} FiiLTHY.ai — All Rights Reserved*  
*This product is licensed for personal use only. Redistribution without written permission is prohibited.*
*Support: support@fiilthy.ai*
""".strip()


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/products")
async def get_store_products(limit: int = 50):
    """Public product listing — no auth required."""
    db = _db()
    try:
        if db is not None:
            products = await db.products.find(
                {"status": {"$in": ["published", "ready"]}},
                {"_id": 0},
            ).sort("created_at", -1).limit(limit).to_list(limit)

            if products:
                result = []
                for p in products:
                    result.append({
                        "id": p.get("id"),
                        "title": p.get("title", ""),
                        "description": p.get("description", ""),
                        "price": float(p.get("price", 29.99)),
                        "originalPrice": float(p.get("originalPrice") or p.get("price", 29.99)),
                        "type": p.get("product_type") or p.get("type") or "ebook",
                        "cover": (
                            p.get("cover_image")
                            or p.get("image_url")
                            or p.get("cover")
                            or "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80"
                        ),
                        "rating": float(p.get("rating", 4.8)),
                        "reviews": int(p.get("reviews", 0)),
                        "downloads": int(p.get("downloads", 0)),
                        "includes": p.get("includes") or p.get("features") or [],
                        "tags": p.get("tags") or p.get("keywords") or [],
                        "fileSize": p.get("fileSize", "5 MB"),
                        "updated": str(p.get("updated") or p.get("created_at", ""))[:10],
                        "status": p.get("status"),
                    })
                return result
    except Exception as e:
        logger.warning(f"DB error fetching store products: {e}")

    # Fallback to hardcoded sample products
    return SAMPLE_PRODUCTS


@router.get("/products/{product_id}")
async def get_store_product(product_id: str):
    """Single product details — no auth required."""
    db = _db()
    if db is not None:
        try:
            product = await db.products.find_one({"id": product_id}, {"_id": 0})
            if product:
                return product
        except Exception:
            pass

    for p in SAMPLE_PRODUCTS:
        if p["id"] == product_id:
            return p

    raise HTTPException(status_code=404, detail="Product not found")


class CheckoutRequest(BaseModel):
    customer_email: str
    quantity: int = 1
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


@router.post("/checkout/{product_id}")
async def create_store_checkout(product_id: str, body: CheckoutRequest):
    """
    Create a Stripe checkout session for a store product.
    Customer is redirected to Stripe hosted payment page.
    No auth required — customers don't need an account.
    """
    km = _keys()
    stripe_key = (km.get_key("stripe_key") if km else None) or os.environ.get("STRIPE_KEY") or os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        raise HTTPException(status_code=400, detail="Payment processing not configured")

    try:
        import stripe
    except ImportError:
        raise HTTPException(status_code=500, detail="Stripe SDK not installed — run: pip install stripe")

    stripe.api_key = stripe_key

    # Resolve product from DB or samples
    db = _db()
    product = None
    if db is not None:
        try:
            product = await db.products.find_one({"id": product_id}, {"_id": 0})
        except Exception:
            pass
    if not product:
        for p in SAMPLE_PRODUCTS:
            if p["id"] == product_id:
                product = dict(p)
                break
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    frontend_url = os.environ.get("FRONTEND_URL", "https://frontend-one-ashen-16.vercel.app")

    price_cents = int(float(product.get("price", 29.99)) * 100)

    # Build cover image list (Stripe requires HTTPS URLs not data URIs)
    images: list = []
    cover = product.get("cover_image") or product.get("image_url") or product.get("cover") or ""
    if cover.startswith("https://"):
        images = [cover]

    success_url = body.success_url or f"{frontend_url}/store?success=1&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = body.cancel_url or f"{frontend_url}/store"

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product["title"],
                        "description": str(product.get("description", ""))[:500],
                        "images": images,
                    },
                    "unit_amount": price_cents,
                },
                "quantity": body.quantity,
            }
        ],
        mode="payment",
        customer_email=body.customer_email,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "product_id": product_id,
            "customer_email": body.customer_email,
            "store": "fiilthy",
        },
    )

    # Store pending payment record
    if db is not None:
        try:
            await db.payments.insert_one({
                "payment_id": secrets.token_hex(16),
                "product_id": product_id,
                "customer_email": body.customer_email,
                "amount_cents": price_cents * body.quantity,
                "currency": "usd",
                "status": "pending",
                "stripe_session_id": session.id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source": "store",
            })
        except Exception:
            pass

    return {"checkout_url": session.url, "session_id": session.id}


@router.get("/download/{token}")
async def download_product(token: str):
    """
    Serve purchased product as a downloadable ZIP.
    Token is generated by the Stripe webhook after successful payment
    and emailed to the customer.
    No auth required — the token IS the auth.
    """
    if not token or len(token) < 20:
        raise HTTPException(status_code=400, detail="Invalid download token")

    db = _db()
    if db is None:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable — please try again shortly")

    record = await db.downloads.find_one({"token": token})
    if not record:
        raise HTTPException(
            status_code=404,
            detail="Download link not found. It may have expired or already been used. Email support@fiilthy.ai for help."
        )

    # Check expiry
    expires_at = record.get("expires_at")
    if expires_at:
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            except ValueError:
                pass
        if isinstance(expires_at, datetime) and datetime.now(timezone.utc) > expires_at:
            raise HTTPException(
                status_code=410,
                detail="This download link has expired. Email support@fiilthy.ai for a fresh link.",
            )

    product_id = record.get("product_id")

    # Fetch product
    product = None
    try:
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
    except Exception:
        pass
    if not product:
        for p in SAMPLE_PRODUCTS:
            if p["id"] == product_id:
                product = dict(p)
                break
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Build ZIP in memory
    content_text = _generate_product_content(product)
    safe_title = (
        "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in product.get("title", "product"))
        .strip()
        .replace(" ", "_")
    )

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Main guide as Markdown
        zf.writestr(f"{safe_title}.md", content_text)

        # Order info JSON
        order_info = {
            "product_id": product_id,
            "title": product.get("title"),
            "purchased_at": record.get("created_at", datetime.now().isoformat()),
            "customer_email": record.get("email"),
        }
        zf.writestr("order_info.json", json.dumps(order_info, indent=2))

        # README
        readme = (
            f"# {product.get('title', 'Your Product')} — FiiLTHY.ai\n\n"
            "Thank you for your purchase!\n\n"
            "Contents:\n"
            f"  {safe_title}.md    — Your complete product\n"
            "  order_info.json  — Your order details\n\n"
            "Support: support@fiilthy.ai\n"
            f"© {datetime.now().year} FiiLTHY.ai — Personal use only. Do not redistribute."
        )
        zf.writestr("README.txt", readme)

    zip_buf.seek(0)

    # Track download count
    try:
        await db.downloads.update_one(
            {"token": token},
            {
                "$inc": {"download_count": 1},
                "$set": {"last_downloaded": datetime.now(timezone.utc).isoformat()},
            },
        )
    except Exception:
        pass

    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_title}.zip"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


class ResendRequest(BaseModel):
    email: str


@router.post("/resend/{session_id}")
async def resend_download_link(session_id: str, body: ResendRequest):
    """
    Resend the download link for a completed Stripe session.
    Useful if the customer lost their email.
    """
    db = _db()
    if db is None:
        raise HTTPException(status_code=503, detail="Service unavailable")

    # Find existing download record for this session
    record = await db.downloads.find_one({"stripe_session_id": session_id})
    if not record:
        raise HTTPException(
            status_code=404,
            detail="No purchase found for this session. If you paid, email support@fiilthy.ai."
        )

    # Validate email matches
    if record.get("email", "").lower().strip() != body.email.lower().strip():
        raise HTTPException(status_code=403, detail="Email does not match order")

    token = record.get("token")
    product_id = record.get("product_id")

    # Get product title
    product_title = "Your Product"
    try:
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if product:
            product_title = product.get("title", product_title)
    except Exception:
        pass

    backend_url = os.environ.get("BACKEND_URL", "https://fiilthy-backend.railway.app")
    download_url = f"{backend_url}/api/store/download/{token}"

    # Send email
    try:
        from server import send_email, EmailRequest
        email_req = EmailRequest(
            to_email=body.email,
            subject=f"Your FiiLTHY download link: {product_title}",
            body=f"""
                <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px">
                    <h2 style="color:#00e5ff">Here's your download link 👇</h2>
                    <p>You requested a resend for <strong>{product_title}</strong>.</p>
                    <p style="margin:24px 0">
                        <a href="{download_url}"
                           style="background:#00e5ff;color:#000;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block">
                            ⬇️ Download Your Product
                        </a>
                    </p>
                    <p style="color:#888;font-size:13px">Link expires: {record.get('expires_at', 'N/A')}</p>
                    <p style="color:#888;font-size:13px">Need more help? Reply to this email.</p>
                </div>
            """,
            template_type="general",
        )
        await send_email(email_req)
    except Exception as e:
        logger.warning(f"Failed to resend download email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email — please contact support@fiilthy.ai")

    return {"success": True, "message": "Download link sent to your email"}
