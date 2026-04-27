"""
Product Team Manager
Automatically creates and manages dedicated AI teams for each product
Each product gets its own team to handle marketing, sales, and optimization
"""
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class ProductTeamManager:
    """Manages AI teams dedicated to each product"""
    
    def __init__(self, db=None):
        self.db = db
    
    async def create_team_for_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Create a specialized AI team for a product"""
        
        team_id = f"team-{uuid.uuid4().hex[:8]}"
        
        # Determine team composition based on product type
        team_composition = self._get_team_composition(product)
        
        team = {
            "id": team_id,
            "product_id": product.get("id"),
            "product_title": product.get("title"),
            "product_type": product.get("product_type"),
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "team_composition": team_composition,
            "assigned_roles": {
                "marketing_lead": f"Agent-Marketing-{team_id[:8]}",
                "sales_specialist": f"Agent-Sales-{team_id[:8]}",
                "content_creator": f"Agent-Content-{team_id[:8]}",
                "analytics_expert": f"Agent-Analytics-{team_id[:8]}",
                "ads_manager": f"Agent-Ads-{team_id[:8]}",
                "partnership_manager": f"Agent-Partners-{team_id[:8]}"
            },
            "current_phase": "launch_preparation",
            "tasks": {
                "immediate": [
                    {"task": "Finalize product listing", "status": "pending", "priority": "high"},
                    {"task": "Create marketing assets", "status": "pending", "priority": "high"},
                    {"task": "Set up analytics tracking", "status": "pending", "priority": "high"},
                    {"task": "Plan advertising strategy", "status": "pending", "priority": "high"}
                ],
                "week_1": [
                    {"task": "Launch on all platforms", "status": "pending", "priority": "high"},
                    {"task": "Create social posts (50+ posts)", "status": "pending", "priority": "high"},
                    {"task": "Set up email sequences", "status": "pending", "priority": "medium"},
                    {"task": "Launch initial ads", "status": "pending", "priority": "high"}
                ],
                "ongoing": [
                    {"task": "Daily social media engagement", "status": "active", "priority": "medium"},
                    {"task": "Monitor and optimize ads", "status": "active", "priority": "high"},
                    {"task": "Respond to customer inquiries", "status": "active", "priority": "high"},
                    {"task": "A/B test landing pages", "status": "active", "priority": "medium"},
                    {"task": "Weekly performance analysis", "status": "active", "priority": "medium"}
                ]
            },
            "marketing_strategy": {
                "channels": ["social_media", "email", "paid_ads", "organic_seo", "partnerships", "affiliates"],
                "platforms": self._get_platform_strategy(product),
                "budget_allocation": {
                    "social_media": "30%",
                    "paid_ads": "40%",
                    "email": "10%",
                    "influencers": "15%",
                    "partnerships": "5%"
                },
                "daily_budget": "$50-100"  # Automated budget from revenue
            },
            "kpis": {
                "daily_visitors_target": 100,
                "conversion_rate_target": "3-5%",
                "daily_revenue_target": "$50+",
                "customer_acquisition_cost": "< 20% of price",
                "monthly_revenue_target": "$1000+"
            },
            "revenue_tracking": {
                "total_sales": 0,
                "total_revenue": 0,
                "daily_revenue": 0,
                "conversion_funnel": {
                    "visitors": 0,
                    "clicks": 0,
                    "sign_ups": 0,
                    "purchases": 0
                },
                "refund_rate": 0,
                "customer_satisfaction": 0
            },
            "content_calendars": self._create_content_calendars(product),
            "ai_tasks": [],
            "last_activity": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to database
        if self.db:
            await self.db.product_teams.insert_one(team)
        
        return team
    
    def _get_team_composition(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Get team composition based on product type"""
        base_team = {
            "team_size": 6,
            "roles": [
                {
                    "role": "Marketing Lead",
                    "responsibilities": [
                        "Overall strategy", "Campaign planning", "Channel optimization",
                        "Budget allocation", "KPI tracking", "A/B testing"
                    ]
                },
                {
                    "role": "Sales Specialist",
                    "responsibilities": [
                        "Sales funnel optimization", "Conversion rate optimization",
                        "Customer objection handling", "Price optimization", "Upsell/cross-sell"
                    ]
                },
                {
                    "role": "Content Creator",
                    "responsibilities": [
                        "Social media content (50+ posts/week)", "Email sequences",
                        "Landing page copy", "Product description", "Video scripts"
                    ]
                },
                {
                    "role": "Analytics Expert",
                    "responsibilities": [
                        "Traffic analysis", "Conversion tracking", "Revenue reporting",
                        "Customer behavior analysis", "Insights generation"
                    ]
                },
                {
                    "role": "Ads Manager",
                    "responsibilities": [
                        "Facebook/Instagram ads", "Google Ads", "TikTok ads",
                        "Budget optimization", "Audience targeting", "Ad creative testing"
                    ]
                },
                {
                    "role": "Partnership Manager",
                    "responsibilities": [
                        "Affiliate recruitment", "Influencer outreach",
                        "Joint ventures", "Cross-promotions", "Strategic partnerships"
                    ]
                }
            ]
        }
        
        # Add product-specific roles
        if product.get("product_type") == "course":
            base_team["roles"].append({
                "role": "Student Success Specialist",
                "responsibilities": [
                    "Student support", "Course feedback", "Curriculum updates",
                    "Success tracking", "Certification management"
                ]
            })
        
        return base_team
    
    def _get_platform_strategy(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Get platform-specific marketing strategy"""
        return {
            "social_media": {
                "twitter": {"posts_per_day": 3, "content_types": ["tips", "testimonials", "case_studies"]},
                "instagram": {"posts_per_day": 2, "content_types": ["carousels", "stories", "reels"]},
                "tiktok": {"posts_per_day": 2, "content_types": ["tutorials", "trends", "behind_the_scenes"]},
                "linkedin": {"posts_per_week": 3, "content_types": ["industry_insights", "success_stories"]},
                "youtube": {"videos_per_week": 1, "content_types": ["tutorials", "reviews", "testimonials"]}
            },
            "paid_ads": {
                "facebook": {"daily_budget": "$20-30", "audience": "broad"},
                "google": {"daily_budget": "$15-20", "audience": "search_intent"},
                "tiktok": {"daily_budget": "$10-15", "audience": "viral_potential"},
                "instagram": {"daily_budget": "$15-20", "audience": "visual"}
            },
            "email": {
                "frequency": "3x per week",
                "segmentation": ["cold", "warm", "customers"],
                "types": ["value", "promotional", "testimonial"]
            }
        }
    
    def _create_content_calendars(self, product: Dict[str, Any]) -> Dict[str, List]:
        """Create content calendars for the team"""
        product_title = product.get("title", "Product")
        return {
            "week_1_launch": [
                f"Launch day announcement - {product_title}",
                "Product overview and features",
                "Customer testimonials (use generated ones initially)",
                "How-to guide",
                "Success stories",
                "Limited time offer promotion",
                "FAQ video",
                "Behind-the-scenes content",
                "Partner/influencer promotion"
            ],
            "month_1_growth": [
                "Weekly product tips",
                "Customer case studies",
                "Email sequence (7-email series)",
                "Social proof/reviews",
                "Comparison content (vs competitors)",
                "Webinar or live Q&A",
                "Special promotions",
                "Affiliate recruitment posts"
            ],
            "ongoing": [
                "Weekly value content",
                "Monthly revenue reports",
                "Seasonal promotions",
                "Product updates/improvements",
                "User-generated content",
                "Community engagement posts",
                "Trending topic tie-ins"
            ]
        }
    
    async def activate_product_team(self, team_id: str) -> Dict[str, Any]:
        """Activate a team to start working on the product"""
        if not self.db:
            return {"success": False, "error": "Database not available"}
        
        # Get team
        team = await self.db.product_teams.find_one({"id": team_id}, {"_id": 0})
        if not team:
            return {"success": False, "error": "Team not found"}
        
        # Update team status
        await self.db.product_teams.update_one(
            {"id": team_id},
            {"$set": {
                "status": "active",
                "activated_at": datetime.now(timezone.utc).isoformat(),
                "current_phase": "launch"
            }}
        )
        
        # Create immediate tasks
        immediate_tasks = [
            {
                "id": f"task-{uuid.uuid4().hex[:8]}",
                "team_id": team_id,
                "task": "Create 50+ social media posts",
                "description": "Generate social posts for all platforms (Twitter, Instagram, TikTok, LinkedIn)",
                "assigned_to": team["assigned_roles"]["content_creator"],
                "status": "in_progress",
                "due_date": datetime.now(timezone.utc).isoformat(),
                "priority": "high"
            },
            {
                "id": f"task-{uuid.uuid4().hex[:8]}",
                "team_id": team_id,
                "task": "Set up advertising campaigns",
                "description": "Create ad campaigns on Facebook, Instagram, Google, TikTok",
                "assigned_to": team["assigned_roles"]["ads_manager"],
                "status": "in_progress",
                "due_date": datetime.now(timezone.utc).isoformat(),
                "priority": "high"
            },
            {
                "id": f"task-{uuid.uuid4().hex[:8]}",
                "team_id": team_id,
                "task": "Optimize landing page",
                "description": "A/B test headlines, CTAs, and page layout",
                "assigned_to": team["assigned_roles"]["sales_specialist"],
                "status": "in_progress",
                "due_date": datetime.now(timezone.utc).isoformat(),
                "priority": "high"
            }
        ]
        
        if self.db:
            await self.db.team_tasks.insert_many(immediate_tasks)
        
        return {
            "success": True,
            "team_id": team_id,
            "status": "active",
            "immediate_tasks": immediate_tasks,
            "message": f"Team activated for {team.get('product_title')}, tasks assigned"
        }
    
    async def get_team_dashboard(self, team_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard for a product team"""
        if not self.db:
            return {"success": False, "error": "Database not available"}
        
        team = await self.db.product_teams.find_one({"id": team_id}, {"_id": 0})
        if not team:
            return {"success": False, "error": "Team not found"}
        
        # Get tasks
        tasks = await self.db.team_tasks.find({"team_id": team_id}, {"_id": 0}).to_list(50)
        
        # Get recent analytics
        analytics = await self.db.team_analytics.find_one(
            {"team_id": team_id}, {"_id": 0},
            sort=[("timestamp", -1)]
        )
        
        return {
            "success": True,
            "team": team,
            "tasks": tasks,
            "analytics": analytics or {},
            "summary": {
                "total_tasks": len(tasks),
                "completed_tasks": len([t for t in tasks if t.get("status") == "completed"]),
                "in_progress_tasks": len([t for t in tasks if t.get("status") == "in_progress"]),
                "pending_tasks": len([t for t in tasks if t.get("status") == "pending"])
            }
        }
    
    async def get_all_product_teams(self, filter_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all product teams"""
        if not self.db:
            return []
        
        query = {}
        if filter_status:
            query["status"] = filter_status
        
        teams = await self.db.product_teams.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
        return teams
    
    async def update_team_revenue(self, team_id: str, daily_revenue: float) -> Dict[str, Any]:
        """Update team revenue tracking"""
        if not self.db:
            return {"success": False}
        
        # Update revenue
        result = await self.db.product_teams.update_one(
            {"id": team_id},
            {"$inc": {
                "revenue_tracking.total_revenue": daily_revenue,
                "revenue_tracking.daily_revenue": daily_revenue,
                "revenue_tracking.purchases": 1
            }}
        )
        
        return {"success": result.modified_count > 0}
