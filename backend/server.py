from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
import random
from datetime import datetime, timezone
from enum import Enum

# Import AI services
from ai_services.opportunity_scout import OpportunityScout
from ai_services.book_writer import BookWriter
from ai_services.course_creator import CourseCreator
from ai_services.product_generator import ProductGenerator
from ai_services.micro_taskforce import MicroTaskforce
from ai_services.revenue_maximizer import RevenueMaximizer
from ai_services.social_media_ai import SocialMediaAI
from ai_services.sales_launch_ai import SalesLaunchAI
from ai_services.affiliate_manager import AffiliateManager


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize AI services
opportunity_scout = OpportunityScout()
book_writer = BookWriter()
course_creator = CourseCreator()
product_generator = ProductGenerator()
micro_taskforce = MicroTaskforce(db)
revenue_maximizer = RevenueMaximizer()
social_media_ai = SocialMediaAI()
sales_launch_ai = SalesLaunchAI()
affiliate_manager = AffiliateManager()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Enums
class ProductType(str, Enum):
    EBOOK = "ebook"
    COURSE = "course"
    TEMPLATE = "template"
    PLANNER = "planner"
    MINI_APP = "mini_app"

class ProductStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    PUBLISHED = "published"
    RETIRED = "retired"

class OpportunityStatus(str, Enum):
    IDENTIFIED = "identified"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class AITaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AITeam(str, Enum):
    OPPORTUNITY_SCOUT = "opportunity_scout"
    BOOK_WRITER = "book_writer"
    COURSE_CREATOR = "course_creator"
    PRODUCT_CREATOR = "product_creator"
    REVENUE_OPTIMIZER = "revenue_optimizer"
    SOCIAL_MEDIA = "social_media"
    SALES_LAUNCH = "sales_launch"
    AFFILIATE_MANAGER = "affiliate_manager"
    MICRO_TASKFORCE = "micro_taskforce"


# Define Models
class MarketplaceLink(BaseModel):
    platform: str
    url: str
    status: str = "ready"

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    product_type: ProductType
    content: Optional[str] = None
    cover_image: Optional[str] = None
    status: ProductStatus = ProductStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revenue: float = 0.0
    clicks: int = 0
    conversions: int = 0
    marketplace_links: List[MarketplaceLink] = []
    tags: List[str] = []
    price: float = 0.0

class ProductCreate(BaseModel):
    title: str
    description: str
    product_type: ProductType
    content: Optional[str] = None
    cover_image: Optional[str] = None
    price: float = 9.99
    tags: List[str] = []

class Opportunity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    niche: str
    trend_score: float
    keywords: List[str]
    status: OpportunityStatus = OpportunityStatus.IDENTIFIED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    suggested_products: List[str] = []
    market_size: Optional[str] = None
    competition_level: Optional[str] = None

class OpportunityCreate(BaseModel):
    niche: str
    trend_score: float
    keywords: List[str]
    suggested_products: List[str] = []
    market_size: Optional[str] = None
    competition_level: Optional[str] = None

class AITask(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    ai_team: AITeam
    status: AITaskStatus = AITaskStatus.PENDING
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class AITaskCreate(BaseModel):
    task_type: str
    ai_team: AITeam
    input_data: Dict[str, Any]

class RevenueMetric(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_revenue: float = 0.0
    total_conversions: int = 0
    total_clicks: int = 0
    top_products: List[Dict[str, Any]] = []
    revenue_by_type: Dict[str, float] = {}

class DashboardStats(BaseModel):
    total_products: int
    products_today: int
    total_revenue: float
    revenue_today: float
    pending_tasks: int
    active_opportunities: int


# API Routes
@api_router.get("/")
async def root():
    return {"message": "CEO AI Empire - Autonomous Product Generation System"}


# Dashboard Stats
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get overall dashboard statistics"""
    try:
        # Count products
        total_products = await db.products.count_documents({})
        
        # Products created today
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        products_today = await db.products.count_documents({
            "created_at": {"$gte": today_start.isoformat()}
        })
        
        # Calculate revenue
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$revenue"}}}
        ]
        revenue_result = await db.products.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0.0
        
        # Revenue today
        revenue_today_pipeline = [
            {"$match": {"created_at": {"$gte": today_start.isoformat()}}},
            {"$group": {"_id": None, "total": {"$sum": "$revenue"}}}
        ]
        revenue_today_result = await db.products.aggregate(revenue_today_pipeline).to_list(1)
        revenue_today = revenue_today_result[0]["total"] if revenue_today_result else 0.0
        
        # Pending tasks
        pending_tasks = await db.ai_tasks.count_documents({"status": "pending"})
        
        # Active opportunities
        active_opportunities = await db.opportunities.count_documents({"status": "identified"})
        
        return DashboardStats(
            total_products=total_products,
            products_today=products_today,
            total_revenue=total_revenue,
            revenue_today=revenue_today,
            pending_tasks=pending_tasks,
            active_opportunities=active_opportunities
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Products CRUD
@api_router.post("/products", response_model=Product)
async def create_product(product_input: ProductCreate):
    """Create a new product"""
    try:
        product = Product(**product_input.model_dump())
        
        # Generate mock marketplace links
        product.marketplace_links = [
            MarketplaceLink(platform="Amazon KDP", url=f"https://amazon.com/dp/{product.id[:8]}", status="ready"),
            MarketplaceLink(platform="Udemy", url=f"https://udemy.com/course/{product.title.lower().replace(' ', '-')}", status="ready"),
            MarketplaceLink(platform="Shopify", url=f"https://mystore.shopify.com/products/{product.id[:8]}", status="ready"),
        ]
        
        doc = product.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['marketplace_links'] = [link.model_dump() for link in product.marketplace_links]
        
        await db.products.insert_one(doc)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/products", response_model=List[Product])
async def get_products(limit: int = 50, status: Optional[str] = None):
    """Get all products with optional filtering"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        products = await db.products.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Convert ISO strings back to datetime
        for product in products:
            if isinstance(product['created_at'], str):
                product['created_at'] = datetime.fromisoformat(product['created_at'])
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    try:
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if isinstance(product['created_at'], str):
            product['created_at'] = datetime.fromisoformat(product['created_at'])
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/products/{product_id}/status")
async def update_product_status(product_id: str, status: ProductStatus):
    """Update product status (draft/ready/published/retired)"""
    try:
        result = await db.products.update_one(
            {"id": product_id},
            {"$set": {"status": status}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"message": "Status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Opportunities CRUD
@api_router.post("/opportunities", response_model=Opportunity)
async def create_opportunity(opportunity_input: OpportunityCreate):
    """Create a new opportunity"""
    try:
        opportunity = Opportunity(**opportunity_input.model_dump())
        
        doc = opportunity.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.opportunities.insert_one(doc)
        return opportunity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/opportunities", response_model=List[Opportunity])
async def get_opportunities(limit: int = 20):
    """Get all opportunities"""
    try:
        opportunities = await db.opportunities.find({}, {"_id": 0}).sort("trend_score", -1).limit(limit).to_list(limit)
        
        for opp in opportunities:
            if isinstance(opp['created_at'], str):
                opp['created_at'] = datetime.fromisoformat(opp['created_at'])
        
        return opportunities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AI Tasks CRUD
@api_router.post("/ai/tasks", response_model=AITask)
async def create_ai_task(task_input: AITaskCreate):
    """Create a new AI task"""
    try:
        task = AITask(**task_input.model_dump())
        
        doc = task.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        if doc.get('completed_at'):
            doc['completed_at'] = doc['completed_at'].isoformat()
        
        await db.ai_tasks.insert_one(doc)
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/ai/tasks", response_model=List[AITask])
async def get_ai_tasks(limit: int = 50, status: Optional[str] = None):
    """Get all AI tasks with optional status filtering"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        tasks = await db.ai_tasks.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        
        for task in tasks:
            if isinstance(task['created_at'], str):
                task['created_at'] = datetime.fromisoformat(task['created_at'])
            if task.get('completed_at') and isinstance(task['completed_at'], str):
                task['completed_at'] = datetime.fromisoformat(task['completed_at'])
        
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Revenue Metrics
@api_router.get("/metrics/revenue", response_model=List[RevenueMetric])
async def get_revenue_metrics(days: int = 7):
    """Get revenue metrics for the past N days"""
    try:
        metrics = await db.revenue_metrics.find({}, {"_id": 0}).sort("date", -1).limit(days).to_list(days)
        
        for metric in metrics:
            if isinstance(metric['date'], str):
                metric['date'] = datetime.fromisoformat(metric['date'])
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/metrics/revenue")
async def record_revenue_metric(metric: RevenueMetric):
    """Record a new revenue metric"""
    try:
        doc = metric.model_dump()
        doc['date'] = doc['date'].isoformat()
        
        await db.revenue_metrics.insert_one(doc)
        return {"message": "Revenue metric recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ AI TEAM ENDPOINTS ============

@api_router.post("/ai/scout-opportunities")
async def scout_opportunities():
    """Trigger Opportunity Scouting AI to find trending niches"""
    try:
        # Create task
        task = AITask(
            task_type="scout_opportunities",
            ai_team=AITeam.OPPORTUNITY_SCOUT,
            status=AITaskStatus.IN_PROGRESS,
            input_data={"sources": ["social media", "marketplaces", "trends"]}
        )
        task_doc = task.model_dump()
        task_doc['created_at'] = task_doc['created_at'].isoformat()
        await db.ai_tasks.insert_one(task_doc)
        
        # Run opportunity scout
        opportunities = await opportunity_scout.scout_opportunities()
        
        # Save opportunities to database
        for opp in opportunities:
            # Remove _id if present
            opp_copy = opp.copy()
            opp_copy.pop('_id', None)
            await db.opportunities.insert_one(opp_copy)
        
        # Update task
        await db.ai_tasks.update_one(
            {"id": task.id},
            {"$set": {
                "status": "completed",
                "output_data": {"opportunities_found": len(opportunities)},
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "opportunities_found": len(opportunities),
            "opportunities": opportunities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateBookRequest(BaseModel):
    niche: str
    keywords: List[str]
    book_length: str = "medium"
    target_audience: str = "general"

@api_router.post("/ai/generate-book")
async def generate_book(request: GenerateBookRequest):
    """Generate an eBook using Book Writing AI"""
    try:
        # Create task
        task = AITask(
            task_type="generate_book",
            ai_team=AITeam.BOOK_WRITER,
            status=AITaskStatus.IN_PROGRESS,
            input_data=request.model_dump()
        )
        task_doc = task.model_dump()
        task_doc['created_at'] = task_doc['created_at'].isoformat()
        await db.ai_tasks.insert_one(task_doc)
        
        # Generate book
        book_data = await book_writer.generate_book(
            niche=request.niche,
            keywords=request.keywords,
            book_length=request.book_length,
            target_audience=request.target_audience
        )
        
        # Add marketplace links and pricing
        book_data['marketplace_links'] = [
            {"platform": "Amazon KDP", "url": f"https://amazon.com/dp/{book_data['id'][:8]}", "status": "ready"},
            {"platform": "Udemy", "url": f"https://udemy.com/course/{book_data['title'].lower().replace(' ', '-')}", "status": "ready"},
            {"platform": "Shopify", "url": f"https://mystore.shopify.com/products/{book_data['id'][:8]}", "status": "ready"}
        ]
        book_data['price'] = 29.99
        book_data['revenue'] = 0.0
        book_data['clicks'] = 0
        book_data['conversions'] = 0
        
        # Save to database
        book_doc = book_data.copy()
        book_doc.pop('_id', None)  # Remove _id if present
        await db.products.insert_one(book_doc)
        
        # Return without _id
        return_data = {k: v for k, v in book_data.items() if k != '_id'}
        
        # Update task
        await db.ai_tasks.update_one(
            {"id": task.id},
            {"$set": {
                "status": "completed",
                "output_data": {"product_id": return_data['id'], "title": return_data['title']},
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "product": return_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateCourseRequest(BaseModel):
    topic: str
    target_audience: str = "beginners"
    duration_hours: int = 3
    learning_objectives: Optional[List[str]] = None

@api_router.post("/ai/generate-course")
async def generate_course(request: GenerateCourseRequest):
    """Generate a course using Course Creation AI"""
    try:
        # Create task
        task = AITask(
            task_type="generate_course",
            ai_team=AITeam.COURSE_CREATOR,
            status=AITaskStatus.IN_PROGRESS,
            input_data=request.model_dump()
        )
        task_doc = task.model_dump()
        task_doc['created_at'] = task_doc['created_at'].isoformat()
        await db.ai_tasks.insert_one(task_doc)
        
        # Generate course
        course_data = await course_creator.generate_course(
            topic=request.topic,
            target_audience=request.target_audience,
            duration_hours=request.duration_hours,
            learning_objectives=request.learning_objectives
        )
        
        # Add marketplace links and pricing
        course_data['marketplace_links'] = [
            {"platform": "Udemy", "url": f"https://udemy.com/course/{course_data['title'].lower().replace(' ', '-')}", "status": "ready"},
            {"platform": "Shopify", "url": f"https://mystore.shopify.com/products/{course_data['id'][:8]}", "status": "ready"}
        ]
        course_data['price'] = 49.99
        course_data['revenue'] = 0.0
        course_data['clicks'] = 0
        course_data['conversions'] = 0
        course_data['tags'] = [request.topic]
        
        # Save to database
        course_doc = course_data.copy()
        course_doc.pop('_id', None)
        await db.products.insert_one(course_doc)
        
        return_data = {k: v for k, v in course_data.items() if k != '_id'}
        
        # Update task
        await db.ai_tasks.update_one(
            {"id": task.id},
            {"$set": {
                "status": "completed",
                "output_data": {"product_id": return_data['id'], "title": return_data['title']},
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "product": return_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateProductRequest(BaseModel):
    product_type: str  # template/planner/mini_app
    keywords: List[str]
    style: str = "professional"
    target_use_case: Optional[str] = None

@api_router.post("/ai/generate-product")
async def generate_product(request: GenerateProductRequest):
    """Generate a digital product using Product AI"""
    try:
        # Create task
        task = AITask(
            task_type=f"generate_{request.product_type}",
            ai_team=AITeam.PRODUCT_CREATOR,
            status=AITaskStatus.IN_PROGRESS,
            input_data=request.model_dump()
        )
        task_doc = task.model_dump()
        task_doc['created_at'] = task_doc['created_at'].isoformat()
        await db.ai_tasks.insert_one(task_doc)
        
        # Generate product
        product_data = await product_generator.generate_product(
            product_type=request.product_type,
            keywords=request.keywords,
            style=request.style,
            target_use_case=request.target_use_case
        )
        
        # Add marketplace links and pricing
        product_data['marketplace_links'] = [
            {"platform": "Amazon KDP", "url": f"https://amazon.com/dp/{product_data['id'][:8]}", "status": "ready"},
            {"platform": "Shopify", "url": f"https://mystore.shopify.com/products/{product_data['id'][:8]}", "status": "ready"}
        ]
        product_data['price'] = 19.99
        product_data['revenue'] = 0.0
        product_data['clicks'] = 0
        product_data['conversions'] = 0
        
        # Save to database
        product_doc = product_data.copy()
        product_doc.pop('_id', None)
        await db.products.insert_one(product_doc)
        
        return_data = {k: v for k, v in product_data.items() if k != '_id'}
        
        # Update task
        await db.ai_tasks.update_one(
            {"id": task.id},
            {"$set": {
                "status": "completed",
                "output_data": {"product_id": return_data['id'], "title": return_data['title']},
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "product": return_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/ai/run-autonomous-cycle")
async def run_autonomous_cycle(background_tasks: BackgroundTasks):
    """
    Run complete autonomous workflow:
    Scout opportunities -> Generate products -> Update dashboard
    """
    try:
        # Run in background to avoid timeout
        results = await micro_taskforce.run_autonomous_cycle()
        
        return {
            "success": results.get("success", False),
            "message": "Autonomous cycle completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/ai/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific AI task"""
    try:
        task = await db.ai_tasks.find_one({"id": task_id}, {"_id": 0})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Convert ISO strings to datetime
        if isinstance(task['created_at'], str):
            task['created_at'] = datetime.fromisoformat(task['created_at'])
        if task.get('completed_at') and isinstance(task['completed_at'], str):
            task['completed_at'] = datetime.fromisoformat(task['completed_at'])
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PHASE 3: MARKETING & REVENUE OPTIMIZATION ============

@api_router.post("/ai/optimize-revenue")
async def optimize_revenue():
    """Run Revenue Maximizer AI to optimize pricing and create bundles"""
    try:
        # Get all products
        products = await db.products.find({}, {"_id": 0}).to_list(100)
        
        # Run revenue optimization
        recommendations = await revenue_maximizer.optimize_pricing(products)
        
        # Store recommendations
        rec_doc = recommendations.copy()
        rec_doc["id"] = f"rec-{random.randint(1000, 9999)}"
        rec_doc.pop('_id', None)
        await db.revenue_recommendations.insert_one(rec_doc)
        
        return {
            "success": True,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateSocialPostsRequest(BaseModel):
    product_id: str
    num_posts: int = 5

@api_router.post("/ai/generate-social-posts")
async def generate_social_posts(request: GenerateSocialPostsRequest):
    """Generate social media posts for a product"""
    try:
        # Get product
        product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Generate posts
        posts = await social_media_ai.generate_posts(product, request.num_posts)
        
        # Store posts
        for post in posts:
            post_doc = post.copy()
            post_doc.pop('_id', None)
            await db.social_media_posts.insert_one(post_doc)
        
        return {
            "success": True,
            "posts_generated": len(posts),
            "posts": posts
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateLaunchCampaignRequest(BaseModel):
    product_id: str
    target_audience: str = "general"

@api_router.post("/ai/create-launch-campaign")
async def create_launch_campaign(request: CreateLaunchCampaignRequest):
    """Create complete launch campaign with funnel and emails"""
    try:
        # Get product
        product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create campaign
        campaign = await sales_launch_ai.create_launch_campaign(product, request.target_audience)
        
        # Store campaign
        campaign_doc = campaign.copy()
        campaign_doc.pop('_id', None)
        await db.launch_campaigns.insert_one(campaign_doc)
        
        return {
            "success": True,
            "campaign": campaign
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/ai/generate-affiliate-program")
async def generate_affiliate_program():
    """Generate affiliate program structure and recruitment materials"""
    try:
        # Get all products
        products = await db.products.find({}, {"_id": 0}).to_list(100)
        
        # Generate program
        program = await affiliate_manager.generate_affiliate_program(products)
        
        # Store program
        program_doc = program.copy()
        program_doc.pop('_id', None)
        await db.affiliate_programs.insert_one(program_doc)
        
        return {
            "success": True,
            "program": program
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/marketing/revenue-recommendations")
async def get_revenue_recommendations(limit: int = 1):
    """Get latest revenue recommendations"""
    try:
        recommendations = await db.revenue_recommendations.find({}, {"_id": 0}).sort("generated_at", -1).limit(limit).to_list(limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/marketing/social-posts")
async def get_social_posts(product_id: Optional[str] = None, limit: int = 20):
    """Get scheduled social media posts"""
    try:
        query = {}
        if product_id:
            query["product_id"] = product_id
        
        posts = await db.social_media_posts.find(query, {"_id": 0}).sort("scheduled_time", -1).limit(limit).to_list(limit)
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/marketing/launch-campaigns")
async def get_launch_campaigns(product_id: Optional[str] = None):
    """Get launch campaigns"""
    try:
        query = {}
        if product_id:
            query["product_id"] = product_id
        
        campaigns = await db.launch_campaigns.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/marketing/affiliate-program")
async def get_affiliate_program():
    """Get latest affiliate program"""
    try:
        program = await db.affiliate_programs.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
        if not program:
            return {"message": "No affiliate program found"}
        return program
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
