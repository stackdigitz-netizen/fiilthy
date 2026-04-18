"""
YouTube Data API v3 Integration
Handles OAuth flow, video uploads, playlist management, and analytics
"""

import os
import json
import base64
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging
from pathlib import Path

# Optional YouTube imports
try:
    import google.auth.transport.requests
    from google_auth_oauthlib.flow import Flow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.urllib3 import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    YOUTUBE_AVAILABLE = True
except ImportError as e:
    YOUTUBE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"YouTube API libraries not available: {str(e)}. YouTube uploads disabled.")

logger = logging.getLogger(__name__)

# OAuth 2.0 Configuration
CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "youtube_client_secret.json")
CLIENT_SECRETS_JSON_ENV = "YOUTUBE_CLIENT_SECRETS_JSON"
CREDENTIALS_JSON_ENV = "YOUTUBE_CREDENTIALS_JSON"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly"
]


def _runtime_json_path(filename: str) -> Path:
    base_dir = Path("/tmp") if (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")) else Path.cwd()
    return base_dir / filename


def _decode_env_json(raw_value: str) -> dict:
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        decoded = base64.b64decode(raw_value).decode("utf-8")
        return json.loads(decoded)


def _materialize_env_json(env_name: str, filename: str) -> Optional[str]:
    raw_value = os.getenv(env_name)
    if not raw_value:
        return None

    payload = _decode_env_json(raw_value)
    target_path = _runtime_json_path(filename)
    target_path.write_text(json.dumps(payload), encoding="utf-8")
    return str(target_path)


class YouTubeDataAPI:
    """YouTube Data API v3 wrapper for video uploads and management"""
    
    def __init__(self, credentials_file: Optional[str] = None):
        if not YOUTUBE_AVAILABLE:
            logger.warning("YouTube API not available")
        
        self.credentials_file = credentials_file or os.getenv("YOUTUBE_CREDENTIALS_FILE")
        self.credentials = None
        self.youtube_service = None
        self.channel_id = None

    def _resolve_client_secrets_path(self) -> str:
        if os.path.exists(CLIENT_SECRETS):
            return CLIENT_SECRETS

        materialized = _materialize_env_json(CLIENT_SECRETS_JSON_ENV, "youtube_client_secret.runtime.json")
        if materialized:
            return materialized

        return CLIENT_SECRETS

    def _resolve_credentials_path(self) -> Optional[str]:
        if self.credentials_file and os.path.exists(self.credentials_file):
            return self.credentials_file

        materialized = _materialize_env_json(
            CREDENTIALS_JSON_ENV,
            Path(self.credentials_file or "youtube_credentials.runtime.json").name,
        )
        if materialized:
            self.credentials_file = materialized
            return materialized

        return self.credentials_file
    
    def get_auth_url(self, redirect_uri: str = "http://localhost:8000/callback") -> str:
        """Get YouTube OAuth authorization URL"""
        
        try:
            if not YOUTUBE_AVAILABLE:
                raise ImportError("YouTube API libraries not installed")
            
            client_secrets_path = self._resolve_client_secrets_path()
            if not os.path.exists(client_secrets_path):
                raise FileNotFoundError(f"Client secrets file not found: {client_secrets_path}")
            
            flow = Flow.from_client_secrets_file(
                client_secrets_path,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            
            auth_url, state = flow.authorization_url()
            
            # Store state for verification
            return auth_url
        
        except Exception as e:
            logger.error(f"OAuth URL generation failed: {str(e)}")
            raise
    
    async def handle_oauth_callback(self, authorization_code: str, redirect_uri: str = "http://localhost:8000/callback") -> Dict[str, Any]:
        """Handle OAuth callback and store credentials"""
        
        try:
            client_secrets_path = self._resolve_client_secrets_path()
            if not os.path.exists(client_secrets_path):
                raise FileNotFoundError(f"Client secrets file not found: {client_secrets_path}")
            
            flow = Flow.from_client_secrets_file(
                client_secrets_path,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            
            # Get credentials
            flow.fetch_token(code=authorization_code)
            self.credentials = flow.credentials
            
            # Save credentials for later use
            if self.credentials_file:
                self._save_credentials()
            
            # Get channel info
            youtube = build("youtube", "v3", credentials=self.credentials)
            channels = youtube.channels().list(part="snippet", mine=True).execute()
            
            if channels.get("items"):
                self.channel_id = channels["items"][0]["id"]
            
            return {
                "success": True,
                "channel_id": self.channel_id,
                "auth_timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"OAuth callback handling failed: {str(e)}")
            raise
    
    async def load_credentials(self) -> bool:
        """Load stored credentials from file"""
        
        try:
            credentials_path = self._resolve_credentials_path()
            if not credentials_path or not os.path.exists(credentials_path):
                return False
            
            with open(credentials_path, "r") as f:
                credentials_data = json.load(f)
            
            self.credentials = Credentials.from_authorized_user_info(credentials_data)
            
            # Refresh if expired
            if self.credentials.expired and self.credentials.refresh_token:
                request = Request()
                self.credentials.refresh(request)
            
            self._init_youtube_service()
            return True
        
        except Exception as e:
            logger.warning(f"Failed to load credentials: {str(e)}")
            return False
    
    def _init_youtube_service(self):
        """Initialize YouTube service"""
        
        if not self.credentials:
            raise ValueError("Credentials not loaded")
        
        self.youtube_service = build("youtube", "v3", credentials=self.credentials)
    
    def _save_credentials(self):
        """Save credentials to file"""
        
        try:
            if not self.credentials:
                return

            credentials_path = self._resolve_credentials_path() or str(_runtime_json_path("youtube_credentials.runtime.json"))
            self.credentials_file = credentials_path
            
            credentials_data = {
                "token": self.credentials.token,
                "refresh_token": self.credentials.refresh_token,
                "token_uri": self.credentials.token_uri,
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "scopes": self.credentials.scopes
            }
            
            with open(credentials_path, "w") as f:
                json.dump(credentials_data, f)
            
            logger.info(f"Credentials saved to {credentials_path}")
        
        except Exception as e:
            logger.error(f"Failed to save credentials: {str(e)}")
    
    async def upload_video(self,
                          video_path: str,
                          title: str,
                          description: str,
                          tags: List[str],
                          category_id: str = "24",  # Video category (Entertainment)
                          privacy_status: str = "public",
                          made_for_kids: bool = False) -> Dict[str, Any]:
        """
        Upload a video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags (max 30 tags, 30 chars each)
            category_id: YouTube category (default 24 for Entertainment)
            privacy_status: 'public', 'unlisted', or 'private'
            made_for_kids: Whether video is made for kids
            
        Returns:
            {
                "success": bool,
                "video_id": str,
                "url": str,
                "status": "uploading" | "processed" | "failed",
                "upload_timestamp": str
            }
        """
        
        try:
            if not self.youtube_service:
                await self.load_credentials()
                if not self.youtube_service:
                    raise ValueError("YouTube service not initialized")
            
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Prepare upload metadata
            request_body = {
                "snippet": {
                    "title": title[:100],
                    "description": description[:5000],
                    "tags": tags[:30],
                    "categoryId": category_id,
                    "defaultLanguage": "en",
                    "localized": {
                        "title": title[:100],
                        "description": description[:5000]
                    }
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": made_for_kids,
                    "madeForKids": made_for_kids
                }
            }
            
            # Prepare media upload
            media = MediaFileUpload(
                video_path,
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024 * 1024  # 1MB chunks
            )
            
            # Initialize upload request
            request = self.youtube_service.videos().insert(
                part="snippet,status",
                body=request_body,
                media_body=media,
                onuploadProgress=self._upload_progress_handler
            )
            
            # Execute upload
            response = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        logger.info(f"Upload progress: {int(status.progress() * 100)}%")
                except HttpError as e:
                    logger.error(f"Upload error: {e}")
                    return {
                        "success": False,
                        "error": str(e),
                        "video_path": video_path
                    }
            
            video_id = response.get("id")
            
            return {
                "success": True,
                "video_id": video_id,
                "url": f"https://youtube.com/watch?v={video_id}",
                "shorts_url": f"https://youtube.com/shorts/{video_id}",
                "status": "processing",
                "upload_timestamp": datetime.now(timezone.utc).isoformat(),
                "title": title,
                "privacy_status": privacy_status
            }
        
        except Exception as e:
            logger.error(f"Video upload failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }
    
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get video processing status"""
        
        try:
            if not self.youtube_service:
                await self.load_credentials()
            
            request = self.youtube_service.videos().list(
                part="status,processingDetails",
                id=video_id
            )
            
            response = await asyncio.to_thread(request.execute)
            
            if not response.get("items"):
                return {"success": False, "error": "Video not found"}
            
            video = response["items"][0]
            status = video.get("status", {})
            processing = video.get("processingDetails", {})
            
            return {
                "video_id": video_id,
                "privacy_status": status.get("privacyStatus"),
                "embeddable": status.get("embeddable"),
                "license_content": status.get("license"),
                "processing_status": processing.get("processingStatus"),
                "processing_progress": processing.get("processingProgress"),
                "processing_failure_reason": processing.get("processingFailureReason"),
                "file_details": processing.get("fileDetails"),
                "editor_suggestions": processing.get("editorSuggestions")
            }
        
        except Exception as e:
            logger.error(f"Failed to get video status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_playlist(self, title: str, description: str = "", privacy_status: str = "public") -> Dict[str, Any]:
        """Create a YouTube playlist"""
        
        try:
            if not self.youtube_service:
                await self.load_credentials()
            
            request_body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            }
            
            request = self.youtube_service.playlists().insert(
                part="snippet,status",
                body=request_body
            )
            
            response = await asyncio.to_thread(request.execute)
            
            playlist_id = response.get("id")
            
            return {
                "success": True,
                "playlist_id": playlist_id,
                "url": f"https://www.youtube.com/playlist?list={playlist_id}",
                "title": title
            }
        
        except Exception as e:
            logger.error(f"Playlist creation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_video_to_playlist(self, playlist_id: str, video_id: str, position: Optional[int] = None) -> Dict[str, Any]:
        """Add video to playlist"""
        
        try:
            if not self.youtube_service:
                await self.load_credentials()
            
            request_body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "videoId": video_id
                }
            }
            
            if position:
                request_body["snippet"]["position"] = position
            
            request = self.youtube_service.playlistItems().insert(
                part="snippet",
                body=request_body
            )
            
            response = await asyncio.to_thread(request.execute)
            
            return {
                "success": True,
                "playlist_item_id": response.get("id"),
                "video_id": video_id,
                "playlist_id": playlist_id
            }
        
        except Exception as e:
            logger.error(f"Failed to add video to playlist: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_channel_analytics(self) -> Dict[str, Any]:
        """Get channel analytics (requires YouTube Analytics API)"""
        
        try:
            if not self.youtube_service:
                await self.load_credentials()
            
            # This requires YouTube Analytics API
            # For now, return basic channel info
            
            request = self.youtube_service.channels().list(
                part="statistics,snippet",
                mine=True
            )
            
            response = await asyncio.to_thread(request.execute)
            
            if not response.get("items"):
                return {"success": False, "error": "Channel not found"}
            
            channel = response["items"][0]
            stats = channel.get("statistics", {})
            
            return {
                "channel_id": self.channel_id,
                "subscribers": stats.get("subscriberCount"),
                "videos": stats.get("videoCount"),
                "views": stats.get("viewCount"),
                "title": channel.get("snippet", {}).get("title"),
                "description": channel.get("snippet", {}).get("description")
            }
        
        except Exception as e:
            logger.error(f"Failed to get channel analytics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _upload_progress_handler(self, status):
        """Handle upload progress"""
        logger.info(f"Upload progress: {int(status.progress() * 100)}%")


async def get_youtube_api() -> YouTubeDataAPI:
    """Get or create YouTube API instance"""
    return YouTubeDataAPI()
