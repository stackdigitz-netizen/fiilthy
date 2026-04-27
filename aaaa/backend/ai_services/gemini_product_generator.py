"""
Gemini Product Generator
Use Google Gemini AI to create products, descriptions, and marketing copy
"""

import asyncio
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiProductGenerator:
    """Generate products using Google Gemini AI"""
    
    def __init__(self):
        # Initialize Gemini API
        self.api_keys = [
            os.getenv("GEMINI_API_KEY"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3")
        ]
        
        # Filter out None keys
        self.api_keys = [key for key in self.api_keys if key]
        
        if not self.api_keys:
            print("⚠️  Warning: No Gemini API keys configured")
            self.current_key_index = 0
        else:
            genai.configure(api_key=self.api_keys[0])
            self.current_key_index = 0
        
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_product(
        self,
        niche: str,
        target_audience: str = "general",
        style: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate a complete product using Gemini
        
        Args:
            niche: Product niche/category
            target_audience: Who should buy this?
            style: Product style (professional, casual, luxury, etc)
        """
        try:
            prompt = f"""
Create a complete digital product for the {niche} niche.

Target Audience: {target_audience}
Style: {style}

Provide ONLY valid JSON output with this structure:
{{
  "title": "Product title",
  "description": "2-3 sentence description",
  "long_description": "Full product description (100-150 words)",
  "price": 97,
  "category": "{niche}",
  "features": ["feature1", "feature2", "feature3", "feature4", "feature5"],
  "benefits": ["benefit1", "benefit2", "benefit3"],
  "target_audience": "{target_audience}",
  "pain_points": ["pain1", "pain2", "pain3"],
  "value_proposition": "What makes this unique?",
  "marketing_hook": "One sentence that sells it",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "medium_format_descriptions": {{
    "twitter": "280 chars max description",
    "instagram": "3 hashtags + short description",
    "tiktok": "Trending hook for TikTok",
    "email": "Email subject line"
  }},
  "recommended_modules": ["module1", "module2", "module3"],
  "sales_angle": "Main angle to sell this product"
}}"""
            
            response = await asyncio.to_thread(
                self._generate_with_retry,
                prompt
            )
            
            return response
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def generate_product_description(
        self,
        product_title: str,
        niche: str,
        length: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate detailed product descriptions
        
        Args:
            product_title: Title of the product
            niche: Product category
            length: short (50 words), medium (150 words), long (400 words)
        """
        try:
            length_map = {
                "short": "50 words maximum",
                "medium": "150 words",
                "long": "400 words"
            }
            
            word_limit = length_map.get(length, "150 words")
            
            prompt = f"""
Write a compelling product description for:

Product: {product_title}
Niche: {niche}
Length: {word_limit}

Focus on:
- Benefits (not features)
- Solving customer pain points
- Creating urgency
- Building desire
- Clear value proposition

Return ONLY the description text, no JSON."""
            
            response = await asyncio.to_thread(
                self._generate_with_retry,
                prompt
            )
            
            return {
                "status": "success",
                "description": response.get("content", ""),
                "length": length,
                "product": product_title
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def generate_marketing_copy(
        self,
        product: Dict[str, Any],
        format_type: str = "email"
    ) -> Dict[str, Any]:
        """
        Generate marketing copy in different formats
        
        Args:
            product: Product data
            format_type: email, sales_page, social, ads
        """
        try:
            format_prompts = {
                "email": f"""Create an email sequence to sell: {product.get('title')}
                
                Generate 3 emails:
                1. Subject line + email 1 (make curiosity)
                2. Subject line + email 2 (tackle objections)
                3. Subject line + email 3 (close the sale)
                
                Return as JSON with keys: email1_subject, email1_body, email2_subject, email2_body, email3_subject, email3_body""",
                
                "sales_page": f"""Create a sales page structure for: {product.get('title')}
                
                Return JSON with:
                - headline: Main attention-grabber
                - subheadline: Supporting message
                - hook: Opening paragraph
                - pain_points_section: Customer problems
                - solution_section: How product fixes it
                - benefits_list: 5-7 key benefits
                - social_proof: Testimonial template
                - cta: Call-to-action button text""",
                
                "social": f"""Create social media content for: {product.get('title')}
                
                Return JSON with:
                - twitter_thread: 7 tweets as array
                - instagram_captions: 5 captions with hashtags
                - tiktok_hooks: 5 different opening lines
                - linkedin_post: Professional post
                - facebook_ad: Ad body text""",
                
                "ads": f"""Create ad copy variants for: {product.get('title')}
                
                Return JSON with:
                - headline1, headline2, headline3: Ad headlines (30 chars max)
                - body1, body2, body3: Ad body text (90 chars max)
                - cta1, cta2, cta3: Call-to-action variations"""
            }
            
            prompt = format_prompts.get(format_type, format_prompts["email"])
            
            response = await asyncio.to_thread(
                self._generate_with_retry,
                prompt
            )
            
            return {
                "status": "success",
                "format": format_type,
                "content": response.get("content", ""),
                "product": product.get("title")
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def brainstorm_products(
        self,
        niche: str,
        count: int = 5
    ) -> Dict[str, Any]:
        """
        Brainstorm product ideas in a niche
        
        Args:
            niche: Product niche
            count: Number of ideas to generate
        """
        try:
            prompt = f"""
Generate {count} unique product ideas for the {niche} niche.

For each, provide:
- Product name
- One-liner description
- Target market
- Estimated demand (high/medium/low)
- Competitive advantage
- Suggested price point

Return as JSON array with keys: name, description, target_market, demand, advantage, price"""
            
            response = await asyncio.to_thread(
                self._generate_with_retry,
                prompt
            )
            
            return {
                "status": "success",
                "niche": niche,
                "ideas": response.get("content", ""),
                "count": count
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def validate_product(
        self,
        product: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate product and suggest improvements
        
        Args:
            product: Product data to validate
        """
        try:
            prompt = f"""
Validate this product and provide improvements:

Title: {product.get('title')}
Description: {product.get('description')}
Price: ${product.get('price')}
Target Audience: {product.get('target_audience')}
Category: {product.get('category')}

Provide JSON response with:
- is_viable: true/false
- demand_score: 1-10
- competition_score: 1-10
- price_assessment: "too low" / "fair" / "too high"
- improvements: ["suggestion1", "suggestion2", "suggestion3"]
- market_fit_score: 1-10
- recommendation: "launch" / "refine" / "avoid"
- reasons: ["reason1", "reason2"]"""
            
            response = await asyncio.to_thread(
                self._generate_with_retry,
                prompt
            )
            
            return {
                "status": "success",
                "product": product.get("title"),
                "validation": response.get("content", "")
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _generate_with_retry(self, prompt: str, retries: int = 3) -> Dict[str, Any]:
        """Generate content with retry logic and key rotation"""
        last_error = None
        
        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                
                # Try to parse as JSON
                import json
                try:
                    content = json.loads(response.text)
                    return {"status": "success", "content": content}
                except json.JSONDecodeError:
                    # Return as plain text if not JSON
                    return {"status": "success", "content": response.text}
            
            except Exception as e:
                last_error = e
                
                # Try rotating API key
                if len(self.api_keys) > 1:
                    self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                    genai.configure(api_key=self.api_keys[self.current_key_index])
                
                if attempt < retries - 1:
                    asyncio.sleep(1)  # Wait before retry
        
        return {
            "status": "error",
            "message": f"Failed after {retries} attempts: {str(last_error)}"
        }
    
    async def analyze_market(self, niche: str) -> Dict[str, Any]:
        """Analyze market for a niche"""
        try:
            prompt = f"""
Analyze the {niche} market:

Provide JSON with:
- total_market_size: "estimated value"
- growth_rate: "% per year"
- key_players: ["player1", "player2", "player3"]
- market_gaps: ["gap1", "gap2"]
- trending_subtopics: ["trend1", "trend2", "trend3"]
- customer_pain_points: ["pain1", "pain2", "pain3"]
- barriers_to_entry: ["barrier1", "barrier2"]
- best_pricing_strategy: "description"
- recommended_marketing_channels: ["channel1", "channel2"]"""
            
            response = await asyncio.to_thread(
                self._generate_with_retry,
                prompt
            )
            
            return {
                "status": "success",
                "niche": niche,
                "analysis": response.get("content", "")
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Singleton instance
_generator = None


def get_gemini_generator() -> GeminiProductGenerator:
    """Get or create Gemini generator instance"""
    global _generator
    if _generator is None:
        _generator = GeminiProductGenerator()
    return _generator
