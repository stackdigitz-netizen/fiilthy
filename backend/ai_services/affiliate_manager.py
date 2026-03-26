"""
Affiliate Management AI
Recruits affiliates, manages campaigns, tracks performance
"""
import asyncio
from typing import Dict, Any, List
import random
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class AffiliateManager:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def generate_affiliate_program(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate affiliate program structure and recruitment materials
        
        Args:
            products: List of products to include in affiliate program
            
        Returns:
            Affiliate program details and assets
        """
        
        # Initialize AI chat
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"affiliate-mgr-{datetime.now().timestamp()}",
            system_message="You are an affiliate marketing expert. You design profitable affiliate programs, create compelling recruitment materials, and structure commission plans that motivate partners."
        ).with_model("openai", "gpt-5.2")
        
        product_list = "\n".join([
            f"- {p.get('title', 'Unknown')} (${p.get('price', 0)})"
            for p in products[:10]
        ])
        
        prompt = f"""
Design a comprehensive affiliate program for these digital products:

{product_list}

Provide:

1. Commission Structure:
   - Base commission rate (%)
   - Tiered commission levels (based on sales volume)
   - Special bonuses

2. Affiliate Recruitment Pitch:
   - Why join this program?
   - Earning potential
   - Support provided

3. Marketing Assets for Affiliates:
   - Email templates
   - Social media post templates
   - Banner ad copy

4. Performance Tiers:
   - Bronze/Silver/Gold/Platinum levels
   - Requirements for each tier
   - Benefits per tier

5. Promotional Campaigns:
   - 3 campaign ideas for affiliates
   - Special offers they can promote

Return as JSON:
{{
  "commission_structure": {{
    "base_rate": 30,
    "tiers": [
      {{"level": "Bronze", "sales_required": 5, "rate": 30}},
      {{"level": "Silver", "sales_required": 20, "rate": 35}},
      {{"level": "Gold", "sales_required": 50, "rate": 40}}
    ],
    "bonuses": ["Bonus description"]
  }},
  "recruitment_pitch": {{
    "headline": "Join Our Program",
    "benefits": ["Benefit 1"],
    "earning_potential": "Earn $X per month",
    "support": "Support description"
  }},
  "marketing_assets": {{
    "email_templates": ["Template 1"],
    "social_templates": ["Post template"],
    "banner_copy": ["Banner text"]
  }},
  "campaigns": [
    {{"name": "Campaign name", "offer": "Special offer", "duration": "30 days"}}
  ]
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
            
            program = json.loads(response_text)
            
            # Add metadata
            program["id"] = f"affiliate-prog-{random.randint(1000, 9999)}"
            program["created_at"] = datetime.now(timezone.utc).isoformat()
            program["active_affiliates"] = 0
            program["total_sales"] = 0
            program["total_revenue"] = 0.0
            
            # Generate mock affiliates
            program["top_affiliates"] = self._generate_mock_affiliates()
            
            return program
            
        except Exception as e:
            print(f"Error generating affiliate program: {str(e)}")
            return self._get_fallback_program()
    
    def _generate_mock_affiliates(self) -> List[Dict[str, Any]]:
        """Generate mock affiliate data for demo"""
        names = ["Sarah Marketing Pro", "John Digital", "Emma Growth Hacker", "Mike Sales Guru", "Lisa Influencer"]
        affiliates = []
        
        for i, name in enumerate(names):
            affiliates.append({
                "id": f"aff-{random.randint(1000, 9999)}",
                "name": name,
                "email": f"{name.lower().replace(' ', '.')}@example.com",
                "tier": ["Gold", "Silver", "Gold", "Bronze", "Silver"][i],
                "sales": random.randint(10, 100),
                "revenue": round(random.uniform(500, 5000), 2),
                "commission_earned": round(random.uniform(150, 1500), 2),
                "joined_date": datetime.now(timezone.utc).isoformat()
            })
        
        return affiliates
    
    def _get_fallback_program(self) -> Dict[str, Any]:
        """Fallback program if AI fails"""
        return {
            "id": f"affiliate-prog-{random.randint(1000, 9999)}",
            "commission_structure": {
                "base_rate": 30,
                "tiers": [
                    {"level": "Bronze", "sales_required": 5, "rate": 30},
                    {"level": "Silver", "sales_required": 20, "rate": 35},
                    {"level": "Gold", "sales_required": 50, "rate": 40}
                ],
                "bonuses": ["First sale bonus: $50", "Monthly top performer: $500"]
            },
            "recruitment_pitch": {
                "headline": "Earn Premium Commissions Promoting Quality Digital Products",
                "benefits": [
                    "Up to 40% commission on all sales",
                    "Recurring commissions on subscriptions",
                    "Dedicated affiliate support",
                    "Ready-made marketing materials"
                ],
                "earning_potential": "Top affiliates earn $3,000-$10,000/month",
                "support": "Dedicated affiliate manager, weekly training, and exclusive resources"
            },
            "marketing_assets": {
                "email_templates": ["Product launch email", "Limited offer email", "Follow-up sequence"],
                "social_templates": ["Instagram post", "Twitter thread", "LinkedIn article"],
                "banner_copy": ["300x250 banner", "728x90 leaderboard", "160x600 skyscraper"]
            },
            "campaigns": [
                {
                    "name": "Spring Launch Bonus",
                    "offer": "Double commissions on first 50 sales",
                    "duration": "30 days"
                },
                {
                    "name": "Bundle Promo",
                    "offer": "45% commission on bundle sales",
                    "duration": "14 days"
                }
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active_affiliates": 127,
            "total_sales": 1543,
            "total_revenue": 67890.50,
            "top_affiliates": self._generate_mock_affiliates()
        }
