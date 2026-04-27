"""
Post Scheduler - Schedule and manage social media posting across platforms
Handles timing, queue management, and platform-specific posting logic
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    POSTING = "posting"
    POSTED = "posted"
    FAILED = "failed"
    ARCHIVED = "archived"


class PlatformPostConfig:
    """Platform-specific posting configuration"""
    
    PLATFORM_LIMITS = {
        "tiktok": {
            "max_videos_per_day": 10,
            "max_videos_per_hour": 3,
            "min_interval_seconds": 300,
            "video_max_length_seconds": 600,
            "supported_formats": ["mp4", "mov"]
        },
        "instagram": {
            "max_posts_per_day": 5,
            "max_posts_per_hour": 2,
            "min_interval_seconds": 600,
            "image_max_size_mb": 8,
            "video_max_length_seconds": 3600,
            "supported_formats": ["jpg", "png", "mp4", "mov"]
        },
        "youtube": {
            "max_videos_per_day": 3,
            "max_videos_per_hour": 1,
            "min_interval_seconds": 3600,
            "video_max_length_seconds": None,  # Unlimited
            "supported_formats": ["mp4", "mov", "avi"]
        },
        "twitter": {
            "max_tweets_per_day": 50,
            "max_tweets_per_hour": 10,
            "min_interval_seconds": 30,
            "image_max_size_mb": 5,
            "supported_formats": ["jpg", "png", "gif", "mp4"]
        },
        "linkedin": {
            "max_posts_per_day": 5,
            "max_posts_per_hour": 1,
            "min_interval_seconds": 900,
            "supported_formats": ["jpg", "png", "mp4"]
        }
    }


class PostScheduler:
    """Manages post scheduling and publishing coordination"""
    
    def __init__(self, db=None):
        self.db = db
        self.posting_queue = []
        self.active_tasks = {}
    
    async def schedule_posts(
        self,
        product_id: str,
        content_items: List[Dict[str, Any]],
        platforms: List[str],
        start_date: Optional[datetime] = None,
        spacing_minutes: int = 60,
        schedule_times: Optional[List[str]] = None  # e.g., ["09:00", "15:00", "21:00"]
    ) -> Dict[str, Any]:
        """
        Schedule multiple posts across platforms
        
        Args:
            product_id: Product to schedule posts for
            content_items: List of content dict with text, media, hashtags
            platforms: Target platforms [tiktok, instagram, youtube, twitter, linkedin]
            start_date: When to start posting (default: now)
            spacing_minutes: Minutes between posts on same platform
            schedule_times: Specific times to post (UTC)
        """
        if not self.db:
            return {"success": False, "error": "Database not configured"}
        
        try:
            schedule_id = f"schedule-{uuid.uuid4().hex[:8]}"
            start_date = start_date or datetime.now(timezone.utc)
            
            schedule_record = {
                "id": schedule_id,
                "product_id": product_id,
                "platforms": platforms,
                "total_content": len(content_items),
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "start_date": start_date.isoformat(),
                "posts": []
            }
            
            # Generate posting schedule
            posts = await self._generate_posting_schedule(
                schedule_id, product_id, content_items, 
                platforms, start_date, spacing_minutes, schedule_times
            )
            
            schedule_record["posts"] = posts
            schedule_record["total_scheduled"] = len(posts)
            
            # Save to database
            await self.db.post_schedules.insert_one(schedule_record)
            
            logger.info(f"✅ Scheduled {len(posts)} posts for product {product_id}")
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "total_scheduled": len(posts),
                "posts": posts[:5],  # Return first 5
                "message": f"Successfully scheduled {len(posts)} posts"
            }
        
        except Exception as e:
            logger.error(f"Schedule error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_posting_schedule(
        self,
        schedule_id: str,
        product_id: str,
        content_items: List[Dict],
        platforms: List[str],
        start_date: datetime,
        spacing_minutes: int,
        schedule_times: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Generate optimal posting times"""
        posts = []
        current_time = start_date
        
        # Default peak times if not specified
        if not schedule_times:
            schedule_times = ["09:00", "12:00", "15:00", "18:00", "21:00"]  # UTC
        
        content_index = 0
        platform_index = 0
        
        for idx, content in enumerate(content_items):
            # Rotate through platforms
            platform = platforms[platform_index % len(platforms)]
            platform_index += 1
            
            # Get the next scheduled time slot
            hour, minute = map(int, schedule_times[idx % len(schedule_times)].split(":"))
            
            # Set posting time
            post_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If this time has passed, move to tomorrow
            if post_time <= datetime.now(timezone.utc):
                post_time += timedelta(days=1)
            
            post = {
                "id": f"post-{uuid.uuid4().hex[:8]}",
                "schedule_id": schedule_id,
                "product_id": product_id,
                "content_id": content.get("id", f"content-{idx}"),
                "platform": platform,
                "scheduled_time": post_time.isoformat(),
                "status": PostStatus.SCHEDULED.value,
                "content": {
                    "text": content.get("text", ""),
                    "media_urls": content.get("media_urls", []),
                    "hashtags": content.get("hashtags", []),
                    "is_video": content.get("is_video", False),
                    "video_duration_seconds": content.get("video_duration_seconds"),
                    "thumbnail_url": content.get("thumbnail_url")
                },
                "platform_config": PlatformPostConfig.PLATFORM_LIMITS.get(platform, {}),
                "retry_count": 0,
                "max_retries": 3,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "posted_at": None,
                "error_message": None
            }
            
            posts.append(post)
            
            # Space out posts
            current_time += timedelta(minutes=spacing_minutes)
        
        return posts
    
    async def get_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Get schedule details"""
        if not self.db:
            return {"success": False, "error": "Database not configured"}
        
        schedule = await self.db.post_schedules.find_one({"id": schedule_id}, {"_id": 0})
        
        if not schedule:
            return {"success": False, "error": "Schedule not found"}
        
        # Get post stats
        posts = schedule.get("posts", [])
        stats = {
            "total": len(posts),
            "posted": len([p for p in posts if p["status"] == PostStatus.POSTED.value]),
            "scheduled": len([p for p in posts if p["status"] == PostStatus.SCHEDULED.value]),
            "queued": len([p for p in posts if p["status"] == PostStatus.QUEUED.value]),
            "failed": len([p for p in posts if p["status"] == PostStatus.FAILED.value])
        }
        
        schedule["stats"] = stats
        return {"success": True, "schedule": schedule}
    
    async def get_upcoming_posts(self, limit: int = 20) -> Dict[str, Any]:
        """Get next posts to be published"""
        if not self.db:
            return {"success": False, "error": "Database not configured"}
        
        now = datetime.now(timezone.utc)
        future_time = now + timedelta(days=7)
        
        posts = await self.db.post_schedules.aggregate([
            {"$unwind": "$posts"},
            {
                "$match": {
                    "posts.status": {"$in": [PostStatus.SCHEDULED.value, PostStatus.QUEUED.value]},
                    "posts.scheduled_time": {
                        "$gte": now.isoformat(),
                        "$lte": future_time.isoformat()
                    }
                }
            },
            {
                "$sort": {"posts.scheduled_time": 1}
            },
            {
                "$limit": limit
            }
        ]).to_list(limit)
        
        upcoming = [p["posts"] for p in posts] if posts else []
        
        return {
            "success": True,
            "upcoming_posts": upcoming,
            "total": len(upcoming)
        }
    
    async def reschedule_post(
        self,
        post_id: str,
        new_time: datetime
    ) -> Dict[str, Any]:
        """Reschedule a single post"""
        if not self.db:
            return {"success": False, "error": "Database not configured"}
        
        try:
            result = await self.db.post_schedules.update_one(
                {"posts.id": post_id},
                {
                    "$set": {
                        "posts.$.scheduled_time": new_time.isoformat(),
                        "posts.$.status": PostStatus.SCHEDULED.value,
                        "posts.$.updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            return {
                "success": result.modified_count > 0,
                "post_id": post_id,
                "new_time": new_time.isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def pause_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Pause all posts in a schedule"""
        if not self.db:
            return {"success": False, "error": "Database not configured"}
        
        try:
            await self.db.post_schedules.update_one(
                {"id": schedule_id},
                {
                    "$set": {
                        "status": "paused",
                        "paused_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            return {"success": True, "schedule_id": schedule_id, "status": "paused"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def resume_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Resume a paused schedule"""
        if not self.db:
            return {"success": False, "error": "Database not configured"}
        
        try:
            await self.db.post_schedules.update_one(
                {"id": schedule_id},
                {
                    "$set": {
                        "status": "active",
                        "resumed_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            return {"success": True, "schedule_id": schedule_id, "status": "active"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Delete entire schedule"""
        if not self.db:
            return {"success": False, "error": "Database not configured"}
        
        try:
            result = await self.db.post_schedules.delete_one({"id": schedule_id})
            return {
                "success": result.deleted_count > 0,
                "schedule_id": schedule_id,
                "message": "Schedule deleted"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


async def get_post_scheduler() -> PostScheduler:
    """Get or create scheduler instance"""
    return PostScheduler()
