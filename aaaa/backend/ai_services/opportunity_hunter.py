"""
Autonomous Opportunity Hunter
Continuously searches for new income-generating opportunities
Creates specialized agent teams when new opportunities are found
"""
import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

class OpportunityHunter:
    """Autonomous system that hunts for new income opportunities 24/7"""
    
    # Categories of opportunities to hunt
    OPPORTUNITY_CATEGORIES = {
        "digital_products": {
            "name": "Digital Products",
            "types": ["ebooks", "courses", "templates", "planners", "printables", "presets", "fonts", "icons"],
            "platforms": ["Gumroad", "Etsy", "Shopify", "Amazon KDP", "Teachable"],
            "revenue_potential": "high"
        },
        "content_creation": {
            "name": "Content Creation",
            "types": ["youtube", "tiktok", "instagram", "twitter", "blog", "podcast", "newsletter"],
            "platforms": ["YouTube", "TikTok", "Instagram", "Twitter", "Medium", "Substack"],
            "revenue_potential": "medium-high"
        },
        "saas_tools": {
            "name": "SaaS & Tools",
            "types": ["chrome_extension", "notion_template", "airtable_base", "zapier_integration", "api_service"],
            "platforms": ["Chrome Store", "Notion", "Airtable", "Zapier", "RapidAPI"],
            "revenue_potential": "very_high"
        },
        "affiliate": {
            "name": "Affiliate Marketing",
            "types": ["product_reviews", "comparison_sites", "deal_aggregators", "coupon_sites"],
            "platforms": ["Amazon Associates", "ShareASale", "CJ Affiliate", "Impact"],
            "revenue_potential": "medium"
        },
        "services": {
            "name": "Automated Services",
            "types": ["ai_writing", "design_generation", "video_editing", "data_analysis"],
            "platforms": ["Fiverr", "Upwork", "Toptal"],
            "revenue_potential": "high"
        },
        "community": {
            "name": "Community & Membership",
            "types": ["discord_server", "slack_community", "membership_site", "patreon"],
            "platforms": ["Discord", "Slack", "Circle", "Patreon", "Gumroad Memberships"],
            "revenue_potential": "recurring"
        }
    }
    
    # Trending niches to monitor
    TRENDING_NICHES = [
        "AI tools", "productivity", "remote work", "side hustles", "investing",
        "fitness", "mental health", "parenting", "cooking", "travel",
        "personal finance", "career development", "entrepreneurship", "marketing",
        "web development", "mobile apps", "crypto", "NFTs", "sustainability",
        "minimalism", "self-improvement", "relationships", "education", "gaming"
    ]
    
    def __init__(self, db=None):
        self.db = db
        self.running = False
        self.discovered_opportunities = []
        self.agent_teams = {}
    
    async def hunt_opportunities(self) -> Dict[str, Any]:
        """Single hunt cycle - find new opportunities"""
        opportunities_found = []
        
        for category_id, category in self.OPPORTUNITY_CATEGORIES.items():
            # Simulate AI analysis of each category
            for opp_type in category["types"]:
                # Find trending niches for this type
                trending = random.sample(self.TRENDING_NICHES, min(3, len(self.TRENDING_NICHES)))
                
                for niche in trending:
                    opportunity = {
                        "id": f"opp-{uuid.uuid4().hex[:8]}",
                        "category": category_id,
                        "category_name": category["name"],
                        "type": opp_type,
                        "niche": niche,
                        "title": f"{niche.title()} {opp_type.replace('_', ' ').title()}",
                        "platforms": category["platforms"],
                        "revenue_potential": category["revenue_potential"],
                        "trend_score": round(random.uniform(0.6, 0.99), 2),
                        "competition_level": random.choice(["low", "medium", "high"]),
                        "estimated_time_to_market": f"{random.randint(1, 14)} days",
                        "estimated_monthly_revenue": f"${random.randint(100, 5000)}",
                        "status": "discovered",
                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                        "action_items": [
                            f"Research {niche} market demand",
                            f"Create {opp_type} product",
                            f"Set up on {random.choice(category['platforms'])}",
                            "Launch marketing campaign"
                        ]
                    }
                    
                    # Only add high-potential opportunities
                    if opportunity["trend_score"] > 0.75:
                        opportunities_found.append(opportunity)
        
        # Sort by trend score and take top opportunities
        opportunities_found.sort(key=lambda x: x["trend_score"], reverse=True)
        top_opportunities = opportunities_found[:10]
        
        # Save to database
        if self.db is not None:
            for opp in top_opportunities:
                await self.db.discovered_opportunities.update_one(
                    {"id": opp["id"]},
                    {"$set": opp},
                    upsert=True
                )
        
        return {
            "success": True,
            "opportunities_found": len(top_opportunities),
            "opportunities": top_opportunities,
            "hunted_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_all_opportunities(self, status: str = None, limit: int = 50) -> List[Dict]:
        """Get all discovered opportunities"""
        if self.db is None:
            return []
        
        query = {}
        if status:
            query["status"] = status
        
        opportunities = await self.db.discovered_opportunities.find(
            query, {"_id": 0}
        ).sort("trend_score", -1).limit(limit).to_list(limit)
        
        return opportunities
    
    async def create_agent_team(self, opportunity_id: str) -> Dict[str, Any]:
        """Create a specialized agent team for an opportunity"""
        if self.db is None:
            return {"success": False, "error": "Database not configured"}
        
        # Get the opportunity
        opp = await self.db.discovered_opportunities.find_one(
            {"id": opportunity_id}, {"_id": 0}
        )
        if not opp:
            return {"success": False, "error": "Opportunity not found"}
        
        # Create specialized team based on opportunity type
        team = {
            "id": f"team-{uuid.uuid4().hex[:8]}",
            "opportunity_id": opportunity_id,
            "opportunity_title": opp["title"],
            "category": opp["category"],
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "agents": self._get_agents_for_category(opp["category"]),
            "tasks_completed": 0,
            "revenue_generated": 0,
            "products_created": 0
        }
        
        # Save team
        await self.db.agent_teams.insert_one(team)
        team.pop("_id", None)  # Remove MongoDB ObjectId before serialization
        
        # Update opportunity status
        await self.db.discovered_opportunities.update_one(
            {"id": opportunity_id},
            {"$set": {"status": "team_assigned", "team_id": team["id"]}}
        )
        
        return {
            "success": True,
            "team": team
        }
    
    def _get_agents_for_category(self, category: str) -> List[Dict]:
        """Get specialized agents for a category"""
        base_agents = [
            {"name": "Research Agent", "role": "market_research", "status": "active"},
            {"name": "Content Agent", "role": "content_creation", "status": "active"},
            {"name": "Marketing Agent", "role": "marketing", "status": "active"},
            {"name": "Analytics Agent", "role": "analytics", "status": "active"}
        ]
        
        category_specific = {
            "digital_products": [
                {"name": "Product Designer", "role": "design", "status": "active"},
                {"name": "Copywriter", "role": "copywriting", "status": "active"}
            ],
            "content_creation": [
                {"name": "Video Editor", "role": "video", "status": "active"},
                {"name": "Social Manager", "role": "social_media", "status": "active"}
            ],
            "saas_tools": [
                {"name": "Developer Agent", "role": "development", "status": "active"},
                {"name": "UX Designer", "role": "ux_design", "status": "active"}
            ],
            "affiliate": [
                {"name": "SEO Agent", "role": "seo", "status": "active"},
                {"name": "Link Builder", "role": "link_building", "status": "active"}
            ],
            "services": [
                {"name": "Quality Agent", "role": "quality_assurance", "status": "active"},
                {"name": "Client Manager", "role": "client_management", "status": "active"}
            ],
            "community": [
                {"name": "Community Manager", "role": "community", "status": "active"},
                {"name": "Engagement Agent", "role": "engagement", "status": "active"}
            ]
        }
        
        return base_agents + category_specific.get(category, [])
    
    async def get_agent_teams(self, status: str = None) -> List[Dict]:
        """Get all agent teams"""
        if self.db is None:
            return []
        
        query = {}
        if status:
            query["status"] = status
        
        teams = await self.db.agent_teams.find(query, {"_id": 0}).to_list(100)
        return teams
    
    async def start_continuous_hunting(self, interval_hours: int = 6):
        """Start continuous opportunity hunting"""
        self.running = True
        while self.running:
            try:
                await self.hunt_opportunities()
                await asyncio.sleep(interval_hours * 3600)
            except Exception as e:
                print(f"Hunting error: {e}")
                await asyncio.sleep(60)  # Wait 1 min on error
    
    def stop_hunting(self):
        """Stop continuous hunting"""
        self.running = False


class ProductDiscoveryEngine:
    """Finds all products across all platforms and tracks performance"""
    
    def __init__(self, db=None):
        self.db = db
    
    async def discover_products(self) -> Dict[str, Any]:
        """Discover all products from all connected platforms"""
        all_products = []
        platform_stats = {}
        
        # Discover from each platform
        platforms = [
            ("gumroad", self._discover_gumroad),
            ("database", self._discover_database),
        ]
        
        for platform_name, discover_func in platforms:
            try:
                products = await discover_func()
                all_products.extend(products)
                platform_stats[platform_name] = len(products)
            except Exception as e:
                platform_stats[platform_name] = {"error": str(e)}
        
        # Store discovery results
        if self.db is not None:
            discovery_record = {
                "id": f"discovery-{uuid.uuid4().hex[:8]}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_products": len(all_products),
                "platform_stats": platform_stats,
                "products": all_products[:100]  # Store top 100
            }
            await self.db.product_discoveries.insert_one(discovery_record)
        
        return {
            "success": True,
            "total_products": len(all_products),
            "platform_stats": platform_stats,
            "products": all_products,
            "discovered_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _discover_gumroad(self) -> List[Dict]:
        """Discover products from Gumroad"""
        import requests
        import os
        
        access_token = os.environ.get("GUMROAD_ACCESS_TOKEN")
        if not access_token:
            return []
        
        try:
            response = requests.get(
                "https://api.gumroad.com/v2/products",
                params={"access_token": access_token}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = []
                    for p in data.get("products", []):
                        products.append({
                            "platform": "gumroad",
                            "id": p.get("id"),
                            "name": p.get("name"),
                            "price": p.get("price"),
                            "sales_count": p.get("sales_count", 0),
                            "revenue": p.get("sales_usd_cents", 0) / 100,
                            "url": p.get("short_url"),
                            "published": p.get("published", False)
                        })
                    return products
        except Exception as e:
            print(f"Gumroad discovery error: {e}")
        
        return []
    
    async def _discover_database(self) -> List[Dict]:
        """Discover products from local database"""
        if self.db is None:
            return []
        
        products = await self.db.products.find({}, {"_id": 0}).to_list(1000)
        return [{
            "platform": "ceo_system",
            "id": p.get("id"),
            "name": p.get("title"),
            "price": p.get("price", 0),
            "sales_count": p.get("conversions", 0),
            "revenue": p.get("revenue", 0),
            "status": p.get("status"),
            "type": p.get("product_type")
        } for p in products]
    
    async def get_product_summary(self) -> Dict[str, Any]:
        """Get summary of all products across platforms"""
        discovery = await self.discover_products()
        
        total_revenue = sum(p.get("revenue", 0) for p in discovery["products"])
        total_sales = sum(p.get("sales_count", 0) for p in discovery["products"])
        
        # Group by platform
        by_platform = {}
        for p in discovery["products"]:
            platform = p.get("platform", "unknown")
            if platform not in by_platform:
                by_platform[platform] = {"count": 0, "revenue": 0, "sales": 0}
            by_platform[platform]["count"] += 1
            by_platform[platform]["revenue"] += p.get("revenue", 0)
            by_platform[platform]["sales"] += p.get("sales_count", 0)
        
        return {
            "total_products": len(discovery["products"]),
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "by_platform": by_platform,
            "top_products": sorted(
                discovery["products"],
                key=lambda x: x.get("revenue", 0),
                reverse=True
            )[:10]
        }
