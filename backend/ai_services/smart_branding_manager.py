"""
Smart Branding Manager - AI-powered branding with full manual control
Generates recommendations but allows complete customization
"""

import asyncio
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import uuid
from enum import Enum
import anthropic
import openai

logger = logging.getLogger(__name__)


class BrandingCategory(str, Enum):
    COLOR_PALETTE = "color_palette"
    TYPOGRAPHY = "typography"
    LOGO = "logo"
    IMAGERY = "imagery"
    TONE_OF_VOICE = "tone_of_voice"
    VISUAL_STYLE = "visual_style"


class SmartBrandingManager:
    """
    Manages product branding with AI recommendations and full manual control
    """
    
    def __init__(self, db=None):
        self.db = db
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate_branding_recommendations(
        self,
        product_id: str,
        product_title: str,
        product_description: str,
        target_audience: Dict[str, Any] = None,
        industry: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate AI-powered branding recommendations
        Includes: color palettes, typography, tone of voice, visual style
        """
        try:
            branding_id = f"brand-{uuid.uuid4().hex[:8]}"
            
            # Generate comprehensive branding recommendations
            recommendations = await asyncio.gather(
                self._generate_color_palette(product_title, product_description, industry),
                self._generate_typography(product_title, target_audience, industry),
                self._generate_tone_of_voice(product_title, product_description, target_audience),
                self._generate_visual_style(product_title, industry),
                self._generate_logo_concepts(product_title),
                self._generate_imagery_style(product_title, industry)
            )
            
            branding_package = {
                "id": branding_id,
                "product_id": product_id,
                "product_title": product_title,
                "status": "recommended",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "recommendations": {
                    "color_palette": recommendations[0],
                    "typography": recommendations[1],
                    "tone_of_voice": recommendations[2],
                    "visual_style": recommendations[3],
                    "logo_concepts": recommendations[4],
                    "imagery_style": recommendations[5]
                },
                "custom_overrides": {},
                "is_consistent": True
            }
            
            # Save to database
            if self.db:
                try:
                    branding_collection = self.db["product_branding"]
                    await branding_collection.insert_one(branding_package)
                except Exception as e:
                    logger.warning(f"Could not save branding to DB: {e}")
            
            return {
                "success": True,
                "branding_id": branding_id,
                "branding": branding_package
            }
        
        except Exception as e:
            logger.error(f"Branding generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _generate_color_palette(
        self,
        product_title: str,
        product_description: str,
        industry: str
    ) -> Dict[str, Any]:
        """Generate AI color palette recommendations"""
        try:
            prompt = f"""
            Generate a professional color palette for a product called "{product_title}".
            
            Description: {product_description}
            Industry: {industry}
            
            Provide exactly 5 colors in this JSON format:
            {{
                "primary": "#HEX_CODE",
                "secondary": "#HEX_CODE",
                "accent": "#HEX_CODE",
                "neutral": "#HEX_CODE",
                "highlight": "#HEX_CODE",
                "reasoning": "Why these colors work well together"
            }}
            """
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                palette = json.loads(json_match.group())
                return palette
            
            return self._default_color_palette()
        
        except Exception as e:
            logger.warning(f"Color palette generation failed: {e}")
            return self._default_color_palette()
    
    async def _generate_typography(
        self,
        product_title: str,
        target_audience: Dict[str, Any],
        industry: str
    ) -> Dict[str, Any]:
        """Generate typography recommendations"""
        try:
            audience_desc = json.dumps(target_audience) if target_audience else "general"
            
            prompt = f"""
            Recommend typography for a product called "{product_title}".
            
            Target Audience: {audience_desc}
            Industry: {industry}
            
            Provide typography recommendations in JSON format:
            {{
                "heading_font": "Font name and why",
                "body_font": "Font name and why",
                "accent_font": "Font name and why",
                "heading_size": "16px-32px range",
                "body_size": "12px-16px range",
                "line_height": "1.4-1.8",
                "font_weight_hierarchy": "description of weights to use"
            }}
            """
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                typography = json.loads(json_match.group())
                return typography
            
            return self._default_typography()
        
        except Exception as e:
            logger.warning(f"Typography generation failed: {e}")
            return self._default_typography()
    
    async def _generate_tone_of_voice(
        self,
        product_title: str,
        product_description: str,
        target_audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate tone of voice guidelines"""
        try:
            audience_desc = json.dumps(target_audience) if target_audience else "general"
            
            prompt = f"""
            Define tone of voice guidelines for a product: "{product_title}"
            
            Description: {product_description}
            Target Audience: {audience_desc}
            
            Provide guidelines in JSON format:
            {{
                "brand_personality": "adjectives describing the brand",
                "dos": ["list of things to do"],
                "donts": ["list of things to avoid"],
                "example_phrases": ["sample messaging"],
                "emotional_tone": "the emotional resonance",
                "language_style": "formal/casual/playful etc"
            }}
            """
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text, re.DOTALL)
            if json_match:
                tone = json.loads(json_match.group())
                return tone
            
            return self._default_tone_of_voice()
        
        except Exception as e:
            logger.warning(f"Tone of voice generation failed: {e}")
            return self._default_tone_of_voice()
    
    async def _generate_visual_style(
        self,
        product_title: str,
        industry: str
    ) -> Dict[str, Any]:
        """Generate visual style guidelines"""
        return {
            "style": "modern and clean",
            "imagery_style": "professional product shots with lifestyle context",
            "icon_style": "rounded, minimalist icons",
            "spacing": "generous white space",
            "corner_radius": "8-12px for consistency",
            "shadow_style": "subtle, soft shadows",
            "animation_style": "smooth, 0.3-0.5s transitions"
        }
    
    async def _generate_logo_concepts(self, product_title: str) -> List[Dict[str, Any]]:
        """Generate logo concept descriptions"""
        concepts = [
            {
                "concept": 1,
                "description": f"Abstract geometric shape representing {product_title}",
                "style": "Minimalist, modern",
                "colors": "Primary + Accent"
            },
            {
                "concept": 2,
                "description": f"Wordmark with custom typography for {product_title}",
                "style": "Bold, memorable",
                "colors": "Primary color only"
            },
            {
                "concept": 3,
                "description": f"Icon + logotype combination for {product_title}",
                "style": "Versatile, scalable",
                "colors": "Multi-color"
            }
        ]
        return concepts
    
    async def _generate_imagery_style(self, product_title: str, industry: str) -> Dict[str, Any]:
        """Generate imagery style guidelines"""
        return {
            "photography_style": "high-quality, well-lit product photography",
            "composition": "rule of thirds with breathing room",
            "filters": "subtle color grading, consistent saturation",
            "models": "diverse, relatable, authentic",
            "background": "clean, minimal, or lifestyle context",
            "mood": "professional, trustworthy, aspirational"
        }
    
    async def update_branding_element(
        self,
        branding_id: str,
        category: BrandingCategory,
        custom_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Allow user to override AI recommendations for any branding element
        Full manual control while maintaining consistency checks
        """
        try:
            if self.db:
                branding_collection = self.db["product_branding"]
                
                # Get existing branding
                existing = await branding_collection.find_one({"id": branding_id})
                if not existing:
                    return {"success": False, "error": "Branding not found"}
                
                # Update the specific category
                update = {
                    "custom_overrides": existing.get("custom_overrides", {})
                }
                update["custom_overrides"][category.value] = {
                    "values": custom_values,
                    "overridden_at": datetime.now(timezone.utc).isoformat(),
                    "is_custom": True
                }
                
                # Check consistency
                consistency_check = self._check_branding_consistency(
                    existing,
                    category,
                    custom_values
                )
                
                update["is_consistent"] = consistency_check["is_consistent"]
                if not consistency_check["is_consistent"]:
                    update["consistency_warnings"] = consistency_check["warnings"]
                
                # Save update
                await branding_collection.update_one(
                    {"id": branding_id},
                    {"$set": update}
                )
                
                return {
                    "success": True,
                    "branding_id": branding_id,
                    "category": category.value,
                    "is_consistent": consistency_check["is_consistent"],
                    "warnings": consistency_check.get("warnings", [])
                }
            
            return {"success": False, "error": "Database not available"}
        
        except Exception as e:
            logger.error(f"Branding update failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _check_branding_consistency(
        self,
        branding: Dict[str, Any],
        category: BrandingCategory,
        custom_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if branding elements work together cohesively"""
        warnings = []
        
        # Color consistency checks
        if category == BrandingCategory.COLOR_PALETTE:
            colors = custom_values.get("colors", {})
            if len(set(colors.values())) < 3:
                warnings.append("⚠️ Only 2+ distinct colors recommended for contrast")
        
        # Typography consistency checks
        if category == BrandingCategory.TYPOGRAPHY:
            fonts = [custom_values.get("heading_font"), custom_values.get("body_font")]
            if fonts[0] == fonts[1]:
                warnings.append("⚠️ Consider using different fonts for heading vs body for hierarchy")
        
        # Visual style checks
        if category == BrandingCategory.VISUAL_STYLE:
            if "corner_radius" in custom_values:
                if custom_values["corner_radius"] > 20:
                    warnings.append("⚠️ Large corner radius might reduce professional appearance")
        
        return {
            "is_consistent": len(warnings) == 0,
            "warnings": warnings
        }
    
    async def get_branding_full(self, branding_id: str) -> Dict[str, Any]:
        """Get complete branding package with AI recommendations + custom overrides"""
        try:
            if self.db:
                branding_collection = self.db["product_branding"]
                branding = await branding_collection.find_one({"id": branding_id})
                
                if branding:
                    branding.pop("_id", None)
                    
                    # Merge recommendations with custom overrides
                    final_branding = self._merge_branding(branding)
                    
                    return {
                        "success": True,
                        "branding_id": branding_id,
                        "ai_recommendations": branding.get("recommendations", {}),
                        "custom_overrides": branding.get("custom_overrides", {}),
                        "final_branding": final_branding,
                        "is_consistent": branding.get("is_consistent", True)
                    }
            
            return {"success": False, "error": "Branding not found"}
        
        except Exception as e:
            logger.error(f"Error fetching branding: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _merge_branding(self, branding: Dict[str, Any]) -> Dict[str, Any]:
        """Merge AI recommendations with custom overrides"""
        final = branding.get("recommendations", {}).copy()
        
        for category, override in branding.get("custom_overrides", {}).items():
            if override.get("is_custom"):
                final[category] = override.get("values", final.get(category, {}))
        
        return final
    
    def _default_color_palette(self) -> Dict[str, Any]:
        """Fallback color palette"""
        return {
            "primary": "#667eea",
            "secondary": "#764ba2",
            "accent": "#f093fb",
            "neutral": "#e0e0e0",
            "highlight": "#ffd89b",
            "reasoning": "Modern, vibrant gradient palette with good contrast"
        }
    
    def _default_typography(self) -> Dict[str, Any]:
        """Fallback typography"""
        return {
            "heading_font": "Inter, sans-serif",
            "body_font": "Inter, sans-serif",
            "accent_font": "Poppins, sans-serif",
            "heading_size": "24px-32px",
            "body_size": "14px-16px",
            "line_height": "1.6",
            "font_weight_hierarchy": "Regular (400) for body, Semi-bold (600) for subheadings, Bold (700) for headings"
        }
    
    def _default_tone_of_voice(self) -> Dict[str, Any]:
        """Fallback tone of voice"""
        return {
            "brand_personality": "Professional, trustworthy, innovative, helpful",
            "dos": ["Be clear and direct", "Use active voice", "Help the customer achieve goals"],
            "donts": ["Use jargon without explanation", "Be condescending", "Make promises you can't keep"],
            "example_phrases": ["Make it happen", "Your success is our mission"],
            "emotional_tone": "Confident and supportive",
            "language_style": "Professional yet approachable"
        }


def get_branding_manager(db=None) -> SmartBrandingManager:
    """Factory function for branding manager"""
    return SmartBrandingManager(db)
