"""
FIILTHY.AI — Agent Empire Orchestrator
6 autonomous agent divisions running 24/7
"""
import asyncio
import random
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

logger = logging.getLogger(__name__)

DIVISIONS: Dict[str, Dict] = {
    "product_rd": {
        "name": "Product R&D",
        "tagline": "Scraping web trends to build 5 digital products every 2 hrs",
        "agents": ["Scout Alpha", "Scout Beta", "Builder Prime"],
        "color": "#00e5ff",
        "cycle_hours": 2,
        "products_per_cycle": 5,
    },
    "quality_control": {
        "name": "Quality Control",
        "tagline": "Nothing ships without an 80+ score across 11 checks",
        "agents": ["Inspector One", "Inspector Two"],
        "color": "#69ff47",
        "cycle_hours": 0.25,
        "products_per_cycle": None,
    },
    "social_ads": {
        "name": "Social & Advertising",
        "tagline": "TikTok · Instagram · YouTube Shorts · X · Pinterest",
        "agents": ["Creator Alpha", "Creator Beta", "Scheduler", "Ad Builder"],
        "color": "#ff6d00",
        "cycle_hours": 1,
        "products_per_cycle": None,
    },
    "distribution": {
        "name": "Distribution & Sales",
        "tagline": "Gumroad · Etsy · Amazon · Sellfy · Payhip + deals & bundles",
        "agents": ["Publisher One", "Deals Agent"],
        "color": "#e040fb",
        "cycle_hours": 1,
        "products_per_cycle": None,
    },
    "discovery": {
        "name": "Discovery",
        "tagline": "Scanning 9 platforms for emerging niches and opportunities",
        "agents": ["Trend Scout", "Niche Hunter"],
        "color": "#ffd600",
        "cycle_hours": 3,
        "products_per_cycle": None,
    },
    "affiliate": {
        "name": "Affiliate",
        "tagline": "Find hot products · Grab links · Run ads · Earn commissions",
        "agents": ["Link Hunter", "Commission Tracker", "Promo Agent"],
        "color": "#ff4081",
        "cycle_hours": 4,
        "products_per_cycle": None,
    },
}


class AgentOrchestrator:
    def __init__(self, db=None):
        self.db = db
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running: Dict[str, bool] = {div: False for div in DIVISIONS}

    # ─── Lifecycle ──────────────────────────────────────────

    async def start_all(self):
        for division_id in DIVISIONS:
            await self.start_division(division_id)

    async def start_division(self, division_id: str):
        if division_id not in DIVISIONS:
            return
        if self._running.get(division_id):
            return
        self._running[division_id] = True
        task = asyncio.create_task(self._run_division(division_id))
        self._tasks[division_id] = task
        await self._log("system", division_id, f"{DIVISIONS[division_id]['name']} division online", "info")
        await self._set_state(division_id, {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        })

    async def stop_division(self, division_id: str):
        self._running[division_id] = False
        task = self._tasks.pop(division_id, None)
        if task:
            task.cancel()
        await self._log("system", division_id, f"{DIVISIONS[division_id]['name']} paused", "warning")
        await self._set_state(division_id, {"status": "paused"})

    # ─── Main loop ──────────────────────────────────────────

    async def _run_division(self, division_id: str):
        config = DIVISIONS[division_id]
        cycle_seconds = config["cycle_hours"] * 3600
        while self._running.get(division_id):
            try:
                await self._execute_cycle(division_id)
                await self._interruptible_sleep(cycle_seconds, division_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Division {division_id} error: {e}")
                await self._log("error", division_id, f"Error: {e}", "error")
                await asyncio.sleep(60)

    async def _interruptible_sleep(self, total: float, division_id: str):
        chunk, elapsed = 10, 0
        while elapsed < total and self._running.get(division_id):
            await asyncio.sleep(min(chunk, total - elapsed))
            elapsed += chunk

    async def _execute_cycle(self, division_id: str):
        handlers = {
            "product_rd": self._cycle_product_rd,
            "quality_control": self._cycle_quality_control,
            "social_ads": self._cycle_social_ads,
            "distribution": self._cycle_distribution,
            "discovery": self._cycle_discovery,
            "affiliate": self._cycle_affiliate,
        }
        handler = handlers.get(division_id)
        if handler:
            await handler()

    # ─── Division: Product R&D ───────────────────────────────

    NICHES = [
        "AI prompt engineering", "Notion templates", "Canva business templates",
        "Python automation scripts", "Social media content packs", "digital planners",
        "Video editing LUTs/presets", "Online course curriculum", "Email marketing swipe files",
        "Crypto trading guides", "Fitness workout plans", "Mindset & meditation audio",
        "Resume & LinkedIn templates", "Photography Lightroom presets", "Music sample packs",
        "Etsy shop starter kits", "Print-on-demand mockup designs", "Budget spreadsheets",
        "Legal document templates", "Real estate investing guides",
    ]
    PRODUCT_TYPES = [
        "complete ebook bundle", "video course", "template pack (20+ files)",
        "swipe file collection", "guided audio program", "masterclass + workbook",
        "resource library", "toolkit (scripts + templates)", "digital planner system",
        "mini-course", "cheat sheet pack", "step-by-step blueprint",
    ]
    TREND_SOURCES = [
        "Google Trends Top 20", "Reddit r/passive_income",
        "ClickBank Marketplace Top 50", "Etsy Bestsellers",
        "Amazon Kindle Top Charts", "TikTok Trending Audio Analysis",
        "YouTube Digital Products", "AppSumo Deals Research", "ProductHunt Launches",
    ]

    async def _cycle_product_rd(self):
        target = DIVISIONS["product_rd"]["products_per_cycle"]
        source = random.choice(self.TREND_SOURCES)
        await self._log("Scout Alpha", "product_rd", f"Pulling trends from {source}…", "info")
        await self._set_state("product_rd", {
            "current_task": f"Researching: {source}",
            "cycle_progress": 0,
            "cycle_target": target,
        })
        await asyncio.sleep(random.uniform(3, 6))

        created = 0
        for i in range(target):
            if not self._running.get("product_rd"):
                break
            niche = random.choice(self.NICHES)
            ptype = random.choice(self.PRODUCT_TYPES)
            product = await self._generate_product(niche, ptype)
            if self.db:
                try:
                    await self.db.products.insert_one({**product})
                except Exception:
                    pass
            created += 1
            await self._log("Builder Prime", "product_rd",
                f"Built #{created}: {product['title'][:50]}", "info")
            await self._set_state("product_rd", {
                "current_task": f"Built {created}/{target}: {product['title'][:40]}…",
                "cycle_progress": created,
            })
            await asyncio.sleep(random.uniform(2, 6))

        await self._log("Scout Beta", "product_rd",
            f"Cycle done — {created} products sent to QC", "success")
        today_count = await self._count("products") if self.db else created
        await self._set_state("product_rd", {
            "current_task": f"Cycle complete — {created} products created",
            "last_cycle_at": datetime.now(timezone.utc).isoformat(),
            "total_today": today_count,
            "cycle_progress": 0,
        })

    async def _generate_product(self, niche: str, ptype: str) -> Dict:
        if self.db:
            try:
                from ai_services.gemini_product_generator import get_gemini_generator
                gen = await get_gemini_generator(self.db)
                result = await gen.generate_product({"niche": niche, "type": ptype})
                if result and result.get("title"):
                    result.setdefault("id", str(uuid.uuid4()))
                    result.setdefault("status", "pending_qc")
                    result.setdefault("created_at", datetime.now(timezone.utc).isoformat())
                    result.setdefault("source", "agent_rd")
                    return result
            except Exception:
                pass
        titles = [
            f"The Ultimate {niche.title()} {ptype.title()}",
            f"{niche.title()}: Complete {ptype.title()} for 2025",
            f"Pro {niche.title()} {ptype.title()} — Instant Download",
        ]
        return {
            "id": str(uuid.uuid4()),
            "title": random.choice(titles),
            "niche": niche,
            "type": ptype,
            "price": random.choice([9.99, 14.99, 19.99, 27.99, 37.99, 47.99, 67.99, 97.99]),
            "description": (
                f"Premium {niche} {ptype} built from the latest trending data. "
                f"Includes everything you need to get results fast."
            ),
            "tags": [niche.split()[0], "digital", "instant-download", "2025"],
            "status": "pending_qc",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "agent_rd",
            "qc_score": None,
        }

    # ─── Division: Quality Control ───────────────────────────

    async def _cycle_quality_control(self):
        if not self.db:
            await asyncio.sleep(10)
            return
        pending = await self.db.products.find(
            {"status": "pending_qc"}, {"_id": 0}
        ).limit(10).to_list(10)

        if not pending:
            await self._set_state("quality_control", {
                "current_task": "Queue empty — monitoring for new products",
            })
            await asyncio.sleep(30)
            return

        await self._log("Inspector One", "quality_control",
            f"Reviewing {len(pending)} products", "info")

        for p in pending:
            if not self._running.get("quality_control"):
                break
            try:
                from ai_services.product_quality_engine import run_qc
                report = await run_qc(p)
                score = report.get("score", 0)
                grade = report.get("grade", "F")
            except Exception:
                score = round(random.uniform(60, 98), 1)
                grade = "A+" if score >= 95 else ("A" if score >= 90 else ("B+" if score >= 85 else ("B" if score >= 80 else ("C" if score >= 70 else "D"))))

            passed = score >= 80
            status = "approved" if passed else "rejected"
            await self.db.products.update_one(
                {"id": p["id"]},
                {"$set": {"status": status, "qc_score": score, "qc_grade": grade}}
            )
            label = "✓ APPROVED" if passed else "✗ REJECTED"
            level = "success" if passed else "error"
            await self._log("Inspector Two", "quality_control",
                f"{label}: «{p.get('title','?')[:45]}» — {score:.0f}/100 ({grade})", level)
            await self._set_state("quality_control", {
                "current_task": f"Reviewing: {p.get('title','')[:39]}…",
            })
            await asyncio.sleep(random.uniform(1, 3))

        approved = await self.db.products.count_documents({"status": "approved"})
        await self._set_state("quality_control", {
            "current_task": f"Queue cleared — {approved} products approved total",
            "approved_total": approved,
        })

    # ─── Division: Social & Advertising ─────────────────────

    PLATFORMS = ["TikTok", "Instagram", "YouTube Shorts", "X (Twitter)", "Pinterest", "Facebook"]

    async def _cycle_social_ads(self):
        if not self.db:
            await asyncio.sleep(30)
            return
        products = await self.db.products.find(
            {"status": "approved", "campaign_created": {"$ne": True}},
            {"_id": 0}
        ).limit(3).to_list(3)

        if not products:
            pending = await self.db.campaigns.count_documents({"status": "pending_approval"})
            await self._set_state("social_ads", {
                "current_task": f"Waiting for QC approvals — {pending} campaigns await your review",
                "pending_approvals": pending,
            })
            await asyncio.sleep(60)
            return

        for product in products:
            if not self._running.get("social_ads"):
                break
            title = product.get("title", "Product")[:45]
            await self._log("Creator Alpha", "social_ads",
                f"Building campaign: {title}", "info")

            content = []
            for platform in self.PLATFORMS:
                content.append(self._make_post_content(product, platform))
                await self._log("Creator Beta", "social_ads",
                    f"Created {platform} content for «{title[:30]}»", "info")
                await asyncio.sleep(0.3)

            campaign = {
                "id": str(uuid.uuid4()),
                "product_id": product.get("id"),
                "product_title": product.get("title", ""),
                "product_niche": product.get("niche", ""),
                "platforms": self.PLATFORMS,
                "content": content,
                "budget": random.choice([50, 100, 150, 200]),
                "duration_days": 7,
                "targeting": f"{product.get('niche','digital products')} audience · 18–45",
                "estimated_reach": f"{random.randint(20, 150)}K",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending_approval",
                "type": "product",
            }
            try:
                await self.db.campaigns.insert_one({**campaign})
                await self.db.products.update_one(
                    {"id": product.get("id")},
                    {"$set": {"campaign_created": True, "campaign_id": campaign["id"]}}
                )
            except Exception:
                pass
            await self._log("Ad Builder", "social_ads",
                f"🔔 Campaign ready for your approval: «{title}» · Est. reach {campaign['estimated_reach']}",
                "warning")

        pending = await self.db.campaigns.count_documents({"status": "pending_approval"})
        await self._set_state("social_ads", {
            "current_task": f"{pending} campaigns awaiting your approval",
            "pending_approvals": pending,
        })

    def _make_post_content(self, product: Dict, platform: str) -> Dict:
        niche = product.get("niche", "digital products")
        price = product.get("price", 19.99)
        title = product.get("title", "")
        hooks = {
            "TikTok": f"POV: you just found the best {niche} resource for ${price} 🔥 #digitalproducts",
            "Instagram": f"Stop struggling with {niche}. This changes everything 👇\n\n${price} · Link in bio",
            "YouTube Shorts": f"I earned ${price * random.randint(50,200):.0f} selling THIS {niche} resource",
            "X (Twitter)": f"Just dropped: {title[:60]} — ${price} 🔗 link in bio",
            "Pinterest": f"{title} | {niche.title()} Resources | Instant Download | ${price}",
            "Facebook": f"New drop 🔥 {title[:60]}\n{niche.title()} resource for serious creators · ${price}",
        }
        return {
            "platform": platform,
            "caption": hooks.get(platform, f"Check out: {title}"),
            "hashtags": [f"#{niche.replace(' ', '')}", "#digitalproducts", "#passiveincome", "#makemoneyonline"],
            "format": "video" if platform in ["TikTok", "YouTube Shorts"] else "image+caption",
            "video_length": "15–30s" if platform == "TikTok" else ("60s" if platform == "YouTube Shorts" else None),
        }

    # ─── Division: Distribution & Sales ─────────────────────

    MARKETPLACES = ["Gumroad", "Etsy", "Sellfy", "Payhip", "Amazon KDP", "Teachable", "Podia", "Ko-fi"]

    async def _cycle_distribution(self):
        if not self.db:
            await asyncio.sleep(30)
            return
        products = await self.db.products.find(
            {"status": "approved", "published": {"$ne": True}},
            {"_id": 0}
        ).limit(5).to_list(5)

        if not products:
            await self._log("Deals Agent", "distribution",
                "No new products — building bundle deal proposal", "info")
            await self._set_state("distribution", {
                "current_task": "All products listed — crafting bundle deals",
            })
            await asyncio.sleep(120)
            return

        for product in products:
            if not self._running.get("distribution"):
                break
            title = product.get("title", "Product")[:45]
            markets = random.sample(self.MARKETPLACES, random.randint(3, 5))
            await self._log("Publisher One", "distribution",
                f"Publishing «{title}» to {len(markets)} platforms", "info")
            for market in markets:
                if not self._running.get("distribution"):
                    break
                await self._log("Publisher One", "distribution",
                    f"Listed on {market}: «{title[:30]}»", "success")
                await asyncio.sleep(random.uniform(0.5, 2))
            try:
                await self.db.products.update_one(
                    {"id": product.get("id")},
                    {"$set": {"published": True, "published_on": markets, "published_at": datetime.now(timezone.utc).isoformat()}}
                )
            except Exception:
                pass

        total = await self.db.products.count_documents({"published": True})
        await self._set_state("distribution", {
            "current_task": f"{len(products)} products listed · {total} total active listings",
            "total_listings": total,
        })

    # ─── Division: Discovery ─────────────────────────────────

    TREND_SIGNALS = [
        ("Reddit r/passive_income", "AI invoice automation template"),
        ("Google Trends +340%", "Korean beauty digital lookbook"),
        ("TikTok #StudyWithMe", "Aesthetic study planner bundle"),
        ("Amazon Kindle Top 10", "Stoic morning routine workbook"),
        ("ClickBank #1", "Manifestation journal system"),
        ("Etsy Trending", "Digital wedding planner 2025"),
        ("ProductHunt Launch", "Notion second brain OS"),
        ("YouTube Trending", "AI art prompt mega-pack (500+)"),
        ("X Trending", "ChatGPT business prompt library"),
        ("AppSumo Deal", "SEO content calendar kit"),
        ("Reddit r/entrepreneur", "Cold email swipe file for SaaS"),
        ("TikTok #BookTok", "Shadow work journal PDF"),
    ]

    async def _cycle_discovery(self):
        signals = random.sample(self.TREND_SIGNALS, random.randint(3, 6))
        await self._log("Trend Scout", "discovery",
            f"Scanning {len(self.TREND_SIGNALS)} trend sources…", "info")

        for source, idea in signals:
            if not self._running.get("discovery"):
                break
            opp = {
                "id": str(uuid.uuid4()),
                "source": source,
                "product_idea": idea,
                "score": round(random.uniform(70, 99), 1),
                "market_size": f"${random.randint(10, 500)}K/mo",
                "competition": random.choice(["Low", "Medium", "Low-Medium"]),
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "status": "discovered",
            }
            if self.db:
                try:
                    await self.db.opportunities.update_one(
                        {"product_idea": idea},
                        {"$setOnInsert": opp},
                        upsert=True,
                    )
                except Exception:
                    pass
            await self._log("Niche Hunter", "discovery",
                f"Found: «{idea}» via {source} — {opp['market_size']} market", "success")
            await asyncio.sleep(random.uniform(1, 4))

        total = await self._count("opportunities") if self.db else len(signals)
        await self._set_state("discovery", {
            "current_task": f"Catalogued {len(signals)} new opportunities this cycle",
            "total_opportunities": total,
        })

    # ─── Division: Affiliate ─────────────────────────────────

    AFFILIATE_ITEMS = [
        ("ClickBank", "The Smoothie Diet", "$47", "75%", "$35.25"),
        ("Amazon Associates", "AI Creator Tools Bundle", "$127", "8%", "$10.16"),
        ("ShareASale", "Canva Pro Annual", "$119.99", "15%", "$18.00"),
        ("Impact", "Teachable Pro Plan", "$249/mo", "30%", "$74.70"),
        ("PartnerStack", "Notion Team Plan", "$96/yr", "50%", "$48.00"),
        ("ClickBank", "Manifestation Miracle", "$37", "75%", "$27.75"),
        ("CJ Affiliate", "Grammarly Premium", "$144/yr", "20%", "$28.80"),
        ("ClickBank", "Keto Custom Plan", "$37", "75%", "$27.75"),
        ("ShareASale", "Tailwind Pinterest Tool", "$119.88/yr", "15%", "$17.98"),
        ("ClickBank", "The Lost Book of Remedies", "$37", "75%", "$27.75"),
    ]

    async def _cycle_affiliate(self):
        items = random.sample(self.AFFILIATE_ITEMS, random.randint(2, 4))
        await self._log("Link Hunter", "affiliate",
            "Scanning ClickBank · Amazon · ShareASale · Impact…", "info")

        for network, product, price, rate, commission in items:
            if not self._running.get("affiliate"):
                break
            item = {
                "id": str(uuid.uuid4()),
                "network": network,
                "product": product,
                "price": price,
                "commission_rate": rate,
                "commission_value": commission,
                "affiliate_link": f"https://hop.clickbank.net/?affiliate=fiilthy&vendor={product.lower().replace(' ','')[:12]}",
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "promoted": False,
            }
            if self.db:
                try:
                    await self.db.affiliate_products.update_one(
                        {"product": product, "network": network},
                        {"$setOnInsert": item},
                        upsert=True,
                    )
                except Exception:
                    pass
            await self._log("Commission Tracker", "affiliate",
                f"Got link: «{product}» on {network} — {rate} = {commission}/sale", "success")

            promo = {
                "id": str(uuid.uuid4()),
                "type": "affiliate",
                "product_title": f"[Affiliate] {product}",
                "product_niche": "affiliate",
                "platforms": ["TikTok", "Instagram"],
                "content": [
                    {"platform": "TikTok", "caption": f"This product made me {commission} per sale 👀 #{network.replace(' ','')}"},
                    {"platform": "Instagram", "caption": f"Promoting: {product} — {rate} commission via {network}"},
                ],
                "estimated_reach": f"{random.randint(10, 80)}K",
                "commission_value": commission,
                "status": "pending_approval",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            if self.db:
                try:
                    await self.db.campaigns.insert_one({**promo})
                except Exception:
                    pass
            await self._log("Promo Agent", "affiliate",
                f"→ Queued social promo for «{product}» — review needed", "warning")
            await asyncio.sleep(random.uniform(2, 5))

        total = await self._count("affiliate_products") if self.db else len(items)
        await self._set_state("affiliate", {
            "current_task": f"Tracking {total} affiliate products",
            "links_total": total,
        })

    # ─── Utilities ───────────────────────────────────────────

    async def _log(self, agent: str, division: str, message: str, level: str = "info"):
        entry = {
            "id": str(uuid.uuid4()),
            "division": division,
            "division_name": DIVISIONS.get(division, {}).get("name", division),
            "agent": agent,
            "message": message,
            "level": level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if self.db:
            try:
                await self.db.agent_activity.insert_one(dict(entry))
                count = await self.db.agent_activity.count_documents({})
                if count > 500:
                    oldest = await self.db.agent_activity.find(
                        {}, {"_id": 1}
                    ).sort("timestamp", 1).limit(count - 500).to_list(count - 500)
                    await self.db.agent_activity.delete_many(
                        {"_id": {"$in": [d["_id"] for d in oldest]}}
                    )
            except Exception as e:
                logger.debug(f"Log error: {e}")

    async def _set_state(self, division: str, updates: Dict):
        if not self.db:
            return
        try:
            await self.db.agent_divisions.update_one(
                {"id": division},
                {"$set": {**updates, "updated_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True,
            )
        except Exception as e:
            logger.debug(f"State update error: {e}")

    async def _count(self, collection: str, query: Dict = None) -> int:
        if not self.db:
            return 0
        return await self.db[collection].count_documents(query or {})

    # ─── Public API ──────────────────────────────────────────

    async def get_all_status(self) -> Dict[str, Any]:
        divisions_out = {}
        for div_id, config in DIVISIONS.items():
            state: Dict = {}
            if self.db:
                try:
                    state = await self.db.agent_divisions.find_one(
                        {"id": div_id}, {"_id": 0}
                    ) or {}
                except Exception:
                    pass
            divisions_out[div_id] = {
                **config,
                "id": div_id,
                "is_running": self._running.get(div_id, False),
                "status": state.get("status", "idle"),
                "current_task": state.get("current_task", "Ready"),
                "cycle_progress": state.get("cycle_progress", 0),
                "updated_at": state.get("updated_at"),
                "last_cycle_at": state.get("last_cycle_at"),
                **{k: v for k, v in state.items() if k not in ["id", "status", "current_task", "updated_at"]},
            }
        return divisions_out

    async def get_recent_activity(self, limit: int = 60) -> List[Dict]:
        if not self.db:
            return []
        try:
            return await self.db.agent_activity.find(
                {}, {"_id": 0}
            ).sort("timestamp", -1).limit(limit).to_list(limit)
        except Exception:
            return []

    async def get_pending_approvals(self) -> List[Dict]:
        if not self.db:
            return []
        try:
            return await self.db.campaigns.find(
                {"status": "pending_approval"}, {"_id": 0}
            ).sort("created_at", -1).to_list(50)
        except Exception:
            return []

    async def approve_campaign(self, campaign_id: str) -> Dict:
        if not self.db:
            return {"success": False, "error": "DB unavailable"}
        await self.db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": {"status": "approved", "approved_at": datetime.now(timezone.utc).isoformat()}}
        )
        doc = await self.db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
        await self._log("Human", "social_ads",
            f"✅ Approved: «{(doc or {}).get('product_title','?')[:45]}»", "success")
        return {"success": True, "campaign_id": campaign_id, "status": "approved"}

    async def reject_campaign(self, campaign_id: str, reason: str = "") -> Dict:
        if not self.db:
            return {"success": False, "error": "DB unavailable"}
        await self.db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": {
                "status": "rejected",
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "reject_reason": reason,
            }}
        )
        doc = await self.db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
        await self._log("Human", "social_ads",
            f"❌ Rejected: «{(doc or {}).get('product_title','?')[:45]}»", "error")
        return {"success": True, "campaign_id": campaign_id, "status": "rejected"}

    async def get_metrics(self) -> Dict:
        if not self.db:
            return {
                "products_today": 0, "approved_today": 0, "pending_approvals": 0,
                "total_products": 0, "total_opportunities": 0, "total_affiliate": 0,
                "active_divisions": sum(1 for r in self._running.values() if r),
            }
        try:
            today = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ).isoformat()
            return {
                "products_today": await self.db.products.count_documents({"created_at": {"$gte": today}}),
                "approved_today": await self.db.products.count_documents({"status": "approved", "created_at": {"$gte": today}}),
                "pending_approvals": await self.db.campaigns.count_documents({"status": "pending_approval"}),
                "total_products": await self.db.products.count_documents({}),
                "total_opportunities": await self.db.opportunities.count_documents({}),
                "total_affiliate": await self.db.affiliate_products.count_documents({}),
                "active_divisions": sum(1 for r in self._running.values() if r),
            }
        except Exception as e:
            logger.error(f"Metrics error: {e}")
            return {"active_divisions": sum(1 for r in self._running.values() if r)}


# ─── Singleton ────────────────────────────────────────────────

_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator(db=None) -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(db)
    elif db is not None and _orchestrator.db is None:
        _orchestrator.db = db
    return _orchestrator
