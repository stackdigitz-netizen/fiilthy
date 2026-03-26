"""
Sales & Launch AI
Builds funnels, landing pages, and email campaigns
"""
import asyncio
from typing import Dict, Any, List
import random
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class SalesLaunchAI:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def create_launch_campaign(self, product: Dict[str, Any], target_audience: str = "general") -> Dict[str, Any]:
        """
        Create complete launch campaign with funnel, landing page, and email sequence
        
        Args:
            product: Product dictionary
            target_audience: Target audience description
            
        Returns:
            Campaign with all assets
        """
        
        # Initialize AI chat
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"sales-launch-{datetime.now().timestamp()}",
            system_message="You are a conversion copywriting expert and sales funnel strategist. You create high-converting landing pages, email sequences, and sales funnels."
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""
Create a complete product launch campaign for:

Product: {product.get('title', 'Unknown')}
Description: {product.get('description', '')}
Price: ${product.get('price', 0)}
Target Audience: {target_audience}

Provide:

1. Landing Page Copy:
   - Headline (attention-grabbing)
   - Subheadline
   - 3 Key Benefits
   - Social proof section
   - CTA (call to action)
   - Urgency element

2. Email Sequence (5 emails):
   - Email 1: Welcome & Introduction
   - Email 2: Problem/Solution
   - Email 3: Social Proof & Testimonials
   - Email 4: Limited Time Offer
   - Email 5: Last Chance
   (Include subject lines and body copy)

3. Upsells/Cross-sells:
   - 2 complementary product suggestions
   - Bundle offers

4. Funnel Flow:
   - Step-by-step customer journey
   - Conversion optimization tips

Return as JSON:
{{
  "landing_page": {{
    "headline": "Headline",
    "subheadline": "Subheadline",
    "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
    "social_proof": "Testimonial or stat",
    "cta": "CTA text",
    "urgency": "Limited time element"
  }},
  "email_sequence": [
    {{"day": 1, "subject": "Subject", "body": "Email body", "goal": "Goal"}}
  ],
  "upsells": [
    {{"title": "Upsell product", "price": 49.99, "pitch": "Why add this"}}
  ],
  "funnel_flow": ["Step 1", "Step 2", "Step 3"],
  "conversion_tips": ["Tip 1", "Tip 2"]
}}
"""
        
        try:
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            import json
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            campaign = json.loads(response_text)
            
            # Add metadata
            campaign["id"] = f"campaign-{random.randint(1000, 9999)}"
            campaign["product_id"] = product.get("id")
            campaign["status"] = "ready"
            campaign["created_at"] = datetime.now(timezone.utc).isoformat()
            campaign["conversions"] = 0
            campaign["revenue"] = 0.0
            
            return campaign
            
        except Exception as e:
            print(f"Error creating launch campaign: {str(e)}")
            return self._get_fallback_campaign(product)
    
    def _get_fallback_campaign(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback campaign if AI fails"""
        title = product.get('title', 'Product')
        return {
            "id": f"campaign-{random.randint(1000, 9999)}",
            "product_id": product.get("id"),
            "landing_page": {
                "headline": f"Transform Your Life with {title}",
                "subheadline": "The complete solution you've been waiting for",
                "benefits": [
                    "Save time and increase productivity",
                    "Learn from experts and proven strategies",
                    "Get results in days, not months"
                ],
                "social_proof": "Join 1000+ satisfied customers",
                "cta": "Get Instant Access Now",
                "urgency": "Limited time offer - 50% off for early adopters"
            },
            "email_sequence": [
                {
                    "day": 1,
                    "subject": f"Welcome! Here's your {title}",
                    "body": "Thanks for your interest. Let me show you what's inside...",
                    "goal": "Welcome and engage"
                }
            ],
            "upsells": [
                {
                    "title": "Premium Bundle",
                    "price": 79.99,
                    "pitch": "Get 3x the value with our complete bundle"
                }
            ],
            "funnel_flow": ["Landing Page", "Checkout", "Upsell", "Thank You"],
            "conversion_tips": ["Use urgency", "Show social proof"],
            "status": "ready",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "conversions": 0,
            "revenue": 0.0
        }
