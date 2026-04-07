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
import json
import openai
import anthropic

# Import managers
from config.keys_manager import keys_manager

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
from ai_services.scheduler import AutomationScheduler
from ai_services.marketplace_integrations import MarketplaceIntegrations
from ai_services.compliance_checker import ComplianceChecker
from ai_services.analytics_engine import AnalyticsEngine
from ai_services.real_product_generator import RealProductGenerator
from ai_services.autonomous_engine import AutonomousEngine
from ai_services.gumroad_publisher import GumroadPublisher
from ai_services.key_vault import SecureKeyVault
from ai_services.opportunity_hunter import OpportunityHunter, ProductDiscoveryEngine
from ai_services.project_manager import ProjectFileManager, PublishingGuide
from ai_services.ai_assistant import AIAssistant
from ai_services.team_engine import AgentTeamEngine

# Import core system
from core.routes import router as core_router
# Note: routes_v2 and routes_v3 are deprecated with missing dependencies
# Using routes.py and routes_v4_production.py instead


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection - try to get from keys first, then env, then demo mode
mongo_url = keys_manager.get_key('mongodb_url') or os.environ.get('MONGO_URL')

# Use the hardcoded MongoDB connection from earlier setup
if not mongo_url:
    mongo_url = 'mongodb+srv://stackdigitz_db_user:xBj1y07Rr0bANp68@cluster0.rfvpl5d.mongodb.net/?appName=Cluster0'

db = None
client = None

if mongo_url:
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000, connectTimeoutMS=10000)
        # Verify connection works
        db_name = os.environ.get('DB_NAME', 'ceo_factory')
        db = client[db_name]
        print(f"✅ MongoDB connected to {db_name}")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to MongoDB immediately: {e}")
        print("⏳ Will try to reconnect on first request...")
        db = None
        client = None
else:
    print("ℹ️  MONGO_URL not available. Running in demo mode.")

# Initialize AI services
opportunity_scout = OpportunityScout()
book_writer = BookWriter()
course_creator = CourseCreator()
product_generator = ProductGenerator()
micro_taskforce = MicroTaskforce(db) if db is not None else None
revenue_maximizer = RevenueMaximizer()
social_media_ai = SocialMediaAI()
sales_launch_ai = SalesLaunchAI()
affiliate_manager = AffiliateManager()
marketplace_integrations = MarketplaceIntegrations()
compliance_checker = ComplianceChecker()
analytics_engine = AnalyticsEngine()
real_product_generator = RealProductGenerator()
gumroad_publisher = GumroadPublisher()
key_vault = SecureKeyVault(db)
opportunity_hunter = OpportunityHunter(db)
product_discovery = ProductDiscoveryEngine(db)
project_manager = ProjectFileManager(db)
publishing_guide = PublishingGuide()
ai_assistant = AIAssistant(db)
team_engine = AgentTeamEngine(db)

# Autonomous engine (initialized after db)
autonomous_engine = None

# Scheduler will be initialized after db is ready
automation_scheduler = None

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


# API Key Models
class APIKeyInput(BaseModel):
    gumroad_key: Optional[str] = None
    gumroad_secret: Optional[str] = None
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None
    dalle_key: Optional[str] = None
    sendgrid_key: Optional[str] = None
    stripe_key: Optional[str] = None
    mongodb_url: Optional[str] = None


class APIKeyResponse(BaseModel):
    status: str
    message: str
    keys_stored: int


# API Routes
@api_router.get("/")
async def root():
    return {"message": "CEO AI Empire - Autonomous Product Generation System"}


# API Keys Management
@api_router.post("/keys/store", response_model=APIKeyResponse)
async def store_api_keys(keys: APIKeyInput):
    """
    Store API keys from frontend
    These keys are encrypted and stored securely
    """
    try:
        keys_data = keys.model_dump(exclude_none=True)
        
        # Store keys using the keys manager
        stored_keys = keys_manager.store_keys(keys_data)
        
        # If MongoDB URL provided, try to reconnect
        if 'mongodb_url' in keys_data and keys_data['mongodb_url']:
            global db, client
            try:
                new_mongo_url = keys_data['mongodb_url']
                if client:
                    client.close()
                client = AsyncIOMotorClient(new_mongo_url, serverSelectionTimeoutMS=5000)
                db = client[os.environ.get('DB_NAME', 'ceo_factory')]
                print(f"✅ MongoDB reconnected with provided URL")
            except Exception as e:
                print(f"⚠️  MongoDB connection failed: {e}")
        
        return APIKeyResponse(
            status="success",
            message="API keys stored securely",
            keys_stored=len(stored_keys)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/keys/status")
async def get_keys_status():
    """Check which API keys are configured"""
    key_names = ['openai_key', 'anthropic_key', 'dalle_key', 'sendgrid_key', 'stripe_key', 'gumroad_key']
    status = {}
    
    for key_name in key_names:
        key_value = keys_manager.get_key(key_name)
        status[key_name] = "✅ Configured" if key_value else "❌ Not configured"
    
    # Also check MongoDB
    status['mongodb'] = "✅ Connected" if db else "⏳ Not connected yet"
    
    return {"api_keys_status": status}


# ==================== AI Service Integrations ====================

class AIProductRequest(BaseModel):
    concept: str = Field(..., description="Product concept or idea")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Related keywords")
    tone: Optional[str] = Field(default="professional", description="Tone of product description")

class AIProductResponse(BaseModel):
    title: str
    description: str
    keywords: List[str]
    price_range: str
    target_audience: str

class AIOpportunityRequest(BaseModel):
    niche: str = Field(..., description="Business niche")
    market_size: Optional[str] = Field(default="medium", description="Target market size")
    keyword_focus: Optional[str] = Field(default=None, description="Key search term to analyze")

class AIOpportunityResponse(BaseModel):
    opportunity_title: str
    demand_level: str  # High, Medium, Low
    competition_level: str  # High, Medium, Low
    trend_direction: str  # Rising, Stable, Declining
    estimated_market_size: str
    recommended_keywords: List[str]
    action_items: List[str]

class AIImageRequest(BaseModel):
    description: str = Field(..., description="Image description")
    style: Optional[str] = Field(default="professional", description="Art style (professional, minimalist, vibrant, etc)")
    size: Optional[str] = Field(default="1024x1024", description="Image size")

class AIImageResponse(BaseModel):
    image_url: str
    prompt_used: str
    created_at: str


@api_router.post("/ai/generate-product", response_model=AIProductResponse)
async def generate_product_with_openai(request: AIProductRequest):
    """Generate product description using OpenAI ChatGPT"""
    try:
        openai_key = keys_manager.get_key('openai_key')
        if not openai_key:
            raise HTTPException(status_code=400, detail="OpenAI API key not configured")
        
        # Initialize OpenAI client with the key from keys_manager
        client = openai.OpenAI(api_key=openai_key)
        
        prompt = f"""You are a product development expert. Generate a compelling product listing based on this concept:

Concept: {request.concept}
Keywords to include: {', '.join(request.keywords) if request.keywords else 'auto-generate relevant keywords'}
Tone: {request.tone}

Please provide a JSON response with:
- title: A catchy product title (max 10 words)
- description: A compelling 2-3 sentence product description
- keywords: Array of 5-8 relevant SEO keywords
- price_range: Estimated price range (e.g., "$19-$49")
- target_audience: Who should buy this product

Return ONLY valid JSON, no markdown formatting."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        # Parse the response
        try:
            import json
            result = json.loads(response.choices[0].message.content)
            return AIProductResponse(**result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            content = response.choices[0].message.content
            return AIProductResponse(
                title=request.concept[:50],
                description=content[:200],
                keywords=request.keywords or ["product", request.concept.lower().split()[0]],
                price_range="$19-$99",
                target_audience="Digital entrepreneurs"
            )
            
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating product: {str(e)}")


@api_router.post("/ai/find-opportunities", response_model=AIOpportunityResponse)
async def find_opportunities_with_claude(request: AIOpportunityRequest):
    """Find market opportunities using Anthropic Claude"""
    try:
        anthropic_key = keys_manager.get_key('anthropic_key')
        if not anthropic_key:
            raise HTTPException(status_code=400, detail="Anthropic Claude API key not configured")
        
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=anthropic_key)
        
        prompt = f"""You are a market research expert specializing in opportunity identification. Analyze this market:

Niche: {request.niche}
Market Size Target: {request.market_size}
Focus Keyword: {request.keyword_focus or request.niche}

Provide a JSON response with:
- opportunity_title: Brief title of the opportunity (max 10 words)
- demand_level: "High", "Medium", or "Low"
- competition_level: "High", "Medium", or "Low"
- trend_direction: "Rising", "Stable", or "Declining"
- estimated_market_size: Your estimate (e.g., "$50M-$100M annually")
- recommended_keywords: Array of 5-8 high-value search keywords
- action_items: Array of 3-5 immediate steps to capitalize on this opportunity

Return ONLY valid JSON, no markdown."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response
        try:
            import json
            result = json.loads(message.content[0].text)
            return AIOpportunityResponse(**result)
        except (json.JSONDecodeError, KeyError, IndexError):
            # Fallback response
            return AIOpportunityResponse(
                opportunity_title=f"{request.niche} Market Opportunity",
                demand_level="Medium",
                competition_level="Medium",
                trend_direction="Rising",
                estimated_market_size="$10M-$50M",
                recommended_keywords=[request.niche.lower(), "trending", "emerging"],
                action_items=["Research target market", "Analyze competitors", "Build MVP"]
            )
            
    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"Anthropic API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding opportunities: {str(e)}")


@api_router.post("/ai/generate-image", response_model=AIImageResponse)
async def generate_image_with_dalle(request: AIImageRequest):
    """Generate product image using DALL-E"""
    try:
        dalle_key = keys_manager.get_key('dalle_key')
        if not dalle_key:
            raise HTTPException(status_code=400, detail="DALL-E API key not configured")
        
        # Initialize OpenAI client for DALL-E (uses same API key)
        client = openai.OpenAI(api_key=dalle_key)
        
        # Create enhanced prompt for better results
        enhanced_prompt = f"{request.description} Style: {request.style} High quality product photography"
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=request.size,
            quality="standard",
            n=1
        )
        
        return AIImageResponse(
            image_url=response.data[0].url,
            prompt_used=enhanced_prompt,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"DALL-E API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")


# ==================== Combined AI Workflow ====================

class FullProductGenerationRequest(BaseModel):
    concept: str
    keywords: Optional[List[str]] = Field(default_factory=list)
    generate_image: bool = Field(default=True)
    save_to_db: bool = Field(default=True)

class FullProductGenerationResponse(BaseModel):
    product: AIProductResponse
    image: Optional[AIImageResponse] = None
    database_id: Optional[str] = None
    status: str


@api_router.post("/ai/generate-full-product", response_model=FullProductGenerationResponse)
async def generate_full_product(request: FullProductGenerationRequest):
    """Complete product generation workflow: concept -> description -> image -> save to DB"""
    try:
        # Step 1: Generate product description
        product_request = AIProductRequest(
            concept=request.concept,
            keywords=request.keywords,
            tone="professional"
        )
        product_response = await generate_product_with_openai(product_request)
        
        # Step 2: Generate image (optional)
        image_response = None
        if request.generate_image:
            try:
                image_request = AIImageRequest(
                    description=product_response.description,
                    style="professional product photography"
                )
                image_response = await generate_image_with_dalle(image_request)
            except Exception as e:
                print(f"Warning: Image generation failed: {e}")
                # Continue without image
        
        # Step 3: Save to MongoDB (optional)
        database_id = None
        if request.save_to_db and db:
            try:
                product_doc = {
                    "id": str(uuid.uuid4()),
                    "title": product_response.title,
                    "description": product_response.description,
                    "keywords": product_response.keywords,
                    "price_range": product_response.price_range,
                    "target_audience": product_response.target_audience,
                    "image_url": image_response.image_url if image_response else None,
                    "status": "generated",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": "ai_generation"
                }
                result = await db.products.insert_one(product_doc)
                database_id = str(result.inserted_id)
            except Exception as e:
                print(f"Warning: Failed to save to database: {e}")
        
        return FullProductGenerationResponse(
            product=product_response,
            image=image_response,
            database_id=database_id,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in full product generation: {str(e)}")


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


# ============ PHASE 4: FULL AUTOMATION & SCALE ============

@api_router.post("/automation/run-scheduled-cycle")
async def run_scheduled_cycle(cycle_type: str):
    """Run a scheduled automation cycle"""
    try:
        global automation_scheduler
        if not automation_scheduler:
            automation_scheduler = AutomationScheduler(db, micro_taskforce)
        
        results = await automation_scheduler.run_scheduled_cycle(cycle_type)
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/automation/schedule")
async def get_automation_schedule():
    """Get next scheduled automation runs"""
    try:
        global automation_scheduler
        if not automation_scheduler:
            automation_scheduler = AutomationScheduler(db, micro_taskforce)
        
        schedule = automation_scheduler.get_next_scheduled_runs()
        return {"schedule": schedule}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PublishToMarketplaceRequest(BaseModel):
    product_id: str
    marketplace: str

@api_router.post("/marketplace/publish")
async def publish_to_marketplace(request: PublishToMarketplaceRequest):
    """Publish product to a marketplace"""
    try:
        # Get product
        product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Publish
        result = await marketplace_integrations.publish_to_marketplace(
            product, 
            request.marketplace
        )
        
        # Store listing
        listing_doc = result.copy()
        listing_doc.pop('_id', None)
        listing_doc['sales'] = 0
        listing_doc['revenue'] = 0.0
        await db.marketplace_listings.insert_one(listing_doc)
        
        return {
            "success": True,
            "listing": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/marketplace/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    try:
        stats = await marketplace_integrations.get_marketplace_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/marketplace/listings")
async def get_marketplace_listings(marketplace: Optional[str] = None, limit: int = 50):
    """Get marketplace listings"""
    try:
        query = {}
        if marketplace:
            query["marketplace"] = marketplace
        
        listings = await db.marketplace_listings.find(query, {"_id": 0}).sort("published_at", -1).limit(limit).to_list(limit)
        return listings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ComplianceCheckRequest(BaseModel):
    product_id: str

@api_router.post("/compliance/check")
async def check_product_compliance(request: ComplianceCheckRequest):
    """Run compliance checks on a product"""
    try:
        # Get product
        product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Run compliance checks
        results = await compliance_checker.check_product_compliance(product)
        
        # Store results
        compliance_doc = results.copy()
        compliance_doc["id"] = f"compliance-{random.randint(1000, 9999)}"
        compliance_doc.pop('_id', None)
        await db.compliance_checks.insert_one(compliance_doc)
        
        return {
            "success": True,
            "compliance": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/compliance/checks")
async def get_compliance_checks(product_id: Optional[str] = None, limit: int = 20):
    """Get compliance check results"""
    try:
        query = {}
        if product_id:
            query["product_id"] = product_id
        
        checks = await db.compliance_checks.find(query, {"_id": 0}).sort("checked_at", -1).limit(limit).to_list(limit)
        return checks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analytics/insights")
async def get_business_insights():
    """Get AI-powered business insights and predictions"""
    try:
        # Get data
        products = await db.products.find({}, {"_id": 0}).to_list(100)
        opportunities = await db.opportunities.find({}, {"_id": 0}).to_list(100)
        revenue_data = []  # Can be enhanced with historical data
        
        # Generate insights
        insights = await analytics_engine.generate_insights(products, opportunities, revenue_data)
        
        # Store insights
        insights_doc = insights.copy()
        insights_doc["id"] = f"insights-{random.randint(1000, 9999)}"
        insights_doc.pop('_id', None)
        await db.analytics_insights.insert_one(insights_doc)
        
        return {
            "success": True,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/system/health")
async def get_system_health():
    """Get system health status"""
    try:
        # Check all systems
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "database": "connected" if db is not None else "unavailable (demo mode)",
                "ai_teams": "operational",
                "automation": "operational",
                "marketplaces": "operational"
            }
        }
        
        # Only count documents if database is available
        if db is not None:
            health["stats"] = {
                "total_products": await db.products.count_documents({}),
                "total_opportunities": await db.opportunities.count_documents({}),
                "pending_tasks": await db.ai_tasks.count_documents({"status": "pending"}),
                "marketplace_listings": await db.marketplace_listings.count_documents({})
            }
        else:
            health["stats"] = {"mode": "demo", "note": "No persistent storage"}
        
        return health
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ============ AUTONOMOUS ENGINE ============

@api_router.post("/autonomous/run-cycle")
async def run_autonomous_cycle():
    """
    Run ONE complete autonomous cycle:
    Scout → Generate REAL product → Compliance → Publish → Market → Track
    
    Returns complete product with files and marketplace links
    """
    try:
        global autonomous_engine
        if not autonomous_engine:
            autonomous_engine = AutonomousEngine(db)
        
        print("\n🚀 Starting autonomous product cycle...")
        results = await autonomous_engine.run_autonomous_product_cycle()
        
        return {
            "success": results["status"] == "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/autonomous/start-continuous")
async def start_continuous_mode(products_per_day: int = 3, background_tasks: BackgroundTasks = None):
    """
    Start continuous autonomous mode - generates products 24/7
    
    Args:
        products_per_day: How many products to generate daily (default: 3)
    """
    try:
        global autonomous_engine
        if not autonomous_engine:
            autonomous_engine = AutonomousEngine(db)
        
        if autonomous_engine.running:
            return {
                "message": "Autonomous mode already running",
                "status": "running"
            }
        
        # Run in background
        if background_tasks:
            background_tasks.add_task(
                autonomous_engine.continuous_autonomous_mode,
                products_per_day=products_per_day
            )
        
        return {
            "success": True,
            "message": f"Continuous autonomous mode started - {products_per_day} products/day",
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/autonomous/stop")
async def stop_autonomous_mode():
    """Stop continuous autonomous mode"""
    try:
        global autonomous_engine
        if autonomous_engine and autonomous_engine.running:
            autonomous_engine.stop()
            return {
                "success": True,
                "message": "Autonomous mode stopped"
            }
        else:
            return {
                "success": False,
                "message": "Autonomous mode was not running"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/autonomous/status")
async def get_autonomous_status():
    """Get status of autonomous engine"""
    try:
        global autonomous_engine
        if not autonomous_engine:
            return {
                "running": False,
                "status": "not_initialized"
            }
        
        return {
            "running": autonomous_engine.running,
            "status": "running" if autonomous_engine.running else "stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products/generate-real")
async def generate_real_product(niche: str, product_type: str = "ebook"):
    """
    Generate a REAL, complete product (not just metadata)
    
    Args:
        niche: The niche/topic
        product_type: ebook or course
    """
    try:
        global real_product_generator
        if not real_product_generator:
            real_product_generator = RealProductGenerator()
        
        if product_type == "ebook":
            product = await real_product_generator.generate_complete_ebook(
                niche=niche,
                keywords=[niche],
                target_audience="general"
            )
        elif product_type == "course":
            product = await real_product_generator.generate_complete_course(
                topic=niche,
                target_audience="beginners",
                duration_hours=3
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid product_type. Use 'ebook' or 'course'")
        
        # Export to file
        file_path = await real_product_generator.export_to_file(product, format='json')
        markdown_path = await real_product_generator.export_to_file(product, format='markdown')
        
        return {
            "success": True,
            "product": {
                "title": product['title'],
                "type": product['product_type'],
                "quality_score": product['quality_score'],
                "word_count": product['metadata'].get('word_count', 0),
                "description": product['description']
            },
            "files": {
                "json": file_path,
                "markdown": markdown_path
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ LAUNCH PRODUCT ONE-CLICK (FULL AUTONOMOUS CYCLE) ============

class LaunchProductRequest(BaseModel):
    niche: Optional[str] = None
    product_type: str = "ebook"  # ebook or course
    auto_publish: bool = True
    generate_social: bool = True

@api_router.post("/launch-product")
async def launch_product_one_click(request: LaunchProductRequest):
    """
    🚀 ONE-CLICK LAUNCH: Full Autonomous Cycle
    
    Scout → Generate → Publish to Gumroad → Create Marketing → Track Analytics
    
    This is the money-making engine that takes AI from idea to revenue.
    """
    results = {
        "success": False,
        "stages": {},
        "product": None,
        "gumroad": None,
        "social_posts": [],
        "analytics": None
    }
    
    try:
        # STAGE 1: Scout Opportunities (if no niche provided)
        niche = request.niche
        if not niche:
            print("🔍 Stage 1: Scouting opportunities...")
            opportunities = await opportunity_scout.scout_opportunities()
            if opportunities:
                # Pick the highest trending opportunity
                best_opp = max(opportunities, key=lambda x: x.get('trend_score', 0))
                niche = best_opp.get('niche', 'productivity')
                results["stages"]["scout"] = {
                    "success": True,
                    "opportunities_found": len(opportunities),
                    "selected_niche": niche,
                    "trend_score": best_opp.get('trend_score', 0)
                }
            else:
                niche = "productivity"  # Default fallback
                results["stages"]["scout"] = {"success": True, "selected_niche": niche, "note": "Using default niche"}
        else:
            results["stages"]["scout"] = {"success": True, "selected_niche": niche, "note": "User provided niche"}
        
        # STAGE 2: Generate Product
        print(f"📚 Stage 2: Generating {request.product_type} for '{niche}'...")
        if request.product_type == "ebook":
            product_data = await book_writer.generate_book(
                niche=niche,
                keywords=[niche, "guide", "tutorial"],
                book_length="medium",
                target_audience="professionals"
            )
        else:
            product_data = await course_creator.generate_course(
                topic=niche,
                target_audience="beginners",
                duration_hours=3
            )
        
        # Add pricing
        product_data['price'] = 29.99 if request.product_type == "ebook" else 49.99
        product_data['revenue'] = 0.0
        product_data['clicks'] = 0
        product_data['conversions'] = 0
        
        results["stages"]["generate"] = {
            "success": True,
            "title": product_data.get('title'),
            "type": request.product_type
        }
        results["product"] = product_data
        
        # STAGE 3: Publish to Gumroad (if enabled)
        gumroad_result = {"success": False, "note": "Auto-publish disabled"}
        if request.auto_publish:
            print("🛒 Stage 3: Publishing to Gumroad...")
            if request.product_type == "ebook":
                gumroad_result = await gumroad_publisher.publish_ebook(product_data)
            else:
                gumroad_result = await gumroad_publisher.publish_course(product_data)
            
            if gumroad_result.get("success"):
                # Update product with Gumroad URL
                product_data['marketplace_links'] = [
                    {
                        "platform": "Gumroad",
                        "url": gumroad_result.get("url", ""),
                        "product_id": gumroad_result.get("product_id"),
                        "status": "live"
                    }
                ]
        
        results["stages"]["publish"] = gumroad_result
        results["gumroad"] = gumroad_result
        
        # STAGE 4: Generate Social Media Posts (if enabled)
        if request.generate_social:
            print("📱 Stage 4: Generating social media content...")
            social_posts = await social_media_ai.generate_posts(product_data, num_posts=5)
            results["social_posts"] = social_posts
            results["stages"]["social"] = {
                "success": True,
                "posts_generated": len(social_posts)
            }
        
        # STAGE 5: Save to Database
        print("💾 Stage 5: Saving to database...")
        if db is not None:
            product_doc = product_data.copy()
            product_doc.pop('_id', None)
            product_doc['created_at'] = datetime.now(timezone.utc).isoformat()
            product_doc['launch_type'] = 'one_click'
            product_doc['gumroad_data'] = gumroad_result if gumroad_result.get("success") else None
            await db.products.insert_one(product_doc)
            results["stages"]["database"] = {"success": True}
        
        # STAGE 6: Generate Analytics Preview
        print("📊 Stage 6: Generating analytics preview...")
        results["analytics"] = {
            "estimated_monthly_revenue": round(product_data['price'] * random.randint(10, 50), 2),
            "target_audience_size": f"{random.randint(10, 100)}K",
            "competition_level": random.choice(["Low", "Medium", "High"]),
            "success_probability": f"{random.randint(60, 95)}%"
        }
        results["stages"]["analytics"] = {"success": True}
        
        results["success"] = True
        print("✅ Launch complete!")
        
        return results
        
    except Exception as e:
        results["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


# ============ REAL GUMROAD INTEGRATION ============

@api_router.get("/gumroad/products")
async def get_gumroad_products():
    """Get all products from your Gumroad account"""
    try:
        result = await gumroad_publisher.get_products()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/gumroad/sales")
async def get_gumroad_sales(product_id: Optional[str] = None):
    """Get sales data from Gumroad"""
    try:
        result = await gumroad_publisher.get_sales(product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/gumroad/publish")
async def publish_to_gumroad(product_id: str):
    """Publish an existing product to Gumroad"""
    try:
        # Get product from database
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Publish based on type
        if product.get("product_type") == "course":
            result = await gumroad_publisher.publish_course(product)
        else:
            result = await gumroad_publisher.publish_ebook(product)
        
        # Update product with Gumroad data
        if result.get("success"):
            await db.products.update_one(
                {"id": product_id},
                {"$set": {
                    "gumroad_data": result,
                    "status": "published",
                    "marketplace_links": [{
                        "platform": "Gumroad",
                        "url": result.get("url"),
                        "product_id": result.get("product_id"),
                        "status": "live"
                    }]
                }}
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ YOUTUBE SHORTS & SOCIAL AUTOMATION ============

class YouTubeShortsRequest(BaseModel):
    product_id: str
    num_scripts: int = 5

@api_router.post("/social/youtube-shorts")
async def generate_youtube_shorts(request: YouTubeShortsRequest):
    """Generate YouTube Shorts scripts for a product"""
    try:
        # Get product
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Generate shorts scripts
        shorts = []
        hooks = [
            "Stop scrolling! This changed my life...",
            "POV: You finally figured out...",
            "Nobody talks about this but...",
            "The secret to {topic} that nobody shares...",
            "I wish I knew this sooner about {topic}..."
        ]
        
        for i in range(request.num_scripts):
            hook = hooks[i % len(hooks)].format(topic=product.get('title', 'this'))
            shorts.append({
                "id": f"short-{uuid.uuid4().hex[:8]}",
                "product_id": request.product_id,
                "platform": "youtube_shorts",
                "hook": hook,
                "script": f"{hook}\n\nHere's what you need to know about {product.get('title', 'this topic')}:\n\n"
                         f"1. {product.get('description', 'Key insight 1')[:100]}...\n"
                         f"2. This will save you hours of trial and error\n"
                         f"3. Link in bio to get the full guide!\n\n"
                         f"#shorts #{product.get('product_type', 'ebook')} #productivity",
                "duration": "30-60 seconds",
                "call_to_action": "Link in bio!",
                "hashtags": ["#shorts", "#productivity", "#success", "#motivation"],
                "status": "ready",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        
        # Save to database
        if db is not None:
            for short in shorts:
                await db.social_content.insert_one(short)
        
        return {
            "success": True,
            "shorts_generated": len(shorts),
            "shorts": shorts
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SocialCampaignRequest(BaseModel):
    product_id: str
    platforms: List[str] = ["twitter", "instagram", "tiktok", "linkedin"]
    posts_per_platform: int = 3

@api_router.post("/social/campaign")
async def create_social_campaign(request: SocialCampaignRequest):
    """Create a full social media campaign for a product"""
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        campaign = {
            "id": f"campaign-{uuid.uuid4().hex[:8]}",
            "product_id": request.product_id,
            "product_title": product.get("title"),
            "platforms": {},
            "total_posts": 0,
            "status": "ready",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Generate posts for each platform
        for platform in request.platforms:
            posts = await social_media_ai.generate_posts(product, request.posts_per_platform)
            # Customize for platform
            for post in posts:
                post["platform"] = platform
                post["id"] = f"post-{uuid.uuid4().hex[:8]}"
            
            campaign["platforms"][platform] = posts
            campaign["total_posts"] += len(posts)
        
        # Save campaign
        if db is not None:
            await db.social_campaigns.insert_one(campaign)
        
        return {
            "success": True,
            "campaign": campaign
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/social/campaigns")
async def get_social_campaigns(product_id: Optional[str] = None):
    """Get all social media campaigns"""
    try:
        if db is None:
            return {"campaigns": [], "note": "Database not configured"}
        
        query = {}
        if product_id:
            query["product_id"] = product_id
        
        campaigns = await db.social_campaigns.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
        return {"success": True, "campaigns": campaigns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ REAL-TIME ANALYTICS & DASHBOARD ============

@api_router.get("/analytics/realtime")
async def get_realtime_analytics():
    """Get real-time analytics dashboard data"""
    try:
        analytics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "products": {"total": 0, "published": 0, "draft": 0},
            "revenue": {"total": 0, "today": 0, "this_week": 0, "this_month": 0},
            "traffic": {"clicks": 0, "conversions": 0, "conversion_rate": 0},
            "top_products": [],
            "gumroad": {"connected": False, "products": 0, "sales": 0}
        }
        
        if db is not None:
            # Product stats
            analytics["products"]["total"] = await db.products.count_documents({})
            analytics["products"]["published"] = await db.products.count_documents({"status": "published"})
            analytics["products"]["draft"] = await db.products.count_documents({"status": "draft"})
            
            # Revenue aggregation
            pipeline = [
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$revenue"},
                    "total_clicks": {"$sum": "$clicks"},
                    "total_conversions": {"$sum": "$conversions"}
                }}
            ]
            result = await db.products.aggregate(pipeline).to_list(1)
            if result:
                analytics["revenue"]["total"] = result[0].get("total_revenue", 0)
                analytics["traffic"]["clicks"] = result[0].get("total_clicks", 0)
                analytics["traffic"]["conversions"] = result[0].get("total_conversions", 0)
                if analytics["traffic"]["clicks"] > 0:
                    analytics["traffic"]["conversion_rate"] = round(
                        analytics["traffic"]["conversions"] / analytics["traffic"]["clicks"] * 100, 2
                    )
            
            # Top products
            top_products = await db.products.find(
                {}, {"_id": 0, "id": 1, "title": 1, "revenue": 1, "conversions": 1}
            ).sort("revenue", -1).limit(5).to_list(5)
            analytics["top_products"] = top_products
        
        # Check Gumroad connection
        gumroad_products = await gumroad_publisher.get_products()
        if gumroad_products.get("success"):
            analytics["gumroad"]["connected"] = True
            analytics["gumroad"]["products"] = len(gumroad_products.get("products", []))
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/revenue-breakdown")
async def get_revenue_breakdown():
    """Get detailed revenue breakdown by product and time"""
    try:
        breakdown = {
            "by_product_type": {},
            "by_marketplace": {},
            "daily_trend": [],
            "projections": {}
        }
        
        if db is not None:
            # By product type
            pipeline = [
                {"$group": {
                    "_id": "$product_type",
                    "revenue": {"$sum": "$revenue"},
                    "count": {"$sum": 1}
                }}
            ]
            by_type = await db.products.aggregate(pipeline).to_list(10)
            for item in by_type:
                breakdown["by_product_type"][item["_id"] or "unknown"] = {
                    "revenue": item["revenue"],
                    "count": item["count"]
                }
        
        # Generate projections
        total_revenue = sum(t.get("revenue", 0) for t in breakdown["by_product_type"].values())
        breakdown["projections"] = {
            "next_week": round(total_revenue * 1.1, 2),
            "next_month": round(total_revenue * 4.5, 2),
            "next_quarter": round(total_revenue * 15, 2)
        }
        
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SECURE KEY VAULT ============

@api_router.get("/vault/credentials")
async def list_credentials():
    """List all stored and available credential types"""
    try:
        return await key_vault.list_credentials()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/vault/credentials/{credential_type}")
async def get_credential_schema(credential_type: str):
    """Get the schema for a credential type"""
    return key_vault.get_credential_schema(credential_type)

class StoreCredentialsRequest(BaseModel):
    credential_type: str
    credentials: Dict[str, str]

@api_router.post("/vault/credentials")
async def store_credentials(request: StoreCredentialsRequest):
    """Store encrypted credentials"""
    try:
        return await key_vault.store_credentials(request.credential_type, request.credentials)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/vault/credentials/{credential_type}/test")
async def test_credentials(credential_type: str):
    """Test if credentials are working"""
    try:
        return await key_vault.test_credentials(credential_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/vault/credentials/{credential_type}")
async def delete_credentials(credential_type: str):
    """Delete stored credentials"""
    try:
        return await key_vault.delete_credentials(credential_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ OPPORTUNITY HUNTER ============

@api_router.post("/hunter/hunt")
async def hunt_opportunities():
    """Hunt for new income-generating opportunities"""
    try:
        return await opportunity_hunter.hunt_opportunities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/hunter/opportunities")
async def get_opportunities(status: Optional[str] = None, limit: int = 50):
    """Get all discovered opportunities"""
    try:
        opportunities = await opportunity_hunter.get_all_opportunities(status, limit)
        return {"success": True, "opportunities": opportunities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/hunter/team")
async def create_agent_team(opportunity_id: str):
    """Create a specialized agent team for an opportunity"""
    try:
        return await opportunity_hunter.create_agent_team(opportunity_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/hunter/teams")
async def get_agent_teams(status: Optional[str] = None):
    """Get all agent teams"""
    try:
        teams = await opportunity_hunter.get_agent_teams(status)
        return {"success": True, "teams": teams}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PRODUCT DISCOVERY ============

@api_router.post("/discovery/discover")
async def discover_products():
    """Discover all products from all connected platforms"""
    try:
        return await product_discovery.discover_products()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/discovery/summary")
async def get_product_summary():
    """Get summary of all products across platforms"""
    try:
        return await product_discovery.get_product_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PROJECT FILE MANAGER ============

@api_router.get("/projects")
async def list_projects():
    """List all projects"""
    try:
        projects = await project_manager.list_projects()
        return {"success": True, "projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project with all files"""
    try:
        return await project_manager.get_project(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/projects/{project_id}/create")
async def create_project_from_product(project_id: str):
    """Create a project folder for a product"""
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        product = await db.products.find_one({"id": project_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return await project_manager.create_project(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}/download")
async def download_project(project_id: str):
    """Download project as ZIP"""
    try:
        return await project_manager.download_project(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}/file")
async def get_project_file(project_id: str, path: str):
    """Get content of a specific file"""
    try:
        return await project_manager.get_file_content(project_id, path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        return await project_manager.delete_project(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PUBLISHING GUIDE ============

@api_router.get("/publishing/options/{product_type}")
async def get_publishing_options(product_type: str):
    """Get publishing options for a product type"""
    try:
        return publishing_guide.get_publishing_options(product_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/publishing/platforms")
async def get_all_platforms():
    """Get all publishing platforms"""
    try:
        return {"platforms": publishing_guide.get_all_platforms()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/publishing/guide/{platform_id}")
async def get_platform_guide(platform_id: str):
    """Get detailed guide for a platform"""
    try:
        return publishing_guide.get_platform_guide(platform_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ AI ASSISTANT ============

@api_router.get("/assistant/status")
async def get_assistant_status():
    """Get comprehensive status update from AI assistant"""
    try:
        return await ai_assistant.get_status_update()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assistant/publishing-guide/{product_id}")
async def get_product_publishing_guide(product_id: str):
    """Get publishing guide for a specific product"""
    try:
        return await ai_assistant.get_product_publishing_guide(product_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assistant/notifications")
async def get_notifications(unread_only: bool = False):
    """Get user notifications"""
    try:
        notifications = await ai_assistant.get_notifications(unread_only)
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/assistant/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    try:
        return await ai_assistant.mark_notification_read(notification_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assistant/quick-stats")
async def get_quick_stats():
    """Get quick stats for assistant widget"""
    try:
        return await ai_assistant.get_quick_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ TEAM ENGINE ============

@api_router.post("/teams/{team_id}/activate")
async def activate_team(team_id: str):
    """Activate a team and start working"""
    try:
        return await team_engine.activate_team(team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/teams/{team_id}/status")
async def get_team_status(team_id: str):
    """Get detailed team status"""
    try:
        return await team_engine.get_team_status(team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/teams/{team_id}/advance")
async def advance_team(team_id: str):
    """Advance team to next phase"""
    try:
        return await team_engine.advance_team(team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/teams/summary")
async def get_teams_summary():
    """Get summary of all teams"""
    try:
        return await team_engine.get_all_teams_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ APP DESCRIPTION ============

@api_router.get("/app/description")
async def get_app_description():
    """Get full description of what this app does"""
    return {
        "name": "CEO AI Empire",
        "tagline": "Your Autonomous AI Company That Builds, Launches & Sells Products 24/7",
        "version": "3.0",
        
        "what_it_does": {
            "summary": "CEO AI Empire is an autonomous system that uses AI agents to discover profitable opportunities, create digital products, publish them to marketplaces, and market them - all automatically.",
            
            "core_functions": [
                {
                    "name": "🎯 Opportunity Discovery",
                    "description": "AI agents continuously scan the market to find trending niches, underserved markets, and profitable opportunities across 6 categories: Digital Products, Content Creation, SaaS Tools, Affiliate Marketing, Automated Services, and Community Building."
                },
                {
                    "name": "📚 Product Creation",
                    "description": "Generate complete digital products automatically - eBooks, online courses, templates, planners, and more. AI writes content, creates outlines, and prepares everything for publishing."
                },
                {
                    "name": "🚀 One-Click Launch",
                    "description": "Launch products with a single click. The system scouts opportunities, generates the product, prepares marketplace listings, creates marketing content, and sets up social media posts."
                },
                {
                    "name": "👥 Agent Teams",
                    "description": "Create specialized AI teams for each opportunity. Teams include Research, Content, Marketing, and Analytics agents that work together to execute the full product lifecycle."
                },
                {
                    "name": "🛒 Multi-Platform Publishing",
                    "description": "Publish to 112+ platforms including Gumroad, Amazon KDP, Etsy, Shopify, Teachable, and more. Automated publishing where APIs allow, step-by-step guides for manual platforms."
                },
                {
                    "name": "📱 Social Media Automation",
                    "description": "Generate and schedule posts across Twitter, Instagram, TikTok, YouTube, LinkedIn, Facebook, and Pinterest. Create YouTube Shorts scripts and full social campaigns."
                },
                {
                    "name": "🔐 Secure Credential Vault",
                    "description": "Safely store API keys and credentials for all platforms with AES-256 encryption. Connect once, automate forever."
                },
                {
                    "name": "📁 Project File Management",
                    "description": "Every product gets an organized project folder. Download as ZIP, view files, copy content - everything neatly organized."
                },
                {
                    "name": "🤖 Atlas AI Assistant",
                    "description": "Personal AI assistant that keeps you updated on everything - alerts, recommendations, publishing guides, and status updates."
                },
                {
                    "name": "📊 Analytics & Revenue Tracking",
                    "description": "Track sales, conversions, revenue across all platforms. AI analyzes data and provides optimization recommendations."
                }
            ]
        },
        
        "how_it_works": {
            "step_1": {
                "title": "Discover Opportunities",
                "description": "Click 'Hunt Now' in Opportunity Hunter. AI scans 24 trending niches across 6 categories and returns the top opportunities with trend scores, competition levels, and revenue estimates."
            },
            "step_2": {
                "title": "Create Agent Team",
                "description": "Click 'Create Team' on any opportunity. A specialized team of 6-8 AI agents is assigned: Research Agent, Content Agent, Marketing Agent, Analytics Agent, plus category-specific agents."
            },
            "step_3": {
                "title": "Team Executes Work",
                "description": "The team works through phases: Research → Creation → Production → Launch → Promotion. Each agent completes tasks and produces outputs."
            },
            "step_4": {
                "title": "Launch Product",
                "description": "Use One-Click Launch or manual controls. The system generates the complete product, prepares listings, and creates marketing materials."
            },
            "step_5": {
                "title": "Publish Everywhere",
                "description": "Atlas tells you which platforms can be automated vs manual. For automated platforms, AI handles posting. For manual, you get step-by-step instructions with direct links."
            },
            "step_6": {
                "title": "Track & Optimize",
                "description": "Monitor sales and engagement across all platforms. AI provides revenue optimization recommendations and identifies what's working."
            }
        },
        
        "platforms_supported": {
            "total": 112,
            "categories": {
                "marketplaces": ["Gumroad", "Amazon KDP", "Etsy", "Shopify", "Teachable", "Udemy", "Payhip", "Ko-fi"],
                "social_media": ["Twitter/X", "Instagram", "TikTok", "YouTube", "LinkedIn", "Facebook", "Pinterest", "Reddit"],
                "email": ["Mailchimp", "ConvertKit", "SendGrid", "Beehiiv", "Substack"],
                "community": ["Discord", "Slack", "Telegram", "Circle", "Skool"],
                "payments": ["Stripe", "PayPal", "Lemon Squeezy", "Paddle"],
                "advertising": ["Google Ads", "Facebook Ads", "TikTok Ads"],
                "analytics": ["Google Analytics", "Mixpanel", "Amplitude"],
                "and_more": "100+ total platforms across all categories"
            }
        },
        
        "agent_team_roles": {
            "core_agents": [
                {"name": "Research Agent", "role": "Market research, competitor analysis, trend identification"},
                {"name": "Content Agent", "role": "Writing, content creation, copywriting"},
                {"name": "Marketing Agent", "role": "Campaign strategy, ad copy, social media"},
                {"name": "Analytics Agent", "role": "Data analysis, performance tracking, optimization"}
            ],
            "specialized_agents": [
                {"name": "Product Designer", "role": "Visual design, covers, graphics"},
                {"name": "Video Editor", "role": "Video content, YouTube, TikTok"},
                {"name": "SEO Agent", "role": "Search optimization, keywords"},
                {"name": "Community Manager", "role": "Engagement, member management"},
                {"name": "Developer Agent", "role": "Technical implementation (for SaaS)"}
            ]
        },
        
        "revenue_potential": {
            "digital_products": "$100 - $5,000/month per product",
            "courses": "$500 - $10,000/month",
            "saas_tools": "$1,000 - $50,000/month",
            "affiliate": "$200 - $5,000/month",
            "community": "$500 - $20,000/month (recurring)"
        },
        
        "getting_started": [
            "1. Click 'Opportunity Hunter' and hunt for opportunities",
            "2. Review opportunities and click 'Create Team' on the best ones",
            "3. Watch your teams work in the Teams tab",
            "4. Use 'Launch Product' to create and publish products",
            "5. Add credentials in 'Key Vault' for automated publishing",
            "6. Check 'Atlas AI' for updates and recommendations"
        ]
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint for deployment monitoring"""
    try:
        response = {
            "status": "healthy",
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Test MongoDB connection if available
        if db is not None:
            try:
                await db.admin.command('ping')
                response["database"] = "connected"
            except Exception as db_error:
                response["database"] = "disconnected"
                response["db_error"] = str(db_error)
        else:
            response["database"] = "not configured (demo mode)"
        
        return response
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, 503

# Include the router in the main app
app.include_router(api_router)
app.include_router(core_router, prefix="/api")

# Configure CORS
allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
if os.environ.get('ENVIRONMENT') != 'production':
    allowed_origins.append('*')

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
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
    if client:
        client.close()
