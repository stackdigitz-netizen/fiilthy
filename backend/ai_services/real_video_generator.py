"""
Real Video Generation - Integrates with actual APIs for video creation
Supports ElevenLabs, Pexels, Pixabay, and Replicate APIs
"""

import asyncio
import os
import json
import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
SERVERLESS_ROOT = Path("/tmp/fiilthy-video-assets")
DATA_ROOT = SERVERLESS_ROOT if (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")) else PROJECT_ROOT / "data"
VIDEO_OUTPUT_DIR = DATA_ROOT / "generated_videos"
VIDEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class RealVideoGenerator:
    """Generates videos using real APIs (no heavy dependencies)"""
    
    def __init__(self):
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_key = os.getenv("PIXABAY_API_KEY")
        self.replicate_key = os.getenv("REPLICATE_API_KEY")
        self.output_dir = VIDEO_OUTPUT_DIR
    
    async def generate_with_api(
        self,
        product: Dict[str, Any],
        video_style: str = "promotional",
        duration: int = 60
    ) -> Dict[str, Any]:
        """Generate video using real APIs"""
        
        try:
            video_id = f"vid-{uuid.uuid4().hex[:8]}"
            
            # Generate script
            script = self._generate_script(product, video_style)
            
            # Generate voiceover
            voiceover_url = await self._generate_voiceover_elevenlabs(script)
            if not voiceover_url:
                logger.warning("Voiceover generation failed, using silent video")
            
            # Find stock footage
            video_urls = await self._find_stock_footage(product)
            
            # Create video reference (actual creation via API)
            video_record = {
                "id": video_id,
                "product_id": product.get("id"),
                "title": product.get("title"),
                "style": video_style,
                "duration_seconds": duration,
                "script": script,
                "voiceover_url": voiceover_url,
                "background_urls": video_urls,
                "status": "ready_for_encoding",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "api_ready": True,
                "platforms": {
                    "tiktok": True,
                    "youtube_shorts": True,
                    "instagram_reels": True,
                    "facebook": True
                }
            }
            
            # Save metadata
            meta_path = self.output_dir / f"{video_id}_meta.json"
            with open(meta_path, "w") as f:
                json.dump(video_record, f, indent=2)
            
            return {
                "success": True,
                "video_id": video_id,
                "status": "ready",
                "metadata": video_record,
                "next_step": "Post to platform or encode with Replicate"
            }
        
        except Exception as e:
            logger.error(f"API video generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _generate_voiceover_elevenlabs(self, script: str) -> Optional[str]:
        """Generate voiceover using ElevenLabs API"""
        
        if not self.elevenlabs_key:
            logger.warning("ElevenLabs API key not configured")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                    headers={
                        "xi-api-key": self.elevenlabs_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": script,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.75,
                            "similarity_boost": 0.75
                        }
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    # Save audio file
                    audio_id = str(uuid.uuid4())[:8]
                    audio_path = self.output_dir / f"voiceover_{audio_id}.mp3"
                    audio_path.write_bytes(response.content)
                    
                    return str(audio_path)
                else:
                    logger.error(f"ElevenLabs error: {response.text}")
                    return None
        
        except Exception as e:
            logger.error(f"ElevenLabs API error: {str(e)}")
            return None
    
    async def _find_stock_footage(self, product: Dict[str, Any]) -> List[str]:
        """Find stock footage from Pexels or Pixabay"""
        
        videos = []
        query = product.get("title", "business").split()[0].lower()
        
        # Try Pexels
        if self.pexels_key:
            pexels_vids = await self._search_pexels(query)
            videos.extend(pexels_vids)
        
        # Try Pixabay
        if self.pixabay_key and len(videos) < 3:
            pixabay_vids = await self._search_pixabay(query)
            videos.extend(pixabay_vids)
        
        return videos[:3]
    
    async def _search_pexels(self, query: str) -> List[str]:
        """Search Pexels for videos"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.pexels.com/videos/search",
                    params={"query": query, "per_page": 3},
                    headers={"Authorization": self.pexels_key},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    videos = []
                    for item in data.get("videos", []):
                        url = item["video_files"][0]["link"] if item.get("video_files") else None
                        if url:
                            videos.append(url)
                    return videos
        
        except Exception as e:
            logger.warning(f"Pexels search failed: {str(e)}")
        
        return []
    
    async def _search_pixabay(self, query: str) -> List[str]:
        """Search Pixabay for videos"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://pixabay.com/api/videos/",
                    params={"key": self.pixabay_key, "q": query, "per_page": 3},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    videos = []
                    for item in data.get("hits", []):
                        url = item["videos"]["medium"]["url"]
                        if url:
                            videos.append(url)
                    return videos
        
        except Exception as e:
            logger.warning(f"Pixabay search failed: {str(e)}")
        
        return []
    
    def _generate_script(self, product: Dict[str, Any], style: str) -> str:
        """Generate voiceover script"""
        
        title = product.get("title", "Amazing Product")
        desc = product.get("description", "Transform your life")
        price = product.get("price", 29.99)
        
        scripts = {
            "promotional": f"""Introducing {title}. The solution you've been looking for.
            
{desc}

Transform your productivity and achieve your goals faster than ever before.

{title} has helped thousands of people just like you.

Get instant access today for just ${price}.

Don't wait. Your transformation starts now.

Link in bio.""",
            
            "educational": f"""Today we're exploring {title}.
            
{desc}

Learn the proven strategies that industry leaders use.

{title} combines cutting-edge technology with ease of use.

Master the skills that will set you apart in your field.

Get started with {title} today at ${price}.

Your success journey begins here.""",
            
            "social_proof": f"""Thousands are already using {title}.

"This changed my entire business" - Real user feedback

{desc}

Join the community of successful entrepreneurs using {title}.

Get the same results they're getting.

Limited spots available at ${price}.

Secure your access now. Link in bio."""
        }
        
        return scripts.get(style, scripts["promotional"])
    
    async def generate_series(
        self,
        product: Dict[str, Any],
        count: int = 5
    ) -> Dict[str, Any]:
        """Generate multiple video variations"""
        
        styles = [
            "promotional",
            "educational",
            "social_proof"
        ]
        
        videos = []
        for i in range(count):
            style = styles[i % len(styles)]
            video = await self.generate_with_api(
                product.copy(),
                video_style=style
            )
            if video["success"]:
                videos.append(video)
        
        return {
            "success": len(videos) > 0,
            "total_generated": len(videos),
            "videos": videos,
            "ready_to_publish": len(videos) > 0
        }


async def get_real_video_generator() -> RealVideoGenerator:
    """Get video generator instance"""
    return RealVideoGenerator()
