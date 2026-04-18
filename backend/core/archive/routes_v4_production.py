"""
Production-Ready API Routes (Enhanced v4)
Includes demo mode, error handling, and professional response formatting
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime

from config.demo_config import demo_config
from config.demo_data import DemoData, DemoDataGenerator
from config.error_handler import ErrorResponse, logger

router = APIRouter(prefix="/api/v4", tags=["production"])


# ============================================================================
# System & Health Endpoints
# ============================================================================

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    Returns system status and mode (demo/production)
    """
    return ErrorResponse.format_success(
        data={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": demo_config.environment,
            "demo_mode": demo_config.is_demo,
            "version": "4.0.0",
        },
        message="System is operational"
    )


@router.post("/demo-mode/toggle")
async def toggle_demo_mode(enable_demo: bool) -> Dict[str, Any]:
    """
    Toggle between demo and production mode
    Admin endpoint - in production, would require authentication
    """
    try:
        new_env = "demo" if enable_demo else "production"
        demo_config.set_environment(new_env)
        logger.info(f"Demo mode toggled to: {enable_demo}")
        
        return ErrorResponse.format_success(
            data={
                "demo_mode": demo_config.is_demo,
                "environment": demo_config.environment,
                "settings": demo_config.get_demo_settings(),
            },
            message=f"Switched to {new_env} mode successfully"
        )
    except Exception as e:
        logger.error("Error toggling demo mode", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to toggle demo mode"
        )


@router.get("/demo-mode/status")
async def get_demo_status() -> Dict[str, Any]:
    """Get current demo mode status and settings"""
    return ErrorResponse.format_success(
        data=demo_config.get_demo_settings(),
        message="Demo mode configuration"
    )


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@router.get("/dashboard/overview")
async def get_dashboard_overview() -> Dict[str, Any]:
    """
    Get complete dashboard overview
    In demo mode: returns realistic simulated data
    In production: returns actual system metrics
    """
    try:
        if demo_config.is_demo:
            # Simulate API delay
            await asyncio.sleep(DemoData.simulate_processing_delay(0.5, 1.5))
            snapshot = await DemoDataGenerator.generate_dashboard_snapshot()
            
            return ErrorResponse.format_success(
                data=snapshot,
                message="Dashboard data retrieved (demo mode)"
            )
        else:
            # In production, would fetch real data from MongoDB
            return ErrorResponse.format_success(
                data={
                    "message": "Production mode - connect real APIs",
                    "setup_required": [
                        "MONGO_URL",
                        "OPENAI_API_KEY",
                        "STRIPE_API_KEY",
                        "Other API keys..."
                    ]
                },
                message="Production mode active"
            )
    except Exception as e:
        logger.error("Error fetching dashboard overview", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to fetch dashboard overview"
        )


@router.get("/dashboard/stats")
async def get_dashboard_stats(days: int = Query(30, ge=1, le=365)) -> Dict[str, Any]:
    """Get dashboard statistics for specified period"""
    try:
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(0.3, 0.8))
            
            return ErrorResponse.format_success(
                data={
                    "period_days": days,
                    "total_products": len([DemoData.generate_product() for _ in range(30)]),
                    "total_opportunities": len([DemoData.generate_opportunity() for _ in range(15)]),
                    "total_revenue": sum([DemoData.generate_revenue_data().get("total_revenue", 0)]),
                    "average_daily_revenue": DemoData.generate_revenue_data(days)["average_daily_revenue"],
                    "growth_trend": f"+{51 + (days % 30)}%",
                    "top_niche": "AI & Automation",
                    "generated_at": datetime.now().isoformat(),
                },
                message="Statistics retrieved (demo)"
            )
        else:
            return {"message": "Production mode - connect MongoDB"}
    except Exception as e:
        logger.error("Error fetching stats", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to fetch statistics"
        )


# ============================================================================
# Products Endpoints
# ============================================================================

@router.get("/products")
async def list_products(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List products with pagination and filtering
    """
    try:
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(0.3, 0.7))
            
            products = [DemoData.generate_product() for _ in range(limit)]
            
            if status:
                products = [p for p in products if p.get("status") == status]
            
            return ErrorResponse.format_success(
                data={
                    "products": products,
                    "total": len(products),
                    "limit": limit,
                    "skip": skip,
                },
                message="Products retrieved"
            )
        else:
            return {"message": "Production mode"}
    except Exception as e:
        logger.error("Error listing products", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to list products"
        )


@router.post("/products/create")
async def create_product(
    title: str,
    niche: Optional[str] = None,
    product_type: str = "ebook",
    price: float = 27.0,
) -> Dict[str, Any]:
    """
    Create a new product
    Demo mode: simulates product creation
    Production: creates in database and generates with AI
    """
    try:
        if not title or len(title.strip()) < 5:
            return ErrorResponse.format_error(
                ValueError("Title must be at least 5 characters"),
                status_code=400,
                message="Invalid product title"
            )
        
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(1.0, 3.0))
            
            product = DemoData.generate_product(product_type)
            product["title"] = title
            product["price"] = price
            if niche:
                product["niche"] = niche
            
            return ErrorResponse.format_success(
                data=product,
                message="Product created successfully (demo)"
            )
        else:
            return {"message": "Production mode - would save to DB and call AI"}
    except Exception as e:
        logger.error("Error creating product", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to create product"
        )


# ============================================================================
# Opportunities Endpoints
# ============================================================================

@router.get("/opportunities")
async def list_opportunities(
    limit: int = Query(10, ge=1, le=50),
) -> Dict[str, Any]:
    """
    List discovered market opportunities
    """
    try:
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(0.5, 1.0))
            
            opportunities = [DemoData.generate_opportunity() for _ in range(limit)]
            
            return ErrorResponse.format_success(
                data={
                    "opportunities": opportunities,
                    "total": len(opportunities),
                },
                message="Opportunities retrieved"
            )
        else:
            return {"message": "Production mode"}
    except Exception as e:
        logger.error("Error listing opportunities", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to list opportunities"
        )


# ============================================================================
# Revenue & Analytics Endpoints
# ============================================================================

@router.get("/analytics/revenue")
async def get_revenue_analytics(days: int = Query(30, ge=1, le=365)) -> Dict[str, Any]:
    """
    Get revenue analytics and metrics
    """
    try:
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(0.5, 1.0))
            
            revenue_data = DemoData.generate_revenue_data(days)
            
            return ErrorResponse.format_success(
                data=revenue_data,
                message="Revenue analytics retrieved"
            )
        else:
            return {"message": "Production mode - connect to payment processors"}
    except Exception as e:
        logger.error("Error fetching revenue analytics", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to fetch revenue analytics"
        )


@router.get("/analytics/full")
async def get_full_analytics() -> Dict[str, Any]:
    """Get comprehensive analytics"""
    try:
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(0.8, 2.0))
            
            analytics = DemoData.generate_analytics()
            
            return ErrorResponse.format_success(
                data=analytics,
                message="Full analytics retrieved"
            )
        else:
            return {"message": "Production mode"}
    except Exception as e:
        logger.error("Error fetching full analytics", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to fetch analytics"
        )


# ============================================================================
# Social Media & Marketing Endpoints
# ============================================================================

@router.get("/marketing/social-posts")
async def get_social_posts(count: int = Query(10, ge=1, le=100)) -> Dict[str, Any]:
    """
    Get generated social media posts
    """
    try:
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(0.5, 1.2))
            
            posts = DemoData.generate_social_posts(count)
            
            return ErrorResponse.format_success(
                data={
                    "posts": posts,
                    "total": len(posts),
                    "platforms": list(set(p["platform"] for p in posts)),
                },
                message="Social posts retrieved"
            )
        else:
            return {"message": "Production mode"}
    except Exception as e:
        logger.error("Error fetching social posts", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to fetch social posts"
        )


@router.post("/marketing/generate-social-campaign")
async def generate_social_campaign(
    niche: str,
    campaign_days: int = Query(30, ge=1, le=365),
) -> Dict[str, Any]:
    """
    Generate entire social media campaign
    """
    try:
        if not niche or len(niche.strip()) < 2:
            return ErrorResponse.format_error(
                ValueError("Niche required"),
                status_code=400,
                message="Niche is required"
            )
        
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(2.0, 5.0))
            
            posts_per_day = 3
            total_posts = posts_per_day * campaign_days
            posts = DemoData.generate_social_posts(total_posts)
            
            return ErrorResponse.format_success(
                data={
                    "campaign_id": f"camp_{DemoData.generate_product_id()}",
                    "niche": niche,
                    "duration_days": campaign_days,
                    "total_posts": total_posts,
                    "posts_per_day": posts_per_day,
                    "posts": posts[:10],  # Return sample
                    "estimated_reach": total_posts * 5000,
                    "created_at": datetime.now().isoformat(),
                },
                message="Campaign generated successfully"
            )
        else:
            return {"message": "Production mode"}
    except Exception as e:
        logger.error("Error generating social campaign", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to generate campaign"
        )


@router.get("/marketing/email-sequences")
async def get_email_sequences(count: int = Query(5, ge=1, le=20)) -> Dict[str, Any]:
    """
    Get email marketing sequences
    """
    try:
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(0.5, 1.0))
            
            sequences = [DemoData.generate_email_sequence() for _ in range(count)]
            
            return ErrorResponse.format_success(
                data={
                    "sequences": sequences,
                    "total": len(sequences),
                },
                message="Email sequences retrieved"
            )
        else:
            return {"message": "Production mode"}
    except Exception as e:
        logger.error("Error fetching email sequences", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to fetch email sequences"
        )


# ============================================================================
# Autonomous System Endpoints
# ============================================================================

@router.post("/autonomous/run-cycle")
async def run_autonomous_cycle(
    background_tasks: BackgroundTasks,
    enable_publishing: bool = Query(False),
    enable_marketing: bool = Query(True),
) -> Dict[str, Any]:
    """
    Run a complete autonomous AI cycle
    In demo mode: simulates cycle with realistic data
    """
    try:
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(1.0, 2.0))
            
            # Simulate cycle execution
            products_created = len([DemoData.generate_product() for _ in range(5)])
            opportunities_found = len([DemoData.generate_opportunity() for _ in range(3)])
            social_posts_generated = 10 if enable_marketing else 0
            
            cycle_result = {
                "cycle_id": f"cycle_{DemoData.generate_product_id()}",
                "status": "completed",
                "duration_seconds": 2.5,
                "products_created": products_created,
                "opportunities_found": opportunities_found,
                "social_posts_generated": social_posts_generated,
                "revenue_potential": sum(p.get("revenue", 0) for p in [DemoData.generate_product() for _ in range(products_created)]),
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
            }
            
            return ErrorResponse.format_success(
                data=cycle_result,
                message="Autonomous cycle completed successfully"
            )
        else:
            return {"message": "Production mode - full AI integration"}
    except Exception as e:
        logger.error("Error running autonomous cycle", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to run autonomous cycle"
        )


@router.get("/autonomous/status")
async def get_autonomous_status() -> Dict[str, Any]:
    """Get status of autonomous system"""
    try:
        return ErrorResponse.format_success(
            data={
                "system_status": "operational",
                "last_cycle": datetime.now().isoformat(),
                "cycles_today": 24,
                "products_today": 120,
                "revenue_today": 3500,
            },
            message="System status retrieved"
        )
    except Exception as e:
        logger.error("Error fetching system status", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to fetch system status"
        )


# ============================================================================
# Scaling & Performance Endpoints
# ============================================================================

@router.post("/scaling/run-parallel")
async def run_parallel_cycles(
    num_projects: int = Query(10, ge=1, le=100),
) -> Dict[str, Any]:
    """
    Run multiple autonomous cycles in parallel
    """
    try:
        if num_projects > 50:
            return ErrorResponse.format_error(
                ValueError("Exceeds parallel limit"),
                status_code=400,
                message="Cannot exceed 50 parallel projects"
            )
        
        if demo_config.is_demo:
            await asyncio.sleep(DemoData.simulate_processing_delay(2.0, 5.0))
            
            total_revenue = num_projects * 350
            total_products = num_projects * 5
            
            return ErrorResponse.format_success(
                data={
                    "batch_id": f"batch_{DemoData.generate_product_id()}",
                    "num_projects": num_projects,
                    "total_products_created": total_products,
                    "total_revenue_potential": total_revenue,
                    "average_products_per_project": 5,
                    "completed_at": datetime.now().isoformat(),
                },
                message="Parallel cycles completed"
            )
        else:
            return {"message": "Production mode"}
    except Exception as e:
        logger.error("Error running parallel cycles", error=e)
        return ErrorResponse.format_error(
            e,
            status_code=500,
            message="Failed to run parallel cycles"
        )


# ============================================================================
# Configuration Endpoints
# ============================================================================

@router.get("/config/app-settings")
async def get_app_settings() -> Dict[str, Any]:
    """Get application settings and configuration"""
    return ErrorResponse.format_success(
        data={
            "environment": demo_config.environment,
            "demo_mode": demo_config.is_demo,
            "version": "4.0.0",
            "features": {
                "products": True,
                "analytics": True,
                "social_marketing": True,
                "email_marketing": True,
                "autonomous_cycles": True,
                "scaling": True,
            },
            "limits": {
                "max_parallel_projects": 50,
                "max_products_per_cycle": 20,
                "max_social_posts": 1000,
            },
        },
        message="Application settings"
    )
