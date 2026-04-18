import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from ai_services.youtube_data_api import YOUTUBE_AVAILABLE, get_youtube_api


logger = logging.getLogger(__name__)


def _clean_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned or None


def _truthy(value: Optional[str]) -> bool:
    return (_clean_value(value) or "").lower() in {"1", "true", "yes", "on"}


def _file_exists(path_value: Optional[str]) -> bool:
    return bool(path_value and Path(path_value).exists())


class LiveDistributionEngine:
    """Real distribution orchestrator for platforms that have live credentials."""

    def __init__(self, db=None):
        self.db = db
        self.instagram_token = _clean_value(os.getenv("INSTAGRAM_ACCESS_TOKEN"))
        self.instagram_business_account_id = _clean_value(os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID"))
        self.tiktok_access_token = _clean_value(os.getenv("TIKTOK_ACCESS_TOKEN"))
        self.tiktok_client_id = _clean_value(os.getenv("TIKTOK_CLIENT_ID"))
        self.tiktok_client_secret = _clean_value(os.getenv("TIKTOK_CLIENT_SECRET"))
        self.tiktok_content_posting_approved = _truthy(os.getenv("TIKTOK_CONTENT_POSTING_APPROVED"))
        self.youtube_client_secrets_file = _clean_value(os.getenv("YOUTUBE_CLIENT_SECRETS_FILE"))
        self.youtube_credentials_file = _clean_value(os.getenv("YOUTUBE_CREDENTIALS_FILE"))
        self.youtube_client_secrets_json = _clean_value(os.getenv("YOUTUBE_CLIENT_SECRETS_JSON"))
        self.youtube_credentials_json = _clean_value(os.getenv("YOUTUBE_CREDENTIALS_JSON"))

    def get_live_readiness(self) -> Dict[str, Any]:
        youtube_missing = []
        if not YOUTUBE_AVAILABLE:
            youtube_missing.append("youtube_api_libraries")
        if not (self.youtube_client_secrets_json or _file_exists(self.youtube_client_secrets_file)):
            youtube_missing.append("YOUTUBE_CLIENT_SECRETS_FILE or YOUTUBE_CLIENT_SECRETS_JSON")
        if not (self.youtube_credentials_json or _file_exists(self.youtube_credentials_file)):
            youtube_missing.append("YOUTUBE_CREDENTIALS_FILE or YOUTUBE_CREDENTIALS_JSON")

        instagram_missing = []
        if not self.instagram_token:
            instagram_missing.append("INSTAGRAM_ACCESS_TOKEN")
        if not self.instagram_business_account_id:
            instagram_missing.append("INSTAGRAM_BUSINESS_ACCOUNT_ID")

        tiktok_missing = []
        if not self.tiktok_access_token:
            tiktok_missing.append("TIKTOK_ACCESS_TOKEN")
        if not self.tiktok_client_id:
            tiktok_missing.append("TIKTOK_CLIENT_ID")
        if not self.tiktok_client_secret:
            tiktok_missing.append("TIKTOK_CLIENT_SECRET")
        if not self.tiktok_content_posting_approved:
            tiktok_missing.append("TIKTOK_CONTENT_POSTING_APPROVED")

        return {
            "youtube": {
                "status": "ready" if not youtube_missing else "blocked",
                "missing": youtube_missing,
                "notes": [] if not youtube_missing else ["YouTube can be made live once OAuth secrets and user credentials are configured."],
            },
            "instagram": {
                "status": "ready" if not instagram_missing else "blocked",
                "missing": instagram_missing,
                "notes": [] if not instagram_missing else ["Instagram Reels publishing requires a live access token and business account id."],
            },
            "tiktok": {
                "status": "ready" if not tiktok_missing else "blocked",
                "missing": tiktok_missing,
                "notes": [] if not tiktok_missing else ["TikTok publishing requires verified Content Posting API approval plus a live user access token."],
            },
        }

    async def publish_video(
        self,
        *,
        video_path: Optional[str],
        title: str,
        description: str,
        hashtags: List[str],
        platforms: List[str],
        privacy_status: str = "public",
        video_public_url: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_platforms = [platform.strip().lower() for platform in platforms if platform and platform.strip()]
        results: Dict[str, Any] = {}
        local_video_exists = bool(video_path and Path(video_path).exists())

        if not local_video_exists and not video_public_url:
            return {
                "success": False,
                "status": "blocked",
                "error": "Provide either a valid local video_path or a public video_public_url.",
            }

        for platform in normalized_platforms:
            if platform == "youtube":
                results[platform] = await self._publish_to_youtube(
                    video_path=video_path,
                    local_video_exists=local_video_exists,
                    title=title,
                    description=description,
                    hashtags=hashtags,
                    privacy_status=privacy_status,
                )
            elif platform == "instagram":
                results[platform] = await self._publish_to_instagram(
                    video_public_url=video_public_url,
                    description=description,
                    hashtags=hashtags,
                )
            elif platform == "tiktok":
                results[platform] = await self._publish_to_tiktok(
                    video_public_url=video_public_url,
                    title=title,
                    description=description,
                    hashtags=hashtags,
                )
            else:
                results[platform] = {
                    "status": "blocked",
                    "message": f"Platform '{platform}' is not supported by the live distribution engine.",
                }

        overall_status = "completed"
        if not results:
            overall_status = "blocked"
        elif all(result.get("status") == "blocked" for result in results.values()):
            overall_status = "blocked"
        elif any(result.get("status") in {"failed", "blocked"} for result in results.values()):
            overall_status = "partial"

        payload = {
            "success": overall_status in {"completed", "partial"},
            "status": overall_status,
            "product_id": product_id,
            "video_path": video_path,
            "video_public_url": video_public_url,
            "title": title,
            "platforms": results,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        await self._store_result(payload)
        return payload

    async def _publish_to_youtube(
        self,
        *,
        video_path: Optional[str],
        local_video_exists: bool,
        title: str,
        description: str,
        hashtags: List[str],
        privacy_status: str,
    ) -> Dict[str, Any]:
        readiness = self.get_live_readiness()["youtube"]
        if readiness["status"] != "ready":
            return {
                "status": "blocked",
                "message": "YouTube is not configured for live uploads.",
                "missing": readiness["missing"],
            }
        if not local_video_exists or not video_path:
            return {
                "status": "blocked",
                "message": "YouTube uploads require a local server-accessible video_path.",
                "missing": ["video_path"],
            }

        try:
            youtube_api = await get_youtube_api()
            result = await youtube_api.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=[tag.lstrip("#") for tag in hashtags],
                privacy_status=privacy_status,
            )
            if result.get("success"):
                return {
                    "status": "uploaded",
                    "video_id": result.get("video_id"),
                    "url": result.get("url"),
                    "shorts_url": result.get("shorts_url"),
                    "raw": result,
                }
            return {
                "status": "failed",
                "message": result.get("error", "YouTube upload failed."),
                "raw": result,
            }
        except Exception as exc:
            logger.exception("YouTube live publish failed")
            return {
                "status": "failed",
                "message": str(exc),
            }

    async def _publish_to_instagram(
        self,
        *,
        video_public_url: Optional[str],
        description: str,
        hashtags: List[str],
    ) -> Dict[str, Any]:
        readiness = self.get_live_readiness()["instagram"]
        if readiness["status"] != "ready":
            return {
                "status": "blocked",
                "message": "Instagram is not configured for live publishing.",
                "missing": readiness["missing"],
            }
        if not video_public_url:
            return {
                "status": "blocked",
                "message": "Instagram Reels publishing requires a publicly accessible video URL.",
                "missing": ["video_public_url"],
            }

        caption = self._build_caption(description, hashtags)

        try:
            container_response = await asyncio.to_thread(
                requests.post,
                f"https://graph.facebook.com/v18.0/{self.instagram_business_account_id}/media",
                data={
                    "media_type": "REELS",
                    "video_url": video_public_url,
                    "caption": caption,
                    "access_token": self.instagram_token,
                },
                timeout=30,
            )
            container_data = container_response.json()
            if container_response.status_code >= 400 or not container_data.get("id"):
                return {
                    "status": "failed",
                    "message": container_data.get("error", {}).get("message", container_response.text),
                    "http_status": container_response.status_code,
                    "raw": container_data,
                }

            publish_response = await asyncio.to_thread(
                requests.post,
                f"https://graph.facebook.com/v18.0/{self.instagram_business_account_id}/media_publish",
                data={
                    "creation_id": container_data["id"],
                    "access_token": self.instagram_token,
                },
                timeout=30,
            )
            publish_data = publish_response.json()
            if publish_response.status_code >= 400 or not publish_data.get("id"):
                return {
                    "status": "failed",
                    "message": publish_data.get("error", {}).get("message", publish_response.text),
                    "http_status": publish_response.status_code,
                    "raw": publish_data,
                }

            return {
                "status": "uploaded",
                "creation_id": container_data["id"],
                "media_id": publish_data.get("id"),
                "raw": publish_data,
            }
        except Exception as exc:
            logger.exception("Instagram live publish failed")
            return {
                "status": "failed",
                "message": str(exc),
            }

    async def _publish_to_tiktok(
        self,
        *,
        video_public_url: Optional[str],
        title: str,
        description: str,
        hashtags: List[str],
    ) -> Dict[str, Any]:
        readiness = self.get_live_readiness()["tiktok"]
        if readiness["status"] != "ready":
            return {
                "status": "blocked",
                "message": "TikTok is not configured for live publishing.",
                "missing": readiness["missing"],
            }
        if not video_public_url:
            return {
                "status": "blocked",
                "message": "TikTok publishing requires a publicly accessible video URL.",
                "missing": ["video_public_url"],
            }

        caption = self._build_caption(description, hashtags)
        payload = {
            "post_info": {
                "title": (title or caption or "FiiLTHY video")[:90],
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_public_url,
            },
        }

        try:
            response = await asyncio.to_thread(
                requests.post,
                "https://open.tiktokapis.com/v2/post/publish/video/init/",
                headers={
                    "Authorization": f"Bearer {self.tiktok_access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )
            data = response.json() if response.content else {}
            if response.status_code >= 400:
                return {
                    "status": "failed",
                    "message": data.get("error", {}).get("message", response.text),
                    "http_status": response.status_code,
                    "raw": data,
                }

            return {
                "status": "submitted",
                "publish_id": data.get("data", {}).get("publish_id"),
                "raw": data,
            }
        except Exception as exc:
            logger.exception("TikTok live publish failed")
            return {
                "status": "failed",
                "message": str(exc),
            }

    async def _store_result(self, payload: Dict[str, Any]) -> None:
        if self.db is None:
            return
        try:
            await self.db.live_distribution_jobs.insert_one(payload)
        except Exception as exc:
            logger.warning("Could not store live distribution result: %s", exc)

    def _build_caption(self, description: str, hashtags: List[str]) -> str:
        hashtag_text = " ".join(tag if tag.startswith("#") else f"#{tag}" for tag in hashtags)
        return " ".join(part for part in [description.strip(), hashtag_text.strip()] if part).strip()


_live_distribution_engine: Optional[LiveDistributionEngine] = None


def get_live_distribution_engine(db=None) -> LiveDistributionEngine:
    global _live_distribution_engine
    if _live_distribution_engine is None:
        _live_distribution_engine = LiveDistributionEngine(db=db)
    elif db is not None and _live_distribution_engine.db is None:
        _live_distribution_engine.db = db
    return _live_distribution_engine