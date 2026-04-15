"""
Product Ranking & Discovery Engine
Identifies top-performing products and recommends them for advertising
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class RankingMetric(Enum):
    """Metrics for ranking products"""
    REVENUE = "revenue"
    SALES_COUNT = "sales_count"
    CONVERSION_RATE = "conversion_rate"
    MARGIN = "margin"
    TRENDING = "trending"
    ENGAGEMENT = "engagement"
    REVIEWS = "reviews"
    VELOCITY = "velocity"  # How fast it's selling


class ProductRankingEngine:
    """Identify and rank products for advertising priority"""
    
    def __init__(self):
        self.db = None  # Will be injected by FastAPI dependency
        self.ranking_cache = {}
        self.update_interval = 3600  # 1 hour
    
    async def set_db(self, database):
        """Set database connection"""
        self.db = database
    
    async def get_top_products(self,
                               limit: int = 10,
                               metrics: Optional[List[str]] = None,
                               time_period: str = "30d",
                               min_sales: int = 0) -> List[Dict[str, Any]]:
        """
        Get top-performing products ranked by specified metrics
        
        Args:
            limit: Number of products to return
            metrics: Ranking metrics (revenue, sales_count, conversion_rate, margin, trending)
            time_period: "7d", "30d", "90d", "all"
            min_sales: Minimum sales threshold
            
        Returns:
            List of ranked products with scores
        """
        
        try:
            if self.db is None:
                logger.warning("Database not configured")
                return []
            
            if not metrics:
                metrics = [RankingMetric.REVENUE.value, RankingMetric.SALES_COUNT.value]
            
            # Get sales data
            end_date = datetime.now(timezone.utc)
            if time_period == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_period == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
            
            # Aggregate sales by product
            pipeline = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": start_date.isoformat(),
                            "$lte": end_date.isoformat()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$product_id",
                        "total_revenue": {"$sum": "$amount"},
                        "sales_count": {"$sum": 1},
                        "avg_rating": {"$avg": "$rating"},
                        "conversion_rate": {"$avg": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}
                    }
                },
                {"$sort": {"total_revenue": -1}},
                {"$limit": limit * 2}  # Get extra in case filtering removes some
            ]
            
            sales_data = await self.db.sales.aggregate(pipeline).to_list(None)
            
            # Enrich with product details
            products = []
            for sale in sales_data:
                product = await self.db.products.find_one(
                    {"id": sale["_id"]},
                    {"_id": 0}
                )
                
                if not product:
                    continue
                
                if sale["sales_count"] < min_sales:
                    continue
                
                # Calculate scores
                score = await self._calculate_ranking_score(
                    product=product,
                    sales_data=sale,
                    metrics=metrics,
                    time_period=time_period
                )
                
                products.append({
                    "product_id": product.get("id"),
                    "title": product.get("title"),
                    "category": product.get("category"),
                    "price": product.get("price"),
                    "description": product.get("description"),
                    "images": product.get("images", [])[:3],
                    "ranking_score": score,
                    "metrics": {
                        "total_revenue": sale.get("total_revenue", 0),
                        "sales_count": sale.get("sales_count", 0),
                        "avg_rating": sale.get("avg_rating", 0),
                        "conversion_rate": sale.get("conversion_rate", 0)
                    },
                    "advertising_ready": True,
                    "recommended_budget": self._recommend_budget(sale),
                    "estimated_roi": self._estimate_roi(product, sale)
                })
            
            # Sort by ranking score
            products.sort(key=lambda x: x["ranking_score"], reverse=True)
            return products[:limit]
        
        except Exception as e:
            logger.error(f"Failed to get top products: {str(e)}")
            return []
    
    async def get_trending_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get products with highest velocity (growing fastest)"""
        
        try:
            if self.db is None:
                return []
            
            # Compare sales velocity (7d vs previous 7d)
            now = datetime.now(timezone.utc)
            week_ago = now - timedelta(days=7)
            two_weeks_ago = now - timedelta(days=14)
            
            current_week = await self.db.sales.aggregate([
                {
                    "$match": {
                        "created_at": {
                            "$gte": week_ago.isoformat(),
                            "$lte": now.isoformat()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$product_id",
                        "count": {"$sum": 1},
                        "revenue": {"$sum": "$amount"}
                    }
                }
            ]).to_list(None)
            
            previous_week = await self.db.sales.aggregate([
                {
                    "$match": {
                        "created_at": {
                            "$gte": two_weeks_ago.isoformat(),
                            "$lte": week_ago.isoformat()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$product_id",
                        "count": {"$sum": 1},
                        "revenue": {"$sum": "$amount"}
                    }
                }
            ]).to_list(None)
            
            # Create maps
            current_map = {item["_id"]: item for item in current_week}
            previous_map = {item["_id"]: item for item in previous_week}
            
            # Calculate velocity
            trending = []
            for product_id, current_data in current_map.items():
                previous_data = previous_map.get(product_id, {"count": 0, "revenue": 0})
                
                velocity = (
                    (current_data["count"] - previous_data["count"]) / 
                    max(previous_data["count"], 1)
                )
                
                if velocity > 0.5:  # At least 50% growth
                    product = await self.db.products.find_one(
                        {"id": product_id},
                        {"_id": 0}
                    )
                    
                    if product:
                        trending.append({
                            "product_id": product_id,
                            "title": product.get("title"),
                            "velocity": velocity,
                            "current_sales": current_data["count"],
                            "previous_sales": previous_data["count"],
                            "growth_percent": velocity * 100
                        })
            
            trending.sort(key=lambda x: x["velocity"], reverse=True)
            return trending[:limit]
        
        except Exception as e:
            logger.error(f"Failed to get trending products: {str(e)}")
            return []
    
    async def get_high_margin_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get products with best profit margins"""
        
        try:
            if self.db is None:
                return []
            
            products = await self.db.products.find(
                {"margin": {"$exists": True}},
                {"_id": 0}
            ).sort("margin", -1).to_list(limit)
            
            # Add sales metrics
            enriched = []
            for product in products:
                sales_count = await self.db.sales.count_documents(
                    {"product_id": product.get("id")}
                )
                
                enriched.append({
                    "product_id": product.get("id"),
                    "title": product.get("title"),
                    "margin_percent": product.get("margin", 0),
                    "price": product.get("price"),
                    "cost": product.get("cost", 0),
                    "sales_count": sales_count,
                    "ideal_for_ads": sales_count > 5 or product.get("margin", 0) > 0.5
                })
            
            return enriched
        
        except Exception as e:
            logger.error(f"Failed to get high margin products: {str(e)}")
            return []
    
    async def _calculate_ranking_score(self,
                                       product: Dict[str, Any],
                                       sales_data: Dict[str, Any],
                                       metrics: List[str],
                                       time_period: str) -> float:
        """Calculate composite ranking score"""
        
        score = 0
        weights = {
            "revenue": 0.35,
            "sales_count": 0.25,
            "conversion_rate": 0.20,
            "margin": 0.15,
            "trending": 0.05
        }
        
        total_weight = 0
        
        for metric in metrics:
            if metric not in weights:
                continue
            
            if metric == "revenue":
                revenue = sales_data.get("total_revenue", 0)
                normalized = min(revenue / 10000, 1.0)  # Normalize to max $10k
                score += normalized * weights[metric]
            
            elif metric == "sales_count":
                count = sales_data.get("sales_count", 0)
                normalized = min(count / 100, 1.0)  # Normalize to max 100 sales
                score += normalized * weights[metric]
            
            elif metric == "conversion_rate":
                conv_rate = sales_data.get("conversion_rate", 0)
                score += conv_rate * weights[metric]
            
            elif metric == "margin":
                margin = product.get("margin", 0)
                score += min(margin, 1.0) * weights[metric]
            
            total_weight += weights[metric]
        
        # Normalize score to 0-100
        return min((score / total_weight) * 100 if total_weight > 0 else 0, 100)
    
    def _recommend_budget(self, sales_data: Dict[str, Any]) -> Dict[str, float]:
        """Recommend ad budget based on sales performance"""
        
        revenue = sales_data.get("total_revenue", 0)
        
        return {
            "recommended_daily": min(max(revenue / 30 * 0.1, 5), 100),  # 10% of daily avg, min $5, max $100
            "recommended_campaign": min(max(revenue * 0.15, 50), 2000),  # 15% of revenue, min $50, max $2k
            "daily_range": [5, min(revenue / 30 * 0.2, 200)],
            "currency": "USD"
        }
    
    def _estimate_roi(self, product: Dict[str, Any], sales_data: Dict[str, Any]) -> Dict[str, float]:
        """Estimate ROI for advertising this product"""
        
        price = product.get("price", 0)
        cost = product.get("cost", 0)
        profit_per_sale = price - cost
        conversion_rate = sales_data.get("conversion_rate", 0.02)
        
        # Assumes typical ad conversion rates
        estimated_cost_per_click = 0.50
        estimated_clicks_per_impression = 0.02
        estimated_conversions_per_click = conversion_rate
        
        cost_per_conversion = estimated_cost_per_click / max(estimated_conversions_per_click, 0.001)
        
        return {
            "estimated_cost_per_sale": cost_per_conversion,
            "profit_per_sale": profit_per_sale,
            "estimated_roi_percent": ((profit_per_sale - cost_per_conversion) / max(cost_per_conversion, 1)) * 100,
            "breakeven_conversion_rate": (estimated_cost_per_click / max(profit_per_sale, 1))
        }
    
    async def get_product_health(self, product_id: str) -> Dict[str, Any]:
        """Get comprehensive health metrics for a product"""
        
        try:
            if self.db is None:
                return {}
            
            product = await self.db.products.find_one(
                {"id": product_id},
                {"_id": 0}
            )
            
            if not product:
                return {"error": "Product not found"}
            
            # Get sales metrics
            sales = await self.db.sales.find(
                {"product_id": product_id}
            ).to_list(None)
            
            total_revenue = sum(s.get("amount", 0) for s in sales)
            avg_rating = (sum(s.get("rating", 0) for s in sales) / len(sales)) if sales else 0
            
            # Get recent trends
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_sales = len([s for s in sales if s.get("created_at", "") > week_ago.isoformat()])
            
            return {
                "product_id": product_id,
                "title": product.get("title"),
                "total_sales": len(sales),
                "total_revenue": total_revenue,
                "avg_rating": avg_rating,
                "recent_sales_7d": recent_sales,
                "price": product.get("price"),
                "margin": product.get("margin", 0),
                "is_trending": recent_sales > (len(sales) / 52) if sales else False,  # Growing vs annual avg
                "ad_readiness_score": self._calculate_ad_readiness(product, sales),
                "recommendation": self._get_recommendation(product, sales)
            }
        
        except Exception as e:
            logger.error(f"Failed to get product health: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_ad_readiness_score(self, product: Dict[str, Any], sales: List[Dict]) -> float:
        """Score 0-100 for how ready a product is for advertising"""
        
        score = 0
        
        # Has description (10 points)
        if product.get("description"):
            score += 10
        
        # Has images (15 points)
        if product.get("images"):
            score += 15
        
        # Has sales history (20 points)
        if len(sales) > 0:
            score += 20
        
        # Good rating (20 points)
        if sales:
            avg_rating = sum(s.get("rating", 0) for s in sales) / len(sales)
            if avg_rating >= 4.5:
                score += 20
            elif avg_rating >= 4.0:
                score += 15
        
        # Profitable margin (20 points)
        if product.get("margin", 0) > 0.3:
            score += 20
        
        # Recent sales momentum (15 points)
        if len(sales) > 10:
            recent_sales = len([s for s in sales if s.get("created_at", "") > (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()])
            if recent_sales > len(sales) / 52 * 2:
                score += 15
        
        return min(score, 100)
    
    def _get_recommendation(self, product: Dict[str, Any], sales: List[Dict]) -> str:
        """Get advertising recommendation for product"""
        
        score = self._calculate_ad_readiness_score(product, sales)
        
        if score >= 80:
            return "STRONGLY RECOMMENDED - High sales, good margin, lots of social proof"
        elif score >= 60:
            return "RECOMMENDED - Good product, ready for advertising investment"
        elif score >= 40:
            return "CONDITIONAL - Needs more reviews/sales history first"
        else:
            return "NOT RECOMMENDED - Build more social proof before advertising"


async def get_product_ranking_engine() -> ProductRankingEngine:
    """Get or create ranking engine"""
    return ProductRankingEngine()
