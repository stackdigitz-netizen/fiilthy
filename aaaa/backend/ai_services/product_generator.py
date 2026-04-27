"""
Product AI
Generates digital products like templates, planners, checklists
"""
import asyncio
from typing import Dict, Any, List
import random
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class ProductGenerator:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def generate_product(self,
                             product_type: str,
                             keywords: List[str],
                             style: str = "professional",
                             target_use_case: str = None) -> Dict[str, Any]:
        """
        Generate a digital product
        
        Args:
            product_type: template/planner/mini_app
            keywords: Relevant keywords
            style: Design style preference
            target_use_case: Specific use case or audience
            
        Returns:
            Dictionary with product structure and content
        """
        
        # Initialize AI chat
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"product-gen-{datetime.now().timestamp()}",
            system_message="You are a product designer specializing in digital products. You create useful, well-designed templates, planners, and tools."
        ).with_model("openai", "gpt-5.2")
        
        use_case_text = f" for {target_use_case}" if target_use_case else ""
        
        # Generate product structure based on type
        if product_type == "template":
            product_data = await self._generate_template(chat, keywords, style, use_case_text)
        elif product_type == "planner":
            product_data = await self._generate_planner(chat, keywords, style, use_case_text)
        elif product_type == "mini_app":
            product_data = await self._generate_mini_app(chat, keywords, use_case_text)
        else:
            raise ValueError(f"Unknown product type: {product_type}")
        
        return product_data
    
    async def _generate_template(self, chat, keywords: List[str], style: str, use_case_text: str) -> Dict[str, Any]:
        """Generate a template product"""
        prompt = f"""
Design a professional template{use_case_text}.

Keywords: {', '.join(keywords)}
Style: {style}

Provide:
1. Template title
2. Description (what it's for, key features)
3. List of included components/sections
4. Use cases
5. File formats included (e.g., PDF, PowerPoint, Google Slides)

Format as JSON:
{{
  "title": "Template Title",
  "description": "Template description",
  "components": ["Component 1", "Component 2"],
  "use_cases": ["Use case 1"],
  "formats": ["PDF", "PPTX"],
  "pages": 10
}}
"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        import json
        response_text = response.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        template_data = json.loads(response_text)
        
        return {
            "id": f"template-{random.randint(1000, 9999)}",
            "title": template_data['title'],
            "description": template_data['description'],
            "product_type": "template",
            "content": template_data,
            "status": "ready",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": keywords,
            "metadata": {
                "components": template_data.get('components', []),
                "formats": template_data.get('formats', []),
                "pages": template_data.get('pages', 0)
            }
        }
    
    async def _generate_planner(self, chat, keywords: List[str], style: str, use_case_text: str) -> Dict[str, Any]:
        """Generate a planner product"""
        prompt = f"""
Design a comprehensive planner{use_case_text}.

Keywords: {', '.join(keywords)}
Style: {style}

Provide:
1. Planner title
2. Description (purpose, key features)
3. Sections included (daily/weekly/monthly, goals, trackers, etc.)
4. Special features (habit tracker, goal setting, etc.)
5. Page count
6. Time period covered (30 days, 90 days, 365 days)

Format as JSON:
{{
  "title": "Planner Title",
  "description": "Planner description",
  "sections": ["Section 1", "Section 2"],
  "features": ["Feature 1"],
  "pages": 100,
  "time_period": "365 days"
}}
"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        import json
        response_text = response.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        planner_data = json.loads(response_text)
        
        return {
            "id": f"planner-{random.randint(1000, 9999)}",
            "title": planner_data['title'],
            "description": planner_data['description'],
            "product_type": "planner",
            "content": planner_data,
            "status": "ready",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": keywords,
            "metadata": {
                "sections": planner_data.get('sections', []),
                "features": planner_data.get('features', []),
                "pages": planner_data.get('pages', 0),
                "time_period": planner_data.get('time_period', '')
            }
        }
    
    async def _generate_mini_app(self, chat, keywords: List[str], use_case_text: str) -> Dict[str, Any]:
        """Generate a mini app/tool product"""
        prompt = f"""
Design a useful mini web app or tool{use_case_text}.

Keywords: {', '.join(keywords)}

Provide:
1. App name
2. Description (what it does, key features)
3. Main features/capabilities
4. User interface components
5. Use cases

Format as JSON:
{{
  "title": "App Name",
  "description": "App description",
  "features": ["Feature 1", "Feature 2"],
  "ui_components": ["Component 1"],
  "use_cases": ["Use case 1"]
}}
"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        import json
        response_text = response.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        app_data = json.loads(response_text)
        
        return {
            "id": f"miniapp-{random.randint(1000, 9999)}",
            "title": app_data['title'],
            "description": app_data['description'],
            "product_type": "mini_app",
            "content": app_data,
            "status": "ready",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": keywords,
            "metadata": {
                "features": app_data.get('features', []),
                "ui_components": app_data.get('ui_components', []),
                "use_cases": app_data.get('use_cases', [])
            }
        }
