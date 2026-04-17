"""
Multi-Project Scaling Engine
Run multiple autonomous cycles in parallel with smart scheduling
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid
from pymongo import MongoClient
import os

MONGO_URL = (os.getenv("MONGO_URL") or "").strip() or None
DB_NAME = (os.getenv("DB_NAME") or "ai_ceo").strip() or "ai_ceo"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]


class ScalingEngine:
    """Run multiple projects simultaneously with smart scheduling"""
    
    def __init__(self):
        self.projects_db = db.projects
        self.scaling_db = db.scaling_config
        self.max_concurrent = int(os.getenv("MAX_CONCURRENT_PROJECTS", "5"))
    
    async def scale_up(self, projects_per_day: int = 5) -> Dict[str, Any]:
        """Configure scaling to run N projects per day"""
        
        config = {
            "_id": "scaling_config",
            "projects_per_day": projects_per_day,
            "max_concurrent": self.max_concurrent,
            "start_time": "08:00",  # Start at 8 AM
            "interval_minutes": int(1440 / projects_per_day),  # Spread throughout day
            "active": True,
            "updated_at": datetime.utcnow()
        }
        
        self.scaling_db.update_one(
            {"_id": "scaling_config"},
            {"$set": config},
            upsert=True
        )
        
        return {
            "success": True,
            "projects_per_day": projects_per_day,
            "concurrent_limit": self.max_concurrent,
            "status": "scaling_activated"
        }
    
    async def schedule_projects(self, num_projects: int) -> List[Dict]:
        """Schedule projects across the day"""
        
        schedule = []
        config = self.scaling_db.find_one({"_id": "scaling_config"}) or {}
        
        interval = config.get("interval_minutes", 288)  # Default 5 projects/day
        start_hour = int(config.get("start_time", "08:00").split(":")[0])
        
        base_time = datetime.utcnow().replace(hour=start_hour, minute=0, second=0)
        
        for i in range(num_projects):
            scheduled_time = base_time + timedelta(minutes=i * interval)
            
            schedule.append({
                "project_num": i + 1,
                "scheduled_time": scheduled_time.isoformat(),
                "status": "queued",
                "priority": "normal"
            })
        
        return schedule
    
    async def run_parallel_projects(self, projects: List[Dict]) -> Dict[str, Any]:
        """Run multiple projects concurrently with limit"""
        
        from core.autonomous_engine import run_autonomous_cycle
        
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def run_with_limit(project_config):
            async with semaphore:
                try:
                    result = run_autonomous_cycle()
                    return {
                        "project_id": result.get("_id"),
                        "status": "completed",
                        "result": result
                    }
                except Exception as e:
                    return {
                        "status": "failed",
                        "error": str(e)
                    }
        
        tasks = [run_with_limit(p) for p in projects]
        results = await asyncio.gather(*tasks)
        
        return {
            "total_projects": len(projects),
            "completed": len([r for r in results if r.get("status") == "completed"]),
            "failed": len([r for r in results if r.get("status") == "failed"]),
            "results": results
        }
    
    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling configuration and status"""
        
        config = self.scaling_db.find_one({"_id": "scaling_config"}) or {}
        
        # Count active projects today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        active_today = self.projects_db.count_documents({
            "created_at": {"$gte": today}
        })
        
        return {
            "projects_per_day": config.get("projects_per_day", 1),
            "max_concurrent": config.get("max_concurrent", 5),
            "active": config.get("active", False),
            "projects_created_today": active_today,
            "next_run": self._calculate_next_run(config)
        }
    
    def _calculate_next_run(self, config: Dict) -> str:
        """Calculate when next project will run"""
        
        interval = config.get("interval_minutes", 288)
        return (datetime.utcnow() + timedelta(minutes=interval)).isoformat()
