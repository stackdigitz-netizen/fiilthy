"""
Social Media Auto-Poster
Posts to TikTok, Instagram, Twitter automatically
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
import json

TIKTOK_API_BASE = "https://open.tiktokapis.com/v1"
INSTAGRAM_API_BASE = "https://graph.instagram.com/v18.0"


class SocialMediaAutoPoster:
    """Auto-post to all social platforms"""
    
    def __init__(self):
        self.tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.instagram_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.twitter_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.posts_created = 0
    
    async def generate_social_posts(self, product: Dict[str, Any], days: int = 90) -> List[Dict]:
        """Generate 3-6 month social content calendar"""
        
        posts = []
        
        # 6 posts per week = 156 posts for 6 months
        post_types = [
            "teaser",
            "benefit_highlight",
            "customer_story",
            "limited_offer",
            "tutorial_snippet",
            "problem_solver",
            "behind_scenes",
            "success_metric"
        ]
        
        current_date = datetime.utcnow()
        
        for week in range(26):  # 26 weeks = 6 months
            for day in range(6):  # 6 posts per week
                post_type = post_types[(week * 6 + day) % len(post_types)]
                post_date = current_date + timedelta(weeks=week, days=day)
                
                post = {
                    "product_id": product.get("id"),
                    "type": post_type,
                    "scheduled_date": post_date.isoformat(),
                    "content": self._generate_caption(product, post_type),
                    "hashtags": self._generate_hashtags(product),
                    "platforms": ["tiktok", "instagram", "twitter"],
                    "status": "scheduled"
                }
                posts.append(post)
        
        return posts
    
    def _generate_caption(self, product: Dict, post_type: str) -> str:
        """Generate caption based on post type"""
        
        captions = {
            "teaser": f"🔥 Something big is coming... {product.get('title', 'New Product')} 🚀 #comingsoon",
            "benefit_highlight": f"✨ Save hours with {product.get('title')} 💎 Limited time: 40% off",
            "customer_story": f"🎉 This changed everything for our users... {product.get('title')}",
            "limited_offer": f"⏰ 48 HOURS ONLY - {product.get('title')} at the lowest price ever",
            "tutorial_snippet": f"Learn this in 60 seconds with {product.get('title')} 📚 #productivity",
            "problem_solver": f"Tired of this? {product.get('title')} solves it permanently ✅",
            "behind_scenes": f"Here's how we built {product.get('title')} 👀 The story...",
            "success_metric": f"Users reported 10x productivity gains with {product.get('title')} 📊"
        }
        
        return captions.get(post_type, f"Check out {product.get('title')} 🎯")
    
    def _generate_hashtags(self, product: Dict) -> List[str]:
        """Generate relevant hashtags"""
        
        base_tags = ["#ProductLaunch", "#Productivity", "#Growth", "#MakeMoneyOnline"]
        product_tags = [f"#{tag.replace(' ', '')}" for tag in product.get("tags", [])[:3]]
        
        return base_tags + product_tags
    
    async def post_to_tiktok(self, post: Dict) -> Dict[str, Any]:
        """Post to TikTok"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.tiktok_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": post["content"],
                "video_title": post.get("product_id", "New Product"),
            }
            
            response = requests.post(
                f"{TIKTOK_API_BASE}/video/publish",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                self.posts_created += 1
                return {
                    "success": True,
                    "platform": "tiktok",
                    "url": response.json().get("data", {}).get("video_url"),
                    "posted_at": datetime.utcnow().isoformat()
                }
            return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def post_to_instagram(self, post: Dict, image_url: str = None) -> Dict[str, Any]:
        """Post to Instagram"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.instagram_token}",
                "Content-Type": "application/json"
            }
            
            caption = post["content"] + "\n" + " ".join(post.get("hashtags", []))
            
            payload = {
                "caption": caption,
                "image_url": image_url or "https://via.placeholder.com/1080x1080"
            }
            
            response = requests.post(
                f"{INSTAGRAM_API_BASE}/me/media",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                self.posts_created += 1
                return {
                    "success": True,
                    "platform": "instagram",
                    "post_id": response.json().get("id"),
                    "posted_at": datetime.utcnow().isoformat()
                }
            return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def schedule_posts(self, posts: List[Dict]) -> Dict[str, Any]:
        """Schedule all posts for future posting"""
        
        scheduled = []
        
        for post in posts:
            scheduled.append({
                "product_id": post.get("product_id"),
                "scheduled_date": post.get("scheduled_date"),
                "platforms": post.get("platforms"),
                "status": "queued"
            })
        
        return {
            "total_posts": len(scheduled),
            "scheduled_posts": scheduled,
            "coverage_days": 180
        }
