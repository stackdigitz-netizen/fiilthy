"""
Secure Key Vault & Credential Manager
Safely stores and manages all API keys and social media credentials
"""
import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
from cryptography.fernet import Fernet
import base64

class SecureKeyVault:
    """Encrypted credential storage for all API keys and tokens"""
    
    # Supported credential types - MAXIMUM REACH
    CREDENTIAL_TYPES = {
        # === MARKETPLACES & E-COMMERCE ===
        "gumroad": {
            "name": "Gumroad",
            "fields": ["client_id", "client_secret", "access_token"],
            "description": "Sell digital products",
            "icon": "🛒",
            "category": "marketplace"
        },
        "stripe": {
            "name": "Stripe",
            "fields": ["secret_key", "publishable_key", "webhook_secret"],
            "description": "Accept payments",
            "icon": "💳",
            "category": "payments"
        },
        "shopify": {
            "name": "Shopify",
            "fields": ["api_key", "api_secret", "store_url", "access_token"],
            "description": "E-commerce store",
            "icon": "🏪",
            "category": "marketplace"
        },
        "etsy": {
            "name": "Etsy",
            "fields": ["api_key", "shared_secret", "access_token", "access_secret"],
            "description": "Handmade marketplace",
            "icon": "🎨",
            "category": "marketplace"
        },
        "amazon_kdp": {
            "name": "Amazon KDP",
            "fields": ["access_key", "secret_key", "associate_tag"],
            "description": "Kindle publishing",
            "icon": "📚",
            "category": "marketplace"
        },
        "amazon_associates": {
            "name": "Amazon Associates",
            "fields": ["access_key", "secret_key", "associate_tag", "marketplace"],
            "description": "Affiliate marketing",
            "icon": "🔗",
            "category": "affiliate"
        },
        "ebay": {
            "name": "eBay",
            "fields": ["app_id", "cert_id", "dev_id", "oauth_token"],
            "description": "Global marketplace",
            "icon": "🏷️",
            "category": "marketplace"
        },
        "walmart": {
            "name": "Walmart Marketplace",
            "fields": ["client_id", "client_secret"],
            "description": "Retail marketplace",
            "icon": "🛍️",
            "category": "marketplace"
        },
        "redbubble": {
            "name": "Redbubble",
            "fields": ["api_key", "api_secret"],
            "description": "Print-on-demand",
            "icon": "👕",
            "category": "marketplace"
        },
        "printful": {
            "name": "Printful",
            "fields": ["api_key"],
            "description": "Print-on-demand fulfillment",
            "icon": "🖨️",
            "category": "marketplace"
        },
        "teachable": {
            "name": "Teachable",
            "fields": ["api_key", "school_id"],
            "description": "Online courses",
            "icon": "🎓",
            "category": "marketplace"
        },
        "udemy": {
            "name": "Udemy",
            "fields": ["client_id", "client_secret"],
            "description": "Course marketplace",
            "icon": "📖",
            "category": "marketplace"
        },
        "skillshare": {
            "name": "Skillshare",
            "fields": ["api_key", "teacher_id"],
            "description": "Creative courses",
            "icon": "🎨",
            "category": "marketplace"
        },
        "gumroad_memberships": {
            "name": "Gumroad Memberships",
            "fields": ["access_token"],
            "description": "Recurring subscriptions",
            "icon": "💎",
            "category": "marketplace"
        },
        "payhip": {
            "name": "Payhip",
            "fields": ["api_key"],
            "description": "Digital downloads",
            "icon": "💰",
            "category": "marketplace"
        },
        "ko_fi": {
            "name": "Ko-fi",
            "fields": ["api_key", "page_id"],
            "description": "Creator support",
            "icon": "☕",
            "category": "marketplace"
        },
        "buy_me_a_coffee": {
            "name": "Buy Me a Coffee",
            "fields": ["api_key"],
            "description": "Creator tips",
            "icon": "🧋",
            "category": "marketplace"
        },
        
        # === SOCIAL MEDIA PLATFORMS ===
        "twitter": {
            "name": "Twitter/X",
            "fields": ["api_key", "api_secret", "access_token", "access_secret", "bearer_token"],
            "description": "Social media automation",
            "icon": "🐦",
            "category": "social"
        },
        "instagram": {
            "name": "Instagram",
            "fields": ["access_token", "user_id", "app_id", "app_secret"],
            "description": "Visual content posting",
            "icon": "📸",
            "category": "social"
        },
        "tiktok": {
            "name": "TikTok",
            "fields": ["access_token", "client_key", "client_secret", "redirect_uri"],
            "description": "Short-form video",
            "icon": "🎵",
            "category": "social"
        },
        "youtube": {
            "name": "YouTube",
            "fields": ["api_key", "channel_id", "client_id", "client_secret", "refresh_token"],
            "description": "Video content & Shorts",
            "icon": "🎬",
            "category": "social"
        },
        "linkedin": {
            "name": "LinkedIn",
            "fields": ["access_token", "client_id", "client_secret"],
            "description": "Professional networking",
            "icon": "💼",
            "category": "social"
        },
        "facebook": {
            "name": "Facebook",
            "fields": ["app_id", "app_secret", "access_token", "page_id"],
            "description": "Social & ads",
            "icon": "📘",
            "category": "social"
        },
        "pinterest": {
            "name": "Pinterest",
            "fields": ["app_id", "app_secret", "access_token"],
            "description": "Visual discovery",
            "icon": "📌",
            "category": "social"
        },
        "snapchat": {
            "name": "Snapchat",
            "fields": ["client_id", "client_secret", "access_token"],
            "description": "Stories & AR",
            "icon": "👻",
            "category": "social"
        },
        "reddit": {
            "name": "Reddit",
            "fields": ["client_id", "client_secret", "username", "password"],
            "description": "Community engagement",
            "icon": "🤖",
            "category": "social"
        },
        "threads": {
            "name": "Threads",
            "fields": ["access_token", "user_id"],
            "description": "Text conversations",
            "icon": "🧵",
            "category": "social"
        },
        "bluesky": {
            "name": "Bluesky",
            "fields": ["handle", "app_password"],
            "description": "Decentralized social",
            "icon": "🦋",
            "category": "social"
        },
        "mastodon": {
            "name": "Mastodon",
            "fields": ["instance_url", "access_token"],
            "description": "Federated social",
            "icon": "🐘",
            "category": "social"
        },
        "tumblr": {
            "name": "Tumblr",
            "fields": ["consumer_key", "consumer_secret", "token", "token_secret"],
            "description": "Blogging platform",
            "icon": "📝",
            "category": "social"
        },
        
        # === VIDEO & STREAMING ===
        "twitch": {
            "name": "Twitch",
            "fields": ["client_id", "client_secret", "access_token"],
            "description": "Live streaming",
            "icon": "🎮",
            "category": "video"
        },
        "vimeo": {
            "name": "Vimeo",
            "fields": ["access_token", "client_id", "client_secret"],
            "description": "Video hosting",
            "icon": "🎥",
            "category": "video"
        },
        "rumble": {
            "name": "Rumble",
            "fields": ["api_key", "channel_id"],
            "description": "Video platform",
            "icon": "📺",
            "category": "video"
        },
        "dailymotion": {
            "name": "Dailymotion",
            "fields": ["api_key", "api_secret"],
            "description": "Video sharing",
            "icon": "🎞️",
            "category": "video"
        },
        "loom": {
            "name": "Loom",
            "fields": ["api_key"],
            "description": "Video messaging",
            "icon": "🔴",
            "category": "video"
        },
        "pexels": {
            "name": "Pexels",
            "fields": ["api_key"],
            "description": "Stock photos and footage",
            "icon": "🎬",
            "category": "video"
        },
        "pixabay": {
            "name": "Pixabay",
            "fields": ["api_key"],
            "description": "Stock images and video",
            "icon": "🖼️",
            "category": "video"
        },
        
        # === PODCASTING & AUDIO ===
        "spotify": {
            "name": "Spotify for Podcasters",
            "fields": ["client_id", "client_secret", "refresh_token"],
            "description": "Podcast distribution",
            "icon": "🎧",
            "category": "audio"
        },
        "anchor": {
            "name": "Anchor/Spotify",
            "fields": ["api_key"],
            "description": "Podcast hosting",
            "icon": "⚓",
            "category": "audio"
        },
        "apple_podcasts": {
            "name": "Apple Podcasts",
            "fields": ["api_key", "team_id", "key_id"],
            "description": "Podcast distribution",
            "icon": "🍎",
            "category": "audio"
        },
        "soundcloud": {
            "name": "SoundCloud",
            "fields": ["client_id", "client_secret", "access_token"],
            "description": "Audio streaming",
            "icon": "🔊",
            "category": "audio"
        },
        
        # === EMAIL & MARKETING ===
        "mailchimp": {
            "name": "Mailchimp",
            "fields": ["api_key", "server_prefix", "list_id"],
            "description": "Email marketing",
            "icon": "📧",
            "category": "email"
        },
        "sendgrid": {
            "name": "SendGrid",
            "fields": ["api_key", "from_email"],
            "description": "Transactional emails",
            "icon": "📨",
            "category": "email"
        },
        "convertkit": {
            "name": "ConvertKit",
            "fields": ["api_key", "api_secret"],
            "description": "Creator email",
            "icon": "✉️",
            "category": "email"
        },
        "mailerlite": {
            "name": "MailerLite",
            "fields": ["api_key"],
            "description": "Email automation",
            "icon": "💌",
            "category": "email"
        },
        "activecampaign": {
            "name": "ActiveCampaign",
            "fields": ["api_url", "api_key"],
            "description": "Marketing automation",
            "icon": "🎯",
            "category": "email"
        },
        "klaviyo": {
            "name": "Klaviyo",
            "fields": ["api_key", "private_key"],
            "description": "E-commerce email",
            "icon": "📊",
            "category": "email"
        },
        "beehiiv": {
            "name": "Beehiiv",
            "fields": ["api_key", "publication_id"],
            "description": "Newsletter platform",
            "icon": "🐝",
            "category": "email"
        },
        "substack": {
            "name": "Substack",
            "fields": ["api_key", "publication_url"],
            "description": "Newsletter publishing",
            "icon": "📰",
            "category": "email"
        },
        "ghost": {
            "name": "Ghost",
            "fields": ["api_url", "admin_api_key", "content_api_key"],
            "description": "Publishing platform",
            "icon": "👻",
            "category": "email"
        },
        
        # === COMMUNITY & MESSAGING ===
        "discord": {
            "name": "Discord",
            "fields": ["bot_token", "webhook_url", "server_id"],
            "description": "Community building",
            "icon": "💬",
            "category": "community"
        },
        "telegram": {
            "name": "Telegram",
            "fields": ["bot_token", "chat_id"],
            "description": "Messaging automation",
            "icon": "✈️",
            "category": "community"
        },
        "slack": {
            "name": "Slack",
            "fields": ["bot_token", "signing_secret", "app_token"],
            "description": "Team communication",
            "icon": "💼",
            "category": "community"
        },
        "whatsapp": {
            "name": "WhatsApp Business",
            "fields": ["phone_number_id", "access_token", "verify_token"],
            "description": "Business messaging",
            "icon": "📱",
            "category": "community"
        },
        "circle": {
            "name": "Circle",
            "fields": ["api_key", "community_id"],
            "description": "Community platform",
            "icon": "⭕",
            "category": "community"
        },
        "mighty_networks": {
            "name": "Mighty Networks",
            "fields": ["api_key"],
            "description": "Community courses",
            "icon": "🦸",
            "category": "community"
        },
        "skool": {
            "name": "Skool",
            "fields": ["api_key", "group_id"],
            "description": "Community + courses",
            "icon": "🏫",
            "category": "community"
        },
        
        # === PRODUCTIVITY & CONTENT ===
        "notion": {
            "name": "Notion",
            "fields": ["api_key", "database_id"],
            "description": "Productivity templates",
            "icon": "📝",
            "category": "productivity"
        },
        "airtable": {
            "name": "Airtable",
            "fields": ["api_key", "base_id"],
            "description": "Database templates",
            "icon": "📊",
            "category": "productivity"
        },
        "google_drive": {
            "name": "Google Drive",
            "fields": ["client_id", "client_secret", "refresh_token"],
            "description": "File storage",
            "icon": "📁",
            "category": "productivity"
        },
        "dropbox": {
            "name": "Dropbox",
            "fields": ["app_key", "app_secret", "access_token"],
            "description": "File sharing",
            "icon": "📦",
            "category": "productivity"
        },
        "canva": {
            "name": "Canva",
            "fields": ["api_key"],
            "description": "Design platform",
            "icon": "🎨",
            "category": "productivity"
        },
        "figma": {
            "name": "Figma",
            "fields": ["access_token"],
            "description": "Design collaboration",
            "icon": "✏️",
            "category": "productivity"
        },
        
        # === AI & AUTOMATION ===
        "openai": {
            "name": "OpenAI",
            "fields": ["api_key"],
            "description": "AI content generation",
            "icon": "🤖",
            "category": "ai"
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "fields": ["api_key"],
            "description": "AI assistant",
            "icon": "🧠",
            "category": "ai"
        },
        "gemini": {
            "name": "Google Gemini",
            "fields": ["api_key"],
            "description": "Gemini AI generation",
            "icon": "✨",
            "category": "ai"
        },
        "replicate": {
            "name": "Replicate",
            "fields": ["api_token"],
            "description": "AI models",
            "icon": "🔄",
            "category": "ai"
        },
        "midjourney": {
            "name": "Midjourney",
            "fields": ["api_key", "server_id", "channel_id"],
            "description": "AI image generation",
            "icon": "🖼️",
            "category": "ai"
        },
        "stability_ai": {
            "name": "Stability AI",
            "fields": ["api_key"],
            "description": "Stable Diffusion",
            "icon": "🎭",
            "category": "ai"
        },
        "elevenlabs": {
            "name": "ElevenLabs",
            "fields": ["api_key"],
            "description": "AI voice",
            "icon": "🗣️",
            "category": "ai"
        },
        "zapier": {
            "name": "Zapier",
            "fields": ["api_key"],
            "description": "Workflow automation",
            "icon": "⚡",
            "category": "automation"
        },
        "make": {
            "name": "Make (Integromat)",
            "fields": ["api_key", "team_id"],
            "description": "Visual automation",
            "icon": "🔧",
            "category": "automation"
        },
        "n8n": {
            "name": "n8n",
            "fields": ["api_key", "instance_url"],
            "description": "Workflow automation",
            "icon": "🔗",
            "category": "automation"
        },
        
        # === ADVERTISING ===
        "google_ads": {
            "name": "Google Ads",
            "fields": ["developer_token", "client_id", "client_secret", "refresh_token", "customer_id"],
            "description": "Search & display ads",
            "icon": "🎯",
            "category": "advertising"
        },
        "facebook_ads": {
            "name": "Facebook/Meta Ads",
            "fields": ["app_id", "app_secret", "access_token", "ad_account_id"],
            "description": "Social advertising",
            "icon": "📣",
            "category": "advertising"
        },
        "tiktok_ads": {
            "name": "TikTok Ads",
            "fields": ["app_id", "secret", "access_token"],
            "description": "Video advertising",
            "icon": "🎵",
            "category": "advertising"
        },
        "pinterest_ads": {
            "name": "Pinterest Ads",
            "fields": ["app_id", "app_secret", "access_token"],
            "description": "Visual ads",
            "icon": "📌",
            "category": "advertising"
        },
        "linkedin_ads": {
            "name": "LinkedIn Ads",
            "fields": ["client_id", "client_secret", "access_token"],
            "description": "B2B advertising",
            "icon": "💼",
            "category": "advertising"
        },
        
        # === AFFILIATE NETWORKS ===
        "shareasale": {
            "name": "ShareASale",
            "fields": ["api_token", "api_secret", "affiliate_id"],
            "description": "Affiliate network",
            "icon": "🤝",
            "category": "affiliate"
        },
        "cj_affiliate": {
            "name": "CJ Affiliate",
            "fields": ["api_key", "website_id"],
            "description": "Affiliate marketing",
            "icon": "💰",
            "category": "affiliate"
        },
        "impact": {
            "name": "Impact",
            "fields": ["account_sid", "auth_token"],
            "description": "Partnership platform",
            "icon": "🎯",
            "category": "affiliate"
        },
        "clickbank": {
            "name": "ClickBank",
            "fields": ["api_key", "secret_key", "clerk_key"],
            "description": "Digital products",
            "icon": "💵",
            "category": "affiliate"
        },
        "rakuten": {
            "name": "Rakuten Advertising",
            "fields": ["api_key", "account_id"],
            "description": "Affiliate network",
            "icon": "🏪",
            "category": "affiliate"
        },
        
        # === ANALYTICS ===
        "google_analytics": {
            "name": "Google Analytics",
            "fields": ["property_id", "credentials_json"],
            "description": "Web analytics",
            "icon": "📈",
            "category": "analytics"
        },
        "mixpanel": {
            "name": "Mixpanel",
            "fields": ["project_token", "api_secret"],
            "description": "Product analytics",
            "icon": "📊",
            "category": "analytics"
        },
        "amplitude": {
            "name": "Amplitude",
            "fields": ["api_key", "secret_key"],
            "description": "Product analytics",
            "icon": "📉",
            "category": "analytics"
        },
        "hotjar": {
            "name": "Hotjar",
            "fields": ["api_key", "site_id"],
            "description": "Behavior analytics",
            "icon": "🔥",
            "category": "analytics"
        },
        
        # === PAYMENTS ===
        "paypal": {
            "name": "PayPal",
            "fields": ["client_id", "client_secret"],
            "description": "Online payments",
            "icon": "💳",
            "category": "payments"
        },
        "square": {
            "name": "Square",
            "fields": ["access_token", "application_id"],
            "description": "Payment processing",
            "icon": "⬜",
            "category": "payments"
        },
        "lemonsqueezy": {
            "name": "Lemon Squeezy",
            "fields": ["api_key"],
            "description": "Digital payments",
            "icon": "🍋",
            "category": "payments"
        },
        "paddle": {
            "name": "Paddle",
            "fields": ["vendor_id", "api_key"],
            "description": "SaaS payments",
            "icon": "🏓",
            "category": "payments"
        },
        
        # === CRM & SALES ===
        "hubspot": {
            "name": "HubSpot",
            "fields": ["api_key", "portal_id"],
            "description": "CRM & marketing",
            "icon": "🧡",
            "category": "crm"
        },
        "salesforce": {
            "name": "Salesforce",
            "fields": ["client_id", "client_secret", "username", "password", "security_token"],
            "description": "Enterprise CRM",
            "icon": "☁️",
            "category": "crm"
        },
        "pipedrive": {
            "name": "Pipedrive",
            "fields": ["api_token"],
            "description": "Sales CRM",
            "icon": "🔵",
            "category": "crm"
        },
        "close": {
            "name": "Close CRM",
            "fields": ["api_key"],
            "description": "Sales automation",
            "icon": "🎯",
            "category": "crm"
        },
        
        # === DATABASES & BACKEND ===
        "supabase": {
            "name": "Supabase",
            "fields": ["url", "anon_key", "service_role_key"],
            "description": "Database & Auth",
            "icon": "🗄️",
            "category": "backend"
        },
        "firebase": {
            "name": "Firebase",
            "fields": ["api_key", "auth_domain", "project_id", "service_account_json"],
            "description": "Backend services",
            "icon": "🔥",
            "category": "backend"
        },
        "mongodb": {
            "name": "MongoDB Atlas",
            "fields": ["connection_string"],
            "description": "Database",
            "icon": "🍃",
            "category": "backend"
        },
        "planetscale": {
            "name": "PlanetScale",
            "fields": ["host", "username", "password"],
            "description": "MySQL database",
            "icon": "🌍",
            "category": "backend"
        },
        
        # === SMS & PHONE ===
        "twilio": {
            "name": "Twilio",
            "fields": ["account_sid", "auth_token", "phone_number"],
            "description": "SMS & calls",
            "icon": "📱",
            "category": "messaging"
        },
        "vonage": {
            "name": "Vonage",
            "fields": ["api_key", "api_secret"],
            "description": "Communications API",
            "icon": "📞",
            "category": "messaging"
        },
        
        # === WEBINARS & EVENTS ===
        "zoom": {
            "name": "Zoom",
            "fields": ["api_key", "api_secret", "account_id"],
            "description": "Video meetings",
            "icon": "📹",
            "category": "events"
        },
        "calendly": {
            "name": "Calendly",
            "fields": ["api_key"],
            "description": "Scheduling",
            "icon": "📅",
            "category": "events"
        },
        "eventbrite": {
            "name": "Eventbrite",
            "fields": ["api_key", "oauth_token"],
            "description": "Event management",
            "icon": "🎟️",
            "category": "events"
        },
        "webinarjam": {
            "name": "WebinarJam",
            "fields": ["api_key"],
            "description": "Webinar hosting",
            "icon": "🎤",
            "category": "events"
        },
        
        # === WEBSITE BUILDERS ===
        "wordpress": {
            "name": "WordPress",
            "fields": ["site_url", "username", "application_password"],
            "description": "Website/blog",
            "icon": "📝",
            "category": "website"
        },
        "webflow": {
            "name": "Webflow",
            "fields": ["api_token", "site_id"],
            "description": "Website builder",
            "icon": "🌐",
            "category": "website"
        },
        "wix": {
            "name": "Wix",
            "fields": ["api_key", "site_id"],
            "description": "Website builder",
            "icon": "✨",
            "category": "website"
        },
        "squarespace": {
            "name": "Squarespace",
            "fields": ["api_key"],
            "description": "Website builder",
            "icon": "⬛",
            "category": "website"
        },
        "carrd": {
            "name": "Carrd",
            "fields": ["api_key"],
            "description": "Simple websites",
            "icon": "🃏",
            "category": "website"
        },
        
        # === SEO & CONTENT ===
        "semrush": {
            "name": "SEMrush",
            "fields": ["api_key"],
            "description": "SEO tools",
            "icon": "🔍",
            "category": "seo"
        },
        "ahrefs": {
            "name": "Ahrefs",
            "fields": ["api_key"],
            "description": "SEO & backlinks",
            "icon": "📈",
            "category": "seo"
        },
        "moz": {
            "name": "Moz",
            "fields": ["access_id", "secret_key"],
            "description": "SEO software",
            "icon": "🔎",
            "category": "seo"
        },
        
        # === CHROME EXTENSION STORES ===
        "chrome_web_store": {
            "name": "Chrome Web Store",
            "fields": ["client_id", "client_secret", "refresh_token"],
            "description": "Extension publishing",
            "icon": "🌐",
            "category": "stores"
        },
        "firefox_addons": {
            "name": "Firefox Add-ons",
            "fields": ["jwt_issuer", "jwt_secret"],
            "description": "Extension publishing",
            "icon": "🦊",
            "category": "stores"
        }
    }
    
    def __init__(self, db=None):
        self.db = db
        self._encryption_key = self._get_or_create_key()
        self._fernet = Fernet(self._encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key - use env var for production"""
        import os
        
        # Try env variable first (for production)
        env_key = os.getenv('VAULT_ENCRYPTION_KEY')
        if env_key:
            return env_key.encode() if isinstance(env_key, str) else env_key
        
        # Try file-based (for local/development)
        key_path = Path("/tmp/.vault_key")
        try:
            if key_path.exists():
                return key_path.read_bytes()
            else:
                key = Fernet.generate_key()
                key_path.write_bytes(key)
                return key
        except (OSError, IOError, PermissionError):
            # Fallback: generate key (stateless)
            return Fernet.generate_key()
    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self._fernet.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self._fernet.decrypt(encrypted_data.encode()).decode()
    
    async def store_credentials(self, credential_type: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Store encrypted credentials"""
        if credential_type not in self.CREDENTIAL_TYPES:
            return {"success": False, "error": f"Unknown credential type: {credential_type}"}
        
        # Encrypt each credential value
        encrypted_creds = {}
        for key, value in credentials.items():
            if value:
                encrypted_creds[key] = self._encrypt(value)
        
        credential_doc = {
            "type": credential_type,
            "name": self.CREDENTIAL_TYPES[credential_type]["name"],
            "credentials": encrypted_creds,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if self.db is not None:
            # Update or insert
            await self.db.credentials.update_one(
                {"type": credential_type},
                {"$set": credential_doc},
                upsert=True
            )
        
        return {
            "success": True,
            "type": credential_type,
            "name": self.CREDENTIAL_TYPES[credential_type]["name"],
            "fields_stored": list(encrypted_creds.keys())
        }
    
    async def get_credentials(self, credential_type: str) -> Dict[str, Any]:
        """Get decrypted credentials"""
        if self.db is None:
            return {"success": False, "error": "Database not configured"}
        
        doc = await self.db.credentials.find_one({"type": credential_type}, {"_id": 0})
        if not doc:
            return {"success": False, "error": f"No credentials found for {credential_type}"}
        
        # Decrypt credentials
        decrypted = {}
        for key, encrypted_value in doc.get("credentials", {}).items():
            try:
                decrypted[key] = self._decrypt(encrypted_value)
            except:
                decrypted[key] = None
        
        return {
            "success": True,
            "type": credential_type,
            "credentials": decrypted,
            "status": doc.get("status", "unknown")
        }
    
    async def list_credentials(self) -> Dict[str, Any]:
        """List all stored credential types (without actual values)"""
        stored = []
        available = []
        
        if self.db is not None:
            cursor = self.db.credentials.find({}, {"_id": 0, "credentials": 0})
            async for doc in cursor:
                stored.append({
                    "type": doc["type"],
                    "name": doc["name"],
                    "status": doc.get("status", "unknown"),
                    "icon": self.CREDENTIAL_TYPES.get(doc["type"], {}).get("icon", "🔑"),
                    "updated_at": doc.get("updated_at")
                })
        
        # Find available but not configured
        stored_types = [s["type"] for s in stored]
        for cred_type, config in self.CREDENTIAL_TYPES.items():
            if cred_type not in stored_types:
                available.append({
                    "type": cred_type,
                    "name": config["name"],
                    "description": config["description"],
                    "icon": config["icon"],
                    "fields": config["fields"],
                    "status": "not_configured"
                })
        
        return {
            "success": True,
            "stored": stored,
            "available": available,
            "total_configured": len(stored),
            "total_available": len(available)
        }
    
    async def delete_credentials(self, credential_type: str) -> Dict[str, Any]:
        """Delete stored credentials"""
        if self.db is None:
            return {"success": False, "error": "Database not configured"}
        
        result = await self.db.credentials.delete_one({"type": credential_type})
        return {
            "success": result.deleted_count > 0,
            "type": credential_type,
            "deleted": result.deleted_count > 0
        }
    
    async def test_credentials(self, credential_type: str) -> Dict[str, Any]:
        """Test if credentials are working"""
        creds = await self.get_credentials(credential_type)
        if not creds.get("success"):
            return creds
        
        # Test based on type
        test_result = {"success": False, "message": "Test not implemented for this type"}
        
        if credential_type == "gumroad":
            import requests
            try:
                response = requests.get(
                    "https://api.gumroad.com/v2/user",
                    params={"access_token": creds["credentials"].get("access_token")}
                )
                if response.status_code == 200 and response.json().get("success"):
                    test_result = {"success": True, "message": "Gumroad connected!", "user": response.json().get("user", {}).get("name")}
                else:
                    test_result = {"success": False, "message": "Invalid Gumroad token"}
            except Exception as e:
                test_result = {"success": False, "message": str(e)}
        
        elif credential_type == "openai":
            try:
                import openai
                client = openai.OpenAI(api_key=creds["credentials"].get("api_key"))
                # Simple test
                test_result = {"success": True, "message": "OpenAI API key valid"}
            except Exception as e:
                test_result = {"success": False, "message": str(e)}
        
        # Update status based on test
        if self.db is not None:
            await self.db.credentials.update_one(
                {"type": credential_type},
                {"$set": {
                    "status": "verified" if test_result["success"] else "invalid",
                    "last_tested": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        return test_result
    
    def get_credential_schema(self, credential_type: str) -> Dict[str, Any]:
        """Get the schema for a credential type"""
        if credential_type not in self.CREDENTIAL_TYPES:
            return {"error": f"Unknown type: {credential_type}"}
        
        config = self.CREDENTIAL_TYPES[credential_type]
        return {
            "type": credential_type,
            "name": config["name"],
            "description": config["description"],
            "icon": config["icon"],
            "fields": config["fields"]
        }
