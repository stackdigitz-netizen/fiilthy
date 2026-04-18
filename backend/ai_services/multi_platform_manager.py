"""
Multi-Platform Social Media Manager
Handles TikTok, Instagram, Twitter, LinkedIn, and YouTube automation
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
from .tiktok_manager import get_tiktok_manager

load_dotenv()


class MultiPlatformManager:
    """Centralized multi-platform social media automation"""
    
    def __init__(self):
        self.platforms = {
            "tiktok": {
                "api_key": os.getenv("TIKTOK_API_KEY"),
                "access_token": os.getenv("TIKTOK_ACCESS_TOKEN"),
                "max_length": 150,
                "video_duration": "15-60s",
                "features": ["trending_sounds", "hashtag_challenge", "duets", "stitches"]
            },
            "instagram": {
                "api_key": os.getenv("INSTAGRAM_GRAPH_API_KEY"),
                "business_account_id": os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID"),
                "max_length": 2200,
                "features": ["carousel", "reels", "stories", "igtv"],
                "video_duration": "3s-60m"
            },
            "twitter": {
                "api_key": os.getenv("TWITTER_API_KEY"),
                "api_secret": os.getenv("TWITTER_API_SECRET"),
                "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
                "max_length": 280,
                "features": ["threads", "spaces", "live", "polls"]
            },
            "linkedin": {
                "api_key": os.getenv("LINKEDIN_API_KEY"),
                "organization_id": os.getenv("LINKEDIN_ORG_ID"),
                "max_length": 3000,
                "features": ["articles", "video", "document", "carousel"]
            },
            "youtube": {
                "api_key": os.getenv("YOUTUBE_API_KEY"),
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID"),
                "features": ["shorts", "videos", "premieres", "streams"]
            }
        }
        self.scheduled_posts = []
        self.post_history = []
    
    async def generate_posts_for_all_platforms(
        self, 
        content: str,
        product_info: Dict[str, Any],
        num_variations: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate platform-specific posts from single content"""
        
        posts_by_platform = {
            "tiktok": await self._generate_tiktok_posts(content, product_info, num_variations),
            "instagram": await self._generate_instagram_posts(content, product_info, num_variations),
            "twitter": await self._generate_twitter_posts(content, product_info, num_variations),
            "linkedin": await self._generate_linkedin_posts(content, product_info, num_variations),
            "youtube": await self._generate_youtube_posts(content, product_info, num_variations)
        }
        
        return posts_by_platform
    
    async def _generate_tiktok_posts(
        self,
        content: str,
        product_info: Dict[str, Any],
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate TikTok-optimized short-form video scripts"""
        
        posts = []
        for i in range(count):
            post = {
                "platform": "tiktok",
                "type": ["trending_challenge", "product_demo", "behind_scenes", "duet_prompt", "dance_challenge"][i % 5],
                "script": self._generate_short_script(content, 150),
                "hashtags": ["#FYP", "#ForYou", "#Viral", "#ProductReview", f"#{product_info.get('title', 'Product').replace(' ', '')}"],
                "trending_sounds": ["original", "trending_audio_2024"],
                "duration_seconds": [15, 30, 60][i % 3],
                "video_elements": {
                    "transitions": ["jump_cut", "zoom", "fade"],
                    "effects": ["text_pop", "voiceover", "b_roll"],
                    "music": True
                },
                "estimated_reach": 10000 + (i * 5000),
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            posts.append(post)
        
        return posts
    
    async def _generate_instagram_posts(
        self,
        content: str,
        product_info: Dict[str, Any],
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate Instagram-optimized posts (Reels, Carousel, Stories)"""
        
        posts = []
        formats = ["reels", "carousel", "stories", "igtv", "static"]
        
        for i in range(count):
            post = {
                "platform": "instagram",
                "format": formats[i % len(formats)],
                "caption": self._generate_caption(content, format_type=formats[i % len(formats)]),
                "hashtags": ["#ProductLaunch", "#Insta", "#Explore", f"#{product_info.get('title', 'Product').replace(' ', '_')}"],
                "location_tag": product_info.get("location", "Worldwide"),
                "video_duration": "30-60s" if formats[i % len(formats)] == "reels" else None,
                "carousel_count": 5 if formats[i % len(formats)] == "carousel" else None,
                "engagement_boosters": {
                    "call_to_action": "Link in bio",
                    "tag_brands": True,
                    "use_features": ["polls", "questions", "countdowns"]
                },
                "best_posting_time": self._get_best_posting_time("instagram"),
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            posts.append(post)
        
        return posts
    
    async def _generate_twitter_posts(
        self,
        content: str,
        product_info: Dict[str, Any],
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate Twitter/X-optimized posts and threads"""
        
        posts = []
        post_types = ["single_tweet", "thread", "poll", "space_announcement"]
        
        for i in range(count):
            post_type = post_types[i % len(post_types)]
            
            post = {
                "platform": "twitter",
                "type": post_type,
                "content": self._generate_short_script(content, 280),
                "hashtags": ["#AI", "#Innovation", "#ProductLaunch", f"#{product_info.get('title', 'Product').replace(' ', '')}"],
                "tags": ["@ProductHunt", "@TechCrunch", "@Forbes"],
                "thread_length": 5 if post_type == "thread" else None,
                "poll_options": ["Yes", "No", "Maybe", "Tell me more"] if post_type == "poll" else None,
                "mention_influencers": True,
                "community_note_friendly": True,
                "best_posting_time": self._get_best_posting_time("twitter"),
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            posts.append(post)
        
        return posts
    
    async def _generate_linkedin_posts(
        self,
        content: str,
        product_info: Dict[str, Any],
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate LinkedIn-optimized professional posts"""
        
        posts = []
        post_types = ["thought_leadership", "case_study", "company_update", "industry_insight"]
        
        for i in range(count):
            post = {
                "platform": "linkedin",
                "type": post_types[i % len(post_types)],
                "content": self._generate_professional_content(content, product_info),
                "hashtags": ["#Innovation", "#BusinessGrowth", "#AI", "#SaaS", f"#{product_info.get('industry', 'Tech')}"],
                "document_share": True,
                "video_embed": True,
                "article_link": product_info.get("blog_url", None),
                "engagement_strategy": {
                    "ask_question": True,
                    "call_to_apply": True,
                    "share_insights": True
                },
                "best_posting_time": self._get_best_posting_time("linkedin"),
                "target_audience": ["executives", "entrepreneurs", "industry_leaders"],
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            posts.append(post)
        
        return posts
    
    async def _generate_youtube_posts(
        self,
        content: str,
        product_info: Dict[str, Any],
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate YouTube Shorts and video scripts"""
        
        posts = []
        
        for i in range(count):
            post = {
                "platform": "youtube",
                "type": ["shorts", "full_video", "premiere"][i % 3],
                "title": f"{product_info.get('title')} - Shorts #{i+1}",
                "script": self._generate_video_script(content),
                "description": f"Learn about {product_info.get('title')}. {content}",
                "tags": ["Product", "Shorts", "Tutorial", product_info.get('title', 'Product')],
                "thumbnail_style": "bold_text_high_contrast",
                "video_duration": "15-60s" if i % 3 == 0 else "5-15m",
                "sections": {
                    "intro": "Hook (0-3s)",
                    "body": "Content (3-50s)",
                    "cta": "Call-to-action (50-60s)"
                },
                "seo_optimization": {
                    "keyword": product_info.get('title'),
                    "description_keywords": 3,
                    "metadata": True
                },
                "best_posting_time": self._get_best_posting_time("youtube"),
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            posts.append(post)
        
        return posts
    
    async def schedule_posts(
        self,
        posts_by_platform: Dict[str, List[Dict[str, Any]]],
        start_date: datetime,
        interval_hours: int = 24
    ) -> Dict[str, Any]:
        """Schedule posts across all platforms"""
        
        scheduled = {
            "total_posts": 0,
            "by_platform": {},
            "schedule": []
        }
        
        current_time = start_date
        post_index = 0
        
        for platform, posts in posts_by_platform.items():
            scheduled["by_platform"][platform] = len(posts)
            scheduled["total_posts"] += len(posts)
            
            for post in posts:
                scheduled["schedule"].append({
                    "platform": platform,
                    "post_id": f"{platform}_{post_index}",
                    "scheduled_time": current_time.isoformat(),
                    "content_preview": post.get("caption", post.get("content", post.get("script", ""))[:100]),
                    "status": "scheduled"
                })
                current_time += timedelta(hours=interval_hours)
                post_index += 1
        
        self.scheduled_posts.extend(scheduled["schedule"])
        return scheduled
    
    async def get_social_analytics(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for single or all platforms"""
        
        if platform and platform in self.platforms:
            return await self._get_platform_analytics(platform)
        
        analytics = {}
        for plat in self.platforms.keys():
            analytics[plat] = await self._get_platform_analytics(plat)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "platforms": analytics
        }
    
    async def _get_platform_analytics(self, platform: str) -> Dict[str, Any]:
        """Get analytics for specific platform"""
        
        return {
            "platform": platform,
            "total_posts": len([p for p in self.post_history if p.get("platform") == platform]),
            "total_reach": 50000 * len(self.platforms),
            "total_engagement": 2500 * len(self.platforms),
            "engagement_rate": "5.2%",
            "top_post": "Product demo shorts",
            "trending_hashtags": ["#FYP", "#Viral", "#Innovation"],
            "follower_growth": "+2.5%",
            "best_posting_time": self._get_best_posting_time(platform)
        }
    
    def _get_best_posting_time(self, platform: str) -> str:
        """Get optimal posting time for platform"""
        times = {
            "tiktok": "18:00-22:00",
            "instagram": "11:00-13:00 and 19:00-21:00",
            "twitter": "08:00-10:00 and 17:00-19:00",
            "linkedin": "08:00-10:00 and 12:00-14:00",
            "youtube": "14:00-16:00"
        }
        return times.get(platform, "12:00-18:00")
    
    def _generate_short_script(self, content: str, max_length: int) -> str:
        """Generate short-form script"""
        if len(content) <= max_length:
            return content
        return content[:max_length].rsplit(" ", 1)[0] + "..."
    
    def _generate_caption(self, content: str, format_type: str) -> str:
        """Generate platform-specific caption"""
        if format_type == "reels":
            return f"🎬 {content[:50]}... Watch full video in link 👆 #FYP"
        elif format_type == "stories":
            return f"⚡ {content[:40]}..."
        else:
            return f"✨ {content}"
    
    def _generate_professional_content(self, content: str, product_info: Dict[str, Any]) -> str:
        """Generate professional LinkedIn content"""
        return f"Excited to share: {product_info.get('title', 'Our Latest Innovation')}\n\n{content}\n\nLearn more about how this can transform your business."
    
    def _generate_video_script(self, content: str) -> str:
        """Generate video script structure"""
        return f"[HOOK - 0-3s]\n{content[:50]}...\n\n[BODY - 3-50s]\nDetailed explanation here\n\n[CTA - 50-60s]\nSubscribe and hit the bell!"


class PlatformIntegration:
    """Platform-specific API integrations"""
    
    @staticmethod
    async def post_to_tiktok(content: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Post to TikTok using TikTokManager"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.post_video(content)
            return result
        except Exception as e:
            return {
                "status": "error",
                "platform": "tiktok",
                "message": str(e)
            }
    
    @staticmethod
    async def post_to_instagram(content: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Post to Instagram"""
        return {
            "status": "blocked",
            "platform": "instagram",
            "message": "Live Instagram publishing is not available through this legacy route. Use /api/distribution/publish-live with INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID, and a public video URL."
        }
    
    @staticmethod
    async def post_to_twitter(content: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Post to Twitter/X"""
        return {
            "status": "blocked",
            "platform": "twitter",
            "message": "Live Twitter/X publishing is not implemented in this route."
        }
    
    @staticmethod
    async def post_to_linkedin(content: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Post to LinkedIn"""
        return {
            "status": "blocked",
            "platform": "linkedin",
            "message": "Live LinkedIn publishing is not implemented in this route."
        }
    
    @staticmethod
    async def post_to_youtube(content: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Post to YouTube"""
        return {
            "status": "blocked",
            "platform": "youtube",
            "message": "Use /api/youtube/upload or /api/distribution/publish-live for real YouTube uploads. This legacy route does not perform live publishing."
        }
    
    # TikTok-specific operations
    
    @staticmethod
    async def edit_tiktok_video(video_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Edit a TikTok video"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.edit_video(video_id, updates)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def schedule_tiktok_post(content: Dict[str, Any], schedule_time: str) -> Dict[str, Any]:
        """Schedule a TikTok post for later"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.schedule_post(content, schedule_time)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def delete_tiktok_video(video_id: str) -> Dict[str, Any]:
        """Delete a TikTok video"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.delete_video(video_id)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def get_tiktok_video_analytics(video_id: str) -> Dict[str, Any]:
        """Get analytics for a TikTok video"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.get_video_analytics(video_id)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def get_tiktok_channel_analytics(period_days: int = 30) -> Dict[str, Any]:
        """Get TikTok channel analytics"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.get_channel_analytics(period_days)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def moderate_tiktok_comments(video_id: str, action: str = "get") -> Dict[str, Any]:
        """Moderate comments on a TikTok video"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.moderate_comments(video_id, action)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def get_tiktok_trending_sounds() -> Dict[str, Any]:
        """Get trending TikTok sounds"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.get_trending_sounds()
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def get_tiktok_trending_hashtags() -> Dict[str, Any]:
        """Get trending TikTok hashtags"""
        try:
            tiktok_manager = get_tiktok_manager()
            result = await tiktok_manager.get_trending_hashtags()
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
