"""
Demo Data Generators
Generate realistic simulated data for all AI services in demo mode
"""

import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid


class DemoData:
    """Generate realistic demo/test data"""
    
    PRODUCT_TITLES = [
        "Ultimate AI Productivity Bundle",
        "10x Your Income with Affiliate Marketing",
        "The Complete Video Marketing Playbook",
        "Launching Your SaaS in 30 Days",
        "Content Calendar for Social Media Success",
        "Email Funnel Templates That Convert",
        "Personal Brand Mastery Blueprint",
        "Automation Stack for Solopreneurs",
    ]
    
    NICHES = [
        "AI & Automation",
        "Digital Marketing",
        "E-commerce",
        "SaaS",
        "Personal Development",
        "Fitness",
        "Design",
        "Writing",
    ]
    
    PLATFORMS = ["Gumroad", "PayPal", "Stripe", "SendOwl", "Appsumo"]
    
    SOCIAL_CAPTIONS = [
        "Just discovered this game-changing strategy... 🔥",
        "They don't want you to know about this",
        "This saved my business $10k/month",
        "If you're not doing this, you're leaving money on the table",
        "The #1 mistake 99% of people make",
        "Here's exactly how we did it",
        "Watch this till the end...",
    ]
    
    @staticmethod
    def generate_product_id() -> str:
        """Generate a product ID"""
        return f"prod_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_product(product_type: str = "ebook") -> Dict[str, Any]:
        """Generate a realistic product"""
        title = random.choice(DemoData.PRODUCT_TITLES)
        niche = random.choice(DemoData.NICHES)
        price = random.choice([17, 27, 47, 67, 97, 147, 197, 297])
        
        return {
            "id": DemoData.generate_product_id(),
            "title": f"{title} - {niche}",
            "description": f"A comprehensive guide to {niche.lower()}. "
                          f"Includes step-by-step instructions, templates, and resources.",
            "niche": niche,
            "type": product_type,
            "price": price,
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "status": random.choice(["draft", "ready", "published"]),
            "sales": random.randint(0, 150),
            "revenue": random.randint(0, 5000),
        }
    
    @staticmethod
    def generate_opportunity() -> Dict[str, Any]:
        """Generate a market opportunity"""
        niche = random.choice(DemoData.NICHES)
        demand = random.randint(60, 98)
        competition = random.randint(20, 80)
        profitability = random.randint(50, 95)
        
        return {
            "id": f"opp_{uuid.uuid4().hex[:12]}",
            "title": f"{niche} x Automation Opportunity",
            "description": f"High-demand {niche.lower()} market with proven buyer intent",
            "niche": niche,
            "demand_score": demand,
            "competition_score": competition,
            "profitability_score": profitability,
            "estimated_monthly_revenue": max(0, (demand - competition) * profitability * 5),
            "discovered_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
            "status": random.choice(["identified", "in_progress"]),
        }
    
    @staticmethod
    def generate_revenue_data(days: int = 30) -> Dict[str, Any]:
        """Generate revenue metrics"""
        events = []
        total_revenue = 0
        total_sales = 0
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i - 1)).date()
            daily_sales = random.randint(5, 40)
            daily_revenue = daily_sales * random.choice([17, 27, 47, 67, 97])
            
            events.append({
                "date": date.isoformat(),
                "sales": daily_sales,
                "revenue": daily_revenue,
                "conversions": random.randint(1, 10),
            })
            
            total_revenue += daily_revenue
            total_sales += daily_sales
        
        return {
            "period": f"Last {days} days",
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "average_daily_revenue": total_revenue // days,
            "average_order_value": total_revenue // total_sales if total_sales > 0 else 0,
            "events": events,
            "top_product": DemoData.generate_product(),
            "growth_rate": f"+{random.randint(15, 120)}%",
        }
    
    @staticmethod
    def generate_social_posts(count: int = 10) -> List[Dict[str, Any]]:
        """Generate social media posts"""
        posts = []
        platforms = ["Twitter", "LinkedIn", "TikTok", "Instagram"]
        
        for i in range(count):
            posts.append({
                "id": f"post_{uuid.uuid4().hex[:12]}",
                "platform": random.choice(platforms),
                "content": random.choice(DemoData.SOCIAL_CAPTIONS),
                "scheduled_for": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
                "status": "scheduled",
                "expected_reach": random.randint(500, 50000),
                "cta": "Learn more",
            })
        
        return posts
    
    @staticmethod
    def generate_email_sequence() -> List[Dict[str, Any]]:
        """Generate email marketing sequence"""
        subjects = [
            "This Changed Everything for Me",
            "You're Missing Out on $$$",
            "Last Chance: Limited Time",
            "Here's What Most People Don't Know",
            "Your Free Access Expires Soon",
        ]
        
        sequence = []
        for i in range(5):
            sequence.append({
                "id": f"email_{uuid.uuid4().hex[:12]}",
                "sequence_position": i + 1,
                "subject": subjects[i] if i < len(subjects) else f"Email #{i+1}",
                "preview": "This is a preview of the email content...",
                "status": "ready",
                "scheduled_for": (datetime.now() + timedelta(days=i+1)).isoformat(),
            })
        
        return sequence
    
    @staticmethod
    def generate_analytics() -> Dict[str, Any]:
        """Generate analytics data"""
        return {
            "id": f"analytics_{uuid.uuid4().hex[:12]}",
            "period": "30 days",
            "total_visitors": random.randint(1000, 50000),
            "total_conversions": random.randint(50, 500),
            "conversion_rate": f"{random.randint(1, 10)}%",
            "average_session_duration": f"{random.randint(30, 300)}s",
            "bounce_rate": f"{random.randint(20, 80)}%",
            "top_traffic_sources": [
                {"source": "Organic Search", "visits": random.randint(500, 5000)},
                {"source": "Social Media", "visits": random.randint(200, 2000)},
                {"source": "Direct", "visits": random.randint(100, 1000)},
            ],
            "generated_at": datetime.now().isoformat(),
        }
    
    @staticmethod
    def simulate_processing_delay(min_seconds: float = 0.5, max_seconds: float = 3.0):
        """Simulate API processing delay"""
        return random.uniform(min_seconds, max_seconds)


class DemoDataGenerator:
    """Generate demo data sets"""
    
    @staticmethod
    async def generate_dashboard_snapshot() -> Dict[str, Any]:
        """Generate complete dashboard data for demo"""
        return {
            "stats": {
                "total_products": random.randint(10, 100),
                "total_revenue": random.randint(5000, 100000),
                "total_sales": random.randint(20, 500),
                "opportunities_found": random.randint(5, 50),
                "active_campaigns": random.randint(3, 20),
            },
            "products": [DemoData.generate_product() for _ in range(8)],
            "opportunities": [DemoData.generate_opportunity() for _ in range(5)],
            "revenue_metrics": DemoData.generate_revenue_data(30),
            "social_posts": DemoData.generate_social_posts(15),
            "email_sequences": DemoData.generate_email_sequence(),
            "analytics": DemoData.generate_analytics(),
            "last_updated": datetime.now().isoformat(),
        }
