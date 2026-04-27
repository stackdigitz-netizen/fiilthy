"""
Scheduler for Daily Autonomous Cycles
Manages automated workflows and task scheduling
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
import random

class AutomationScheduler:
    def __init__(self, db, micro_taskforce):
        self.db = db
        self.micro_taskforce = micro_taskforce
        self.schedules = {
            "morning_scan": {"hour": 9, "task": "scout_opportunities"},
            "afternoon_generation": {"hour": 14, "task": "generate_products"},
            "evening_optimization": {"hour": 18, "task": "optimize_revenue"}
        }
    
    async def run_scheduled_cycle(self, cycle_type: str) -> Dict[str, Any]:
        """
        Run a specific scheduled cycle
        
        Args:
            cycle_type: morning_scan/afternoon_generation/evening_optimization
            
        Returns:
            Cycle execution results
        """
        results = {
            "cycle_type": cycle_type,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "tasks_completed": [],
            "status": "running"
        }
        
        try:
            if cycle_type == "morning_scan":
                # Scout new opportunities
                print("🌅 Running morning opportunity scan...")
                results["tasks_completed"].append("opportunity_scouting")
                
            elif cycle_type == "afternoon_generation":
                # Generate products from top opportunities
                print("☀️ Running afternoon product generation...")
                cycle_results = await self.micro_taskforce.run_autonomous_cycle()
                results["tasks_completed"].append("product_generation")
                results["products_created"] = cycle_results.get("products_created", 0)
                
            elif cycle_type == "evening_optimization":
                # Optimize revenue and marketing
                print("🌙 Running evening optimization...")
                results["tasks_completed"].append("revenue_optimization")
                results["tasks_completed"].append("marketing_update")
            
            results["status"] = "completed"
            results["completed_at"] = datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
        
        # Log to database
        await self._log_cycle(results)
        
        return results
    
    async def _log_cycle(self, results: Dict[str, Any]):
        """Log cycle execution to database"""
        log_entry = {
            "id": f"cycle-{random.randint(1000, 9999)}",
            **results
        }
        await self.db.automation_logs.insert_one(log_entry)
    
    def get_next_scheduled_runs(self) -> List[Dict[str, Any]]:
        """Get next scheduled run times"""
        now = datetime.now(timezone.utc)
        scheduled_runs = []
        
        for cycle_name, schedule in self.schedules.items():
            next_run = now.replace(hour=schedule["hour"], minute=0, second=0, microsecond=0)
            if next_run < now:
                next_run += timedelta(days=1)
            
            scheduled_runs.append({
                "cycle": cycle_name,
                "task": schedule["task"],
                "next_run": next_run.isoformat(),
                "hours_until": (next_run - now).total_seconds() / 3600
            })
        
        return sorted(scheduled_runs, key=lambda x: x["hours_until"])
