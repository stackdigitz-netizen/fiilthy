"""
Gemini/Google AI Integration
Centralized API key management for Google's Generative AI services
"""

import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import warnings

# Suppress FutureWarning about google.generativeai deprecation
warnings.filterwarnings('ignore', category=FutureWarning, module='google.generativeai')

import google.generativeai as genai

load_dotenv()


class GeminiKeyManager:
    """Centralized Gemini/Google AI API key management"""
    
    # Primary and fallback keys from environment
    PRIMARY_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    FALLBACK_KEY = os.getenv("GEMINI_API_KEY_BACKUP", "").strip()
    
    # All available keys (don't expose these in logs)
    _KEYS = []
    _CURRENT_KEY_INDEX = 0
    
    def __init__(self):
        """Initialize Gemini with primary key"""
        self.is_initialized = False
        self.current_model = "gemini-pro"
        self.error_count = 0
        self.max_retries = 3
        
        # Load keys
        self._load_keys()
        
        # Initialize with first valid key
        if self._KEYS:
            self._initialize_gemini()
    
    @staticmethod
    def _load_keys() -> None:
        """Load all available API keys from environment"""
        keys = []
        
        # Add primary key
        if GeminiKeyManager.PRIMARY_KEY:
            keys.append(GeminiKeyManager.PRIMARY_KEY)
        
        # Add fallback key
        if GeminiKeyManager.FALLBACK_KEY and GeminiKeyManager.FALLBACK_KEY != GeminiKeyManager.PRIMARY_KEY:
            keys.append(GeminiKeyManager.FALLBACK_KEY)
        
        # Try to load from .env file directly
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    if "GEMINI_API_KEY" in line and "=" in line:
                        _, key = line.split("=", 1)
                        key = key.strip().strip('"').strip("'")
                        if key and key not in keys and not key.startswith("#"):
                            keys.append(key)
        
        GeminiKeyManager._KEYS = keys
        
        if not keys:
            print("⚠️  NO GEMINI API KEYS FOUND!")
            print("   Set GEMINI_API_KEY or GEMINI_API_KEY_BACKUP in .env")
    
    def _initialize_gemini(self) -> bool:
        """Initialize Gemini with current key"""
        try:
            if not self._KEYS:
                print("❌ No Gemini API keys available")
                return False
            
            current_key = self._KEYS[self._CURRENT_KEY_INDEX]
            genai.configure(api_key=current_key)
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {str(e)}")
            return False
    
    def switch_to_next_key(self) -> bool:
        """Switch to next available API key (for rate limiting)"""
        if len(self._KEYS) <= 1:
            return False
        
        self._CURRENT_KEY_INDEX = (self._CURRENT_KEY_INDEX + 1) % len(self._KEYS)
        return self._initialize_gemini()
    
    async def generate_content(
        self,
        prompt: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Optional[str]:
        """
        Generate content using Gemini
        
        Args:
            prompt: The prompt to send
            model: Model name (default: gemini-pro)
            temperature: Creativity level (0-2)
            max_tokens: Max response length
        
        Returns:
            Generated text or None on error
        """
        if not self.is_initialized:
            print("❌ Gemini not initialized")
            return None
        
        try:
            genai_model = genai.GenerativeModel(model)
            response = genai_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            return response.text if response else None
        
        except Exception as e:
            self.error_count += 1
            
            # Try next key if available
            if self.error_count > self.max_retries and self.switch_to_next_key():
                self.error_count = 0
                return await self.generate_content(prompt, model, temperature, max_tokens)
            
            print(f"❌ Gemini generation error: {str(e)}")
            return None
    
    async def generate_image_description(self, image_url: str, prompt: str = "") -> Optional[str]:
        """Generate description for an image"""
        if not self.is_initialized:
            return None
        
        try:
            model = genai.GenerativeModel("gemini-pro-vision")
            
            full_prompt = f"Describe this image in detail. {prompt}" if prompt else "Describe this image in detail."
            
            response = model.generate_content([full_prompt, image_url])
            return response.text if response else None
        
        except Exception as e:
            print(f"❌ Image description error: {str(e)}")
            return None
    
    async def generate_product_description(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Generate marketing description for a product"""
        title = product_data.get("title", "Product")
        category = product_data.get("category", "")
        features = product_data.get("features", [])
        
        prompt = f"""
Create a compelling, SEO-optimized product description for Etsy listing:

Title: {title}
Category: {category}
Key Features: {', '.join(features) if features else 'Not specified'}

Generate a 200-300 word description that:
1. Highlights key benefits
2. Is engaging and persuasive
3. Includes relevant keywords for Etsy SEO
4. Addresses customer pain points
5. Includes unique selling proposition

Format: Plain text, no markdown, ready to paste on Etsy.
"""
        
        return await self.generate_content(prompt, temperature=0.7)
    
    async def generate_etsy_tags(self, product_data: Dict[str, Any]) -> Optional[List[str]]:
        """Generate optimal Etsy tags for a product"""
        title = product_data.get("title", "")
        description = product_data.get("description", "")
        category = product_data.get("category", "")
        
        prompt = f"""
Generate 13 OPTIMAL Etsy search tags for this product:

Title: {title}
Category: {category}
Description: {description}

Return ONLY the tags, one per line, no numbers, no quotes, no explanations.
Each tag should be:
- 1-3 words long
- Searchable and relevant
- High volume keywords
- Etsy-specific terminology

CRITICAL: Return exactly 13 tags, nothing else.
"""
        
        response = await self.generate_content(prompt, temperature=0.5)
        
        if response:
            tags = [tag.strip() for tag in response.split("\n") if tag.strip()]
            return tags[:13]
        
        return None
    
    async def generate_product_title(
        self,
        product_type: str,
        key_features: List[str],
        target_keywords: List[str] = []
    ) -> Optional[str]:
        """Generate SEO-optimized Etsy product title"""
        features_str = ", ".join(key_features)
        keywords_str = ", ".join(target_keywords) if target_keywords else ""
        
        prompt = f"""
Generate ONE perfect SEO-optimized Etsy product title:

Product Type: {product_type}
Key Features: {features_str}
Target Keywords: {keywords_str}

Requirements:
- Maximum 120 characters
- Include high-volume keywords
- Clear and descriptive
- Avoids all caps for important words
- No special characters except dash/hyphen
- Etsy-optimized for search visibility

Return ONLY the title, nothing else.
"""
        
        return await self.generate_content(prompt, temperature=0.5)
    
    def get_status(self) -> Dict[str, Any]:
        """Get Gemini integration status"""
        return {
            "initialized": self.is_initialized,
            "current_model": self.current_model,
            "keys_available": len(self._KEYS),
            "active_key_index": self._CURRENT_KEY_INDEX,
            "error_count": self.error_count,
            "status": "✅ Ready" if self.is_initialized else "❌ Not Ready"
        }


# Global Gemini manager instance
_gemini_manager = None


def get_gemini_manager() -> GeminiKeyManager:
    """Get or create Gemini manager"""
    global _gemini_manager
    if _gemini_manager is None:
        _gemini_manager = GeminiKeyManager()
    return _gemini_manager


def initialize_gemini() -> bool:
    """Initialize Gemini on app startup"""
    manager = get_gemini_manager()
    print(f"Gemini Status: {manager.get_status()}")
    return manager.is_initialized
