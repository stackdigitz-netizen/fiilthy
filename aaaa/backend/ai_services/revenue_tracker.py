"""
Advanced Revenue Tracking & Optimization
Track real revenue, optimize pricing, manage affiliates
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pymongo import MongoClient
import os
import json

MONGO_URL = (os.getenv("MONGO_URL") or "").strip() or None
DB_NAME = (os.getenv("DB_NAME") or "ai_ceo").strip() or "ai_ceo"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]


class RevenueTracker:
    """Track all revenue streams and optimize"""
    
    def __init__(self):
        self.revenue_db = db.revenue
        self.sales_db = db.sales
        self.affiliates_db = db.affiliates
    
    async def record_sale(self, product_id: str, amount: float, source: str, customer_id: str = None) -> Dict:
        """Record a sale"""
        
        sale = {
            "product_id": product_id,
            "amount": amount,
            "source": source,  # gumroad, stripe, affiliate, etc
            "customer_id": customer_id,
            "timestamp": datetime.utcnow(),
            "status": "completed"
        }
        
        result = self.sales_db.insert_one(sale)
        
        # Update revenue summary
        self._update_revenue_summary(product_id, amount)
        
        return {
            "success": True,
            "sale_id": str(result.inserted_id),
            "amount": amount
        }
    
    def _update_revenue_summary(self, product_id: str, amount: float):
        """Update daily/monthly revenue summary"""
        
        today = datetime.utcnow().date()
        
        self.revenue_db.update_one(
            {
                "product_id": product_id,
                "date": today
            },
            {
                "$inc": {"total": amount, "sales_count": 1},
                "$set": {"last_updated": datetime.utcnow()}
            },
            upsert=True
        )
    
    async def get_revenue_metrics(self, product_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive revenue metrics"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = {"timestamp": {"$gte": cutoff_date}}
        if product_id:
            query["product_id"] = product_id
        
        sales = list(self.sales_db.find(query))
        
        total_revenue = sum(s.get("amount", 0) for s in sales)
        avg_sale = total_revenue / len(sales) if sales else 0
        
        # Group by source
        revenue_by_source = {}
        for sale in sales:
            source = sale.get("source", "unknown")
            revenue_by_source[source] = revenue_by_source.get(source, 0) + sale.get("amount", 0)
        
        return {
            "period_days": days,
            "total_revenue": round(total_revenue, 2),
            "total_sales": len(sales),
            "average_sale_value": round(avg_sale, 2),
            "revenue_by_source": revenue_by_source,
            "daily_average": round(total_revenue / days, 2) if days > 0 else 0
        }
    
    async def optimize_pricing(self, product_id: str) -> Dict[str, Any]:
        """Analyze sales and recommend price adjustment"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        sales = list(self.sales_db.find({
            "product_id": product_id,
            "timestamp": {"$gte": cutoff_date}
        }))
        
        if not sales:
            return {"recommendation": "No data", "current_price": 29.99}
        
        total_revenue = sum(s.get("amount", 0) for s in sales)
        avg_price = total_revenue / len(sales)
        
        # Simple optimization logic
        if len(sales) > 20:  # High volume - increase price
            recommended_price = avg_price * 1.15  # 15% increase
            reason = "High sales volume detected - increase price for better margin"
        elif len(sales) < 5:  # Low volume - decrease price
            recommended_price = avg_price * 0.85  # 15% decrease
            reason = "Low sales volume - reduce price to increase conversions"
        else:
            recommended_price = avg_price
            reason = "Sales volume optimal - maintain current pricing"
        
        return {
            "current_average": round(avg_price, 2),
            "recommended_price": round(recommended_price, 2),
            "confidence": "high" if len(sales) > 10 else "medium",
            "reason": reason,
            "sales_last_30_days": len(sales)
        }
    
    async def setup_affiliate(self, product_id: str, commission_rate: float = 0.2) -> Dict[str, Any]:
        """Setup affiliate program for product"""
        
        affiliate = {
            "product_id": product_id,
            "commission_rate": commission_rate,
            "status": "active",
            "created_at": datetime.utcnow(),
            "affiliates": [],
            "total_affiliate_revenue": 0
        }
        
        result = self.affiliates_db.insert_one(affiliate)
        
        # Generate affiliate link (simplified)
        affiliate_code = f"AFFIL_{product_id}_{int(datetime.utcnow().timestamp())}"
        
        return {
            "success": True,
            "affiliate_id": str(result.inserted_id),
            "affiliate_code": affiliate_code,
            "commission_rate": f"{commission_rate * 100}%",
            "tracking_url": f"https://yoursite.com/?aff={affiliate_code}"
        }
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top performing products by revenue"""
        
        pipeline = [
            {
                "$group": {
                    "_id": "$product_id",
                    "total_revenue": {"$sum": "$amount"},
                    "sales_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"total_revenue": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        results = list(self.sales_db.aggregate(pipeline))
        
        return [
            {
                "rank": i + 1,
                "product_id": r.get("_id"),
                "revenue": round(r.get("total_revenue", 0), 2),
                "sales": r.get("sales_count", 0)
            }
            for i, r in enumerate(results)
        ]
