from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Header, Depends, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
import os
import logging
import io
import zipfile
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
# Force redeployment - learning system update
import uuid
import random
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import openai
import anthropic

# Import managers
from config.keys_manager import keys_manager

# Import AI services
from ai_services.multi_platform_manager import MultiPlatformManager, PlatformIntegration
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
from ai_services.learning_engine import LearningEngine
from ai_services.key_vault import SecureKeyVault
from ai_services.opportunity_hunter import OpportunityHunter, ProductDiscoveryEngine
from ai_services.project_manager import ProjectFileManager, PublishingGuide
from ai_services.ai_assistant import AIAssistant
from ai_services.team_engine import AgentTeamEngine
from ai_services.product_tiktok_integration import get_product_tiktok_integration
from ai_services.etsy_manager import get_etsy_manager
from ai_services.gemini_manager import get_gemini_manager, initialize_gemini
from ai_services.gemini_product_generator import get_gemini_generator
from ai_services.auth_utils import (
    create_access_token, decode_token, hash_password, verify_password,
    UserCreate, UserResponse, TokenResponse, require_auth
)
from ai_services.faceless_video_generator import FacelessVideoGenerator, get_faceless_video_generator
from ai_services.multi_platform_product_sync import MultiPlatformProductSync, get_product_sync_manager
from ai_services.youtube_data_api import YouTubeDataAPI, get_youtube_api
from ai_services.live_distribution_engine import get_live_distribution_engine
from ai_services.product_ranking_engine import ProductRankingEngine, get_product_ranking_engine
from ai_services.multi_platform_ad_manager import MultiPlatformAdCampaignManager, get_campaign_manager
from ai_services.revenue_attribution_engine import RevenueAttributionEngine
from ai_services.post_scheduler import PostScheduler, get_post_scheduler
from ai_services.quality_control import run_qc_check, ContentQualityControl
from ai_services.real_video_generator import get_real_video_generator

# Import core system
from core.routes_v5_production import router_v5
from core.routes_v5_production_new import router as router_v5_new, init_services
from core.routes_product_launch import router as router_product_launch
from core.routes_quality import router as router_quality
from core.routes_agents import router as router_agents
from core.routes_store import router as router_store, SAMPLE_PRODUCTS
from core.routes_intelligence import router as router_intelligence
from core.product_content import generate_product_files
from ai_services.product_cycle_scheduler import get_cycle_scheduler
from ai_services.agent_orchestrator import get_orchestrator

# Canonical production surfaces:
# - campaigns, branding, and storefront publishing: routes_product_launch
# - agent control and approval workflows: routes_agents
# - autonomous execution APIs: /api/autonomous/* in this module plus /api/v5


ROOT_DIR = Path(__file__).parent


def normalize_env_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned_value = value.strip()
    return cleaned_value or None


def iter_mongo_url_candidates():
    yield normalize_env_value(keys_manager.get_key('mongodb_url'))
    yield normalize_env_value(os.environ.get('MONGO_URI'))
    yield normalize_env_value(os.environ.get('MONGO_URL'))


def resolve_raw_mongo_url() -> Optional[str]:
    for candidate in iter_mongo_url_candidates():
        if candidate:
            return candidate
    return None


def is_supported_mongo_url(candidate: Optional[str]) -> bool:
    if not candidate:
        return False

    normalized_candidate = candidate.lower()
    unsupported_markers = [
        'atlas-sql-',
        '.query.mongodb.net'
    ]
    return not any(marker in normalized_candidate for marker in unsupported_markers)


def resolve_mongo_url() -> Optional[str]:
    for candidate in iter_mongo_url_candidates():
        if candidate and is_supported_mongo_url(candidate):
            return candidate
    return None


def resolve_db_name() -> str:
    return (
        normalize_env_value(os.environ.get('DB_NAME'))
        or normalize_env_value(os.environ.get('MONGO_DB_NAME'))
        or 'ceo_ai'
    )


load_dotenv(ROOT_DIR.parent / '.env')
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection - try to get from keys first, then env
raw_mongo_url = resolve_raw_mongo_url()
mongo_url = resolve_mongo_url()

db = None
client = None

if mongo_url:
    try:
        import certifi
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000, connectTimeoutMS=10000, tlsCAFile=certifi.where())
        # Verify connection works
        db_name = resolve_db_name()
        db = client[db_name]
        print(f"[OK] MongoDB connected to {db_name}")
    except Exception as e:
        print(f"[WARN] Could not connect to MongoDB immediately: {e}")
        print("[INFO] Will try to reconnect on first request...")
        db = None
        client = None
else:
    if raw_mongo_url:
        print("[WARN] Configured MongoDB URL points to an unsupported Atlas SQL/query endpoint. Persistent storage disabled.")
    else:
        print("[INFO] MongoDB URL not available. Persistent storage disabled.")


def is_database_query_error(error: Exception) -> bool:
    if isinstance(error, PyMongoError):
        return True

    message = str(error).lower()
    database_error_markers = [
        'authentication failed',
        'auth required',
        'unauthorized',
        'not authorized',
        'replicasetnoprimary',
        'no replica set members',
        'server selection timed out'
    ]
    return any(marker in message for marker in database_error_markers)


def raise_openai_http_error(error: Exception, service_name: str):
    if isinstance(error, openai.RateLimitError):
        raise HTTPException(
            status_code=429,
            detail=f"{service_name} quota exceeded or rate limited: {str(error)}"
        )

    if isinstance(error, openai.AuthenticationError):
        raise HTTPException(
            status_code=401,
            detail=f"{service_name} authentication failed: {str(error)}"
        )

    if isinstance(error, openai.PermissionDeniedError):
        raise HTTPException(
            status_code=403,
            detail=f"{service_name} permission denied: {str(error)}"
        )

    if isinstance(error, openai.BadRequestError):
        raise HTTPException(
            status_code=400,
            detail=f"{service_name} request rejected: {str(error)}"
        )

    raise HTTPException(status_code=502, detail=f"{service_name} API error: {str(error)}")

# Initialize AI services
opportunity_scout = OpportunityScout()
book_writer = BookWriter()
course_creator = CourseCreator()
product_generator = ProductGenerator()
micro_taskforce = MicroTaskforce(db) if db is not None else None
revenue_maximizer = RevenueMaximizer()
social_media_ai = SocialMediaAI()
multi_platform_manager = MultiPlatformManager()
sales_launch_ai = SalesLaunchAI()
affiliate_manager = AffiliateManager()
marketplace_integrations = MarketplaceIntegrations()
compliance_checker = ComplianceChecker()
analytics_engine = AnalyticsEngine(db)
learning_engine = LearningEngine(db) if db is not None else None
real_product_generator = RealProductGenerator()
gumroad_publisher = GumroadPublisher()
key_vault = SecureKeyVault(db)
opportunity_hunter = OpportunityHunter(db)
product_discovery = ProductDiscoveryEngine(db)
project_manager = ProjectFileManager(db)
publishing_guide = PublishingGuide()
ai_assistant = AIAssistant(db)
team_engine = AgentTeamEngine(db)

# NEW: Post Scheduler and Quality Control
post_scheduler = PostScheduler(db) if db is not None else None

# Autonomous engine (initialized after db)
autonomous_engine = None

# Scheduler will be initialized after db is ready
automation_scheduler = None

# Create the main app without a prefix
app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.state.db = db

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
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_QC = "pending_qc"
    GENERATED = "generated"
    DUPLICATE = "duplicate"

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
    subtitle: Optional[str] = None
    description: str
    benefits: List[str] = []
    includes: List[str] = []
    perfect_for: List[str] = []
    cta: Optional[str] = None
    product_type: ProductType = ProductType.TEMPLATE
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
    original_price: Optional[float] = None

class ProductCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: str
    benefits: List[str] = []
    includes: List[str] = []
    perfect_for: List[str] = []
    cta: Optional[str] = None
    product_type: ProductType
    content: Optional[str] = None
    cover_image: Optional[str] = None
    price: float = 9.99
    original_price: Optional[float] = None
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
    sendgrid_from_email: Optional[str] = None
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


# Authentication Routes
@api_router.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate):
    """Create a new user account"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        users_collection = db['users']
        
        # Check if user already exists
        existing = await users_collection.find_one({"email": user_data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user document
        user_doc = {
            "id": str(uuid.uuid4()),
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await users_collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        # Create token
        token = create_access_token(user_doc["id"], user_data.email)
        
        user_response = UserResponse(
            id=user_doc["id"],
            email=user_doc["email"],
            first_name=user_doc["first_name"],
            last_name=user_doc["last_name"],
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str


@api_router.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Login with email and password"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        users_collection = db['users']
        user_doc = await users_collection.find_one({"email": login_data.email})
        
        if not user_doc:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(login_data.password, user_doc["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_access_token(user_doc["id"], user_doc["email"])
        
        user_response = UserResponse(
            id=user_doc["id"],
            email=user_doc["email"],
            first_name=user_doc.get("first_name"),
            last_name=user_doc.get("last_name"),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current authenticated user - reads from Authorization header"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = parts[1]
        
        # Decode token
        payload = decode_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload.get("sub")
        
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        users_collection = db['users']
        user_doc = await users_collection.find_one({"id": user_id})
        
        if not user_doc:
            raise HTTPException(status_code=401, detail="User not found")
        
        return UserResponse(
            id=user_doc["id"],
            email=user_doc["email"],
            first_name=user_doc.get("first_name"),
            last_name=user_doc.get("last_name"),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@api_router.post("/auth/logout")
async def logout():
    """Logout (client-side token removal)"""
    return {"message": "Logged out successfully"}


# API Keys Management
@api_router.post("/keys/store", response_model=APIKeyResponse)
async def store_api_keys(keys: APIKeyInput, _auth: dict = Depends(require_auth)):
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
            global db, client, mongo_url
            try:
                new_mongo_url = keys_data['mongodb_url']
                if client is not None:
                    client.close()
                if is_supported_mongo_url(new_mongo_url):
                    import certifi
                    client = AsyncIOMotorClient(new_mongo_url, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
                    db = client[resolve_db_name()]
                    mongo_url = new_mongo_url
                    print("[OK] MongoDB reconnected with provided URL")
                else:
                    client = None
                    db = None
                    mongo_url = None
                    print("[WARN] MongoDB connection skipped: unsupported Atlas SQL/query endpoint")
            except Exception as e:
                print(f"[WARN] MongoDB connection failed: {e}")
            app.state.db = db
        
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
    current_mongo_url = resolve_raw_mongo_url() or mongo_url
    supported_mongo_url = resolve_mongo_url() or mongo_url
    key_names = [
        'openai_key',
        'anthropic_key',
        'dalle_key',
        'gemini_key',
        'sendgrid_key',
        'sendgrid_from_email',
        'mailchimp_key',
        'stripe_key',
        'stripe_webhook_secret',
        'gumroad_key',
        'gumroad_secret',
        'tiktok_api_key',
        'tiktok_api_secret',
        'instagram_graph_api_key',
        'twitter_api_key',
        'linkedin_api_key',
        'youtube_api_key',
        'elevenlabs_key',
        'pexels_key',
        'pixabay_key',
        'mongodb_url'
    ]
    status = {}
    
    for key_name in key_names:
        key_value = keys_manager.get_key(key_name)
        if key_name == 'mongodb_url' and not key_value:
            key_value = current_mongo_url
        status[key_name] = "[OK] Configured" if key_value else "[FAIL] Not configured"
    
    # Report database reachability separately from key storage.
    if current_mongo_url and not is_supported_mongo_url(current_mongo_url):
        status['database_connection'] = "[WARN] Unsupported connection string"
        status['mongodb_url'] = "[WARN] Configured, unsupported connection string"
    elif client is not None and supported_mongo_url:
        try:
            await client.admin.command('ping')
            status['database_connection'] = "[OK] Connected"
        except Exception:
            status['database_connection'] = "[WARN] Disconnected"
            status['mongodb_url'] = "[WARN] Configured, database disconnected"
    else:
        status['database_connection'] = "[INFO] Not connected yet"
    
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
        raise_openai_http_error(e, "OpenAI")
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
        raise_openai_http_error(e, "DALL-E")
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
async def generate_full_product(request: FullProductGenerationRequest, _auth: dict = Depends(require_auth)):
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
        if request.save_to_db and db is not None:
            try:
                product_doc = {
                    "id": str(uuid.uuid4()),
                    "title": product_response.title,
                    "description": product_response.description,
                    "product_type": "template",
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
        if db is None:
            return DashboardStats(
                total_products=0,
                products_today=0,
                total_revenue=0.0,
                revenue_today=0.0,
                pending_tasks=0,
                active_opportunities=0
            )
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
        if is_database_query_error(e):
            return DashboardStats(
                total_products=0,
                products_today=0,
                total_revenue=0.0,
                revenue_today=0.0,
                pending_tasks=0,
                active_opportunities=0
            )
        raise HTTPException(status_code=500, detail=str(e))


# Products CRUD
@api_router.post("/products", response_model=Product)
async def create_product(product_input: ProductCreate, _auth: dict = Depends(require_auth)):
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
        if db is None:
            return []

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
        if is_database_query_error(e):
            return []
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


# Product Marketing & Content Generation
@api_router.post("/products/{product_id}/generate-marketing")
async def generate_marketing_content(product_id: str):
    """Generate video scripts, hooks, and captions for a product"""
    try:
        # Fetch product from database
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        openai_key = await keys_manager.get_key('openai_key')
        if not openai_key:
            raise HTTPException(status_code=400, detail="OpenAI key not configured")
        
        client = openai.OpenAI(api_key=openai_key)
        
        # Generate marketing assets
        prompt = f"""
        For this digital product: "{product['title']}"
        Description: {product['description']}
        
        Generate engaging marketing content:
        1. Three 15-second video scripts (for TikTok, Instagram Reels, YouTube Shorts)
        2. Five attention-grabbing hooks
        3. Three social media captions (Instagram, Twitter, LinkedIn)
        4. Two strong call-to-action statements
        
        Format as JSON with keys: video_scripts, hooks, captions, ctas
        Make it compelling and conversion-focused.
        """
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        import json
        try:
            content = json.loads(response.choices[0].message.content)
        except:
            content = {
                "video_scripts": [],
                "hooks": [],
                "captions": [],
                "ctas": []
            }
        
        return {
            "product_id": product_id,
            "product_title": product['title'],
            "videoScripts": content.get("video_scripts", []),
            "hooks": content.get("hooks", []),
            "captions": content.get("captions", []),
            "ctas": content.get("ctas", []),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate marketing content: {str(e)}")


@api_router.post("/products/{product_id}/generate-email")
async def generate_email_campaign(product_id: str):
    """Generate email campaign sequence for a product"""
    try:
        # Fetch product from database
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        openai_key = await keys_manager.get_key('openai_key')
        if not openai_key:
            raise HTTPException(status_code=400, detail="OpenAI key not configured")
        
        client = openai.OpenAI(api_key=openai_key)
        
        # Generate email campaign
        prompt = f"""
        For this digital product: "{product['title']}"
        Description: {product['description']}
        
        Create a 5-email sales sequence:
        Email 1: Problem Awareness (subject line + body)
        Email 2: Deeper Pain (subject line + body)
        Email 3: Solution Introduction (subject line + body)
        Email 4: Social Proof (subject line + body, with testimonial if applicable)
        Email 5: Final CTA & Urgency (subject line + body)
        
        Format as JSON with keys: emails (array of objects with subject, body, day_to_send)
        Make it persuasive and conversion-focused.
        """
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        import json
        try:
            content = json.loads(response.choices[0].message.content)
        except:
            content = {"emails": []}
        
        return {
            "product_id": product_id,
            "product_title": product['title'],
            "emailSequence": content.get("emails", []),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate email campaign: {str(e)}")


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
        if db is None:
            return []

        opportunities = await db.opportunities.find({}, {"_id": 0}).sort("trend_score", -1).limit(limit).to_list(limit)
        
        for opp in opportunities:
            if isinstance(opp['created_at'], str):
                opp['created_at'] = datetime.fromisoformat(opp['created_at'])
        
        return opportunities
    except Exception as e:
        if is_database_query_error(e):
            return []
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
async def scout_opportunities(_auth: dict = Depends(require_auth)):
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
async def generate_book(request: GenerateBookRequest, _auth: dict = Depends(require_auth)):
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
async def generate_course(request: GenerateCourseRequest, _auth: dict = Depends(require_auth)):
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
async def generate_social_posts(request: GenerateSocialPostsRequest, _auth: dict = Depends(require_auth)):
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
async def create_launch_campaign(request: CreateLaunchCampaignRequest, _auth: dict = Depends(require_auth)):
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
async def generate_affiliate_program(_auth: dict = Depends(require_auth)):
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
        if db is None:
            return []

        query = {}
        if product_id:
            query["product_id"] = product_id
        
        posts = await db.social_media_posts.find(query, {"_id": 0}).sort("scheduled_time", -1).limit(limit).to_list(limit)
        return posts
    except Exception as e:
        if is_database_query_error(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/marketing/launch-campaigns")
async def get_launch_campaigns(product_id: Optional[str] = None):
    """Get launch campaigns"""
    try:
        if db is None:
            return []

        query = {}
        if product_id:
            query["product_id"] = product_id
        
        campaigns = await db.launch_campaigns.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
        return campaigns
    except Exception as e:
        if is_database_query_error(e):
            return []
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
        if db is None:
            return {
                "success": True,
                "insights": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "product_performance": {
                        "top_performers": [],
                        "underperformers": [],
                        "rising_stars": [],
                        "average_metrics": {}
                    },
                    "revenue_forecast": {
                        "current_month": 0,
                        "next_month": 0,
                        "next_quarter": 0,
                        "next_year": 0,
                        "growth_rate": 0,
                        "confidence": "low",
                        "assumptions": ["Database not available"]
                    },
                    "opportunity_analysis": {"status": "no_data"},
                    "recommendations": [],
                    "kpis": {
                        "total_revenue": 0,
                        "total_conversions": 0,
                        "conversion_rate": 0,
                        "average_order_value": 0,
                        "total_products": 0,
                        "products_published": 0
                    }
                }
            }

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
        if is_database_query_error(e):
            return {
                "success": True,
                "insights": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "product_performance": {
                        "top_performers": [],
                        "underperformers": [],
                        "rising_stars": [],
                        "average_metrics": {}
                    },
                    "revenue_forecast": {
                        "current_month": 0,
                        "next_month": 0,
                        "next_quarter": 0,
                        "next_year": 0,
                        "growth_rate": 0,
                        "confidence": "low",
                        "assumptions": ["Database authentication failed"]
                    },
                    "opportunity_analysis": {"status": "no_data"},
                    "recommendations": [],
                    "kpis": {
                        "total_revenue": 0,
                        "total_conversions": 0,
                        "conversion_rate": 0,
                        "average_order_value": 0,
                        "total_products": 0,
                        "products_published": 0
                    }
                }
            }
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/system/health")
async def get_system_health():
    """Get system health status"""
    try:
        current_mongo_url = resolve_raw_mongo_url() or mongo_url
        supported_mongo_url = resolve_mongo_url() or mongo_url
        database_status = "connected" if db is not None else "unavailable"
        if current_mongo_url and not is_supported_mongo_url(current_mongo_url):
            database_status = "misconfigured"

        # Check all systems
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "database": database_status,
                "ai_teams": "operational",
                "automation": "operational",
                "marketplaces": "operational"
            }
        }
        
        # Only count documents if database is available
        if current_mongo_url and not is_supported_mongo_url(current_mongo_url):
            health["status"] = "degraded"
            health["stats"] = {
                "mode": "degraded",
                "note": "Configured MongoDB URL points to an unsupported Atlas SQL/query endpoint"
            }
        elif db is not None and supported_mongo_url:
            try:
                health["stats"] = {
                    "total_products": await db.products.count_documents({}),
                    "total_opportunities": await db.opportunities.count_documents({}),
                    "pending_tasks": await db.ai_tasks.count_documents({"status": "pending"}),
                    "marketplace_listings": await db.marketplace_listings.count_documents({})
                }
            except Exception as db_error:
                if not is_database_query_error(db_error):
                    raise

                health["status"] = "degraded"
                health["services"]["database"] = "disconnected"
                health["db_error"] = str(db_error)
                health["stats"] = {
                    "total_products": 0,
                    "total_opportunities": 0,
                    "pending_tasks": 0,
                    "marketplace_listings": 0
                }
        else:
            health["status"] = "degraded"
            health["stats"] = {"mode": "degraded", "note": "No persistent storage configured"}
        
        return health
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ============ AUTONOMOUS ENGINE ============

@api_router.post("/autonomous/run-cycle")
async def run_autonomous_cycle(_auth: dict = Depends(require_auth)):
    """
    Run ONE complete autonomous cycle:
    Scout → Generate REAL product → Compliance → Publish → Market → Track
    
    Returns complete product with files and marketplace links
    """
    try:
        global autonomous_engine
        if not autonomous_engine:
            autonomous_engine = AutonomousEngine(db)
        
        print("\n[START] Starting autonomous product cycle...")
        results = await autonomous_engine.run_autonomous_product_cycle()
        
        return {
            "success": results["status"] == "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/autonomous/start-continuous")
async def start_continuous_mode(products_per_day: int = 3, background_tasks: BackgroundTasks = None, _auth: dict = Depends(require_auth)):
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
async def launch_product_one_click(request: LaunchProductRequest, _auth: dict = Depends(require_auth)):
    """
    ONE-CLICK LAUNCH: Full Autonomous Cycle
    
    Scout -> Generate -> Publish to Gumroad -> Create Marketing -> Track Analytics
    
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
            print("[SCOUT] Stage 1: Scouting opportunities...")
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
        print(f"[GEN] Stage 2: Generating {request.product_type} for '{niche}'...")
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
            print("[PUB] Stage 3: Publishing to Gumroad...")
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
            print("[SOCIAL] Stage 4: Generating social media content...")
            social_posts = await social_media_ai.generate_posts(product_data, num_posts=5)
            results["social_posts"] = social_posts
            results["stages"]["social"] = {
                "success": True,
                "posts_generated": len(social_posts)
            }
        
        # STAGE 5: Save to Database
        print("[DB] Stage 5: Saving to database...")
        if db is not None:
            product_doc = product_data.copy()
            product_doc.pop('_id', None)
            product_doc['created_at'] = datetime.now(timezone.utc).isoformat()
            product_doc['launch_type'] = 'one_click'
            product_doc['gumroad_data'] = gumroad_result if gumroad_result.get("success") else None
            await db.products.insert_one(product_doc)
            results["stages"]["database"] = {"success": True}
        
        # STAGE 6: Generate Analytics Preview
        print("[ANALYTICS] Stage 6: Generating analytics preview...")
        results["analytics"] = {
            "estimated_monthly_revenue": round(product_data['price'] * random.randint(10, 50), 2),
            "target_audience_size": f"{random.randint(10, 100)}K",
            "competition_level": random.choice(["Low", "Medium", "High"]),
            "success_probability": f"{random.randint(60, 95)}%"
        }
        results["stages"]["analytics"] = {"success": True}
        
        results["success"] = True
        print("[OK] Launch complete!")
        
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
async def publish_to_gumroad(product_id: str, _auth: dict = Depends(require_auth)):
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
                    "gumroad_id": result.get("gumroad_id"),
                    "gumroad_url": result.get("url"),
                    "status": "published",
                    "marketplace_links": [{
                        "platform": "Gumroad",
                        "url": result.get("url"),
                        "product_id": result.get("gumroad_id"),
                        "status": "live"
                    }]
                }}
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ GUMROAD COMPREHENSIVE ENDPOINTS ============

@api_router.get("/gumroad/status")
async def get_gumroad_status():
    """Get Gumroad connection status and account info"""
    try:
        result = await gumroad_publisher.get_account_info()
        return {
            "status": "connected" if result else "disconnected",
            "account": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@api_router.post("/gumroad/create-product")
async def create_gumroad_product(
    product_data: Dict[str, Any]
):
    """Create a brand new product on Gumroad"""
    try:
        result = await gumroad_publisher.create_product(product_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/gumroad/{gumroad_product_id}/update")
async def update_gumroad_product(
    gumroad_product_id: str,
    updates: Dict[str, Any]
):
    """Update an existing Gumroad product"""
    try:
        result = await gumroad_publisher.update_product(gumroad_product_id, updates)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/gumroad/{gumroad_product_id}")
async def delete_gumroad_product(gumroad_product_id: str):
    """Delete a Gumroad product"""
    try:
        result = await gumroad_publisher.delete_product(gumroad_product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/gumroad/{gumroad_product_id}")
async def get_gumroad_product_details(gumroad_product_id: str):
    """Get detailed information about a Gumroad product"""
    try:
        result = await gumroad_publisher.get_product_details(gumroad_product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/gumroad/{gumroad_product_id}/upload-file")
async def upload_file_to_gumroad(
    gumroad_product_id: str,
    file_path: str,
    file_name: Optional[str] = None
):
    """Upload a digital file to a Gumroad product"""
    try:
        result = await gumroad_publisher.upload_product_file(
            gumroad_product_id,
            file_path,
            file_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/gumroad/{gumroad_product_id}/analytics")
async def get_gumroad_product_analytics(
    gumroad_product_id: str,
    period: str = "30_days"
):
    """Get analytics for a Gumroad product"""
    try:
        result = await gumroad_publisher.get_product_analytics(
            gumroad_product_id,
            period
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/gumroad/analytics/summary")
async def get_gumroad_analytics_summary():
    """Get overall Gumroad account analytics"""
    try:
        result = await gumroad_publisher.get_account_analytics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/gumroad/{gumroad_product_id}/variant")
async def create_product_variant(
    gumroad_product_id: str,
    variant_data: Dict[str, Any]
):
    """Create a product variant (license tier, option, etc)"""
    try:
        result = await gumroad_publisher.create_variant(
            gumroad_product_id,
            variant_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/gumroad/{gumroad_product_id}/license")
async def get_license_info(gumroad_product_id: str):
    """Get license info for a Gumroad product"""
    try:
        result = await gumroad_publisher.get_license_info(gumroad_product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/gumroad/{product_id}/sync-from-app")
async def sync_product_to_gumroad(product_id: str):
    """Sync a product from this app to Gumroad (from local database)"""
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        # Fetch product from local DB
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # If product already on Gumroad, update it
        if product.get("gumroad_id"):
            result = await gumroad_publisher.update_product(
                product.get("gumroad_id"),
                product
            )
        else:
            # Create new Gumroad product
            result = await gumroad_publisher.create_product(product)
            
            # Update local DB with Gumroad ID
            if result.get("success"):
                await db.products.update_one(
                    {"id": product_id},
                    {"$set": {"gumroad_id": result.get("gumroad_product_id")}}
                )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products/{product_id}/publish-all-platforms")
async def publish_product_all_platforms(
    product_id: str,
    platforms: List[str] = ["gumroad", "tiktok"]
):
    """Publish a product to multiple platforms simultaneously"""
    try:
        results = {}
        product_data = {}
        
        # Get product from DB if available
        if db is not None:
            db_product = await db.products.find_one({"id": product_id}, {"_id": 0})
            if db_product:
                product_data = db_product
        
        # Publish to each platform
        if "gumroad" in platforms:
            results["gumroad"] = await gumroad_publisher.create_product(product_data)
        
        if "tiktok" in platforms:
            integration = get_product_tiktok_integration()
            results["tiktok"] = await integration.post_product_series_to_tiktok(product_data, series_count=5)
        
        if "etsy" in platforms:
            etsy_manager = get_etsy_manager()
            results["etsy"] = await etsy_manager.create_listing(product_data)
        
        return {
            "status": "success",
            "product_id": product_id,
            "platforms_published": list(results.keys()),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
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
                short_doc = short.copy()
                short_doc.pop('_id', None)
                await db.social_content.insert_one(short_doc)
        
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
            try:
                campaign_doc = campaign.copy()
                campaign_doc.pop('_id', None)
                await db.social_campaigns.insert_one(campaign_doc)
            except Exception as db_error:
                if not is_database_query_error(db_error):
                    raise
        
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
        if is_database_query_error(e):
            return {"success": True, "campaigns": [], "note": "Database unavailable"}
        raise HTTPException(status_code=500, detail=str(e))


# ============ MULTI-PLATFORM SOCIAL MEDIA ENDPOINTS ============

class GenerateMultiPlatformPostsRequest(BaseModel):
    content: str = Field(..., description="Content to repurpose for all platforms")
    product_id: Optional[str] = None
    product_info: Optional[Dict[str, Any]] = None
    num_variations: int = 5

@api_router.post("/social/generate-multi-platform")
async def generate_multi_platform_posts(request: GenerateMultiPlatformPostsRequest):
    """Generate platform-specific posts from single content"""
    try:
        # Get product info if product_id provided
        product_info = request.product_info or {}
        if request.product_id and db is not None:
            product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
            if product:
                product_info = {
                    "title": product.get("title"),
                    "description": product.get("description"),
                    "price": product.get("price"),
                    "keywords": product.get("keywords", [])
                }
        
        # Generate posts for all platforms
        posts_by_platform = await multi_platform_manager.generate_posts_for_all_platforms(
            content=request.content,
            product_info=product_info,
            num_variations=request.num_variations
        )
        
        return {
            "success": True,
            "posts_by_platform": posts_by_platform,
            "total_posts": sum(len(posts) for posts in posts_by_platform.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ScheduleMultiPlatformRequest(BaseModel):
    posts_by_platform: Dict[str, List[Dict[str, Any]]]
    start_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    interval_hours: int = 24

@api_router.post("/social/schedule-multi-platform")
async def schedule_multi_platform_posts(request: ScheduleMultiPlatformRequest):
    """Schedule posts across all platforms"""
    try:
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        
        scheduled = await multi_platform_manager.schedule_posts(
            posts_by_platform=request.posts_by_platform,
            start_date=start_date,
            interval_hours=request.interval_hours
        )
        
        # Store in database if available
        if db is not None:
            schedule_doc = {
                "id": f"schedule-{uuid.uuid4().hex[:8]}",
                "scheduled_posts": scheduled["schedule"],
                "total_posts": scheduled["total_posts"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "scheduled"
            }
            try:
                await db.social_schedules.insert_one(schedule_doc)
            except Exception as db_error:
                if not is_database_query_error(db_error):
                    raise
        
        return {
            "success": True,
            "scheduled": scheduled
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/social/analytics")
async def get_social_analytics(platform: Optional[str] = None):
    """Get social media analytics"""
    try:
        analytics = await multi_platform_manager.get_social_analytics(platform)
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/social/post-tiktok")
async def post_to_tiktok(content: Dict[str, Any]):
    """Post to TikTok (requires API key)"""
    try:
        api_key = keys_manager.get_key('tiktok_api_key')
        if not api_key:
            raise HTTPException(status_code=400, detail="TikTok API key not configured")
        
        result = await PlatformIntegration.post_to_tiktok(content, api_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/social/post-instagram")
async def post_to_instagram(content: Dict[str, Any], _auth: dict = Depends(require_auth)):
    """Post to Instagram (requires Graph API key)"""
    try:
        api_key = keys_manager.get_key('instagram_graph_api_key')
        if not api_key:
            raise HTTPException(status_code=400, detail="Instagram Graph API key not configured")
        
        result = await PlatformIntegration.post_to_instagram(content, api_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/social/post-twitter")
async def post_to_twitter(content: Dict[str, Any], _auth: dict = Depends(require_auth)):
    """Post to Twitter/X (requires API v2 keys)"""
    try:
        api_key = keys_manager.get_key('twitter_api_key')
        if not api_key:
            raise HTTPException(status_code=400, detail="Twitter API key not configured")
        
        result = await PlatformIntegration.post_to_twitter(content, api_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/social/post-linkedin")
async def post_to_linkedin(content: Dict[str, Any], _auth: dict = Depends(require_auth)):
    """Post to LinkedIn (requires Share API key)"""
    try:
        api_key = keys_manager.get_key('linkedin_api_key')
        if not api_key:
            raise HTTPException(status_code=400, detail="LinkedIn API key not configured")
        
        result = await PlatformIntegration.post_to_linkedin(content, api_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/social/post-youtube")
async def post_to_youtube(content: Dict[str, Any], _auth: dict = Depends(require_auth)):
    """Post to YouTube (requires YouTube Data API key)"""
    try:
        api_key = keys_manager.get_key('youtube_api_key')
        if not api_key:
            raise HTTPException(status_code=400, detail="YouTube API key not configured")
        
        result = await PlatformIntegration.post_to_youtube(content, api_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TikTok-specific operations

@api_router.post("/social/tiktok/edit")
async def edit_tiktok_video(video_id: str, updates: Dict[str, Any]):
    """Edit an existing TikTok video"""
    try:
        result = await PlatformIntegration.edit_tiktok_video(video_id, updates)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/social/tiktok/schedule")
async def schedule_tiktok_post(content: Dict[str, Any], schedule_time: str):
    """Schedule a TikTok post for a future time"""
    try:
        result = await PlatformIntegration.schedule_tiktok_post(content, schedule_time)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/social/tiktok/{video_id}")
async def delete_tiktok_video(video_id: str):
    """Delete a TikTok video"""
    try:
        result = await PlatformIntegration.delete_tiktok_video(video_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/social/tiktok/analytics/{video_id}")
async def get_tiktok_video_analytics(video_id: str):
    """Get analytics for a specific TikTok video"""
    try:
        result = await PlatformIntegration.get_tiktok_video_analytics(video_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/social/tiktok/analytics/channel/summary")
async def get_tiktok_channel_analytics(period_days: int = 30):
    """Get overall TikTok channel analytics"""
    try:
        result = await PlatformIntegration.get_tiktok_channel_analytics(period_days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/social/tiktok/comments/{video_id}")
async def moderate_tiktok_comments(video_id: str, action: str = "get"):
    """Moderate comments on a TikTok video (get, delete, hide, pin, report)"""
    try:
        result = await PlatformIntegration.moderate_tiktok_comments(video_id, action)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/social/tiktok/trending/sounds")
async def get_tiktok_trending_sounds(limit: int = 10):
    """Get trending TikTok sounds for content creation"""
    try:
        result = await PlatformIntegration.get_tiktok_trending_sounds()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/social/tiktok/trending/hashtags")
async def get_tiktok_trending_hashtags(limit: int = 10):
    """Get trending TikTok hashtags for content creation"""
    try:
        result = await PlatformIntegration.get_tiktok_trending_hashtags()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Product + TikTok Integration ====================

@api_router.post("/products/{product_id}/post-tiktok")
async def post_product_to_tiktok(
    product_id: str,
    product_data: Dict[str, Any],
    video_file: Optional[str] = None,
    auto_generate_caption: bool = True
):
    """Post a created product to TikTok"""
    try:
        integration = get_product_tiktok_integration()
        result = await integration.post_product_to_tiktok(
            product_data,
            video_file=video_file,
            auto_generate_caption=auto_generate_caption
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products/{product_id}/post-tiktok-series")
async def post_product_series_to_tiktok(
    product_id: str,
    product_data: Dict[str, Any],
    series_count: int = 5
):
    """Post a series of videos for a product (5-10 videos)"""
    try:
        integration = get_product_tiktok_integration()
        result = await integration.post_product_series_to_tiktok(
            product_data,
            series_count=series_count
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products/{product_id}/schedule-tiktok")
async def schedule_product_tiktok_posts(
    product_id: str,
    product_data: Dict[str, Any],
    schedule_dates: List[str]
):
    """Schedule product posts to TikTok for specific dates"""
    try:
        integration = get_product_tiktok_integration()
        result = await integration.schedule_product_posts(
            product_data,
            schedule_dates
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Etsy Integration ====================

@api_router.post("/products/{product_id}/post-etsy")
async def create_etsy_listing(
    product_id: str,
    product_data: Dict[str, Any]
):
    """Create an Etsy listing from a product"""
    try:
        etsy = get_etsy_manager()
        result = await etsy.create_listing(product_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/etsy/listing/{listing_id}/update")
async def update_etsy_listing(
    listing_id: str,
    updates: Dict[str, Any]
):
    """Update an Etsy listing"""
    try:
        etsy = get_etsy_manager()
        result = await etsy.update_listing(listing_id, updates)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/etsy/listing/{listing_id}")
async def delete_etsy_listing(listing_id: str):
    """Delete an Etsy listing"""
    try:
        etsy = get_etsy_manager()
        result = await etsy.delete_listing(listing_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/etsy/listing/{listing_id}/analytics")
async def get_etsy_listing_analytics(listing_id: str):
    """Get analytics for an Etsy listing"""
    try:
        etsy = get_etsy_manager()
        result = await etsy.get_listing_analytics(listing_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/etsy/analytics/shop")
async def get_etsy_shop_analytics(period_days: int = 30):
    """Get shop-wide Etsy analytics"""
    try:
        etsy = get_etsy_manager()
        result = await etsy.get_shop_analytics(period_days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/etsy/inventory/{listing_id}")
async def update_etsy_inventory(
    listing_id: str,
    quantity: int
):
    """Update Etsy listing inventory"""
    try:
        etsy = get_etsy_manager()
        result = await etsy.manage_inventory(listing_id, quantity)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/etsy/listings")
async def list_etsy_shop_listings(limit: int = 20):
    """List all Etsy shop listings"""
    try:
        etsy = get_etsy_manager()
        result = await etsy.list_shop_listings(limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/etsy/categories/trending")
async def get_etsy_trending_categories():
    """Get trending Etsy categories"""
    try:
        etsy = get_etsy_manager()
        result = await etsy.get_trending_categories()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Gemini/Google AI Integration ====================

@api_router.get("/ai/gemini/status")
async def get_gemini_status():
    """Get Gemini API status"""
    try:
        gemini = get_gemini_manager()
        return gemini.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/ai/gemini/generate")
async def generate_with_gemini(
    prompt: str,
    model: str = "gemini-pro",
    temperature: float = 0.7,
    max_tokens: int = 2048
):
    """Generate content using Gemini"""
    try:
        gemini = get_gemini_manager()
        result = await gemini.generate_content(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return {
            "status": "success" if result else "error",
            "content": result,
            "model": model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products/{product_id}/generate-etsy-description")
async def generate_etsy_product_description(
    product_id: str,
    product_data: Dict[str, Any]
):
    """Generate Etsy product description using Gemini"""
    try:
        gemini = get_gemini_manager()
        description = await gemini.generate_product_description(product_data)
        return {
            "status": "success" if description else "error",
            "description": description,
            "product_id": product_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products/{product_id}/generate-etsy-tags")
async def generate_etsy_tags(
    product_id: str,
    product_data: Dict[str, Any]
):
    """Generate Etsy search tags using Gemini"""
    try:
        gemini = get_gemini_manager()
        tags = await gemini.generate_etsy_tags(product_data)
        return {
            "status": "success" if tags else "error",
            "tags": tags or [],
            "tag_count": len(tags) if tags else 0,
            "product_id": product_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products/generate-etsy-title")
async def generate_etsy_title(
    product_type: str,
    key_features: List[str],
    target_keywords: List[str] = []
):
    """Generate SEO-optimized Etsy title using Gemini"""
    try:
        gemini = get_gemini_manager()
        title = await gemini.generate_product_title(
            product_type,
            key_features,
            target_keywords
        )
        return {
            "status": "success" if title else "error",
            "title": title,
            "character_count": len(title) if title else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/social/platforms")
async def get_all_social_platforms():
    """Get list of all supported social media platforms with details"""
    try:
        platforms_info = await multi_platform_manager.get_social_analytics()
        return {
            "success": True,
             "platforms": {
                "tiktok": {
                    "name": "TikTok",
                    "icon": "🎵",
                    "description": "Short-form video platform",
                    "best_time": "6-10 PM",
                    "content_length": "15-60 seconds",
                    "features": ["trending_sounds", "hashtag_challenge", "duets", "stitches"]
                },
                "instagram": {
                    "name": "Instagram",
                    "icon": "📸",
                    "description": "Photo and video sharing",
                    "best_time": "11 AM-1 PM, 7-9 PM",
                    "content_length": "3s-60m for Reels",
                    "features": ["carousel", "reels", "stories", "igtv"]
                },
                "twitter": {
                    "name": "Twitter/X",
                    "icon": "𝕏",
                    "description": "Real-time conversations",
                    "best_time": "8-10 AM, 5-7 PM",
                    "content_length": "280 characters",
                    "features": ["threads", "spaces", "live", "polls"]
                },
                "linkedin": {
                    "name": "LinkedIn",
                    "icon": "[WORK]",
                    "description": "Professional network",
                    "best_time": "8-10 AM, 12-2 PM",
                    "content_length": "3000 characters",
                    "features": ["articles", "video", "document", "carousel"]
                },
                "youtube": {
                    "name": "YouTube",
                    "icon": "▶️",
                    "description": "Video hosting platform",
                    "best_time": "2-4 PM",
                    "content_length": "15-60s for Shorts, unlimited for videos",
                    "features": ["shorts", "videos", "premieres", "streams"]
                }
            }
        }
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
            try:
                analytics["products"]["total"] = await db.products.count_documents({})
                analytics["products"]["published"] = await db.products.count_documents({"status": "published"})
                analytics["products"]["draft"] = await db.products.count_documents({"status": "draft"})
                
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
                
                top_products = await db.products.find(
                    {}, {"_id": 0, "id": 1, "title": 1, "revenue": 1, "conversions": 1}
                ).sort("revenue", -1).limit(5).to_list(5)
                analytics["top_products"] = top_products
            except Exception as db_error:
                if not is_database_query_error(db_error):
                    raise
                analytics["database_status"] = "disconnected"
        
        try:
            gumroad_products = await gumroad_publisher.get_products()
            if gumroad_products.get("success"):
                analytics["gumroad"]["connected"] = True
                analytics["gumroad"]["products"] = len(gumroad_products.get("products", []))
        except Exception:
            analytics["gumroad"]["connected"] = False
        
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
            try:
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
            except Exception as db_error:
                if not is_database_query_error(db_error):
                    raise
                breakdown["database_status"] = "disconnected"
        
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


# ============ QUALITY CHECKLIST ============

QUALITY_CHECKLIST = [
    # Category: Content
    {"id": "title_set",        "category": "Content",    "label": "Title is clear and compelling",        "required": True},
    {"id": "description_written", "category": "Content", "label": "Description is detailed (150+ words)", "required": True},
    {"id": "price_set",        "category": "Content",    "label": "Price is set",                         "required": True},
    {"id": "cover_created",    "category": "Content",    "label": "Cover / thumbnail image created",      "required": True},
    # Category: Product files
    {"id": "files_generated",  "category": "Files",      "label": "Product files generated",              "required": True},
    {"id": "files_reviewed",   "category": "Files",      "label": "Files manually reviewed for quality",  "required": True},
    {"id": "no_placeholder",   "category": "Files",      "label": "No placeholder / lorem ipsum content", "required": True},
    # Category: Marketing
    {"id": "email_sequence",   "category": "Marketing",  "label": "Email sequence created (5+ emails)",   "required": True},
    {"id": "social_posts",     "category": "Marketing",  "label": "3+ social media posts drafted",        "required": True},
    {"id": "sales_copy",       "category": "Marketing",  "label": "Sales page / landing copy written",    "required": True},
    {"id": "keywords_researched", "category": "Marketing", "label": "Keywords / tags researched",         "required": False},
    # Category: Launch
    {"id": "platform_listing", "category": "Launch",     "label": "Listed on at least 1 sales platform",  "required": True},
    {"id": "payment_tested",   "category": "Launch",     "label": "Checkout / payment link tested",       "required": True},
    {"id": "delivery_confirmed", "category": "Launch",   "label": "Delivery & download confirmed working", "required": True},
    {"id": "legal_reviewed",   "category": "Launch",     "label": "Refund policy / legal terms included", "required": False},
]

REQUIRED_IDS = {c["id"] for c in QUALITY_CHECKLIST if c["required"]}
MIN_SCORE_TO_PUBLISH = 80  # percent

@api_router.get("/projects/{project_id}/checklist")
async def get_checklist(project_id: str):
    """Get quality checklist state for a project"""
    try:
        if db is None:
            return {"items": QUALITY_CHECKLIST, "checked": [], "score": 0, "ready": False}
        doc = await db.project_checklists.find_one({"project_id": project_id}, {"_id": 0})
        checked = doc.get("checked", []) if doc else []
        # Auto-detect from product data
        product = await db.products.find_one({"id": project_id}, {"_id": 0})
        if product:
            auto = []
            if product.get("title"):          auto.append("title_set")
            if len(product.get("description", "")) >= 150: auto.append("description_written")
            if product.get("price"):          auto.append("price_set")
            if product.get("cover_image"):    auto.append("cover_created")
            if product.get("files") or product.get("content"): auto.append("files_generated")
            if product.get("checkout_url") or product.get("gumroad_url"): auto.append("platform_listing")
            # Merge auto-detected with manually checked
            checked = list(set(checked) | set(auto))
        total = len(QUALITY_CHECKLIST)
        score = round(len(checked) / total * 100) if total else 0
        required_met = all(r in checked for r in REQUIRED_IDS)
        return {
            "items": QUALITY_CHECKLIST,
            "checked": checked,
            "score": score,
            "ready": score >= MIN_SCORE_TO_PUBLISH and required_met,
            "min_score": MIN_SCORE_TO_PUBLISH,
            "blocking": [c["label"] for c in QUALITY_CHECKLIST if c["required"] and c["id"] not in checked],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/projects/{project_id}/checklist")
async def save_checklist(project_id: str, body: dict):
    """Save quality checklist progress for a project"""
    try:
        checked = [str(i) for i in body.get("checked", []) if isinstance(i, str)]
        valid_ids = {c["id"] for c in QUALITY_CHECKLIST}
        checked = [i for i in checked if i in valid_ids]
        if db is not None:
            await db.project_checklists.update_one(
                {"project_id": project_id},
                {"$set": {"project_id": project_id, "checked": checked, "updated_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True,
            )
        total = len(QUALITY_CHECKLIST)
        score = round(len(checked) / total * 100) if total else 0
        required_met = all(r in checked for r in REQUIRED_IDS)
        return {
            "success": True,
            "checked": checked,
            "score": score,
            "ready": score >= MIN_SCORE_TO_PUBLISH and required_met,
        }
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

@api_router.get("/projects/{project_id}/video-prompts")
async def get_project_video_prompts(project_id: str):
    """Get reusable video-generation prompts for a project."""
    try:
        return await project_manager.get_video_prompts(project_id)
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
                    "name": "[PRODUCT] Product Creation",
                    "description": "Generate complete digital products automatically - eBooks, online courses, templates, planners, and more. AI writes content, creates outlines, and prepares everything for publishing."
                },
                {
                    "name": "[LAUNCH] One-Click Launch",
                    "description": "Launch products with a single click. The system scouts opportunities, generates the product, prepares marketplace listings, creates marketing content, and sets up social media posts."
                },
                {
                    "name": "👥 Agent Teams",
                    "description": "Create specialized AI teams for each opportunity. Teams include Research, Content, Marketing, and Analytics agents that work together to execute the full product lifecycle."
                },
                {
                    "name": "[SHOP] Multi-Platform Publishing",
                    "description": "Publish to 112+ platforms including Gumroad, Amazon KDP, Etsy, Shopify, Teachable, and more. Automated publishing where APIs allow, step-by-step guides for manual platforms."
                },
                {
                    "name": "[SOCIAL] Social Media Automation",
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
                    "name": "[ANALYTICS] Analytics & Revenue Tracking",
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


# ==================== FIILTHY DIGITAL STOREFRONT ====================

class DigitalProduct(BaseModel):
    id: str
    title: str
    description: str
    fullDescription: Optional[str] = None
    price: float
    originalPrice: Optional[float] = None
    type: str  # template, course, guide, tool
    cover: str
    rating: float = 4.8
    reviews: int = 0
    downloads: int = 0
    includes: List[str] = []
    tags: List[str] = []
    fileSize: str = "0 MB"
    updated: str
    downloadUrl: Optional[str] = None

class Purchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    user_email: str
    amount: float
    status: str = "completed"  # completed, pending, refunded
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    download_expires_at: Optional[datetime] = None

@app.get("/api/fiilthy/products", response_model=List[DigitalProduct])
async def get_fiilthy_products():
    """Get all Fiilthy digital products"""
    try:
        products = [
            {
                "id": "6a472559-3ab9-4fd4-afec-9a4ed3316cb6",
                "title": "AI-Powered Content Strategy Mastery",
                "description": "Freelance marketers struggling to create consistent, high-quality content—meet your new best friend.",
                "fullDescription": "Transform your content creation process with AI-driven insights that save time and increase engagement. Discover proven strategies and tools that streamline your workflow, enabling you to produce compelling content that resonates with your audience and boosts your bottom line.",
                "price": 149,
                "originalPrice": 299,
                "type": "template",
                "cover": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-QbPOFuIwfINU4APXuftAIXAv/user-sDce6KMPZefHEaRP6CvLW3FO/img-gs0FHst9jCVhM9LlwpeNHBDJ.png",
                "rating": 4.8,
                "reviews": 24,
                "downloads": 1200,
                "includes": [
                    "Step-by-step guides",
                    "AI content calendars",
                    "Actionable checklists",
                    "Automation tools",
                    "Email templates",
                    "Video training"
                ],
                "tags": ["AI", "Content", "Marketing", "Templates"],
                "fileSize": "245 MB",
                "updated": "2026-04-12"
            }
        ]
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fiilthy/purchase")
async def create_purchase(purchase_data: dict, _auth: dict = Depends(require_auth)):
    """Create a purchase for a digital product"""
    try:
        purchase = Purchase(
            product_id=purchase_data.get("product_id"),
            user_id=_auth.get("user_id"),
            user_email=_auth.get("email"),
            amount=purchase_data.get("amount"),
            download_expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        if db is not None:
            doc = purchase.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            if doc.get('download_expires_at'):
                doc['download_expires_at'] = doc['download_expires_at'].isoformat()
            await db.purchases.insert_one(doc)
        
        return {
            "status": "success",
            "purchase_id": purchase.id,
            "message": "Purchase completed successfully",
            "download_expires_at": purchase.download_expires_at.isoformat() if purchase.download_expires_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _resolve_auth_user_id(auth_payload: dict) -> Optional[str]:
    return auth_payload.get("sub") or auth_payload.get("user_id")


def _configured_owner_emails() -> set[str]:
    configured_emails: set[str] = set()
    for env_name in ("OWNER_EMAIL", "OWNER_EMAILS", "ADMIN_EMAIL", "ADMIN_EMAILS"):
        raw_value = normalize_env_value(os.environ.get(env_name))
        if not raw_value:
            continue
        configured_emails.update(
            email.strip().lower()
            for email in raw_value.split(",")
            if email.strip()
        )
    return configured_emails


async def _auth_has_owner_download_access(auth_payload: dict) -> bool:
    if auth_payload.get("is_admin"):
        return True

    role_value = normalize_env_value(auth_payload.get("role"))
    if role_value and role_value.lower() in {"admin", "owner"}:
        return True

    normalized_email = normalize_env_value(auth_payload.get("email"))
    normalized_email = normalized_email.lower() if normalized_email else None
    configured_emails = _configured_owner_emails()

    if db is not None:
        try:
            users_collection = db["users"]
            user_doc = None
            user_id = _resolve_auth_user_id(auth_payload)

            if user_id:
                user_doc = await users_collection.find_one({"id": user_id}, {"_id": 0, "is_admin": 1})

            if not user_doc and normalized_email:
                user_doc = await users_collection.find_one({"email": normalized_email}, {"_id": 0, "is_admin": 1})

            if user_doc and user_doc.get("is_admin"):
                return True
        except Exception:
            pass

    if configured_emails:
        return normalized_email in configured_emails

    return False


def _build_owner_product_zip(product: dict, owner_email: Optional[str]) -> tuple[io.BytesIO, str]:
    product_files = generate_product_files(product)
    safe_title = (
        "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in product.get("title", "product"))
        .strip()
        .replace(" ", "_")
    )

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in product_files.items():
            zf.writestr(filename, content)

        zf.writestr(
            "owner_download_info.json",
            json.dumps(
                {
                    "product_id": product.get("id"),
                    "title": product.get("title"),
                    "owner_email": owner_email,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "owner-download",
                },
                indent=2,
            ),
        )

    zip_buf.seek(0)
    return zip_buf, safe_title

@app.get("/api/fiilthy/purchases")
async def get_user_purchases(_auth: dict = Depends(require_auth)):
    """Get user's digital product purchases"""
    try:
        if not db:
            return []
        
        purchases = await db.purchases.find(
            {"user_id": _auth.get("user_id")},
            {"_id": 0}
        ).to_list(100)
        
        return purchases
    except Exception as e:
        if is_database_query_error(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fiilthy/owner-download/{product_id}")
async def owner_download_product(product_id: str, _auth: dict = Depends(require_auth)):
    """Download a product bundle directly from the app without a purchase.

    Intended for the operator/owner workflow while building and QA'ing products.
    """
    try:
        if not await _auth_has_owner_download_access(_auth):
            raise HTTPException(
                status_code=403,
                detail="Owner access required. Set OWNER_EMAIL/OWNER_EMAILS or mark your user as is_admin.",
            )

        product = None
        if db is not None:
            try:
                product = await db.products.find_one({"id": product_id}, {"_id": 0})
            except Exception:
                product = None

        if not product:
            for sample_product in SAMPLE_PRODUCTS:
                if sample_product.get("id") == product_id:
                    product = dict(sample_product)
                    break

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        zip_buf, safe_title = _build_owner_product_zip(product, _auth.get("email"))

        return StreamingResponse(
            zip_buf,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_title}.zip"',
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fiilthy/download/{product_id}")
async def get_download_link(product_id: str, _auth: dict = Depends(require_auth)):
    """Get download link for purchased product"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Check if user has purchased this product
        purchase = await db.purchases.find_one({
            "product_id": product_id,
            "user_id": _auth.get("user_id"),
            "status": "completed"
        })
        
        if not purchase:
            raise HTTPException(status_code=403, detail="You haven't purchased this product")
        
        # Check if download link has expired
        if purchase.get('download_expires_at'):
            expires = datetime.fromisoformat(purchase['download_expires_at'])
            if datetime.now(timezone.utc) > expires:
                raise HTTPException(status_code=410, detail="Download link has expired")
        
        # Return mock download URL (replace with real file storage)
        return {
            "status": "success",
            "download_url": f"/api/fiilthy/files/{product_id}/{_auth.get('user_id')}",
            "filename": f"fiilthy-product-{product_id}.zip",
            "expires_in_hours": 24
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint for deployment monitoring"""
    try:
        current_mongo_url = resolve_raw_mongo_url() or mongo_url
        supported_mongo_url = resolve_mongo_url() or mongo_url
        response = {
            "status": "healthy",
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Test MongoDB connection if available
        if current_mongo_url and not is_supported_mongo_url(current_mongo_url):
            response["status"] = "degraded"
            response["database"] = "misconfigured"
            response["db_error"] = "Configured MongoDB URL points to an unsupported Atlas SQL/query endpoint"
        elif client is not None and supported_mongo_url:
            try:
                await client.admin.command('ping')
                response["database"] = "connected"
            except Exception as db_error:
                response["status"] = "degraded"
                response["database"] = "disconnected"
                response["db_error"] = str(db_error)
        else:
            response["status"] = "degraded"
            response["database"] = "not configured"
        
        return response
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, 503


# ==================== Email & Notifications ====================

class EmailRequest(BaseModel):
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body (HTML supported)")
    template_type: Optional[str] = Field(default="general", description="Email template type")

class EmailResponse(BaseModel):
    status: str
    message_id: Optional[str] = None
    message: str
    sent_at: str

class NotificationRequest(BaseModel):
    recipient_id: str
    type: str  # product_ready, opportunity_found, task_completed, revenue_update
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    notification_id: str
    status: str
    created_at: str


@api_router.post("/email/send", response_model=EmailResponse)
async def send_email(request: EmailRequest, _auth: dict = Depends(require_auth)):
    """Send email using SendGrid"""
    try:
        sendgrid_key = keys_manager.get_key('sendgrid_key')
        if not sendgrid_key:
            raise HTTPException(status_code=400, detail="SendGrid API key not configured")

        from_email = keys_manager.get_key('sendgrid_from_email')
        if not from_email:
            raise HTTPException(status_code=400, detail="SendGrid sender email not configured")
        
        # Import SendGrid SDK
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        # Create email message
        message = Mail(
            from_email=from_email,
            to_emails=request.to_email,
            subject=request.subject,
            html_content=request.body
        )
        
        # Send via SendGrid
        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)
        
        return EmailResponse(
            status="success",
            message_id=response.headers.get('X-Message-Id', 'unknown'),
            message="Email sent successfully",
            sent_at=datetime.now(timezone.utc).isoformat()
        )
        
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="SendGrid SDK not installed. Run: pip install sendgrid"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")


@api_router.post("/email/send-template", response_model=EmailResponse)
async def send_templated_email(
    to_email: str,
    template_type: str = "product_ready",
    template_data: Optional[Dict[str, Any]] = None
):
    """Send email using predefined templates"""
    try:
        sendgrid_key = keys_manager.get_key('sendgrid_key')
        if not sendgrid_key:
            raise HTTPException(status_code=400, detail="SendGrid API key not configured")
        
        if template_data is None:
            template_data = {}
        
        # Define email templates
        templates = {
            "product_ready": {
                "subject": f"🚀 Your Product '{template_data.get('product_title', 'New Product')}' is Ready!",
                "body": f"""
                    <h1>Great News! 🎉</h1>
                    <p>Your AI-generated product <strong>{template_data.get('product_title', 'product')}</strong> is now ready to publish!</p>
                    <p><strong>Description:</strong> {template_data.get('product_description', '')}</p>
                    <p><strong>Price Range:</strong> {template_data.get('price_range', 'To be determined')}</p>
                    <p>You can now publish it to your marketplaces and start generating revenue.</p>
                    <p>Ready to get started? Log in to your dashboard now!</p>
                """
            },
            "opportunity_found": {
                "subject": "💡 New Market Opportunity Identified!",
                "body": f"""
                    <h1>Exciting Opportunity! 💰</h1>
                    <p>Our AI discovered a high-potential market opportunity in <strong>{template_data.get('niche', 'your niche')}</strong></p>
                    <p><strong>Market Size:</strong> {template_data.get('market_size', 'Large')}</p>
                    <p><strong>Demand Level:</strong> {template_data.get('demand_level', 'High')}</p>
                    <p><strong>Top Keywords:</strong> {', '.join(template_data.get('keywords', []))}</p>
                    <p>Check your dashboard to create a product for this opportunity!</p>
                """
            },
            "task_completed": {
                "subject": "✅ AI Task Completed",
                "body": f"""
                    <h1>Task Completed! ✨</h1>
                    <p>Your AI task has completed successfully.</p>
                    <p><strong>Task:</strong> {template_data.get('task_name', 'Unknown')}</p>
                    <p><strong>Results:</strong> {template_data.get('results', 'Check your dashboard')}</p>
                """
            },
            "revenue_update": {
                "subject": "💰 Revenue Update",
                "body": f"""
                    <h1>Revenue Report 📊</h1>
                    <p>Amazing progress!</p>
                    <p><strong>Today's Revenue:</strong> ${template_data.get('revenue_today', 0)}</p>
                    <p><strong>Total Revenue:</strong> ${template_data.get('total_revenue', 0)}</p>
                    <p><strong>New Conversions:</strong> {template_data.get('conversions', 0)}</p>
                """
            }
        }
        
        template = templates.get(template_type, templates["product_ready"])
        
        # Send email
        request_obj = EmailRequest(
            to_email=to_email,
            subject=template["subject"],
            body=template["body"],
            template_type=template_type
        )
        
        return await send_email(request_obj)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending template email: {str(e)}")


@api_router.post("/notifications", response_model=NotificationResponse)
async def create_notification(request: NotificationRequest):
    """Create and store a notification"""
    try:
        notification = {
            "notification_id": str(uuid.uuid4()),
            "recipient_id": request.recipient_id,
            "type": request.type,
            "title": request.title,
            "message": request.message,
            "data": request.data or {},
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in database if available
        if db is not None:
            await db.notifications.insert_one(notification)
        
        return NotificationResponse(
            notification_id=notification["notification_id"],
            status="created",
            created_at=notification["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")


@api_router.get("/notifications/{recipient_id}")
async def get_notifications(recipient_id: str, limit: int = 20, unread_only: bool = False):
    """Get notifications for a user"""
    try:
        if db is None:
            return {"notifications": [], "total": 0}
        
        query = {"recipient_id": recipient_id}
        if unread_only:
            query["read"] = False
        
        notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        
        return {
            "notifications": notifications,
            "total": len(notifications),
            "recipient_id": recipient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")


@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""
    try:
        if db is None:
            return {"status": "database_not_available"}
        
        result = await db.notifications.update_one(
            {"notification_id": notification_id},
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"status": "marked_read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification: {str(e)}")


@api_router.post("/email/send-product-notification")
async def send_product_notification(product_id: str, to_email: str, _auth: dict = Depends(require_auth)):
    """Send email notification when product is ready (recommended for workflow)"""
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not available")
        
        # Get product from database
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Prepare email with product details
        email_request = EmailRequest(
            to_email=to_email,
            subject=f"🚀 Your AI-Generated Product is Ready: {product['title']}",
            body=f"""
                <h1>{product['title']}</h1>
                <p><strong>Description:</strong> {product['description']}</p>
                <p><strong>Keywords:</strong> {', '.join(product.get('keywords', []))}</p>
                <p><strong>Target Audience:</strong> {product.get('target_audience', 'Everyone')}</p>
                <p><strong>Price Range:</strong> {product.get('price_range', '$9.99-$99.99')}</p>
                {f'<img src="{product.get("image_url", "")}" style="max-width: 300px; height: auto;" />' if product.get('image_url') else ''}
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Review the product details</li>
                    <li>Adjust pricing if needed</li>
                    <li>Add to your marketplace</li>
                    <li>Start selling!</li>
                </ol>
            """,
            template_type="product_ready"
        )
        
        return await send_email(email_request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending product notification: {str(e)}")


# ==================== FACELESS VIDEO GENERATION (REAL) ====================

class FacelessVideoRequest(BaseModel):
    product_id: str
    style: str = Field(default="motivational", description="Video style: motivational, tutorial, demo, testimonial, comparison")
    duration: int = Field(default=60, description="Video duration in seconds (max 60 for YouTube Shorts)")
    count: int = Field(default=1, description="Number of video variations to generate")

@api_router.post("/videos/generate-faceless")
async def generate_faceless_video(request: FacelessVideoRequest, background_tasks: BackgroundTasks):
    """
    Generate faceless YouTube Shorts/TikTok videos with voiceovers and background footage
    
    Returns professional vertical 1080x1920 videos ready for YouTube Shorts, TikTok, and Instagram Reels
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        # Get product
        product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Generate videos
        generator = await get_faceless_video_generator()
        
        if request.count == 1:
            video_result = await generator.generate_full_video(
                product=product,
                video_style=request.style,
                duration=request.duration
            )
            videos = [video_result]
        else:
            videos = await generator.generate_video_series(
                product=product,
                count=request.count,
                styles=[request.style]
            )
        
        # Store in database
        video_records = []
        for video in videos:
            record = {
                "id": video.get("video_id"),
                "product_id": request.product_id,
                "product_title": product.get("title"),
                "video_path": video.get("video_path"),
                "style": request.style,
                "duration": request.duration,
                "format": "1080x1920",
                "platforms_ready": video.get("platforms_ready"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "ready"
            }
            
            if db is not None:
                await db.generated_videos.insert_one(record)
            video_records.append(record)
        
        return {
            "success": all(v.get("success", False) for v in videos),
            "product_id": request.product_id,
            "videos_generated": len(videos),
            "videos": videos,
            "ready_for": {
                "youtube_shorts": True,
                "tiktok": True,
                "instagram_reels": True,
                "instagram_stories": True
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/videos/product/{product_id}")
async def get_product_videos(product_id: str):
    """Get all generated videos for a product"""
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        videos = await db.generated_videos.find(
            {"product_id": product_id},
            {"_id": 0}
        ).to_list(100)
        
        return {
            "product_id": product_id,
            "videos_count": len(videos),
            "videos": videos
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== YOUTUBE DATA API (VIDEO UPLOADING) ====================

class YouTubeUploadRequest(BaseModel):
    video_id: str
    title: str
    description: str
    tags: List[str] = []
    privacy_status: str = Field(default="public", description="public, unlisted, or private")
    category_id: str = Field(default="24", description="YouTube category ID")
    made_for_kids: bool = False


class LiveDistributionRequest(BaseModel):
    video_path: Optional[str] = None
    title: str
    description: str = ""
    hashtags: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=lambda: ["youtube", "instagram", "tiktok"])
    privacy_status: str = "public"
    video_public_url: Optional[str] = None
    product_id: Optional[str] = None

@api_router.get("/youtube/auth/url")
async def get_youtube_auth_url(redirect_uri: str = "http://localhost:8000/api/youtube/auth/callback"):
    """Get YouTube OAuth authorization URL"""
    try:
        youtube_api = await get_youtube_api()
        auth_url = youtube_api.get_auth_url(redirect_uri)
        
        return {
            "success": True,
            "auth_url": auth_url,
            "message": "Visit this URL to authorize YouTube access"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/youtube/auth/callback")
async def youtube_auth_callback(code: str, redirect_uri: str = "http://localhost:8000/api/youtube/auth/callback"):
    """Handle YouTube OAuth callback"""
    try:
        youtube_api = await get_youtube_api()
        result = await youtube_api.handle_oauth_callback(code, redirect_uri)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/youtube/upload")
async def upload_to_youtube(request: YouTubeUploadRequest, background_tasks: BackgroundTasks):
    """
    Upload a generated video to YouTube Shorts
    
    Requirements:
    - YouTube API credentials configured
    - User must have authorized YouTube access
    - Video file must exist
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        # Get generated video
        video_record = await db.generated_videos.find_one(
            {"id": request.video_id},
            {"_id": 0}
        )
        
        if not video_record:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_path = video_record.get("video_path")
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=400, detail=f"Video file not found: {video_path}")
        
        # Upload to YouTube
        youtube_api = await get_youtube_api()
        upload_result = await youtube_api.upload_video(
            video_path=video_path,
            title=request.title,
            description=request.description,
            tags=request.tags,
            category_id=request.category_id,
            privacy_status=request.privacy_status,
            made_for_kids=request.made_for_kids
        )
        
        if upload_result.get("success"):
            video_id = upload_result.get("video_id")
            
            # Store upload record
            await db.youtube_uploads.insert_one({
                "local_video_id": request.video_id,
                "youtube_video_id": video_id,
                "title": request.title,
                "url": upload_result.get("url"),
                "shorts_url": upload_result.get("shorts_url"),
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "privacy_status": request.privacy_status
            })
        
        return upload_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/distribution/live-readiness")
async def get_live_distribution_readiness():
    """Return truthful live-readiness for each supported platform."""
    try:
        engine = get_live_distribution_engine(db)
        return {
            "success": True,
            "platforms": engine.get_live_readiness(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/distribution/publish-live")
async def publish_video_live(request: LiveDistributionRequest):
    """Attempt real platform uploads using only configured live integrations."""
    try:
        engine = get_live_distribution_engine(db)
        result = await engine.publish_video(
            video_path=request.video_path,
            title=request.title,
            description=request.description,
            hashtags=request.hashtags,
            platforms=request.platforms,
            privacy_status=request.privacy_status,
            video_public_url=request.video_public_url,
            product_id=request.product_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/youtube/video/{video_id}/status")
async def get_youtube_video_status(video_id: str):
    """Get YouTube video processing status"""
    try:
        youtube_api = await get_youtube_api()
        status = await youtube_api.get_video_status(video_id)
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/youtube/channel/analytics")
async def get_youtube_channel_analytics():
    """Get YouTube channel analytics"""
    try:
        youtube_api = await get_youtube_api()
        analytics = await youtube_api.get_channel_analytics()
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/youtube/playlist/create")
async def create_youtube_playlist(name: str, description: str = "", privacy_status: str = "public"):
    """Create a YouTube playlist for product videos"""
    try:
        youtube_api = await get_youtube_api()
        playlist = await youtube_api.create_playlist(
            title=name,
            description=description,
            privacy_status=privacy_status
        )
        
        if db is not None and playlist.get("success"):
            await db.youtube_playlists.insert_one({
                "playlist_id": playlist.get("playlist_id"),
                "name": name,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        
        return playlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MULTI-PLATFORM PRODUCT SYNC (REAL) ====================

class ProductSyncRequest(BaseModel):
    product_id: str
    platforms: Optional[List[str]] = Field(default=None, description="Etsy, Shopify, Amazon, TikTok Shop, Gumroad. If None, syncs to all configured.")

class InventorySyncRequest(BaseModel):
    product_id: str
    inventory_updates: Dict[str, int] = Field(description="Platform-specific inventory: {'etsy': 50, 'shopify': 100, ...}")

class PricingSyncRequest(BaseModel):
    product_id: str
    pricing: Dict[str, float] = Field(description="Platform-specific pricing: {'etsy': 29.99, 'shopify': 39.99, ...}")

@api_router.post("/products/{product_id}/sync-all-platforms")
async def sync_product_to_all_platforms(product_id: str, request: ProductSyncRequest):
    """
    Sync a product to all configured marketplaces (Etsy, Shopify, Amazon, TikTok Shop, Gumroad)
    
    One-click publishing to all your stores with product data, images, and pricing
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        # Get product
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Sync to platforms
        sync_manager = await get_product_sync_manager()
        result = await sync_manager.sync_product_to_all_platforms(
            product=product,
            platforms=request.platforms
        )
        
        # Store sync record
        if db is not None:
            sync_record = {
                "product_id": product_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sync_result": result,
                "status": "success" if result.get("success") else "partial"
            }
            await db.product_syncs.insert_one(sync_record)
        
        return result
    
    except Exception as e:
        logger.error(f"Product sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/products/{product_id}/sync-inventory")
async def sync_product_inventory(product_id: str, request: InventorySyncRequest):
    """
    Update product inventory across all synced platforms simultaneously
    
    Keep inventory in sync across Etsy, Shopify, Amazon, TikTok Shop, etc with one call
    """
    try:
        sync_manager = await get_product_sync_manager()
        result = await sync_manager.sync_inventory_across_platforms(
            product_id=product_id,
            inventory_updates=request.inventory_updates
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/products/{product_id}/sync-pricing")
async def sync_product_pricing(product_id: str, request: PricingSyncRequest):
    """
    Update product pricing across platforms with different prices per marketplace
    
    Set platform-specific prices (e.g., $29.99 on Etsy, $39.99 on Shopify)
    """
    try:
        sync_manager = await get_product_sync_manager()
        result = await sync_manager.sync_pricing_rules(
            product_id=product_id,
            pricing=request.pricing
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products/{product_id}/sync-status")
async def get_product_sync_status(product_id: str):
    """Get product publishing status across all platforms"""
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        # Check sync history
        sync_records = await db.product_syncs.find(
            {"product_id": product_id},
            {"_id": 0}
        ).sort("timestamp", -1).to_list(10)
        
        sync_manager = await get_product_sync_manager()
        current_status = await sync_manager.get_product_status_across_platforms(product_id)
        
        return {
            "product_id": product_id,
            "current_status": current_status,
            "recent_syncs": sync_records
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/products/sync-batch")
async def sync_multiple_products(product_ids: List[str]):
    """Sync multiple products to all platforms in parallel"""
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        results = {}
        sync_manager = await get_product_sync_manager()
        
        for product_id in product_ids:
            product = await db.products.find_one({"id": product_id}, {"_id": 0})
            if product:
                result = await sync_manager.sync_product_to_all_platforms(product)
                results[product_id] = result
            else:
                results[product_id] = {"error": "Product not found"}
        
        return {
            "success": True,
            "total": len(product_ids),
            "synced": sum(1 for r in results.values() if r.get("success")),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Payment Processing (Stripe) ====================

class StripeProduct(BaseModel):
    product_id: str
    price_cents: int = Field(..., description="Price in cents (e.g., 2999 for $29.99)")
    currency: str = Field(default="usd", description="Currency code")
    quantity_available: Optional[int] = Field(default=None, description="Unlimited if None")

class StripeCheckoutRequest(BaseModel):
    product_id: str
    customer_email: str
    success_url: str = "http://localhost:3000/success"
    cancel_url: str = "http://localhost:3000/cancel"
    quantity: int = 1

class StripeCheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
    payment_status: str

class StripeWebhookEvent(BaseModel):
    event_type: str
    session_id: Optional[str] = None
    payment_intent_id: Optional[str] = None
    data: Dict[str, Any]

class PaymentRecord(BaseModel):
    payment_id: str
    product_id: str
    customer_email: str
    amount_cents: int
    currency: str
    status: str  # succeeded, pending, failed
    payment_intent_id: str
    created_at: str


@api_router.post("/payments/create-checkout", response_model=StripeCheckoutResponse)
async def create_stripe_checkout(request: StripeCheckoutRequest):
    """Create a Stripe checkout session"""
    try:
        stripe_key = normalize_env_value(keys_manager.get_key('stripe_key'))
        if not stripe_key:
            raise HTTPException(status_code=400, detail="Stripe API key not configured")
        
        # Import Stripe
        try:
            import stripe
        except ImportError:
            raise HTTPException(status_code=500, detail="Stripe SDK not installed. Run: pip install stripe")
        
        # Initialize Stripe
        stripe.api_key = stripe_key
        
        # Get product details
        if db is None:
            raise HTTPException(status_code=400, detail="Database not available")
        
        product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get price from product or use default
        price_cents = int(product.get("price", 29.99) * 100)
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product['title'],
                            'description': product['description'][:500],  # Limit description
                            'images': [product['image_url']] if product.get('image_url') else [],
                        },
                        'unit_amount': price_cents,
                    },
                    'quantity': request.quantity,
                }
            ],
            mode='payment',
            customer_email=request.customer_email,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                'product_id': request.product_id,
                'customer_email': request.customer_email
            }
        )
        
        # Store payment record
        payment_record = {
            "payment_id": str(uuid.uuid4()),
            "product_id": request.product_id,
            "customer_email": request.customer_email,
            "amount_cents": price_cents * request.quantity,
            "currency": "usd",
            "status": "pending",
            "payment_intent_id": checkout_session.payment_intent,
            "stripe_session_id": checkout_session.id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.payments.insert_one(payment_record)
        
        return StripeCheckoutResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id,
            payment_status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating checkout: {str(e)}")


@api_router.post("/payments/webhook")
async def handle_stripe_webhook(request: Request):
    """Handle Stripe webhook events with signature verification"""
    try:
        stripe_key = normalize_env_value(keys_manager.get_key('stripe_key'))
        if not stripe_key:
            raise HTTPException(status_code=400, detail="Stripe API key not configured")

        import stripe as stripe_lib
        stripe_lib.api_key = stripe_key

        # Verify webhook signature
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        webhook_secret = (
            normalize_env_value(os.environ.get('STRIPE_WEBHOOK_SECRET'))
            or normalize_env_value(keys_manager.get_key('stripe_webhook_secret'))
        )

        if not webhook_secret:
            raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing Stripe signature header")

        try:
            event = stripe_lib.Webhook.construct_event(payload, sig_header, webhook_secret)
        except stripe_lib.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid Stripe signature")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")

        event_type = event['type']
        
        # Handle checkout.session.completed event
        if event_type == 'checkout.session.completed':
            session_data = event['data']['object']
            session_id = session_data.get('id')
            payment_intent_id = session_data.get('payment_intent')
            customer_email = session_data.get('customer_email')
            metadata = session_data.get('metadata', {})
            completed_at = datetime.now(timezone.utc).isoformat()
            amount_total = float(session_data.get('amount_total', 0)) / 100
            
            # Update payment record
            if db is not None:
                await db.payments.update_one(
                    {"stripe_session_id": session_id},
                    {
                        "$set": {
                            "status": "succeeded",
                            "completed_at": completed_at
                        }
                    }
                )
                
                await db.sales.update_one(
                    {"stripe_session_id": session_id},
                    {
                        "$set": {
                            "sale_id": str(uuid.uuid4()),
                            "product_id": metadata.get('product_id'),
                            "customer_email": customer_email,
                            "amount": amount_total,
                            "status": "completed",
                            "source": "main-backend",
                            "created_at": completed_at,
                            "payment_intent_id": payment_intent_id,
                            "stripe_session_id": session_id,
                        }
                    },
                    upsert=True,
                )
                
                # Update product stats
                product_id = metadata.get('product_id')
                if product_id:
                    await db.products.update_one(
                        {"id": product_id},
                        {
                            "$inc": {
                                "conversions": 1,
                                "revenue": amount_total
                            }
                        }
                    )
                
                # Generate secure download token and email customer the real link
                try:
                    import secrets as _secrets
                    download_token = _secrets.token_urlsafe(32)
                    backend_url = os.environ.get("BACKEND_URL", "https://fiilthy-backend.railway.app")

                    # Store download record with 7-day expiry
                    await db.downloads.insert_one({
                        "token": download_token,
                        "product_id": product_id,
                        "email": customer_email,
                        "stripe_session_id": session_id,
                        "created_at": completed_at,
                        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                        "download_count": 0,
                    })

                    product = await db.products.find_one({"id": product_id}, {"_id": 0})
                    product_title = product["title"] if product else "Your Product"
                    download_url = f"{backend_url}/api/store/download/{download_token}"

                    email_request = EmailRequest(
                        to_email=customer_email,
                        subject=f"\u2705 Your Download Is Ready: {product_title}",
                        body=f"""
                            <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;background:#0d1117;color:#fff">
                                <h1 style="color:#00e5ff">\U0001f389 Thank you for your purchase!</h1>
                                <p>Your product <strong>{product_title}</strong> is ready to download.</p>
                                <p style="margin:24px 0">
                                    <a href="{download_url}"
                                       style="background:#00e5ff;color:#000;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block">
                                        \u2b07\ufe0f Download Your Product Now
                                    </a>
                                </p>
                                <p style="color:#888;font-size:14px">This link expires in 7 days. Save it somewhere safe.</p>
                                <p style="color:#888;font-size:14px">Questions? Reply to this email or contact support@fiilthy.ai</p>
                                <hr style="border:1px solid #1a2a3a;margin:24px 0">
                                <p style="color:#444;font-size:12px">FiiLTHY.ai | Automated AI Income Systems</p>
                            </div>
                        """,
                        template_type="general"
                    )
                    await send_email(email_request)
                except Exception as e:
                    print(f"Warning: Failed to send download email: {e}")
        
        return {"status": "received"}
        
    except Exception as e:
        print(f"Webhook handling error: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")


@api_router.get("/payments/{product_id}/stats")
async def get_product_payment_stats(product_id: str):
    """Get payment statistics for a product"""
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not available")
        
        # Get product
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get payment records for this product
        payments = await db.payments.find(
            {
                "product_id": product_id,
                "status": "succeeded"
            },
            {"_id": 0}
        ).to_list(None)
        
        # Calculate stats
        total_revenue = sum(p['amount_cents'] for p in payments) / 100
        total_sales = len(payments)
        
        return {
            "product_id": product_id,
            "product_title": product['title'],
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "average_sale": total_revenue / total_sales if total_sales > 0 else 0,
            "payment_records": payments,
            "currency": "usd"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting payment stats: {str(e)}")


@api_router.get("/payments/all-stats")
async def get_all_payment_stats():
    """Get overall payment statistics"""
    try:
        if db is None:
            return {
                "total_revenue": 0,
                "total_sales": 0,
                "products_with_sales": 0,
                "average_order_value": 0,
                "today_revenue": 0,
                "today_sales": 0
            }
        
        try:
            # Get all successful payments
            all_payments = await db.payments.find(
                {"status": "succeeded"},
                {"_id": 0}
            ).to_list(None)
        except:
            all_payments = []
        
        total_revenue = sum(p.get('amount_cents', 0) for p in all_payments) / 100 if all_payments else 0
        total_sales = len(all_payments)
        
        # Get unique products with sales
        products_with_sales = len(set(p.get('product_id') for p in all_payments if p.get('product_id')))
        
        # Average order value
        average_order_value = total_revenue / total_sales if total_sales > 0 else 0
        
        # Today's stats
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            today_payments = await db.payments.find(
                {
                    "status": "succeeded",
                    "created_at": {"$gte": today_start.isoformat()}
                },
                {"_id": 0}
            ).to_list(None)
        except:
            today_payments = []
        
        today_revenue = sum(p.get('amount_cents', 0) for p in today_payments) / 100 if today_payments else 0
        today_sales = len(today_payments)
        
        return {
            "total_revenue": round(total_revenue, 2),
            "total_sales": total_sales,
            "products_with_sales": products_with_sales,
            "average_order_value": round(average_order_value, 2),
            "today_revenue": round(today_revenue, 2),
            "today_sales": today_sales
        }
    except Exception as e:
        print(f"Error in get_all_payment_stats: {str(e)}")
        return {
            "total_revenue": 0,
            "total_sales": 0,
            "products_with_sales": 0,
            "average_order_value": 0,
            "today_revenue": 0,
            "today_sales": 0,
            "error": str(e)
        }


# ==================== PRODUCT RANKING & ADVERTISING CAMPAIGNS ====================

class ProductRankingRequest(BaseModel):
    limit: int = Field(default=10, description="Number of products to return")
    metrics: Optional[List[str]] = Field(default=["revenue", "sales_count"], description="Ranking metrics")
    time_period: str = Field(default="30d", description="7d, 30d, 90d, or all")
    min_sales: int = Field(default=0, description="Minimum sales threshold")

class AdCampaignRequest(BaseModel):
    product_id: str
    platforms: List[str] = Field(description="Ad platforms: google_ads, facebook_ads, tiktok_ads, linkedin_ads, pinterest_ads, amazon_ads, youtube_ads")
    total_budget: float = Field(description="Total campaign budget in USD")
    daily_budget: float = Field(description="Daily budget per platform in USD")
    duration_days: int = Field(default=30)
    target_audience: Optional[Dict[str, Any]] = Field(default=None)

@api_router.get("/products/ranking/top")
async def get_top_products(limit: int = 10, 
                           metrics: str = "revenue,sales_count",
                           time_period: str = "30d",
                           min_sales: int = 0):
    """
    Get top-performing products ranked by specified metrics
    
    Identifies bestsellers and products ready for advertising investment
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        ranker = await get_product_ranking_engine()
        await ranker.set_db(db)
        
        metric_list = [m.strip() for m in metrics.split(",")]
        
        top_products = await ranker.get_top_products(
            limit=limit,
            metrics=metric_list,
            time_period=time_period,
            min_sales=min_sales
        )
        
        return {
            "success": True,
            "count": len(top_products),
            "products": top_products
        }
    except Exception as e:
        logger.error(f"Failed to get top products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products/ranking/trending")
async def get_trending_products(limit: int = 5):
    """
    Get trending products (fastest growing)
    
    Products with highest sales velocity week-over-week
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        ranker = await get_product_ranking_engine()
        await ranker.set_db(db)
        
        trending = await ranker.get_trending_products(limit=limit)
        
        return {
            "success": True,
            "count": len(trending),
            "products": trending
        }
    except Exception as e:
        logger.error(f"Failed to get trending products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products/ranking/high-margin")
async def get_high_margin_products(limit: int = 10):
    """
    Get most profitable products (high margin)
    
    Best products for profitability optimization
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        ranker = await get_product_ranking_engine()
        await ranker.set_db(db)
        
        products = await ranker.get_high_margin_products(limit=limit)
        
        return {
            "success": True,
            "count": len(products),
            "products": products
        }
    except Exception as e:
        logger.error(f"Failed to get high margin products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products/{product_id}/health")
async def get_product_health(product_id: str):
    """
    Get product health metrics for advertising readiness
    
    Comprehensive assessment of whether a product is ready for ad campaigns
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        ranker = await get_product_ranking_engine()
        await ranker.set_db(db)
        
        health = await ranker.get_product_health(product_id)
        
        return health
    except Exception as e:
        logger.error(f"Failed to get product health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/campaigns/create")
async def create_advertising_campaign(request: AdCampaignRequest):
    """
    Create and launch advertising campaigns on multiple platforms
    
    One-click multi-platform ad campaign setup with automated creative generation
    Supports: Google Ads, Facebook Ads, TikTok Ads, LinkedIn Ads, Pinterest Ads, Amazon Ads, YouTube Ads
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        manager = await get_campaign_manager()
        await manager.set_db(db)
        
        result = await manager.create_campaign(
            product_id=request.product_id,
            platforms=request.platforms,
            budget=request.total_budget,
            daily_budget=request.daily_budget,
            duration_days=request.duration_days,
            target_audience=request.target_audience
        )
        
        return result
    except Exception as e:
        logger.error(f"Failed to create campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(campaign_id: str):
    """
    Get real-time campaign performance metrics
    
    Comprehensive metrics across all platforms: impressions, clicks, conversions, spend, ROI
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        manager = await get_campaign_manager()
        await manager.set_db(db)
        
        performance = await manager.get_campaign_performance(campaign_id)
        
        return performance
    except Exception as e:
        logger.error(f"Failed to get campaign performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/campaigns/{campaign_id}/optimize")
async def optimize_campaign(campaign_id: str):
    """
    Get campaign optimization recommendations
    
    AI-powered suggestions to improve CTR, conversion rate, and ROI
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        manager = await get_campaign_manager()
        await manager.set_db(db)
        
        optimizations = await manager.optimize_campaign(campaign_id)
        
        return optimizations
    except Exception as e:
        logger.error(f"Failed to optimize campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """
    Pause a campaign across all platforms
    
    Stops spending and impressions immediately on all connected platforms
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        manager = await get_campaign_manager()
        await manager.set_db(db)
        
        result = await manager.pause_campaign(campaign_id)
        
        return result
    except Exception as e:
        logger.error(f"Failed to pause campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/campaigns")
async def list_campaigns(product_id: Optional[str] = None, 
                        status: Optional[str] = None,
                        limit: int = 20):
    """
    List all advertising campaigns
    
    Filter by product, status, or get all active campaigns
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        manager = await get_campaign_manager()
        await manager.set_db(db)
        
        campaigns = await manager.list_campaigns(
            product_id=product_id,
            status=status,
            limit=limit
        )
        
        return {
            "count": len(campaigns),
            "campaigns": campaigns
        }
    except Exception as e:
        logger.error(f"Failed to list campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/campaigns/roi/dashboard")
async def get_revenue_dashboard(product_id: Optional[str] = None):
    """
    Get comprehensive revenue attribution dashboard
    
    Track total spend, revenue, ROI, conversions across all campaigns and platforms
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        attribution = RevenueAttributionEngine()
        await attribution.set_db(db)
        
        dashboard = await attribution.get_revenue_dashboard(product_id=product_id)
        
        return dashboard
    except Exception as e:
        logger.error(f"Failed to get revenue dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/campaigns/{campaign_id}/roi")
async def get_campaign_roi(campaign_id: str, attribution_model: str = "last_touch"):
    """
    Get detailed ROI calculation for a campaign
    
    Attributes sales revenue to campaigns and calculates profitability metrics
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        attribution = RevenueAttributionEngine()
        await attribution.set_db(db)
        
        roi = await attribution.get_campaign_roi(campaign_id, attribution_model)
        
        return roi
    except Exception as e:
        logger.error(f"Failed to get campaign ROI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/campaigns/{campaign_id}/roi/by-platform")
async def get_platform_attribution(campaign_id: str):
    """
    Get ROI breakdown by ad platform
    
    See which platforms are performing best for this campaign
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        attribution = RevenueAttributionEngine()
        await attribution.set_db(db)
        
        platform_roi = await attribution.get_platform_attribution(campaign_id)
        
        return platform_roi
    except Exception as e:
        logger.error(f"Failed to get platform attribution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/campaigns/{campaign_id}/roi/time-series")
async def get_campaign_roi_time_series(campaign_id: str, interval: str = "daily"):
    """
    Get ROI progression over time
    
    Track cumulative spend, revenue, and ROI daily/weekly/hourly
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        attribution = RevenueAttributionEngine()
        await attribution.set_db(db)
        
        time_series = await attribution.get_time_series_roi(campaign_id, interval)
        
        return {
            "campaign_id": campaign_id,
            "interval": interval,
            "data": time_series
        }
    except Exception as e:
        logger.error(f"Failed to get ROI time series: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/sales/record")
async def record_sale(product_id: str,
                     amount: float,
                     campaign_id: Optional[str] = None,
                     platform: Optional[str] = None,
                     user_id: Optional[str] = None):
    """
    Record a sale for attribution tracking
    
    Link sales to advertising campaigns for accurate ROI measurement
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")
        
        attribution = RevenueAttributionEngine()
        await attribution.set_db(db)
        
        result = await attribution.record_sale(
            product_id=product_id,
            amount=amount,
            source="campaign" if campaign_id else "organic",
            campaign_id=campaign_id,
            platform=platform,
            user_id=user_id
        )
        
        return result
    except Exception as e:
        logger.error(f"Failed to record sale: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LEARNING & EVOLUTION ENDPOINTS ====================

class PerformanceMetrics(BaseModel):
    revenue: float = 0.0
    conversions: int = 0
    clicks: int = 0
    engagement_score: float = 0.0
    customer_satisfaction: float = 0.0
    retention_rate: float = 0.0

class ProductVariant(BaseModel):
    variant_id: str
    title: str
    description: str
    price: float
    category: str
    target_audience: str

@api_router.post("/learning/record-performance")
async def record_product_performance(product_id: str, metrics: PerformanceMetrics):
    """
    Record product performance metrics for machine learning

    This data is used to improve future product generation strategies
    """
    try:
        if learning_engine is None:
            raise HTTPException(status_code=400, detail="Learning engine not configured")

        await learning_engine.record_product_performance(
            product_id=product_id,
            metrics=metrics.dict()
        )

        return {
            "success": True,
            "message": "Performance data recorded for learning",
            "product_id": product_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/learning/optimal-strategy")
async def get_optimal_product_strategy(opportunity: Dict[str, Any]):
    """
    Get AI-optimized product generation strategy based on learned patterns

    Uses historical performance data to recommend the best approach
    """
    try:
        if learning_engine is None:
            raise HTTPException(status_code=400, detail="Learning engine not configured")

        strategy = await learning_engine.get_optimal_product_strategy(opportunity)

        return {
            "success": True,
            "strategy": strategy,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/learning/ab-test")
async def run_ab_test(variants: List[ProductVariant]):
    """
    Run A/B testing on product variants to determine optimal approach

    Tests different product variations and learns which performs best
    """
    try:
        if learning_engine is None:
            raise HTTPException(status_code=400, detail="Learning engine not configured")

        test_result = await learning_engine.run_ab_test([v.dict() for v in variants])

        return {
            "success": True,
            "test_id": test_result["test_id"],
            "groups": test_result["groups"],
            "expected_completion": test_result["expected_completion"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/learning/ab-results/{test_id}")
async def get_ab_test_results(test_id: str):
    """
    Get A/B test results and winner determination

    Analyzes test performance and provides insights for future optimization
    """
    try:
        if learning_engine is None:
            raise HTTPException(status_code=400, detail="Learning engine not configured")

        results = await learning_engine.analyze_ab_results(test_id)

        return {
            "success": True,
            "test_id": test_id,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/learning/predict-success")
async def predict_product_success(product_features: Dict[str, Any]):
    """
    Predict product success probability using learned model

    Analyzes product characteristics against historical performance data
    """
    try:
        if learning_engine is None:
            raise HTTPException(status_code=400, detail="Learning engine not configured")

        prediction = await learning_engine.predict_product_success(product_features)

        return {
            "success": True,
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/learning/analytics")
async def get_learning_analytics():
    """
    Get comprehensive learning analytics and evolution insights

    Shows how the system is improving over time
    """
    try:
        if db is None:
            raise HTTPException(status_code=400, detail="Database not configured")

        # Get learning data
        total_learned = await db.learning_data.count_documents({})
        ab_tests = await db.learning_data.count_documents({"type": "ab_test_learning"})
        performance_records = await db.performance_collection.count_documents({})

        # Get recent insights
        recent_insights = await db.learning_data.find(
            {"type": "ab_test_learning"},
            {"_id": 0}
        ).sort("timestamp", -1).limit(5).to_list(length=None)

        return {
            "success": True,
            "analytics": {
                "total_learning_events": total_learned,
                "ab_tests_completed": ab_tests,
                "performance_records": performance_records,
                "system_evolution": "actively_learning" if total_learned > 0 else "initializing",
                "recent_insights": recent_insights
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the main app
app.include_router(api_router)
app.include_router(router_v5)
app.include_router(router_v5_new)  # NEW: Production factory routes
app.include_router(router_product_launch)  # NEW: Product launch routes
app.include_router(router_quality)          # NEW: Quality control routes
app.include_router(router_agents)           # NEW: Agent empire routes
app.include_router(router_store)            # NEW: Public storefront + delivery
app.include_router(router_intelligence)     # Intelligence: competitor, email, shorts

# Configure CORS
_cors_env = os.environ.get('CORS_ORIGINS', '')
allowed_origins = [o.strip() for o in _cors_env.split(',') if o.strip()] if _cors_env else []
# Always allow localhost dev and Vercel deployments
_defaults = ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002',
             'https://frontend-one-ashen-16.vercel.app']
for _o in _defaults:
    if _o not in allowed_origins:
        allowed_origins.append(_o)
if os.environ.get('ENVIRONMENT') != 'production':
    allowed_origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Error monitoring middleware
# ---------------------------------------------------------------------------
from starlette.middleware.base import BaseHTTPMiddleware
import time as _time

class ErrorMonitoringMiddleware(BaseHTTPMiddleware):
    """Logs every request with timing, and captures 5xx errors with full detail."""

    async def dispatch(self, request, call_next):
        start = _time.perf_counter()
        try:
            response = await call_next(request)
            elapsed = (_time.perf_counter() - start) * 1000
            if response.status_code >= 500:
                logging.getLogger("monitor").error(
                    "5xx | %s %s | %d | %.0fms",
                    request.method, request.url.path, response.status_code, elapsed,
                )
            elif response.status_code >= 400:
                logging.getLogger("monitor").warning(
                    "4xx | %s %s | %d | %.0fms",
                    request.method, request.url.path, response.status_code, elapsed,
                )
            else:
                logging.getLogger("monitor").info(
                    "OK  | %s %s | %d | %.0fms",
                    request.method, request.url.path, response.status_code, elapsed,
                )
            return response
        except Exception as exc:
            elapsed = (_time.perf_counter() - start) * 1000
            logging.getLogger("monitor").exception(
                "ERR | %s %s | %.0fms | %s", request.method, request.url.path, elapsed, exc,
            )
            raise

app.add_middleware(ErrorMonitoringMiddleware)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_services():
    """Initialize production factory services on startup"""
    app.state.db = db
    await init_services(db)
    logger.info("✅ Production factory services initialized")
    # Start automated 2-hour product generation cycle
    if db is not None:
        scheduler = get_cycle_scheduler(db)
        scheduler.start()
        logger.info("✅ Product cycle scheduler started — generating 10+ products every 2 hours")
    # Start Agent Empire orchestrator
    try:
        orchestrator = get_orchestrator(db)
        await orchestrator.start_all()
        logger.info("✅ Agent Empire online — 6 divisions active")
    except Exception as e:
        logger.warning(f"Agent orchestrator start: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()

# Start the server
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    print(f"[INFO] Starting FastAPI server on http://0.0.0.0:{port}")
    print(f"[INFO] API Docs: http://0.0.0.0:{port}/docs")
    print(f"[INFO] ReDoc: http://0.0.0.0:{port}/redoc")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=os.environ.get('ENVIRONMENT') != 'production',
        log_level="info"
    )
