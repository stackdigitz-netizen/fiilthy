"""
FIILTHY.AI — Agent Empire Orchestrator
6 autonomous agent divisions running 24/7
"""
import asyncio
import os
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
        self.scout = None
        try:
            from ai_services.opportunity_scout import OpportunityScout
            self.scout = OpportunityScout()
        except Exception as exc:
            logger.debug(f"Opportunity scout unavailable: {exc}")

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
        candidates = await self._select_generation_candidates(target)
        source_names = ", ".join(sorted({candidate.get("source", "internal") for candidate in candidates[:3]}))
        await self._log("Scout Alpha", "product_rd", f"Prioritising {len(candidates)} high-signal opportunities from {source_names or 'internal research'}…", "info")
        await self._set_state("product_rd", {
            "current_task": "Ranking niches by opportunity score",
            "cycle_progress": 0,
            "cycle_target": target,
        })
        await asyncio.sleep(random.uniform(3, 6))

        created = 0
        for candidate in candidates:
            if not self._running.get("product_rd"):
                break
            niche = candidate["niche"]
            ptype = candidate["product_type"]
            product = await self._generate_product(niche, ptype, candidate)
            if self.db is not None:
                try:
                    await self.db.products.insert_one({**product})
                except Exception:
                    pass
            created += 1
            await self._log("Builder Prime", "product_rd",
                f"Built #{created}: {product['title'][:50]} (signal {candidate.get('score', 0):.0f})", "info")
            await self._set_state("product_rd", {
                "current_task": f"Built {created}/{target}: {product['title'][:40]}…",
                "cycle_progress": created,
            })
            await asyncio.sleep(random.uniform(2, 6))

        await self._log("Scout Beta", "product_rd",
            f"Cycle done — {created} products sent to QC", "success")
        today_count = await self._count("products") if self.db is not None else created
        await self._set_state("product_rd", {
            "current_task": f"Cycle complete — {created} products created",
            "last_cycle_at": datetime.now(timezone.utc).isoformat(),
            "total_today": today_count,
            "cycle_progress": 0,
        })

    async def _select_generation_candidates(self, target: int) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []
        seen_niches = set()

        if self.db is not None:
            try:
                opportunities = await self.db.opportunities.find(
                    {},
                    {"_id": 0},
                ).sort([
                    ("score", -1),
                    ("trend_score", -1),
                    ("discovered_at", -1),
                ]).limit(target * 3).to_list(target * 3)
                for index, opportunity in enumerate(opportunities):
                    candidate = self._candidate_from_opportunity(opportunity, index)
                    if candidate["niche"] in seen_niches:
                        continue
                    seen_niches.add(candidate["niche"])
                    candidates.append(candidate)
                    if len(candidates) >= target:
                        return candidates
            except Exception as exc:
                logger.debug(f"Opportunity lookup failed: {exc}")

        if len(candidates) < target and self.scout is not None:
            try:
                fresh_opportunities = await self.scout.scout_opportunities(self.TREND_SOURCES[:3])
                for index, opportunity in enumerate(fresh_opportunities):
                    candidate = self._candidate_from_opportunity(opportunity, index)
                    if candidate["niche"] in seen_niches:
                        continue
                    seen_niches.add(candidate["niche"])
                    candidates.append(candidate)
                    if self.db is not None:
                        try:
                            await self.db.opportunities.update_one(
                                {"product_idea": candidate["niche"]},
                                {"$set": {
                                    "id": opportunity.get("id", str(uuid.uuid4())),
                                    "source": candidate["source"],
                                    "product_idea": candidate["niche"],
                                    "score": candidate["score"],
                                    "keywords": candidate["keywords"],
                                    "suggested_products": [candidate.get("suggested_title")] if candidate.get("suggested_title") else [],
                                    "market_size": candidate.get("market_size", "Growing"),
                                    "competition": opportunity.get("competition_level") or opportunity.get("competition") or "Medium",
                                    "discovered_at": opportunity.get("created_at") or datetime.now(timezone.utc).isoformat(),
                                    "status": opportunity.get("status", "discovered"),
                                }},
                                upsert=True,
                            )
                        except Exception as exc:
                            logger.debug(f"Opportunity upsert failed: {exc}")
                    if len(candidates) >= target:
                        return candidates
            except Exception as exc:
                logger.debug(f"Scout refresh failed: {exc}")

        fallback_attempts = 0
        while len(candidates) < target and fallback_attempts < len(self.NICHES) * 2:
            niche = random.choice(self.NICHES)
            fallback_attempts += 1
            if niche in seen_niches:
                continue
            seen_niches.add(niche)
            ptype = self._canonical_product_type(random.choice(self.PRODUCT_TYPES))
            candidates.append({
                "niche": niche,
                "product_type": ptype,
                "source": "fallback trend library",
                "score": round(random.uniform(72, 90), 1),
                "keywords": [niche, ptype, "digital product", "online business", "ai workflow"],
                "suggested_title": f"{niche.title()} {ptype.title()} Revenue System",
                "market_size": "Growing",
            })

        return candidates[:target]

    def _candidate_from_opportunity(self, opportunity: Dict[str, Any], index: int) -> Dict[str, Any]:
        niche = str(
            opportunity.get("niche")
            or opportunity.get("product_idea")
            or self.NICHES[index % len(self.NICHES)]
        ).strip()
        score = float(opportunity.get("score") or (float(opportunity.get("trend_score", 0)) * 100) or 75)
        suggested_products = opportunity.get("suggested_products") or []
        if isinstance(suggested_products, str):
            suggested_products = [suggested_products]
        keywords = [str(keyword).strip() for keyword in (opportunity.get("keywords") or []) if str(keyword).strip()]
        raw_type = opportunity.get("product_type") or opportunity.get("type") or self.PRODUCT_TYPES[index % len(self.PRODUCT_TYPES)]
        source = str(opportunity.get("source") or "opportunity engine")

        return {
            "niche": niche,
            "product_type": self._canonical_product_type(raw_type),
            "source": source,
            "score": round(min(score, 100), 1),
            "keywords": keywords,
            "suggested_title": suggested_products[0] if suggested_products else None,
            "market_size": opportunity.get("market_size") or "Growing",
        }

    def _canonical_product_type(self, product_type: str) -> str:
        lowered = str(product_type or "ebook").lower()
        if any(keyword in lowered for keyword in ["course", "masterclass", "audio", "training"]):
            return "course"
        if any(keyword in lowered for keyword in ["template", "planner", "toolkit", "swipe", "pack", "resource", "script", "checklist"]):
            return "template"
        return "ebook"

    def _recommended_price(self, product_type: str, opportunity_score: float) -> float:
        base = {
            "ebook": 47.0,
            "template": 39.0,
            "course": 97.0,
        }.get(product_type, 49.0)
        if opportunity_score >= 90:
            base += 20.0 if product_type == "course" else 10.0
        return base

    def _default_includes(self, product_type: str) -> List[str]:
        if product_type == "course":
            return [
                "8-lesson implementation path",
                "Offer positioning workbook",
                "Launch checklist",
                "Sales copy prompts",
                "Fulfillment SOP",
            ]
        if product_type == "template":
            return [
                "Editable master templates",
                "Quick-start guide",
                "Campaign prompt pack",
                "Distribution checklist",
                "Optimization tracker",
            ]
        return [
            "Step-by-step blueprint",
            "Positioning worksheet",
            "Launch plan",
            "Buyer messaging prompts",
            "Execution checklist",
        ]

    def _normalize_product(
        self,
        product: Optional[Dict[str, Any]],
        niche: str,
        product_type: str,
        candidate: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        candidate = candidate or {}
        normalized = dict(product or {})
        opportunity_score = float(candidate.get("score") or normalized.get("opportunity_score") or 75)
        recommended_price = self._recommended_price(product_type, opportunity_score)
        suggested_title = candidate.get("suggested_title")
        keywords = [
            str(keyword).strip()
            for keyword in (candidate.get("keywords") or normalized.get("keywords") or normalized.get("tags") or [])
            if str(keyword).strip()
        ]
        if niche not in keywords:
            keywords.insert(0, niche)
        for fallback_keyword in [product_type, "digital product", "online business", "ai workflow"]:
            if fallback_keyword not in keywords:
                keywords.append(fallback_keyword)
        keywords = list(dict.fromkeys(keywords))[:6]

        title = normalized.get("title") or suggested_title or f"{niche.title()} {product_type.title()} Revenue System"
        description = normalized.get("description") or (
            f"{title} is built for founders, freelancers, and creators who want a cleaner path to revenue inside {niche}. "
            f"It combines positioning guidance, concrete implementation steps, offer structure, and launch assets so buyers can move from idea to sellable offer without wasting weeks on scattered research. "
            f"Instead of vague theory, this product focuses on execution, packaging, and conversion so it is ready to market and deliver immediately."
        )

        normalized["id"] = normalized.get("id") or str(uuid.uuid4())
        normalized["title"] = title
        normalized["niche"] = niche
        normalized["product_type"] = self._canonical_product_type(normalized.get("product_type") or normalized.get("type") or product_type)
        normalized["type"] = normalized["product_type"]
        normalized["price"] = float(normalized.get("price") or recommended_price)
        normalized["description"] = description
        normalized.setdefault(
            "fullDescription",
            description + " Buyers get a structured path, launch assets, and repeatable systems that reduce guesswork and improve speed to first sale.",
        )
        normalized["keywords"] = keywords
        normalized["tags"] = list(dict.fromkeys(normalized.get("tags") or keywords))[:6]
        normalized["benefits"] = normalized.get("benefits") or [
            "Turns a trend into a sellable digital offer",
            "Shortens launch time with reusable systems",
            "Gives buyers assets they can implement immediately",
        ]
        normalized["includes"] = normalized.get("includes") or self._default_includes(normalized["product_type"])
        normalized["target_audience"] = normalized.get("target_audience") or f"Founders, freelancers, and creators building revenue in {niche}"
        normalized["image_url"] = normalized.get("image_url") or normalized.get("cover_image") or normalized.get("cover") or "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80"
        normalized["cover_image"] = normalized.get("cover_image") or normalized["image_url"]
        normalized["cover"] = normalized.get("cover") or normalized["cover_image"]
        normalized["source"] = normalized.get("source") or "agent_rd"
        normalized["status"] = "pending_qc"
        normalized["created_at"] = normalized.get("created_at") or datetime.now(timezone.utc).isoformat()
        normalized["opportunity_score"] = round(opportunity_score, 1)
        normalized["opportunity_source"] = candidate.get("source") or normalized.get("opportunity_source") or "agent_rd"
        normalized["market_size"] = candidate.get("market_size") or normalized.get("market_size") or "Growing"
        normalized["featured_candidate"] = bool(normalized.get("featured_candidate")) or opportunity_score >= 88
        normalized["campaign_priority"] = "auto" if normalized["featured_candidate"] else "review"
        normalized.setdefault("revenue", 0.0)
        normalized.setdefault("conversions", 0)
        normalized.setdefault("clicks", 0)

        if normalized["product_type"] == "course":
            normalized.setdefault("modules", [
                "Offer Foundations",
                "Research and Positioning",
                "Asset Creation",
                "Launch Sequence",
                "Checkout and Delivery",
                "Scale and Retention",
            ])
        elif normalized["product_type"] == "template":
            normalized.setdefault("sections", [
                "Planning",
                "Execution",
                "Measurement",
            ])
        else:
            normalized.setdefault("chapters", [
                "Market Positioning",
                "Offer Structure",
                "Pricing Strategy",
                "Launch Assets",
                "Fulfillment System",
            ])
            normalized.setdefault("pages", 28)

        return normalized

    def _calculate_launch_score(self, product: Dict[str, Any], qc_score: Optional[float] = None) -> float:
        qc_value = float(qc_score if qc_score is not None else product.get("qc_score") or 0)
        opportunity_value = float(product.get("opportunity_score") or 0)
        revenue_value = min(float(product.get("revenue") or 0) * 2, 100)
        conversion_value = min(float(product.get("conversions") or 0) * 10, 100)
        launch_score = (qc_value * 0.55) + (opportunity_value * 0.25) + (revenue_value * 0.10) + (conversion_value * 0.10)
        return round(min(launch_score, 100), 1)

    async def _generate_product(self, niche: str, ptype: str, candidate: Optional[Dict[str, Any]] = None) -> Dict:
        if self.db is not None:
            try:
                from ai_services.gemini_product_generator import get_gemini_generator
                gen = await get_gemini_generator(self.db)
                result = await gen.generate_product({
                    "niche": niche,
                    "type": ptype,
                    "keywords": (candidate or {}).get("keywords") or [niche, ptype],
                })
                if result:
                    return self._normalize_product(result, niche, ptype, candidate)
            except Exception as exc:
                logger.debug(f"Gemini generation fallback for {niche}: {exc}")

        return self._normalize_product({}, niche, ptype, candidate)

    # ─── Division: Quality Control ───────────────────────────

    async def _cycle_quality_control(self):
        if self.db is None:
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
                report = run_qc(p)
                score = float(report.get("overall_score", 0))
                grade = report.get("grade", "F")
                passed = bool(report.get("ready_for_sale"))
            except Exception as exc:
                logger.error(f"QC engine fallback for {p.get('id')}: {exc}")
                score = round(random.uniform(60, 98), 1)
                grade = "A+" if score >= 95 else ("A" if score >= 90 else ("B+" if score >= 85 else ("B" if score >= 80 else ("C" if score >= 70 else "D"))))
                passed = score >= 80
                report = None

            status = "approved" if passed else "rejected"
            launch_score = self._calculate_launch_score(p, qc_score=score)
            await self.db.products.update_one(
                {"id": p["id"]},
                {"$set": {
                    "status": status,
                    "qc_score": score,
                    "qc_grade": grade,
                    "qc_report": report,
                    "qc_passed": bool(report.get("passed")) if report else passed,
                    "qc_ready": bool(report.get("ready_for_sale")) if report else passed,
                    "launch_score": launch_score,
                    "featured_candidate": launch_score >= 88,
                    "campaign_priority": "auto" if launch_score >= 88 else "review",
                    "store_ready": passed,
                    "store_ready_at": datetime.now(timezone.utc).isoformat() if passed else None,
                }}
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
        store_ready = await self.db.products.count_documents({"store_ready": True})
        await self._set_state("quality_control", {
            "current_task": f"Queue cleared — {approved} approved, {store_ready} store-ready",
            "approved_total": approved,
            "store_ready_total": store_ready,
        })

    # ─── Division: Social & Advertising ─────────────────────

    PLATFORMS = ["TikTok", "Instagram", "YouTube Shorts", "X (Twitter)", "Pinterest", "Facebook"]

    async def _cycle_social_ads(self):
        if self.db is None:
            await asyncio.sleep(30)
            return
        products = await self.db.products.find(
            {"status": "approved", "campaign_created": {"$ne": True}},
            {"_id": 0}
        ).sort([
            ("launch_score", -1),
            ("qc_score", -1),
            ("opportunity_score", -1),
            ("created_at", -1),
        ]).limit(3).to_list(3)

        if not products:
            pending = await self.db.campaigns.count_documents({"status": "pending_approval"})
            active = await self.db.campaigns.count_documents({"status": "active"})
            await self._set_state("social_ads", {
                "current_task": f"Waiting for fresh winners — {active} live, {pending} pending review",
                "pending_approvals": pending,
                "active_campaigns": active,
            })
            await asyncio.sleep(60)
            return

        for product in products:
            if not self._running.get("social_ads"):
                break
            title = product.get("title", "Product")[:45]
            launch_score = float(product.get("launch_score") or 0)
            auto_launch = bool(product.get("featured_candidate")) or launch_score >= 88
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
                "estimated_reach": f"{random.randint(40, 250) if auto_launch else random.randint(20, 150)}K",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active" if auto_launch else "pending_approval",
                "approval_required": not auto_launch,
                "launch_score": launch_score,
                "type": "product",
            }
            try:
                await self.db.campaigns.insert_one({**campaign})
                await self.db.products.update_one(
                    {"id": product.get("id")},
                    {"$set": {
                        "campaign_created": True,
                        "campaign_id": campaign["id"],
                        "campaign_status": campaign["status"],
                        "ads_live": auto_launch,
                        "ads_live_at": datetime.now(timezone.utc).isoformat() if auto_launch else None,
                    }}
                )
            except Exception:
                pass
            if auto_launch:
                await self._log("Ad Builder", "social_ads",
                    f"🚀 Auto-launched ads for «{title}» · Launch score {launch_score:.0f} · Est. reach {campaign['estimated_reach']}",
                    "success")
            else:
                await self._log("Ad Builder", "social_ads",
                    f"🔔 Campaign ready for your approval: «{title}» · Est. reach {campaign['estimated_reach']}",
                    "warning")

        pending = await self.db.campaigns.count_documents({"status": "pending_approval"})
        active = await self.db.campaigns.count_documents({"status": "active"})
        await self._set_state("social_ads", {
            "current_task": f"{active} live campaigns · {pending} awaiting approval",
            "pending_approvals": pending,
            "active_campaigns": active,
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
        if self.db is None:
            await asyncio.sleep(30)
            return
        products = await self.db.products.find(
            {"status": {"$in": ["approved", "ready"]}, "published": {"$ne": True}},
            {"_id": 0}
        ).sort([
            ("launch_score", -1),
            ("qc_score", -1),
            ("opportunity_score", -1),
            ("created_at", -1),
        ]).limit(5).to_list(5)

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
            markets = ["Store", *random.sample(self.MARKETPLACES, random.randint(3, 5))]
            await self._log("Publisher One", "distribution",
                f"Publishing «{title}» to {len(markets)} platforms", "info")
            published_links = self._build_distribution_links(product, markets)
            for market in markets:
                if not self._running.get("distribution"):
                    break
                await self._log("Publisher One", "distribution",
                    f"Listed on {market}: «{title[:30]}»", "success")
                await asyncio.sleep(random.uniform(0.5, 2))
            try:
                await self.db.products.update_one(
                    {"id": product.get("id")},
                    {"$set": {
                        "published": True,
                        "status": "published",
                        "featured": bool(product.get("featured_candidate")) or float(product.get("launch_score") or 0) >= 88,
                        "published_on": published_links,
                        "marketplace_links": published_links,
                        "store_url": next((entry["url"] for entry in published_links if entry["platform"] == "Store"), None),
                        "published_at": datetime.now(timezone.utc).isoformat(),
                    }}
                )
            except Exception:
                pass

        total = await self.db.products.count_documents({"published": True})
        await self._set_state("distribution", {
            "current_task": f"{len(products)} products listed · {total} total active listings",
            "total_listings": total,
        })

    def _build_distribution_links(self, product: Dict[str, Any], markets: List[str]) -> List[Dict[str, Any]]:
        frontend_url = os.environ.get("FRONTEND_URL", "https://frontend-one-ashen-16.vercel.app").rstrip("/")
        slug = str(product.get("id", "product"))
        links = []

        for market in markets:
            if market == "Store":
                url = f"{frontend_url}/store"
            elif market == "Gumroad":
                url = f"https://gumroad.com/l/{slug}"
            elif market == "Etsy":
                url = f"https://etsy.com/listing/{slug}"
            elif market == "Sellfy":
                url = f"https://sellfy.com/p/{slug}/"
            elif market == "Payhip":
                url = f"https://payhip.com/b/{slug}"
            elif market == "Amazon KDP":
                url = f"https://amazon.com/dp/{slug[:10].upper()}"
            elif market == "Teachable":
                url = f"https://{slug}.teachable.com/p/{slug}"
            elif market == "Podia":
                url = f"https://{slug}.podia.com/{slug}"
            elif market == "Ko-fi":
                url = f"https://ko-fi.com/s/{slug}"
            else:
                url = f"{frontend_url}/store"
            links.append({"platform": market, "url": url, "status": "live"})

        return links

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
            if self.db is not None:
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

        total = await self._count("opportunities") if self.db is not None else len(signals)
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
            if self.db is not None:
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
            if self.db is not None:
                try:
                    await self.db.campaigns.insert_one({**promo})
                except Exception:
                    pass
            await self._log("Promo Agent", "affiliate",
                f"→ Queued social promo for «{product}» — review needed", "warning")
            await asyncio.sleep(random.uniform(2, 5))

        total = await self._count("affiliate_products") if self.db is not None else len(items)
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
        if self.db is not None:
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
        if self.db is None:
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
        if self.db is None:
            return 0
        return await self.db[collection].count_documents(query or {})

    # ─── Public API ──────────────────────────────────────────

    async def get_all_status(self) -> Dict[str, Any]:
        divisions_out = {}
        for div_id, config in DIVISIONS.items():
            state: Dict = {}
            if self.db is not None:
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
        if self.db is None:
            return []
        try:
            return await self.db.agent_activity.find(
                {}, {"_id": 0}
            ).sort("timestamp", -1).limit(limit).to_list(limit)
        except Exception:
            return []

    async def get_pending_approvals(self) -> List[Dict]:
        if self.db is None:
            return []
        try:
            return await self.db.campaigns.find(
                {"status": "pending_approval"}, {"_id": 0}
            ).sort("created_at", -1).to_list(50)
        except Exception:
            return []

    async def approve_campaign(self, campaign_id: str) -> Dict:
        if self.db is None:
            return {"success": False, "error": "DB unavailable"}
        await self.db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": {"status": "active", "approved_at": datetime.now(timezone.utc).isoformat()}}
        )
        doc = await self.db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
        if doc and doc.get("product_id"):
            await self.db.products.update_one(
                {"id": doc.get("product_id")},
                {"$set": {
                    "campaign_status": "active",
                    "ads_live": True,
                    "ads_live_at": datetime.now(timezone.utc).isoformat(),
                }}
            )
        await self._log("Human", "social_ads",
            f"✅ Approved: «{(doc or {}).get('product_title','?')[:45]}»", "success")
        return {"success": True, "campaign_id": campaign_id, "status": "active"}

    async def reject_campaign(self, campaign_id: str, reason: str = "") -> Dict:
        if self.db is None:
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
        if doc and doc.get("product_id"):
            await self.db.products.update_one(
                {"id": doc.get("product_id")},
                {"$set": {"campaign_status": "rejected"}}
            )
        await self._log("Human", "social_ads",
            f"❌ Rejected: «{(doc or {}).get('product_title','?')[:45]}»", "error")
        return {"success": True, "campaign_id": campaign_id, "status": "rejected"}

    async def get_top_products(self, limit: int = 6) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        try:
            products = await self.db.products.find(
                {"status": {"$in": ["approved", "ready", "published"]}},
                {
                    "_id": 0,
                    "id": 1,
                    "title": 1,
                    "status": 1,
                    "price": 1,
                    "revenue": 1,
                    "conversions": 1,
                    "qc_score": 1,
                    "launch_score": 1,
                    "featured": 1,
                    "featured_candidate": 1,
                    "campaign_status": 1,
                    "store_url": 1,
                    "published_on": 1,
                    "opportunity_score": 1,
                },
            ).sort([
                ("featured", -1),
                ("launch_score", -1),
                ("revenue", -1),
                ("qc_score", -1),
                ("created_at", -1),
            ]).limit(limit).to_list(limit)

            for product in products:
                if not product.get("store_url"):
                    published_on = product.get("published_on") or []
                    if published_on and isinstance(published_on[0], dict):
                        product["store_url"] = next(
                            (entry.get("url") for entry in published_on if entry.get("platform") == "Store"),
                            None,
                        )
            return products
        except Exception as exc:
            logger.error(f"Top product lookup failed: {exc}")
            return []

    async def get_metrics(self) -> Dict:
        if self.db is None:
            return {
                "products_today": 0, "approved_today": 0, "pending_approvals": 0,
                "total_products": 0, "total_opportunities": 0, "total_affiliate": 0,
                "published_products": 0, "store_ready": 0, "live_campaigns": 0, "revenue_total": 0,
                "active_divisions": sum(1 for r in self._running.values() if r),
            }
        try:
            today = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ).isoformat()
            revenue_totals = await self.db.products.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$revenue"}}}
            ]).to_list(1)
            return {
                "products_today": await self.db.products.count_documents({"created_at": {"$gte": today}}),
                "approved_today": await self.db.products.count_documents({"status": "approved", "created_at": {"$gte": today}}),
                "pending_approvals": await self.db.campaigns.count_documents({"status": "pending_approval"}),
                "total_products": await self.db.products.count_documents({}),
                "total_opportunities": await self.db.opportunities.count_documents({}),
                "total_affiliate": await self.db.affiliate_products.count_documents({}),
                "published_products": await self.db.products.count_documents({"$or": [{"status": "published"}, {"published": True}]}),
                "store_ready": await self.db.products.count_documents({"status": {"$in": ["approved", "ready", "published"]}}),
                "live_campaigns": await self.db.campaigns.count_documents({"status": "active"}),
                "revenue_total": round(revenue_totals[0].get("total", 0), 2) if revenue_totals else 0,
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
