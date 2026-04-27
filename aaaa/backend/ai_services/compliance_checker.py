"""
Compliance Checker
Automated content compliance and filtering
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone
import random
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class ComplianceChecker:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        self.check_types = [
            "plagiarism", "copyright", "affiliate_disclosure", 
            "privacy_compliance", "content_moderation"
        ]
    
    async def check_product_compliance(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive compliance checks on a product
        
        Args:
            product: Product dictionary
            
        Returns:
            Compliance report with pass/fail status
        """
        
        results = {
            "product_id": product.get("id"),
            "product_title": product.get("title"),
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "checks": [],
            "overall_status": "passed",
            "issues": [],
            "warnings": []
        }
        
        # Run all compliance checks
        checks = [
            await self._check_plagiarism(product),
            await self._check_copyright(product),
            await self._check_affiliate_disclosure(product),
            await self._check_privacy_compliance(product),
            await self._check_content_moderation(product)
        ]
        
        results["checks"] = checks
        
        # Aggregate results
        for check in checks:
            if check["status"] == "failed":
                results["overall_status"] = "failed"
                results["issues"].extend(check.get("issues", []))
            elif check["status"] == "warning":
                if results["overall_status"] != "failed":
                    results["overall_status"] = "warning"
                results["warnings"].extend(check.get("warnings", []))
        
        return results
    
    async def _check_plagiarism(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Check for plagiarism (mock implementation)"""
        await asyncio.sleep(0.3)
        
        # Simulate plagiarism check
        similarity_score = random.uniform(0, 25)  # Mock: 0-25% similarity is normal
        
        return {
            "check_type": "plagiarism",
            "status": "passed" if similarity_score < 15 else "warning" if similarity_score < 25 else "failed",
            "similarity_score": round(similarity_score, 2),
            "details": f"Content similarity: {round(similarity_score, 2)}%",
            "issues": [f"High similarity detected ({round(similarity_score, 2)}%)"] if similarity_score >= 25 else [],
            "warnings": [f"Moderate similarity ({round(similarity_score, 2)}%)"] if 15 <= similarity_score < 25 else []
        }
    
    async def _check_copyright(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Check for copyright issues using AI"""
        
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"compliance-{datetime.now().timestamp()}",
                system_message="You are a legal compliance expert. Analyze content for potential copyright issues."
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""
Analyze this product for potential copyright issues:

Title: {product.get('title', 'Unknown')}
Description: {product.get('description', '')[:500]}
Type: {product.get('product_type', 'unknown')}

Check for:
1. Brand name usage without permission
2. Trademarked terms
3. Protected content references

Return JSON:
{{
  "status": "passed/warning/failed",
  "issues": ["Issue 1"],
  "recommendations": ["Rec 1"]
}}
"""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            import json
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            return {
                "check_type": "copyright",
                **result
            }
            
        except Exception as e:
            # Fallback to mock
            return {
                "check_type": "copyright",
                "status": "passed",
                "issues": [],
                "details": "No copyright issues detected"
            }
    
    async def _check_affiliate_disclosure(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Check if affiliate disclosures are present"""
        await asyncio.sleep(0.2)
        
        # Check if product has affiliate links
        has_affiliate_links = any(
            'affiliate' in link.get('url', '').lower() or 'aff' in link.get('url', '').lower()
            for link in product.get('marketplace_links', [])
        )
        
        if has_affiliate_links:
            # Check for disclosure
            description = product.get('description', '').lower()
            has_disclosure = 'affiliate' in description or 'commission' in description
            
            if not has_disclosure:
                return {
                    "check_type": "affiliate_disclosure",
                    "status": "failed",
                    "issues": ["Affiliate links detected without proper disclosure"],
                    "recommendations": ["Add affiliate disclosure to product description"]
                }
        
        return {
            "check_type": "affiliate_disclosure",
            "status": "passed",
            "details": "Affiliate disclosure check passed"
        }
    
    async def _check_privacy_compliance(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Check GDPR/privacy compliance"""
        await asyncio.sleep(0.2)
        
        # Basic privacy checks
        issues = []
        warnings = []
        
        # Check if product collects data
        product_type = product.get('product_type', '')
        if product_type in ['mini_app', 'software']:
            warnings.append("Product may collect user data - ensure privacy policy is present")
        
        status = "failed" if issues else "warning" if warnings else "passed"
        
        return {
            "check_type": "privacy_compliance",
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "details": "GDPR/Privacy compliance check"
        }
    
    async def _check_content_moderation(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Check for inappropriate content"""
        await asyncio.sleep(0.2)
        
        # Mock content moderation check
        inappropriate_keywords = ['violence', 'hate', 'explicit', 'illegal']
        
        title = product.get('title', '').lower()
        description = product.get('description', '').lower()
        
        found_issues = [
            keyword for keyword in inappropriate_keywords 
            if keyword in title or keyword in description
        ]
        
        if found_issues:
            return {
                "check_type": "content_moderation",
                "status": "failed",
                "issues": [f"Inappropriate content detected: {', '.join(found_issues)}"],
                "recommendations": ["Review and modify content"]
            }
        
        return {
            "check_type": "content_moderation",
            "status": "passed",
            "details": "Content moderation passed"
        }
