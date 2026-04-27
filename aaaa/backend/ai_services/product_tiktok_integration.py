"""
Product + TikTok Integration
Automatically post products to TikTok after creation
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from ai_services.tiktok_manager import get_tiktok_manager
from ai_services.social_media_ai import SocialMediaAI


class ProductTikTokIntegration:
    """Post products to TikTok automatically"""
    
    def __init__(self):
        self.tiktok_manager = get_tiktok_manager()
        self.social_media_ai = SocialMediaAI()
    
    async def post_product_to_tiktok(
        self,
        product: Dict[str, Any],
        video_file: Optional[str] = None,
        auto_generate_caption: bool = True
    ) -> Dict[str, Any]:
        """
        Post a created product to TikTok
        
        Args:
            product: Product data with title, description, price, etc.
            video_file: Optional path to product video/demo
            auto_generate_caption: Generate caption using AI if True
        
        Returns:
            Result of TikTok post
        """
        try:
            # Generate caption if not provided
            if auto_generate_caption:
                caption = await self._generate_product_caption(product)
            else:
                caption = product.get("caption", product.get("title", "Check out this product!"))
            
            hashtags = await self._generate_hashtags(product)
            
            post_data = {
                "caption": caption,
                "hashtags": hashtags,
                "privacy_level": "PUBLIC"
            }
            
            # Add video if provided
            if video_file:
                post_data["video_file_path"] = video_file
            
            # Post to TikTok
            result = await self.tiktok_manager.post_video(post_data)
            
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "platform": "tiktok",
                    "product_id": product.get("id"),
                    "video_id": result.get("video_id"),
                    "post_url": result.get("post_url"),
                    "caption": caption,
                    "hashtags": hashtags,
                    "posted_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": result.get("message", "Failed to post to TikTok")
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def post_product_series_to_tiktok(
        self,
        product: Dict[str, Any],
        series_count: int = 5
    ) -> Dict[str, Any]:
        """
        Create and post a series of videos for a product
        
        Args:
            product: Product to promote
            series_count: Number of videos to create (5-10 recommended)
        
        Returns:
            Results of all posts
        """
        try:
            # Generate different angles/hooks
            captions = await self._generate_product_series(product, series_count)
            
            results = []
            for i, caption in enumerate(captions):
                result = await self.tiktok_manager.post_video({
                    "caption": caption,
                    "hashtags": await self._generate_hashtags(product),
                    "privacy_level": "PUBLIC"
                })
                
                results.append({
                    "video_number": i + 1,
                    "status": result.get("status"),
                    "video_id": result.get("video_id"),
                    "caption": caption
                })
            
            return {
                "status": "success",
                "product_id": product.get("id"),
                "videos_posted": len(results),
                "results": results,
                "message": f"Posted {len(results)} videos for {product.get('title')}"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _generate_product_caption(self, product: Dict[str, Any]) -> str:
        """Generate engaging TikTok caption for product"""
        try:
            title = product.get("title", "Product")
            description = product.get("description", "")
            price = product.get("price", "")
            
            prompt = f"""
Create a SHORT, engaging TikTok caption (max 150 chars) for this product:

Title: {title}
Description: {description}
Price: ${price}

Make it punchy, use relevant emojis, and include a call-to-action.
Format: Just the caption text, nothing else.
"""
            
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            chat = LlmChat(api_key="", session_id="product-caption").with_model("openai", "gpt-3.5-turbo")
            response = await chat.send_message(UserMessage(content=prompt))
            
            return response or title
        
        except Exception as e:
            # Fallback caption
            return f"🚀 {product.get('title', 'New Product')} - Limited time offer! 🔥"
    
    async def _generate_hashtags(self, product: Dict[str, Any]) -> list:
        """Generate relevant hashtags for product"""
        try:
            base_hashtags = ["productlaunch", "newtoy", "producthunt", "startup"]
            
            # Add category-specific hashtags
            category = product.get("category", "").lower()
            
            category_hashtags = {
                "ai": ["ai", "artificialintelligence", "aitools"],
                "course": ["learning", "education", "onlinecourse", "skillbuilding"],
                "template": ["template", "design", "producttemplate"],
                "software": ["software", "saas", "app", "productivity"],
                "book": ["book", "author", "writing", "kindle"]
            }
            
            specific = []
            for key, tags in category_hashtags.items():
                if key in category:
                    specific.extend(tags)
                    break
            
            return (base_hashtags + specific[:3])[:8]  # Max 8 hashtags
        
        except:
            return ["productlaunch", "newtoy", "startup"]
    
    async def _generate_product_series(self, product: Dict[str, Any], count: int) -> list:
        """Generate multiple video captions with different angles"""
        angles = [
            "benefit-focused",
            "pain-point",
            "social-proof",
            "limited-offer",
            "problem-solution"
        ]
        
        captions = []
        title = product.get("title", "Product")
        
        angle_templates = {
            "benefit-focused": f"🎯 {title} will literally change your life... 🚀",
            "pain-point": f"Tired of the OLD way? {title} fixes it ALL",
            "social-proof": f"10K+ people are using {title}... are YOU? 🔥",
            "limited-offer": f"⏰ LIMITED TIME: Get {title} before prices go UP",
            "problem-solution": f"Problem: [issue]. Solution: {title} ✅"
        }
        
        for i in range(min(count, len(angles))):
            angle = angles[i % len(angles)]
            captions.append(angle_templates.get(angle, f"Check out {title}!"))
        
        return captions
    
    async def schedule_product_posts(
        self,
        product: Dict[str, Any],
        schedule_dates: list
    ) -> Dict[str, Any]:
        """
        Schedule product posts for specific dates
        
        Args:
            product: Product to post
            schedule_dates: List of ISO datetime strings
        
        Returns:
            Scheduled post confirmations
        """
        try:
            captions = await self._generate_product_series(product, len(schedule_dates))
            results = []
            
            for date, caption in zip(schedule_dates, captions):
                result = await self.tiktok_manager.schedule_post(
                    {
                        "caption": caption,
                        "hashtags": await self._generate_hashtags(product)
                    },
                    date
                )
                results.append({
                    "schedule_time": date,
                    "scheduled_id": result.get("scheduled_id"),
                    "status": result.get("status")
                })
            
            return {
                "status": "success",
                "product_id": product.get("id"),
                "posts_scheduled": len(results),
                "results": results
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Singleton instance
_integration = None


def get_product_tiktok_integration() -> ProductTikTokIntegration:
    """Get or create product-TikTok integration"""
    global _integration
    if _integration is None:
        _integration = ProductTikTokIntegration()
    return _integration
