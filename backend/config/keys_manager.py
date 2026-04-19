"""
Secure API Keys Manager
Handles encryption and storage of API keys from frontend
"""
import os
import json
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64
import hashlib
from pathlib import Path

from config.runtime_secrets import get_runtime_secret


class KeysManager:
    """Manages secure storage and retrieval of API keys"""

    ENV_KEY_ALIASES = {
        'openai_key': ['OPENAI_API_KEY', 'OPENAI_KEY'],
        'anthropic_key': ['ANTHROPIC_API_KEY', 'ANTHROPIC_KEY'],
        'dalle_key': ['DALLE_API_KEY', 'DALLE_KEY', 'OPENAI_API_KEY'],
        'sendgrid_key': ['SENDGRID_API_KEY', 'SENDGRID_KEY'],
        'sendgrid_from_email': ['SENDGRID_FROM_EMAIL', 'SENDGRID_VERIFIED_SENDER', 'DEFAULT_FROM_EMAIL'],
        'stripe_key': ['STRIPE_SECRET_KEY', 'STRIPE_API_KEY', 'STRIPE_KEY'],
        'stripe_webhook_secret': ['STRIPE_WEBHOOK_SECRET'],
        'gumroad_key': ['GUMROAD_ACCESS_TOKEN', 'GUMROAD_TOKEN', 'GUMROAD_API_KEY', 'GUMROAD_KEY', 'GUMROAD_CLIENT_ID'],
        'gumroad_secret': ['GUMROAD_SECRET', 'GUMROAD_CLIENT_SECRET'],
        'mongodb_url': ['MONGO_URL', 'MONGO_URI', 'MONGODB_URL'],
        # Social platform keys — map to Railway env var names
        'tiktok_api_key': ['TIKTOK_CLIENT_KEY', 'TIKTOK_CLIENT_ID', 'TIKTOK_API_KEY'],
        'tiktok_api_secret': ['TIKTOK_CLIENT_SECRET', 'TIKTOK_API_SECRET'],
        'instagram_graph_api_key': ['META_ACCESS_TOKEN', 'INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_GRAPH_API_KEY'],
        'twitter_api_key': ['TWITTER_BEARER_TOKEN', 'TWITTER_API_KEY'],
        'linkedin_api_key': ['LINKEDIN_CLIENT_ID', 'LINKEDIN_API_KEY'],
        'youtube_api_key': ['YOUTUBE_API_KEY', 'GOOGLE_API_KEY'],
        'mailchimp_key': ['MAILCHIMP_API_KEY', 'MAILCHIMP_KEY'],
        'gemini_key': ['GEMINI_API_KEY', 'GOOGLE_GEMINI_API_KEY'],
        # Video generation keys
        'elevenlabs_key': ['ELEVENLABS_API_KEY', 'ELEVENLABS_KEY'],
        'pexels_key': ['PEXELS_API_KEY', 'PEXELS_KEY'],
        'pixabay_key': ['PIXABAY_API_KEY', 'PIXABAY_KEY'],
    }
    
    def __init__(self):
        # Use a derived key from environment or generate one
        master_key = os.environ.get('MASTER_KEY')
        if not master_key or not self._is_valid_fernet_key(master_key):
            master_key = get_runtime_secret(
                'MASTER_KEY',
                warning_message='MASTER_KEY missing or invalid.',
                generator=lambda: Fernet.generate_key().decode(),
                validator=self._is_valid_fernet_key
            )
        
        self.cipher = Fernet(master_key.encode() if isinstance(master_key, str) else master_key)
        self.storage_path = Path(__file__).resolve().parent / '.secure_keys.json'
        self.keys_cache: Dict[str, str] = {}
        self._load_persisted_keys()

    @staticmethod
    def _is_valid_fernet_key(candidate: str) -> bool:
        try:
            Fernet(candidate.encode() if isinstance(candidate, str) else candidate)
            return True
        except ValueError:
            return False

    @staticmethod
    def _normalize_value(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        cleaned_value = value.strip()
        return cleaned_value or None

    def _read_persisted_keys(self) -> Dict[str, str]:
        if not self.storage_path.exists():
            return {}

        try:
            with self.storage_path.open('r', encoding='utf-8') as storage_file:
                stored = json.load(storage_file)
        except Exception:
            return {}

        return stored if isinstance(stored, dict) else {}

    def _write_persisted_keys(self, encrypted_keys: Dict[str, str]):
        with self.storage_path.open('w', encoding='utf-8') as storage_file:
            json.dump(encrypted_keys, storage_file, indent=2)

    def _load_persisted_keys(self):
        encrypted_keys = self._read_persisted_keys()

        for key_name, encrypted_value in encrypted_keys.items():
            try:
                normalized_value = self._normalize_value(self.decrypt_key(encrypted_value))
                if normalized_value:
                    self.keys_cache[key_name] = normalized_value
            except ValueError:
                continue
    
    def encrypt_key(self, key: str) -> str:
        """Encrypt an API key"""
        encrypted = self.cipher.encrypt(key.encode())
        return encrypted.decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key"""
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt key: {e}")
    
    def store_keys(self, keys_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store keys from frontend
        keys_data format: {
            'gumroad_key': '...',
            'gumroad_secret': '...',
            'openai_key': '...',
            'anthropic_key': '...',
            'dalle_key': '...',
            'sendgrid_key': '...',
            'sendgrid_from_email': '...',
            'stripe_key': '...',
            'mongodb_url': '...'
        }
        """
        encrypted_keys = self._read_persisted_keys()
        stored_keys = {}
        for key_name, key_value in keys_data.items():
            normalized_value = self._normalize_value(key_value)
            if normalized_value:
                encrypted = self.encrypt_key(normalized_value)
                encrypted_keys[key_name] = encrypted
                stored_keys[key_name] = encrypted
                # Also cache in memory
                self.keys_cache[key_name] = normalized_value
                os.environ[key_name.upper()] = normalized_value
                for alias in self.ENV_KEY_ALIASES.get(key_name, []):
                    os.environ[alias] = normalized_value

        if stored_keys:
            self._write_persisted_keys(encrypted_keys)
        
        return stored_keys
    
    def get_key(self, key_name: str) -> Optional[str]:
        """Retrieve a key from cache or decrypt it"""
        # First check cache
        if key_name in self.keys_cache:
            normalized_value = self._normalize_value(self.keys_cache[key_name])
            if normalized_value:
                self.keys_cache[key_name] = normalized_value
            return normalized_value
        
        # Try canonical and provider-specific environment variable aliases.
        env_names = [key_name.upper(), *self.ENV_KEY_ALIASES.get(key_name, [])]
        for env_name in env_names:
            env_value = self._normalize_value(os.environ.get(env_name))
            if env_value:
                self.keys_cache[key_name] = env_value
                return env_value
        
        return None

    def get_env_key(self, key_name: str) -> Optional[str]:
        """Read the live environment for a key without relying on cached values."""
        env_names = [key_name.upper(), *self.ENV_KEY_ALIASES.get(key_name, [])]
        seen_names = []

        for env_name in env_names:
            if env_name in seen_names:
                continue
            seen_names.append(env_name)

            env_value = self._normalize_value(os.environ.get(env_name))
            if env_value:
                return env_value

        return None

    def sync_from_environment(self) -> Dict[str, str]:
        """Persist canonical key names from provider-specific environment variables."""
        keys_to_store: Dict[str, str] = {}

        for key_name in self.ENV_KEY_ALIASES:
            env_value = self.get_env_key(key_name)
            if env_value:
                keys_to_store[key_name] = env_value

        if not keys_to_store:
            return {}

        return self.store_keys(keys_to_store)
    
    def set_key(self, key_name: str, key_value: str):
        """Set a key in cache"""
        if key_value:
            self.store_keys({key_name: key_value})


# Global instance
keys_manager = KeysManager()
