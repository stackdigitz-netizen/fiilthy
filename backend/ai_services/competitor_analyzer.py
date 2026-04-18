"""
Competitor Analyzer - Real implementation using OpenAI GPT.
Analyzes competitors, finds market gaps, and generates competitive intelligence.
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import openai

logger = logging.getLogger(__name__)

PRODUCTION_READY = True
PRODUCTION_STATUS = "production"


class CompetitorAnalyzer:
    """Analyze competitors and find opportunities using AI."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY") or ""

    def _client(self) -> openai.OpenAI:
        return openai.OpenAI(api_key=self.api_key)

    async def _ask(self, prompt: str, system: str = "You are an expert market researcher and competitive analyst. Respond only with valid JSON.") -> dict:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not configured")
        client = self._client()

        def _call():
            return client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

        response = await asyncio.to_thread(_call)
        text = response.choices[0].message.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.split("```")[0].strip()
        return json.loads(text)

    async def analyze_competitor(self, competitor_name: str, competitor_url: str = None) -> Dict[str, Any]:
        """Analyze a specific competitor using AI."""
        url_context = f" (website: {competitor_url})" if competitor_url else ""
        prompt = f"""Analyze the competitor "{competitor_name}"{url_context} in the digital products / online business space.
Return ONLY valid JSON (no markdown fences):
{{
  "competitor_name": "{competitor_name}",
  "pricing": {{"entry_level": <number>, "mid_level": <number>, "premium": <number>}},
  "strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "weaknesses": ["<weakness1>", "<weakness2>", "<weakness3>"],
  "market_share": "<percentage string>",
  "estimated_revenue": "<revenue string>",
  "growth_rate": "<YoY growth string>",
  "target_audience": "<description>",
  "key_differentiators": ["<diff1>", "<diff2>"],
  "threat_level": "Low|Medium|High"
}}"""
        try:
            result = await self._ask(prompt)
            result["analyzed_at"] = datetime.now(timezone.utc).isoformat()
            return result
        except Exception as e:
            logger.error("analyze_competitor error: %s", e)
            return {
                "competitor_name": competitor_name,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "pricing": {"entry_level": 0, "mid_level": 0, "premium": 0},
                "strengths": [],
                "weaknesses": [],
            }

    async def find_market_gaps(self, niche: str) -> List[Dict]:
        """Find underserved market segments in niche using AI."""
        prompt = f"""Identify 4 specific underserved market gaps within the "{niche}" niche for digital products.
Return ONLY valid JSON (no markdown fences):
{{
  "gaps": [
    {{
      "gap": "<specific gap name>",
      "demand_score": <0.0-1.0>,
      "competition_score": <0.0-1.0>,
      "opportunity_score": <0.0-1.0>,
      "estimated_market_size": "<size>",
      "recommendation": "<one sentence action>",
      "target_customer": "<who to target>"
    }}
  ]
}}"""
        try:
            result = await self._ask(prompt)
            gaps = result.get("gaps", [])
            return sorted(gaps, key=lambda x: x.get("opportunity_score", 0), reverse=True)
        except Exception as e:
            logger.error("find_market_gaps error: %s", e)
            return []

    async def analyze_customer_sentiment(self, competitor_name: str, source: str = "reviews") -> Dict[str, Any]:
        """Analyze what customers say about a competitor using AI."""
        prompt = f"""Based on your knowledge of "{competitor_name}", analyze customer sentiment from {source}.
Return ONLY valid JSON (no markdown fences):
{{
  "competitor": "{competitor_name}",
  "source": "{source}",
  "sentiment_score": <1.0-5.0>,
  "positive_mentions": <integer>,
  "negative_mentions": <integer>,
  "common_complaints": ["<complaint1>", "<complaint2>", "<complaint3>"],
  "common_praise": ["<praise1>", "<praise2>", "<praise3>"],
  "net_promoter_score": <-100 to 100>,
  "key_insight": "<one actionable insight for competing against them>"
}}"""
        try:
            return await self._ask(prompt)
        except Exception as e:
            logger.error("analyze_customer_sentiment error: %s", e)
            return {"competitor": competitor_name, "source": source, "error": str(e)}

    async def find_underpriced_markets(self) -> List[Dict]:
        """Find digital product market segments that are underpriced relative to their value."""
        prompt = """Identify 4 digital product market segments that are currently underpriced relative to their delivered value.
Return ONLY valid JSON (no markdown fences):
{{
  "markets": [
    {{
      "market": "<market name>",
      "current_avg_price": <number>,
      "recommended_price": <number>,
      "value_justification": "<why it deserves higher pricing>",
      "potential_uplift": "<percentage>",
      "buyer_persona": "<who buys this>"
    }}
  ]
}}"""
        try:
            result = await self._ask(prompt)
            return result.get("markets", [])
        except Exception as e:
            logger.error("find_underpriced_markets error: %s", e)
            return []

    async def get_competitive_intelligence(self, niche: str) -> Dict[str, Any]:
        """Get full competitive landscape for a niche."""
        prompt = f"""Provide a comprehensive competitive intelligence report for the "{niche}" digital products niche.
Return ONLY valid JSON (no markdown fences):
{{
  "niche": "{niche}",
  "total_competitors": <integer>,
  "market_leader": "<leader name>",
  "market_consolidation": "Fragmented|Moderate|Consolidated",
  "entry_barriers": "Low|Low-Medium|Medium|Medium-High|High",
  "growth_opportunities": ["<opp1>", "<opp2>", "<opp3>", "<opp4>"],
  "recommended_positioning": "<specific positioning strategy>",
  "potential_revenue": "<revenue range>",
  "top_competitors": [
    {{"name": "<name>", "strength": "Low|Medium|High", "notable_for": "<what they do well>"}}
  ],
  "winning_strategy": "<how to win in this niche>"
}}"""
        try:
            result = await self._ask(prompt)
            result["market_analysis_date"] = datetime.now(timezone.utc).isoformat()
            return result
        except Exception as e:
            logger.error("get_competitive_intelligence error: %s", e)
            return {"niche": niche, "error": str(e), "market_analysis_date": datetime.now(timezone.utc).isoformat()}
