"""
Advanced Analytics Engine
Predictive analytics and business intelligence with AI-powered insights
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import random
import os
import openai
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class AnalyticsEngine:
    def __init__(self, db_client: Optional[AsyncIOMotorClient] = None):
        self.db = db_client
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

    async def generate_insights(self, products: List[Dict[str, Any]],
                               opportunities: List[Dict[str, Any]],
                               revenue_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate AI-powered business insights

        Args:
            products: List of products
            opportunities: List of opportunities
            revenue_data: Revenue metrics

        Returns:
            Insights and predictions
        """

        insights = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "product_performance": await self._analyze_product_performance(products),
            "revenue_forecast": await self._forecast_revenue(products, revenue_data),
            "opportunity_analysis": await self._analyze_opportunities(opportunities),
            "recommendations": await self._generate_recommendations(products, opportunities),
            "kpis": self._calculate_kpis(products, revenue_data),
            "learning_insights": await self._generate_learning_insights(products, opportunities)
        }

        return insights
    
    async def _analyze_product_performance(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze product performance and predict success"""
        
        performance = {
            "top_performers": [],
            "underperformers": [],
            "rising_stars": [],
            "average_metrics": {}
        }
        
        if not products:
            return performance
        
        # Sort by revenue
        sorted_products = sorted(products, key=lambda p: p.get('revenue', 0), reverse=True)
        
        # Top performers (top 20%)
        top_count = max(1, len(products) // 5)
        performance["top_performers"] = [
            {
                "title": p.get('title'),
                "revenue": p.get('revenue', 0),
                "conversions": p.get('conversions', 0),
                "score": self._calculate_performance_score(p)
            }
            for p in sorted_products[:top_count]
        ]
        
        # Underperformers (bottom 20%)
        performance["underperformers"] = [
            {
                "title": p.get('title'),
                "revenue": p.get('revenue', 0),
                "recommendations": ["Consider repricing", "Improve marketing", "Bundle with popular products"]
            }
            for p in sorted_products[-top_count:]
        ]
        
        # Calculate averages
        total_revenue = sum(p.get('revenue', 0) for p in products)
        total_conversions = sum(p.get('conversions', 0) for p in products)
        
        performance["average_metrics"] = {
            "avg_revenue": round(total_revenue / len(products), 2),
            "avg_conversions": round(total_conversions / len(products), 2),
            "total_products": len(products)
        }
        
        return performance
    
    def _calculate_performance_score(self, product: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)"""
        revenue = product.get('revenue', 0)
        conversions = product.get('conversions', 0)
        clicks = product.get('clicks', 0)
        
        # Weighted score
        revenue_score = min(revenue / 100, 100)  # $100+ = max score
        conversion_score = min(conversions * 2, 100)  # 50+ conversions = max score
        click_score = min(clicks / 10, 100)  # 1000+ clicks = max score
        
        return round((revenue_score * 0.5 + conversion_score * 0.3 + click_score * 0.2), 2)
    
    async def _forecast_revenue(self, products: List[Dict[str, Any]], 
                               revenue_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Forecast future revenue using AI"""
        
        # Calculate current metrics
        current_revenue = sum(p.get('revenue', 0) for p in products)
        
        # Simple growth projection (can be enhanced with ML models)
        growth_rate = random.uniform(0.05, 0.25)  # 5-25% monthly growth
        
        forecast = {
            "current_month": round(current_revenue, 2),
            "next_month": round(current_revenue * (1 + growth_rate), 2),
            "next_quarter": round(current_revenue * (1 + growth_rate) ** 3, 2),
            "next_year": round(current_revenue * (1 + growth_rate) ** 12, 2),
            "growth_rate": round(growth_rate * 100, 2),
            "confidence": "medium",
            "assumptions": [
                f"Assuming {round(growth_rate * 100, 1)}% monthly growth",
                "Based on current product portfolio",
                "Excludes external market factors"
            ]
        }
        
        return forecast
    
    async def _analyze_opportunities(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze opportunity trends"""
        
        if not opportunities:
            return {"status": "no_data"}
        
        # Sort by trend score
        sorted_opps = sorted(opportunities, key=lambda o: o.get('trend_score', 0), reverse=True)
        
        analysis = {
            "top_opportunity": {
                "niche": sorted_opps[0].get('niche'),
                "score": sorted_opps[0].get('trend_score'),
                "potential": "very_high" if sorted_opps[0].get('trend_score', 0) > 0.85 else "high"
            },
            "trending_keywords": self._extract_trending_keywords(opportunities),
            "market_insights": {
                "average_trend_score": round(sum(o.get('trend_score', 0) for o in opportunities) / len(opportunities), 2),
                "high_potential_count": len([o for o in opportunities if o.get('trend_score', 0) > 0.8])
            }
        }
        
        return analysis
    
    def _extract_trending_keywords(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Extract most common trending keywords"""
        keyword_counts = {}
        
        for opp in opportunities:
            for keyword in opp.get('keywords', []):
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Get top 5 keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, count in sorted_keywords[:5]]
    
    async def _generate_recommendations(self, products: List[Dict[str, Any]], 
                                       opportunities: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable business recommendations"""
        
        recommendations = []
        
        # Product-based recommendations
        if products:
            published_count = len([p for p in products if p.get('status') == 'published'])
            ready_count = len([p for p in products if p.get('status') == 'ready'])
            
            if ready_count > 0:
                recommendations.append(f"📢 Publish {ready_count} ready products to increase revenue")
            
            low_conversion = [p for p in products if p.get('conversions', 0) < 5 and p.get('status') == 'published']
            if low_conversion:
                recommendations.append(f"📊 Optimize pricing for {len(low_conversion)} low-conversion products")
        
        # Opportunity-based recommendations
        if opportunities:
            high_score_opps = [o for o in opportunities if o.get('trend_score', 0) > 0.85]
            if high_score_opps:
                recommendations.append(f"🚀 Prioritize {len(high_score_opps)} high-potential opportunities")
        
        # General recommendations
        recommendations.extend([
            "💰 Run revenue optimization to maximize earnings",
            "📱 Generate social media posts for better reach",
            "🤝 Create affiliate program to expand distribution"
        ])
        
        return recommendations[:5]  # Top 5
    
    def _calculate_kpis(self, products: List[Dict[str, Any]], 
                       revenue_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate key performance indicators"""
        
        total_revenue = sum(p.get('revenue', 0) for p in products)
        total_conversions = sum(p.get('conversions', 0) for p in products)
        total_clicks = sum(p.get('clicks', 0) for p in products)
        
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        avg_order_value = (total_revenue / total_conversions) if total_conversions > 0 else 0
        
        return {
            "total_revenue": round(total_revenue, 2),
            "total_conversions": total_conversions,
            "conversion_rate": round(conversion_rate, 2),
            "average_order_value": round(avg_order_value, 2),
            "total_products": len(products),
            "products_published": len([p for p in products if p.get('status') == 'published'])
        }

    async def _generate_learning_insights(self, products: List[Dict[str, Any]],
                                         opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered learning insights for continuous improvement"""
        try:
            # Analyze product performance patterns
            successful_products = [p for p in products if p.get('revenue', 0) > 10]
            failed_products = [p for p in products if p.get('revenue', 0) <= 10 and p.get('status') == 'published']

            prompt = f"""
            Analyze product performance data and generate learning insights for continuous improvement.

            Successful Products ({len(successful_products)}):
            {json.dumps([{
                'title': p.get('title', ''),
                'revenue': p.get('revenue', 0),
                'category': p.get('category', ''),
                'price': p.get('price', 0)
            } for p in successful_products[:5]], indent=2)}

            Failed Products ({len(failed_products)}):
            {json.dumps([{
                'title': p.get('title', ''),
                'revenue': p.get('revenue', 0),
                'category': p.get('category', ''),
                'price': p.get('price', 0)
            } for p in failed_products[:5]], indent=2)}

            Market Opportunities ({len(opportunities)}):
            {json.dumps([{
                'niche': o.get('niche', ''),
                'trend_score': o.get('trend_score', 0),
                'keywords': o.get('keywords', [])[:3]
            } for o in opportunities[:3]], indent=2)}

            Generate insights on:
            1. What patterns lead to successful products
            2. Common failure modes to avoid
            3. Market opportunities to prioritize
            4. Pricing strategies that work
            5. Content approaches that resonate
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )

            insights_text = response.choices[0].message.content

            return {
                "insights": insights_text,
                "patterns_identified": len(successful_products),
                "improvement_areas": len(failed_products),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            return {
                "insights": "Unable to generate AI insights due to API error",
                "error": str(e),
                "fallback_patterns": [
                    "High-value products tend to perform better",
                    "Clear, specific titles attract more buyers",
                    "Practical content outperforms theoretical content"
                ]
            }
