"""
Social Media AI
Automatically generates and schedules social media posts
"""
import asyncio
from typing import Dict, Any, List
import random
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class SocialMediaAI:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        self.platforms = ["Twitter/X", "LinkedIn", "Instagram", "TikTok", "Facebook"]
        
    async def generate_posts(self, product: Dict[str, Any], num_posts: int = 5) -> List[Dict[str, Any]]:
        """
        Generate social media posts for a product
        
        Args:
            product: Product dictionary
            num_posts: Number of posts to generate
            
        Returns:
            List of social media post dictionaries
        """
        
        # Initialize AI chat
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"social-media-{datetime.now().timestamp()}",
            system_message="You are a social media marketing expert. You create engaging, platform-optimized content that drives clicks and conversions. You understand platform-specific best practices."
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""
Create {num_posts} social media posts for this product:

Product: {product.get('title', 'Unknown Product')}
Description: {product.get('description', '')}
Type: {product.get('product_type', 'digital product')}
Price: ${product.get('price', 0)}

Generate posts optimized for different platforms:
- Twitter/X: Short, punchy, with hashtags
- LinkedIn: Professional, value-focused
- Instagram: Visual-focused with emojis
- TikTok: Casual, trend-aware
- Facebook: Conversational, community-focused

For each post provide:
1. Platform
2. Post content (optimized length for platform)
3. 3-5 relevant hashtags
4. Best posting time (morning/afternoon/evening)
5. Call-to-action

Return as JSON:
{{
  "posts": [
    {{
      "platform": "Twitter/X",
      "content": "Post content here...",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "post_time": "morning",
      "cta": "Get it now →",
      "engagement_type": "click/comment/share"
    }}
  ]
}}
"""
        
        try:
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            import json
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            posts = data.get("posts", [])
            if not isinstance(posts, list) or len(posts) == 0:
                return self._get_fallback_posts(product)
            
            # Add scheduling and IDs
            scheduled_posts = []
            base_time = datetime.now(timezone.utc)
            
            for i, post in enumerate(posts):
                # Schedule posts at different times
                time_offset = timedelta(hours=i * 4)
                scheduled_time = base_time + time_offset
                
                post["id"] = f"post-{random.randint(1000, 9999)}"
                post["scheduled_time"] = scheduled_time.isoformat()
                post["status"] = "scheduled"
                post["product_id"] = product.get("id")
                post["created_at"] = datetime.now(timezone.utc).isoformat()
                post["engagement"] = {
                    "views": 0,
                    "clicks": 0,
                    "likes": 0,
                    "shares": 0
                }
                scheduled_posts.append(post)
            
            return scheduled_posts
            
        except Exception as e:
            print(f"Error generating social posts: {str(e)}")
            return self._get_fallback_posts(product)
    
    def _get_fallback_posts(self, product: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback posts if AI fails"""
        title = product.get('title', 'Amazing Product')
        return [
            {
                "id": f"post-{random.randint(1000, 9999)}",
                "platform": "Twitter/X",
                "content": f"🚀 Just launched: {title}! Transform your workflow today. {product.get('description', '')[:50]}...",
                "hashtags": ["#productivity", "#digital"],
                "post_time": "morning",
                "cta": "Learn more →",
                "scheduled_time": datetime.now(timezone.utc).isoformat(),
                "status": "scheduled",
                "product_id": product.get("id"),
                "engagement": {"views": 0, "clicks": 0, "likes": 0, "shares": 0}
            }
        ]
