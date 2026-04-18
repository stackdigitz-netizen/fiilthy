"""
TikTok Integration - Usage Examples
Complete guide to using all TikTok API features
"""

import asyncio
import json
from ai_services.tiktok_manager import get_tiktok_manager


async def demo_post_video():
    """Demo: Post a video to TikTok"""
    print("\n=== POSTING VIDEO ===")
    
    tiktok = get_tiktok_manager()
    
    video_data = {
        "video_file_path": "/path/to/video.mp4",  # or video_url
        "caption": "Check out this amazing product!",
        "hashtags": ["viral", "trending", "foryou"],
        "privacy_level": "PUBLIC"
    }
    
    result = await tiktok.post_video(video_data)
    print(json.dumps(result, indent=2))
    return result.get("video_id")


async def demo_edit_video(video_id):
    """Demo: Edit a TikTok video caption"""
    print("\n=== EDITING VIDEO ===")
    
    tiktok = get_tiktok_manager()
    
    updates = {
        "caption": "Updated caption with new hashtags!",
        "hashtags": ["newtag", "updated"],
        "privacy_level": "PRIVATE"
    }
    
    result = await tiktok.edit_video(video_id, updates)
    print(json.dumps(result, indent=2))


async def demo_schedule_post():
    """Demo: Schedule a post for later"""
    print("\n=== SCHEDULING POST ===")
    
    tiktok = get_tiktok_manager()
    
    video_data = {
        "video_file_path": "/path/to/scheduled_video.mp4",
        "caption": "This will post tomorrow!",
        "hashtags": ["scheduled"]
    }
    
    # Schedule for tomorrow at 2 PM
    schedule_time = "2026-04-09T14:00:00Z"
    
    result = await tiktok.schedule_post(video_data, schedule_time)
    print(json.dumps(result, indent=2))


async def demo_delete_video(video_id):
    """Demo: Delete a video"""
    print("\n=== DELETING VIDEO ===")
    
    tiktok = get_tiktok_manager()
    
    result = await tiktok.delete_video(video_id)
    print(json.dumps(result, indent=2))


async def demo_video_analytics(video_id):
    """Demo: Get video analytics"""
    print("\n=== VIDEO ANALYTICS ===")
    
    tiktok = get_tiktok_manager()
    
    result = await tiktok.get_video_analytics(video_id)
    print(json.dumps(result, indent=2))


async def demo_channel_analytics():
    """Demo: Get channel analytics"""
    print("\n=== CHANNEL ANALYTICS ===")
    
    tiktok = get_tiktok_manager()
    
    result = await tiktok.get_channel_analytics(period_days=30)
    print(json.dumps(result, indent=2))


async def demo_moderate_comments(video_id):
    """Demo: Moderate comments"""
    print("\n=== COMMENT MODERATION ===")
    
    tiktok = get_tiktok_manager()
    
    # Get all comments
    result = await tiktok.moderate_comments(video_id, action="get")
    print("All comments:")
    print(json.dumps(result, indent=2))
    
    # Delete a comment
    result = await tiktok.moderate_comments(video_id, action="delete")
    print("\nComment deleted:")
    print(json.dumps(result, indent=2))
    
    # Pin a comment
    result = await tiktok.moderate_comments(video_id, action="pin")
    print("\nComment pinned:")
    print(json.dumps(result, indent=2))


async def demo_trending_sounds():
    """Demo: Get trending sounds"""
    print("\n=== TRENDING SOUNDS ===")
    
    tiktok = get_tiktok_manager()
    
    result = await tiktok.get_trending_sounds(limit=10)
    print(json.dumps(result, indent=2))


async def demo_trending_hashtags():
    """Demo: Get trending hashtags"""
    print("\n=== TRENDING HASHTAGS ===")
    
    tiktok = get_tiktok_manager()
    
    result = await tiktok.get_trending_hashtags(limit=10)
    print(json.dumps(result, indent=2))


async def run_all_demos():
    """Run all demos"""
    print("=" * 60)
    print("TikTok Integration Demo - All Features")
    print("=" * 60)
    
    try:
        # Post a video
        video_id = await demo_post_video()
        
        # Edit the video
        await demo_edit_video(video_id)
        
        # Schedule another post
        await demo_schedule_post()
        
        # Get video analytics
        await demo_video_analytics(video_id)
        
        # Get channel analytics
        await demo_channel_analytics()
        
        # Moderate comments
        await demo_moderate_comments(video_id)
        
        # Get trending content
        await demo_trending_sounds()
        await demo_trending_hashtags()
        
        # Delete the video
        await demo_delete_video(video_id)
        
    except Exception as e:
        print(f"Error: {e}")


# API Endpoint Examples using cURL

CURL_EXAMPLES = """
# POST A VIDEO
curl -X POST http://localhost:8000/api/social/post-tiktok \\
  -H "Content-Type: application/json" \\
  -d '{
    "video_file_path": "/path/to/video.mp4",
    "caption": "Amazing product launch! 🚀",
    "hashtags": ["viral", "trending"]
  }'

# EDIT A VIDEO
curl -X POST http://localhost:8000/api/social/tiktok/edit \\
  -H "Content-Type: application/json" \\
  -d '{
    "video_id": "1234567890",
    "updates": {
      "caption": "Updated caption!",
      "hashtags": ["newtag"]
    }
  }'

# SCHEDULE A POST
curl -X POST http://localhost:8000/api/social/tiktok/schedule \\
  -H "Content-Type: application/json" \\
  -d '{
    "content": {
      "video_file_path": "/path/to/video.mp4",
      "caption": "Posting tomorrow!"
    },
    "schedule_time": "2026-04-09T14:00:00Z"
  }'

# DELETE A VIDEO
curl -X DELETE http://localhost:8000/api/social/tiktok/1234567890

# GET VIDEO ANALYTICS
curl -X GET http://localhost:8000/api/social/tiktok/analytics/1234567890

# GET CHANNEL ANALYTICS
curl -X GET http://localhost:8000/api/social/tiktok/analytics/channel/summary?period_days=30

# MODERATE COMMENTS
curl -X POST http://localhost:8000/api/social/tiktok/comments/1234567890 \\
  -H "Content-Type: application/json" \\
  -d '{"action": "get"}'

# GET TRENDING SOUNDS
curl -X GET http://localhost:8000/api/social/tiktok/trending/sounds?limit=10

# GET TRENDING HASHTAGS
curl -X GET http://localhost:8000/api/social/tiktok/trending/hashtags?limit=10
"""


if __name__ == "__main__":
    print("TikTok Integration Examples\n")
    print(CURL_EXAMPLES)
    print("\n" + "=" * 60)
    print("Running Python demos...\n")
    asyncio.run(run_all_demos())
