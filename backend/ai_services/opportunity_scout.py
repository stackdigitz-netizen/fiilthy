"""
Opportunity Scouting AI
Automatically identifies trending niches, keywords, and products.
Uses standard OpenAI SDK.
"""
import asyncio
import json
import logging
from typing import List, Dict, Any
import random
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import openai

load_dotenv()
logger = logging.getLogger(__name__)


class OpportunityScout:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_KEY') or ''
        
    async def scout_opportunities(self, sources: List[str] = None) -> List[Dict[str, Any]]:
        if sources is None:
            sources = ["social media trends", "digital product marketplaces", "search trends"]
        
        if not self.api_key:
            return self._get_fallback_opportunities()
        
        client = openai.OpenAI(api_key=self.api_key)
        
        prompt = f"""Analyze current market trends and identify 5 high-potential opportunities for digital products (eBooks, courses, templates, planners).

For each opportunity, provide niche name, trend score (0.0-1.0), 3-5 keywords, 2-3 product titles, market size, and competition level.

Focus on niches that are trending, have monetization potential, and aren't oversaturated.
Sources: {', '.join(sources)}

Return ONLY valid JSON (no markdown fences):
{{"opportunities": [
  {{"niche": "Niche Name", "trend_score": 0.85, "keywords": ["kw1","kw2","kw3"], "suggested_products": ["Title1","Title2"], "market_size": "Large", "competition_level": "Medium"}}
]}}"""

        try:
            def _call():
                return client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert market researcher specializing in profitable digital product opportunities."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.8,
                    max_tokens=1000,
                )

            response = await asyncio.to_thread(_call)
            text = response.choices[0].message.content.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.split("```")[0].strip()
            
            data = json.loads(text)
            opportunities = data.get("opportunities", [])
            
            for opp in opportunities:
                opp["id"] = f"opp-{random.randint(1000, 9999)}"
                opp["status"] = "identified"
                opp["created_at"] = datetime.now(timezone.utc).isoformat()
            
            return opportunities
            
        except Exception as e:
            logger.error("Opportunity scouting error: %s", e)
            return self._get_fallback_opportunities()
    
    def _get_fallback_opportunities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": f"opp-{random.randint(1000, 9999)}",
                "niche": "AI Tools for Content Creators",
                "trend_score": 0.89,
                "keywords": ["AI tools", "content creation", "automation"],
                "suggested_products": ["AI Content Guide", "Creator Toolkit"],
                "market_size": "Large",
                "competition_level": "Medium",
                "status": "identified",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
