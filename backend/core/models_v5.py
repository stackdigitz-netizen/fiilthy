"""
Enhanced Database Models for AI Product Development Factory v5
MongoDB schemas for products, branding, sales funnels, analytics, and growth
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ProductType(str, Enum):
    EBOOK = "ebook"
    COURSE = "course"
    TOOL = "tool"
    TEMPLATE = "template"
    PROMPT_PACK = "prompt_pack"
    LEAD_MAGNET = "lead_magnet"
    SAAS = "saas"
    PDF_GUIDE = "pdf_guide"
    SOCIAL_PACK = "social_pack"
    AUTOMATION = "automation"


class ProductStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    GENERATED = "generated"
    BRANDING = "branding"
    FUNNEL_BUILDING = "funnel_building"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    OPTIMIZING = "optimizing"
    ARCHIVED = "archived"


class ContentType(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM_REEL = "instagram_reel"
    FACEBOOK_POST = "facebook_post"
    TWITTER_THREAD = "twitter_thread"
    YOUTUBE_SHORT = "youtube_short"
    BLOG_POST = "blog_post"
    EMAIL = "email"
    AD_COPY = "ad_copy"


class ExperimentType(str, Enum):
    PRICE_TEST = "price_test"
    COPY_TEST = "copy_test"
    DESIGN_TEST = "design_test"
    AUDIENCE_TEST = "audience_test"
    LANDING_PAGE_TEST = "landing_page_test"


class ExperimentStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# ============================================================================
# PRODUCT & CONTENT
# ============================================================================

class ProductMetadata(BaseModel):
    """Metadata about a product"""
    niche: str
    target_audience: str
    unique_value_prop: str
    pain_points: List[str]
    keywords: List[str]
    market_size: Optional[str] = None
    competition_level: Optional[str] = None  # low, medium, high


class ProductContent(BaseModel):
    """Content files for a product"""
    title: str
    description: str
    long_description: str
    main_file_url: Optional[str] = None  # PDF, ZIP, etc
    supplementary_files: List[Dict[str, str]] = Field(default_factory=list)  # {name, url}
    preview_url: Optional[str] = None
    file_size_kb: int = 0
    demo_content: Optional[str] = None


class Product(BaseModel):
    """Main product model"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: str
    type: ProductType
    status: ProductStatus = ProductStatus.DRAFT
    
    # Core content
    metadata: ProductMetadata
    content: ProductContent
    
    # Pricing
    price: float
    currency: str = "USD"
    tier_2_price: Optional[float] = None
    tier_3_price: Optional[float] = None
    
    # Branding reference
    branding_id: Optional[str] = None
    
    # Funnel reference
    funnel_id: Optional[str] = None
    
    # Publishing info
    published_platforms: List[str] = Field(default_factory=list)
    shopify_store_url: Optional[str] = None
    gumroad_url: Optional[str] = None
    website_store_url: Optional[str] = None
    
    # Stats
    views: int = 0
    clicks: int = 0
    sales: int = 0
    revenue: float = 0.0
    refunds: int = 0
    refund_rate: float = 0.0
    
    # Relationships
    content_assets: List[str] = Field(default_factory=list)  # Asset IDs
    marketing_assets: List[str] = Field(default_factory=list)  # Marketing asset IDs
    experiments: List[str] = Field(default_factory=list)  # Experiment IDs
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    launched_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    
    # AI metadata
    generated_by_ai: bool = True
    generation_prompt: Optional[str] = None


# ============================================================================
# BRANDING
# ============================================================================

class BrandingAssets(BaseModel):
    """All branding assets for a product"""
    logo_url: str
    logo_variations: List[str] = Field(default_factory=list)
    favicon_url: Optional[str] = None
    
    # Cover/display images
    cover_image_url: str
    cover_variations: List[str] = Field(default_factory=list)
    
    # Thumbnails
    thumbnail_16_9_url: str
    thumbnail_1_1_url: str
    thumbnail_9_16_url: str
    
    # Landing page visuals
    hero_image_url: str
    feature_images: List[str] = Field(default_factory=list)
    benefit_graphics: List[str] = Field(default_factory=list)
    testimonial_graphics: List[str] = Field(default_factory=list)
    
    # Ad creatives
    ad_creative_facebook_url: str
    ad_creative_instagram_url: str
    ad_creative_tiktok_url: str
    ad_creative_pinterest_urls: List[str] = Field(default_factory=list)
    
    # Social media templates
    instagram_post_template: str
    instagram_story_template: str
    facebook_post_template: str
    twitter_header_template: str
    tiktok_thumbnail: str
    
    # Email templates
    email_header: str
    email_footer: str


class ColorPalette(BaseModel):
    """Brand color palette"""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    success: str
    warning: str
    error: str


class BrandGuidelines(BaseModel):
    """Complete brand guidelines"""
    brand_name: str
    tagline: str
    mission: str
    tone_of_voice: str
    
    # Visual identity
    colors: ColorPalette
    primary_font: str
    secondary_font: str
    
    # Usage guidelines
    logo_usage_rules: str
    imagery_style: str
    messaging_principles: List[str]


class ProductBranding(BaseModel):
    """Branding package for a product"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    product_id: str
    
    assets: BrandingAssets
    guidelines: BrandGuidelines
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_regenerated_at: Optional[datetime] = None
    regeneration_count: int = 0


# ============================================================================
# SALES FUNNEL
# ============================================================================

class EmailTemplate(BaseModel):
    """Email template in a sequence"""
    sequence_number: int
    subject: str
    preview_text: str
    body_html: str
    send_delay_hours: int
    personalization_variables: List[str] = Field(default_factory=list)


class FunnelPage(BaseModel):
    """A page in the sales funnel"""
    page_type: str  # landing, product, checkout, upsell, downsell, thank_you
    title: str
    meta_description: str
    headline: str
    subheadline: str
    body_html: str
    cta_text: str
    cta_color: str
    form_fields: List[Dict[str, str]] = Field(default_factory=list)  # {label, type, required}
    images: List[str] = Field(default_factory=list)
    conversion_tracking_id: Optional[str] = None


class SalesFunnel(BaseModel):
    """Complete sales funnel for a product"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    product_id: str
    
    # Funnel pages
    landing_page: FunnelPage
    product_page: FunnelPage
    checkout_page: FunnelPage
    upsell_page: Optional[FunnelPage] = None
    downsell_page: Optional[FunnelPage] = None
    thank_you_page: FunnelPage
    
    # Email sequences
    email_sequences: List[EmailTemplate] = Field(default_factory=list)
    abandoned_cart_sequence: List[EmailTemplate] = Field(default_factory=list)
    
    # Referral program
    referral_enabled: bool = False
    referral_commission_percentage: float = 10.0
    referral_page_html: Optional[str] = None
    
    # Payment settings
    stripe_product_id: Optional[str] = None
    payment_gateway: str = "stripe"  # stripe, gumroad, shopify, etc
    
    # A/B test setup
    primary_variant_id: str = "default"
    test_variants: Dict[str, FunnelPage] = Field(default_factory=dict)
    
    # Analytics
    views: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0
    avg_order_value: float = 0.0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_optimization_at: Optional[datetime] = None


# ============================================================================
# MARKETING ASSETS
# ============================================================================

class MarketingAsset(BaseModel):
    """Marketing asset (video script, post, ad copy, etc)"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    product_id: str
    
    type: ContentType
    platform: str  # tiktok, instagram, facebook, twitter, youtube, blog, email, ads
    
    # Content
    title: str
    content: str
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    cta: str
    
    # Media
    media_urls: List[str] = Field(default_factory=list)
    video_script: Optional[str] = None
    video_duration_seconds: Optional[int] = None
    
    # Scheduling
    scheduled_posting_times: List[datetime] = Field(default_factory=list)
    posted_at: Optional[datetime] = None
    auto_post_enabled: bool = True
    
    # Performance
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    conversions: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    posted_platforms: List[str] = Field(default_factory=list)


class ContentCalendar(BaseModel):
    """Content calendar for a product"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    product_id: str
    
    # Calendar data
    assets: List[str] = Field(default_factory=list)  # Asset IDs
    total_pieces: int = 0
    posting_frequency: str  # daily, every_other_day, weekly
    auto_scheduling_enabled: bool = True
    regenerate_on_failure: bool = True
    
    # Coverage
    platforms_covered: List[str] = Field(default_factory=list)
    content_types: List[ContentType] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    ends_at: Optional[datetime] = None


# ============================================================================
# ANALYTICS
# ============================================================================

class DailyMetrics(BaseModel):
    """Daily performance metrics"""
    date: datetime
    
    # Traffic
    views: int = 0
    visitors: int = 0
    sessions: int = 0
    avg_session_duration: float = 0.0
    
    # Engagement
    clicks: int = 0
    ctr: float = 0.0  # Click-through rate
    time_on_page: float = 0.0
    
    # Conversions
    conversions: int = 0
    conversion_rate: float = 0.0
    revenue: float = 0.0
    avg_order_value: float = 0.0
    
    # Customer
    new_customers: int = 0
    returning_customers: int = 0
    
    # Refunds
    refunds: int = 0
    refund_revenue: float = 0.0
    
    # Traffic sources
    source_breakdown: Dict[str, int] = Field(default_factory=dict)  # {source: count}
    platform_breakdown: Dict[str, int] = Field(default_factory=dict)  # {platform: count}


class Analytics(BaseModel):
    """Product analytics"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    product_id: str
    
    # Aggregated metrics
    total_views: int = 0
    total_clicks: int = 0
    total_conversions: int = 0
    total_revenue: float = 0.0
    total_refunds: int = 0
    total_customers: int = 0
    
    # Rates
    overall_ctr: float = 0.0
    overall_conversion_rate: float = 0.0
    overall_refund_rate: float = 0.0
    
    # Customer metrics
    avg_customer_value: float = 0.0
    repeat_purchase_rate: float = 0.0
    churn_rate: float = 0.0
    
    # Time series
    daily_metrics: List[DailyMetrics] = Field(default_factory=list)
    
    # Channel breakdown
    channel_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# GROWTH & EXPERIMENTS
# ============================================================================

class ExperimentVariant(BaseModel):
    """Variant in an experiment"""
    variant_id: str
    name: str
    description: str
    
    # For different experiment types
    price: Optional[float] = None
    copy_version: Optional[str] = None
    design_version: Optional[str] = None
    target_audience: Optional[str] = None
    landing_page_id: Optional[str] = None
    
    # Results
    views: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0
    revenue: float = 0.0


class GrowthExperiment(BaseModel):
    """A/B test or growth experiment"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    product_id: str
    
    type: ExperimentType
    status: ExperimentStatus = ExperimentStatus.RUNNING
    
    # Variants
    control_variant: ExperimentVariant
    test_variants: List[ExperimentVariant] = Field(default_factory=list)
    
    # Configuration
    split_traffic_percentage: float = 50.0
    min_sample_size: int = 100
    confidence_level: float = 0.95
    
    # Results
    winner_variant_id: Optional[str] = None
    winner_improvement_percentage: float = 0.0
    statistical_significance: float = 0.0
    
    # Timeline
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    scheduled_end_date: Optional[datetime] = None


# ============================================================================
# OPPORTUNITIES
# ============================================================================

class OpportunityMetrics(BaseModel):
    """Metrics for a market opportunity"""
    search_volume: int
    cpc: float
    competition_level: str  # low, medium, high
    demand_signal: float  # 0-100
    trending_score: float  # 0-100
    viral_potential: float  # 0-100
    market_size: str  # $10k, $100k, $1M, etc


class MarketOpportunity(BaseModel):
    """Market opportunity to target"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    
    niche: str
    sub_niche: str
    keywords: List[str]
    pain_points: List[str]
    target_audience_profile: Dict[str, str]
    
    metrics: OpportunityMetrics
    
    # Products already created in this niche
    existing_products: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommended_product_types: List[ProductType] = Field(default_factory=list)
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    discovered_at: datetime = Field(default_factory=datetime.now)
    last_updated_at: datetime = Field(default_factory=datetime.now)
    flagged_for_creation: bool = False


# ============================================================================
# AUTOMATION & WORKFLOW
# ============================================================================

class AutomationWorkflow(BaseModel):
    """Automation workflow configuration"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    product_id: str
    
    name: str
    description: str
    enabled: bool = True
    
    # Workflow steps
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Triggers
    trigger_type: str  # manual, schedule, event
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Retry policy
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    # Notifications
    notify_on_success: bool = True
    notify_on_failure: bool = True
    notification_emails: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[str] = None


class TaskQueue(BaseModel):
    """Background task in queue"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    
    product_id: str
    task_type: str  # generate, publish, optimize, etc
    status: str  # pending, running, completed, failed
    
    priority: int = 0  # 0 = normal, 1+ = high priority
    
    # Task data
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Retry
    retry_count: int = 0
    max_retries: int = 3
    
    # Timeline
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ============================================================================
# SETTINGS & CONFIG
# ============================================================================

class PlatformIntegration(BaseModel):
    """Platform integration settings"""
    platform_name: str
    enabled: bool = False
    api_key: Optional[str] = None  # Encrypted in real system
    credentials: Dict[str, Any] = Field(default_factory=dict)  # Encrypted
    rate_limit: Optional[int] = None
    auto_publish_enabled: bool = False
    auto_monetize_enabled: bool = False
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None


class FactorySettings(BaseModel):
    """Global factory settings"""
    id: str = "factory_settings"
    
    # API keys
    openai_api_key: Optional[str] = None  # Encrypted
    anthropic_api_key: Optional[str] = None  # Encrypted
    dalle_api_key: Optional[str] = None  # Encrypted
    
    # Platform integrations
    integrations: Dict[str, PlatformIntegration] = Field(default_factory=dict)
    
    # Automation settings
    auto_generation_enabled: bool = True
    max_products_per_day: int = 10
    daily_generation_schedule: str = "06:00-22:00"  # UTC
    
    # Default configurations
    default_product_price: float = 27.0
    default_currency: str = "USD"
    default_commission_rate: float = 30.0  # Revenue share
    
    # Growth settings
    auto_scaling_enabled: bool = True
    a_b_test_enabled: bool = True
    bundle_creation_enabled: bool = True
    
    # Notification settings
    admin_email: str
    alert_on_high_refund_rate: bool = True
    refund_rate_threshold: float = 10.0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

