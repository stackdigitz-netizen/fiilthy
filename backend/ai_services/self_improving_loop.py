"""
Self-Improving AI Loop
Make the AI system learn and improve from each cycle
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pymongo import MongoClient
import os

MONGO_URL = (os.getenv("MONGO_URL") or "").strip() or None
DB_NAME = (os.getenv("DB_NAME") or "ai_ceo").strip() or "ai_ceo"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]


class SelfImprovingLoop:
    """AI that learns from each project and improves"""
    
    def __init__(self):
        self.projects_db = db.projects
        self.optimization_db = db.optimization_metrics
        self.learnings_db = db.learnings
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze what worked and what didn't"""
        
        # Get last 100 projects
        projects = list(self.projects_db.find().sort("created_at", -1).limit(100))
        
        if not projects:
            return {"status": "insufficient_data"}
        
        # Analyze metrics
        successful = [p for p in projects if p.get("status") == "completed"]
        success_rate = len(successful) / len(projects)
        
        # Analyze opportunities that converted best
        opportunities_performance = {}
        for project in projects:
            outputs = project.get("outputs", [])
            opportunity = next((o for o in outputs if o.get("type") == "opportunity"), None)
            
            if opportunity:
                niche = opportunity.get("data", {}).get("niche", "unknown")
                score = opportunity.get("data", {}).get("trend_score", 0)
                
                if niche not in opportunities_performance:
                    opportunities_performance[niche] = {"score": score, "count": 0}
                opportunities_performance[niche]["count"] += 1
        
        # Find best performing niches
        best_niches = sorted(
            opportunities_performance.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:5]
        
        return {
            "success_rate": f"{success_rate * 100:.1f}%",
            "total_projects": len(projects),
            "successful": len(successful),
            "best_performing_niches": [{"niche": n[0], "projects": n[1]["count"]} for n in best_niches],
            "analysis_samples": len(projects)
        }
    
    async def recommend_optimizations(self) -> List[Dict[str, Any]]:
        """Recommend improvements based on learnings"""
        
        performance = await self.analyze_performance()
        
        recommendations = []
        
        # Recommendation 1: Focus on top niches
        if "best_performing_niches" in performance:
            top_niches = performance["best_performing_niches"]
            if top_niches:
                recommendations.append({
                    "optimization": "focus_niches",
                    "description": f"Focus on top 5 performing niches: {', '.join([n['niche'] for n in top_niches])}",
                    "impact": "high",
                    "effort": "low"
                })
        
        # Recommendation 2: Increase scaling if success rate is high
        if performance.get("success_rate", "0%").endswith("%"):
            success_pct = float(performance["success_rate"].rstrip("%"))
            if success_pct > 80:
                recommendations.append({
                    "optimization": "increase_scaling",
                    "description": "Success rate > 80%. Increase projects_per_day to 10+",
                    "impact": "very_high",
                    "effort": "low"
                })
        
        # Recommendation 3: Optimize pricing
        recommendations.append({
            "optimization": "dynamic_pricing",
            "description": "Apply ML-based pricing optimization to each product",
            "impact": "medium",
            "effort": "medium"
        })
        
        # Recommendation 4: Improve marketing
        recommendations.append({
            "optimization": "marketing_expansion",
            "description": "Expand to TikTok/YouTube automation for better reach",
            "impact": "high",
            "effort": "medium"
        })
        
        return recommendations
    
    async def apply_learning(self, learning: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a specific optimization"""
        
        learning_record = {
            "learning_id": str(datetime.utcnow().timestamp()),
            "optimization": learning.get("optimization"),
            "applied_at": datetime.utcnow(),
            "status": "active"
        }
        
        self.learnings_db.insert_one(learning_record)
        
        return {
            "success": True,
            "learning_id": learning_record["learning_id"],
            "optimization": learning.get("optimization"),
            "applied_at": datetime.utcnow().isoformat()
        }
    
    async def get_improvement_metrics(self) -> Dict[str, Any]:
        """Track AI improvement over time"""
        
        # Get weekly performance
        weeks = 4
        weekly_performance = []
        
        for week in range(weeks):
            start_date = datetime.utcnow() - timedelta(weeks=week+1)
            end_date = datetime.utcnow() - timedelta(weeks=week)
            
            projects = self.projects_db.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            
            completed = len([p for p in projects if p.get("status") == "completed"])
            total = len(list(projects))
            
            weekly_performance.append({
                "week": week + 1,
                "success_rate": f"{(completed/total*100 if total > 0 else 0):.1f}%",
                "projects": total
            })
        
        return {
            "weekly_trends": weekly_performance,
            "latest_optimizations": list(self.learnings_db.find().sort("applied_at", -1).limit(5))
        }
