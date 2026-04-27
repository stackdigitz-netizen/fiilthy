"""
Micro-Team Taskforce
Orchestrates all AI teams and automates task assignment
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone
import random

from .opportunity_scout import OpportunityScout
from .book_writer import BookWriter
from .course_creator import CourseCreator
from .product_generator import ProductGenerator

class MicroTaskforce:
    def __init__(self, db):
        self.db = db
        self.opportunity_scout = OpportunityScout()
        self.book_writer = BookWriter()
        self.course_creator = CourseCreator()
        self.product_generator = ProductGenerator()
        
    async def run_autonomous_cycle(self) -> Dict[str, Any]:
        """
        Run a complete autonomous workflow:
        1. Scout opportunities
        2. Select top opportunities
        3. Generate products for each
        4. Update dashboard
        
        Returns:
            Summary of what was created
        """
        results = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "opportunities_found": 0,
            "products_created": 0,
            "tasks_completed": 0,
            "errors": []
        }
        
        try:
            # Step 1: Scout opportunities
            print("🔍 Scouting opportunities...")
            task_id = await self._create_task("scout_opportunities", "opportunity_scout", {})
            
            opportunities = await self.opportunity_scout.scout_opportunities()
            results["opportunities_found"] = len(opportunities)
            
            # Save opportunities to database
            for opp in opportunities:
                await self.db.opportunities.insert_one(opp)
            
            await self._complete_task(task_id, {"opportunities": len(opportunities)})
            results["tasks_completed"] += 1
            
            # Step 2: Select top 2 opportunities
            top_opportunities = sorted(opportunities, key=lambda x: x.get('trend_score', 0), reverse=True)[:2]
            
            # Step 3: Generate products for each opportunity
            for opp in top_opportunities:
                try:
                    # Randomly choose product type based on opportunity
                    product_types = ["ebook", "course", "template", "planner"]
                    weights = [0.35, 0.35, 0.15, 0.15]  # Favor books and courses
                    product_type = random.choices(product_types, weights=weights)[0]
                    
                    if product_type == "ebook":
                        print(f"📚 Generating eBook for: {opp['niche']}")
                        task_id = await self._create_task("generate_book", "book_writer", {"niche": opp['niche']})
                        product_data = await self.book_writer.generate_book(
                            niche=opp['niche'],
                            keywords=opp['keywords'],
                            book_length="medium"
                        )
                        await self._complete_task(task_id, {"product_id": product_data['id']})
                        
                    elif product_type == "course":
                        print(f"🎓 Generating Course for: {opp['niche']}")
                        task_id = await self._create_task("generate_course", "course_creator", {"topic": opp['niche']})
                        product_data = await self.course_creator.generate_course(
                            topic=opp['niche'],
                            target_audience="beginners",
                            duration_hours=3
                        )
                        await self._complete_task(task_id, {"product_id": product_data['id']})
                        
                    elif product_type in ["template", "planner"]:
                        print(f"📄 Generating {product_type} for: {opp['niche']}")
                        task_id = await self._create_task(f"generate_{product_type}", "product_creator", {"keywords": opp['keywords']})
                        product_data = await self.product_generator.generate_product(
                            product_type=product_type,
                            keywords=opp['keywords'],
                            style="professional"
                        )
                        await self._complete_task(task_id, {"product_id": product_data['id']})
                    
                    # Save product to database
                    # Add marketplace links
                    product_data['marketplace_links'] = [
                        {"platform": "Amazon KDP", "url": f"https://amazon.com/dp/{product_data['id'][:8]}", "status": "ready"},
                        {"platform": "Udemy", "url": f"https://udemy.com/course/{product_data['title'].lower().replace(' ', '-')}", "status": "ready"},
                        {"platform": "Shopify", "url": f"https://mystore.shopify.com/products/{product_data['id'][:8]}", "status": "ready"},
                    ]
                    
                    # Set pricing
                    price_ranges = {"ebook": (19.99, 49.99), "course": (39.99, 99.99), "template": (9.99, 29.99), "planner": (14.99, 34.99)}
                    min_price, max_price = price_ranges.get(product_type, (19.99, 49.99))
                    product_data['price'] = round(random.uniform(min_price, max_price), 2)
                    product_data['revenue'] = 0.0
                    product_data['clicks'] = 0
                    product_data['conversions'] = 0
                    
                    await self.db.products.insert_one(product_data)
                    results["products_created"] += 1
                    results["tasks_completed"] += 1
                    
                    print(f"✅ Created: {product_data['title']}")
                    
                except Exception as e:
                    error_msg = f"Error creating product for {opp['niche']}: {str(e)}"
                    print(f"❌ {error_msg}")
                    results["errors"].append(error_msg)
                    continue
            
            results["completed_at"] = datetime.now(timezone.utc).isoformat()
            results["success"] = True
            
        except Exception as e:
            results["errors"].append(str(e))
            results["success"] = False
            results["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        return results
    
    async def _create_task(self, task_type: str, ai_team: str, input_data: Dict) -> str:
        """Create and track an AI task"""
        task = {
            "id": f"task-{random.randint(1000, 9999)}",
            "task_type": task_type,
            "ai_team": ai_team,
            "status": "in_progress",
            "input_data": input_data,
            "output_data": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "error_message": None
        }
        await self.db.ai_tasks.insert_one(task)
        return task["id"]
    
    async def _complete_task(self, task_id: str, output_data: Dict):
        """Mark task as completed"""
        await self.db.ai_tasks.update_one(
            {"id": task_id},
            {
                "$set": {
                    "status": "completed",
                    "output_data": output_data,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
