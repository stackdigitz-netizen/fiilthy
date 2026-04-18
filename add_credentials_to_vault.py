#!/usr/bin/env python3
"""
Add all credentials from .env to the vault
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "ceo" / "backend"))

from ai_services.key_vault import SecureKeyVault
from config.keys_manager import KeysManager
import motor.motor_asyncio

async def add_all_credentials():
    # Connect to DB
    km = KeysManager()
    mongo_url = km.get_key('mongodb_url')
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client['ceo_ai']

    vault = SecureKeyVault(db)

    # Mapping from .env keys to vault types and fields
    credential_mapping = {
        'gumroad': {
            'access_token': os.getenv('GUMROAD_ACCESS_TOKEN'),
            'client_id': os.getenv('GUMROAD_CLIENT_ID'),
            'client_secret': os.getenv('GUMROAD_CLIENT_SECRET')
        },
        'stripe': {
            'secret_key': os.getenv('STRIPE_SECRET_KEY'),
            'publishable_key': os.getenv('STRIPE_API_KEY'),
            'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET')
        },
        'openai': {
            'api_key': os.getenv('OPENAI_API_KEY')
        },
        'anthropic': {
            'api_key': os.getenv('ANTHROPIC_API_KEY')
        },
        'gemini': {
            'api_key': os.getenv('GEMINI_API_KEY')
        },
        'elevenlabs': {
            'api_key': os.getenv('ELEVENLABS_API_KEY')
        },
        'pexels': {
            'api_key': os.getenv('PEXELS_API_KEY')
        },
        'pixabay': {
            'api_key': os.getenv('PIXABAY_API_KEY')
        },
        'instagram': {
            'access_token': os.getenv('META_ACCESS_TOKEN'),
            'business_account_id': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        },
        'tiktok': {
            'client_key': os.getenv('TIKTOK_CLIENT_KEY'),
            'client_secret': os.getenv('TIKTOK_CLIENT_SECRET'),
            'redirect_uri': os.getenv('TIKTOK_REDIRECT_URI')
        },
        'youtube': {
            'api_key': os.getenv('YOUTUBE_API_KEY'),
            'channel_id': os.getenv('YOUTUBE_CHANNEL_ID')
        },
        'mailchimp': {
            'api_key': os.getenv('MAILCHIMP_API_KEY')
        },
        'sendgrid': {
            'api_key': os.getenv('SENDGRID_API_KEY')
        },
        'supabase': {
            'url': os.getenv('SUPABASE_URL'),
            'anon_key': os.getenv('SUPABASE_ANON_KEY'),
            'service_role_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        }
    }

    for cred_type, fields in credential_mapping.items():
        # Filter out None values
        clean_fields = {k: v for k, v in fields.items() if v is not None}
        if clean_fields:
            print(f"Adding {cred_type} credentials...")
            try:
                result = await vault.store_credentials(cred_type, clean_fields)
                print(f"✅ Added {cred_type}")
            except Exception as e:
                print(f"❌ Failed {cred_type}: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(add_all_credentials())