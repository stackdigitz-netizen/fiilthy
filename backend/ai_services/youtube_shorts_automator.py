"""
YouTube Shorts Automator - Real implementation using OpenAI for scripts
and the YouTubeDataAPI wrapper for uploads.
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import openai

logger = logging.getLogger(__name__)

PRODUCTION_READY = True
PRODUCTION_STATUS = "production"

YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY") or ""


class YouTubeShortsAutomator:
    """Auto-create YouTube Shorts scripts and upload via YouTube Data API."""

    def __init__(self):
        self.channel_id = YOUTUBE_CHANNEL_ID
        self.openai_key = OPENAI_API_KEY
        self.shorts_created = 0

    async def generate_shorts_script(self, product: Dict[str, Any], count: int = 30) -> List[Dict]:
        """Generate AI-powered short video scripts for a product."""
        if not self.openai_key:
            return []

        client = openai.OpenAI(api_key=self.openai_key)
        title = product.get("title", "Product")
        description = product.get("description", "")
        price = product.get("price", "")

        prompt = f"""Create {count} unique YouTube Shorts scripts (max 60 seconds each) for this product:
Title: {title}
Description: {description}
Price: {price}

Cycle through these video types: product_demo, benefit_highlight, problem_solver, testimonial, how_to_snippet, behind_scenes, controversial_take, trending_audio, quick_tip, success_story

For each script provide a unique hook (first 3 seconds), body, CTA, and 5 relevant hashtags.
Return ONLY valid JSON (no markdown fences):
{{
  "scripts": [
    {{
      "day": 1,
      "type": "product_demo",
      "title": "<YouTube title under 100 chars>",
      "hook": "<attention-grabbing first line - under 10 words>",
      "body": "<main content 3-5 sentences>",
      "cta": "<clear call to action>",
      "hashtags": ["#shorts", "<tag2>", "<tag3>", "<tag4>", "<tag5>"],
      "music_suggestion": "<style or mood>",
      "duration_seconds": 60
    }}
  ]
}}"""

        def _call():
            return client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert YouTube Shorts content creator who specializes in viral short-form video scripts."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.9,
                max_tokens=4000,
            )

        try:
            response = await asyncio.to_thread(_call)
            text = response.choices[0].message.content.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.split("```")[0].strip()
            data = json.loads(text)
            scripts = data.get("scripts", [])
            for i, script in enumerate(scripts):
                script["scheduled_date"] = (
                    datetime.now(timezone.utc) + timedelta(days=i)
                ).isoformat()
            return scripts
        except Exception as e:
            logger.error("generate_shorts_script error: %s", e)
            return []

    async def upload_short(self, script: Dict, video_path: str = None) -> Dict[str, Any]:
        """Upload a Short to YouTube via YouTubeDataAPI."""
        if not video_path:
            return {
                "success": False,
                "error": "video_path is required for upload",
                "script_title": script.get("title"),
                "status": "pending_video",
            }

        try:
            from ai_services.youtube_data_api import YouTubeDataAPI  # noqa: PLC0415

            yt = YouTubeDataAPI()
            await yt.load_credentials()

            tags = [t.lstrip("#") for t in script.get("hashtags", [])]
            result = await yt.upload_video(
                video_path=video_path,
                title=script.get("title", "FiiLTHY.ai Short"),
                description=f"{script.get('body', '')}\n\n{script.get('cta', '')}",
                tags=tags + ["shorts"],
                privacy_status="public",
                category_id="22",
            )
            self.shorts_created += 1
            return result
        except Exception as e:
            logger.error("upload_short error: %s", e)
            return {"success": False, "error": str(e), "status": "upload_failed"}

    async def schedule_daily_upload(self, scripts: List[Dict]) -> Dict[str, Any]:
        """Return a schedule manifest for daily uploads."""
        scheduled = [
            {
                "day": s.get("day"),
                "title": s.get("title"),
                "scheduled_date": s.get("scheduled_date"),
                "type": s.get("type"),
                "status": "queued",
            }
            for s in scripts
        ]
        return {
            "success": True,
            "total_shorts": len(scripts),
            "schedule": scheduled,
            "upload_time": "09:00 UTC",
            "platform": "youtube_shorts",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_shorts_analytics(self, video_id: str) -> Dict[str, Any]:
        """Get analytics for a Short via YouTube Data API."""
        try:
            from ai_services.youtube_data_api import YouTubeDataAPI  # noqa: PLC0415

            yt = YouTubeDataAPI()
            return await yt.get_video_status(video_id)
        except Exception as e:
            logger.error("get_shorts_analytics error: %s", e)
            return {"video_id": video_id, "error": str(e)}
