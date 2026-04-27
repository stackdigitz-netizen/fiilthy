"""
Branding Management Routes - Full control over product branding
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

from ai_services.smart_branding_manager import get_branding_manager, BrandingCategory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/branding", tags=["branding"])


# Models
class BrandingGenerationRequest(BaseModel):
    product_id: str
    product_title: str
    product_description: str
    target_audience: Optional[Dict[str, Any]] = None
    industry: str = "general"


class BrandingUpdateRequest(BaseModel):
    category: str  # color_palette, typography, tone_of_voice, visual_style, logo, imagery
    custom_values: Dict[str, Any]


class ColorPaletteOverride(BaseModel):
    primary: str
    secondary: str
    accent: str
    neutral: str
    highlight: str


class TypographyOverride(BaseModel):
    heading_font: str
    body_font: str
    accent_font: str
    heading_size: str
    body_size: str
    line_height: str


# Endpoints

@router.post("/generate")
async def generate_branding(
    request: BrandingGenerationRequest,
    background_tasks: BackgroundTasks,
    db = None
):
    """
    Generate AI-powered branding recommendations for a product
    Fully editable - user can override any element
    """
    try:
        manager = get_branding_manager(db)
        
        result = await manager.generate_branding_recommendations(
            product_id=request.product_id,
            product_title=request.product_title,
            product_description=request.product_description,
            target_audience=request.target_audience,
            industry=request.industry
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Branding generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{branding_id}")
async def update_branding_element(
    branding_id: str,
    request: BrandingUpdateRequest,
    db = None
):
    """
    Update a specific branding element
    User has full control to customize any aspect
    Consistency checks applied to ensure cohesive branding
    """
    try:
        manager = get_branding_manager(db)
        
        # Validate category
        try:
            category = BrandingCategory[request.category.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join([c.value for c in BrandingCategory])}"
            )
        
        result = await manager.update_branding_element(
            branding_id=branding_id,
            category=category,
            custom_values=request.custom_values
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Branding update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{branding_id}")
async def get_branding(branding_id: str, db = None):
    """
    Get complete branding package
    Returns merged AI recommendations + custom overrides
    """
    try:
        manager = get_branding_manager(db)
        result = await manager.get_branding_full(branding_id)
        return result
    
    except Exception as e:
        logger.error(f"Error fetching branding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/colors/{branding_id}")
async def update_color_palette(
    branding_id: str,
    colors: ColorPaletteOverride,
    db = None
):
    """Update color palette with custom colors"""
    try:
        manager = get_branding_manager(db)
        
        result = await manager.update_branding_element(
            branding_id=branding_id,
            category=BrandingCategory.COLOR_PALETTE,
            custom_values=colors.dict()
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Color update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/typography/{branding_id}")
async def update_typography(
    branding_id: str,
    typography: TypographyOverride,
    db = None
):
    """Update typography settings"""
    try:
        manager = get_branding_manager(db)
        
        result = await manager.update_branding_element(
            branding_id=branding_id,
            category=BrandingCategory.TYPOGRAPHY,
            custom_values=typography.dict()
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Typography update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tone/{branding_id}")
async def update_tone_of_voice(
    branding_id: str,
    tone: Dict[str, Any],
    db = None
):
    """Update tone of voice guidelines"""
    try:
        manager = get_branding_manager(db)
        
        result = await manager.update_branding_element(
            branding_id=branding_id,
            category=BrandingCategory.TONE_OF_VOICE,
            custom_values=tone
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Tone update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visual-style/{branding_id}")
async def update_visual_style(
    branding_id: str,
    style: Dict[str, Any],
    db = None
):
    """Update visual style guidelines"""
    try:
        manager = get_branding_manager(db)
        
        result = await manager.update_branding_element(
            branding_id=branding_id,
            category=BrandingCategory.VISUAL_STYLE,
            custom_values=style
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Visual style update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
