"""
Gumroad Auto-Publisher
Creates and manages products on Gumroad via their v2 API.
"""
import os
import logging
from datetime import datetime, timezone
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GUMROAD_API_URL = "https://api.gumroad.com/v2"


class GumroadPublisher:
    """Gumroad integration — create products, track sales."""
    
    def __init__(self):
        self.access_token = os.environ.get("GUMROAD_ACCESS_TOKEN")

    # ------------------------------------------------------------------
    # Product creation
    # ------------------------------------------------------------------

    async def publish_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Create a real product on Gumroad via API and return the live URL."""
        if not self.access_token:
            return {"success": False, "error": "GUMROAD_ACCESS_TOKEN not configured"}

        product_type = (product.get("product_type") or product.get("type") or "ebook").lower()
        title = product.get("title", "Untitled Product")
        description = product.get("description", "")
        price_cents = int(float(product.get("price", 9.99)) * 100)

        payload = {
            "access_token": self.access_token,
            "name": title,
            "description": description,
            "price": price_cents,
            "preview_url": product.get("image_url") or product.get("cover_image_url") or "",
            "published": True,
        }

        try:
            resp = requests.post(f"{GUMROAD_API_URL}/products", data=payload, timeout=30)
            data = resp.json()
            if data.get("success"):
                gumroad_product = data.get("product", {})
                return {
                    "success": True,
                    "platform": "gumroad",
                    "gumroad_id": gumroad_product.get("id"),
                    "url": gumroad_product.get("short_url") or gumroad_product.get("url"),
                    "name": gumroad_product.get("name"),
                    "price_cents": gumroad_product.get("price"),
                    "published": gumroad_product.get("published"),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            return {"success": False, "error": data.get("message", f"HTTP {resp.status_code}")}
        except Exception as e:
            logger.error("Gumroad publish error: %s", e)
            return {"success": False, "error": str(e)}

    # Convenience aliases
    async def publish_ebook(self, product: Dict[str, Any]) -> Dict[str, Any]:
        return await self.publish_product(product)

    async def publish_course(self, product: Dict[str, Any]) -> Dict[str, Any]:
        return await self.publish_product(product)

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    async def get_products(self) -> Dict[str, Any]:
        """Get all products from Gumroad account"""
        if not self.access_token:
            return {"success": False, "error": "GUMROAD_ACCESS_TOKEN not configured"}
            
        try:
            response = requests.get(
                f"{GUMROAD_API_URL}/products",
                params={"access_token": self.access_token},
                timeout=15,
            )
            data = response.json()
            if data.get("success"):
                return {"success": True, "products": data.get("products", [])}
            return {"success": False, "error": data.get("message", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_sales(self, product_id: str = None) -> Dict[str, Any]:
        """Get sales data from Gumroad"""
        if not self.access_token:
            return {"success": False, "error": "GUMROAD_ACCESS_TOKEN not configured"}
            
        try:
            params: Dict[str, Any] = {"access_token": self.access_token}
            if product_id:
                params["product_id"] = product_id
                
            response = requests.get(f"{GUMROAD_API_URL}/sales", params=params, timeout=15)
            data = response.json()
            if data.get("success"):
                return {"success": True, "sales": data.get("sales", [])}
            return {"success": False, "error": data.get("message", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user(self) -> Dict[str, Any]:
        """Get Gumroad user/account info"""
        if not self.access_token:
            return {"success": False, "error": "GUMROAD_ACCESS_TOKEN not configured"}
            
        try:
            response = requests.get(
                f"{GUMROAD_API_URL}/user",
                params={"access_token": self.access_token},
                timeout=15,
            )
            data = response.json()
            if data.get("success"):
                return {"success": True, "user": data.get("user", {})}
            return {"success": False, "error": data.get("message", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Aliases expected by server.py endpoints
    async def get_account_info(self) -> Dict[str, Any]:
        return await self.get_user()

    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.publish_product(product_data)

    async def update_product(self, gumroad_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        if not self.access_token:
            return {"success": False, "error": "GUMROAD_ACCESS_TOKEN not configured"}
        try:
            payload = {"access_token": self.access_token, **updates}
            resp = requests.put(f"{GUMROAD_API_URL}/products/{gumroad_id}", data=payload, timeout=15)
            data = resp.json()
            return {"success": data.get("success", False), "product": data.get("product", {})}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete_product(self, gumroad_id: str) -> Dict[str, Any]:
        if not self.access_token:
            return {"success": False, "error": "GUMROAD_ACCESS_TOKEN not configured"}
        try:
            resp = requests.delete(
                f"{GUMROAD_API_URL}/products/{gumroad_id}",
                data={"access_token": self.access_token},
                timeout=15,
            )
            data = resp.json()
            return {"success": data.get("success", False)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_product_details(self, gumroad_id: str) -> Dict[str, Any]:
        if not self.access_token:
            return {"success": False, "error": "GUMROAD_ACCESS_TOKEN not configured"}
        try:
            resp = requests.get(
                f"{GUMROAD_API_URL}/products/{gumroad_id}",
                params={"access_token": self.access_token},
                timeout=15,
            )
            data = resp.json()
            if data.get("success"):
                return {"success": True, "product": data.get("product", {})}
            return {"success": False, "error": data.get("message", "Unknown")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def upload_product_file(self, gumroad_id: str, file_path: str = "", **kw) -> Dict[str, Any]:
        return {"success": False, "error": "File upload requires multipart form — use Gumroad dashboard"}

    async def get_product_analytics(self, gumroad_id: str = "", **kw) -> Dict[str, Any]:
        return await self.get_sales(product_id=gumroad_id)

    async def get_account_analytics(self) -> Dict[str, Any]:
        return await self.get_sales()

    async def create_variant(self, gumroad_id: str = "", **kw) -> Dict[str, Any]:
        return {"success": False, "error": "Variant creation not yet implemented"}

    async def get_license_info(self, gumroad_id: str) -> Dict[str, Any]:
        return {"success": False, "error": "License info not yet implemented"}
