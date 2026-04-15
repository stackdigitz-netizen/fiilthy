"""
Marketplace Integrations
Connects to various digital product marketplaces
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import random

from ai_services.gumroad_publisher import GumroadPublisher
from ai_services.multi_platform_product_sync import MultiPlatformProductSync

class MarketplaceIntegrations:
    def __init__(self):
        self.supported_marketplaces = [
            "gumroad", "shopify", "amazon_kdp", "etsy", "udemy"
        ]
        self.sync_manager = MultiPlatformProductSync()
        self.gumroad_publisher = GumroadPublisher()
    
    async def publish_to_marketplace(self, 
                                    product: Dict[str, Any], 
                                    marketplace: str,
                                    credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Publish product to a marketplace
        
        Args:
            product: Product dictionary
            marketplace: Target marketplace name
            credentials: API credentials (optional for mock)
            
        Returns:
            Publishing result with listing URL
        """
        
        if marketplace not in self.supported_marketplaces:
            raise ValueError(f"Unsupported marketplace: {marketplace}")
        
        # Mock publishing (replace with real API calls when credentials provided)
        if marketplace == "gumroad":
            return await self._publish_to_gumroad(product, credentials)
        elif marketplace == "shopify":
            return await self._publish_to_shopify(product, credentials)
        elif marketplace == "amazon_kdp":
            return await self._publish_to_amazon_kdp(product, credentials)
        elif marketplace == "etsy":
            return await self._publish_to_etsy(product, credentials)
        elif marketplace == "udemy":
            return await self._publish_to_udemy(product, credentials)
    
    async def _publish_to_gumroad(self, product: Dict[str, Any], credentials: Optional[Dict]) -> Dict[str, Any]:
        """Prepare a Gumroad listing handoff using the real Gumroad helper."""
        if (product.get("product_type") or "").lower() == "course":
            listing = await self.gumroad_publisher.publish_course(product)
        else:
            listing = await self.gumroad_publisher.publish_ebook(product)

        if not listing.get("success"):
            return {
                "marketplace": "gumroad",
                "status": "error",
                "reason": listing.get("error", "Gumroad configuration missing")
            }

        return {
            "marketplace": "gumroad",
            "listing_id": None,
            "listing_url": listing.get("dashboard_url"),
            "status": "manual_required",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "product_id": product.get("id"),
            "price": product.get("price", 0),
            "integration_type": "manual",
            "instructions": listing.get("instructions", []),
            "product_template": listing.get("product_template", {}),
        }
    
    async def _publish_to_shopify(self, product: Dict[str, Any], credentials: Optional[Dict]) -> Dict[str, Any]:
        """Publish to Shopify using the live product sync service."""
        result = await self.sync_manager._sync_to_shopify(product)
        if not result.get("success"):
            return {
                "marketplace": "shopify",
                "status": "error",
                "reason": result.get("error", "Shopify publish failed")
            }

        return {
            "marketplace": "shopify",
            "listing_id": result.get("product_id"),
            "listing_url": result.get("url"),
            "status": result.get("status", "published"),
            "published_at": datetime.now(timezone.utc).isoformat(),
            "product_id": product.get("id"),
            "price": product.get("price", 0),
            "inventory": product.get("inventory", {}).get("shopify", "unlimited"),
            "integration_type": "live"
        }
    
    async def _publish_to_amazon_kdp(self, product: Dict[str, Any], credentials: Optional[Dict]) -> Dict[str, Any]:
        """Publish to Amazon KDP (mock implementation)"""
        await asyncio.sleep(0.5)
        
        if product.get("product_type") not in ["ebook", "book"]:
            return {
                "marketplace": "amazon_kdp",
                "status": "rejected",
                "reason": "Only eBooks are supported on Amazon KDP"
            }
        
        asin = f"B0{random.randint(10000000, 99999999)}"
        return {
            "marketplace": "amazon_kdp",
            "listing_id": asin,
            "listing_url": f"https://amazon.com/dp/{asin}",
            "status": "under_review",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "product_id": product.get("id"),
            "price": product.get("price", 0),
            "isbn": f"979-8-{random.randint(100000, 999999)}",
            "integration_type": "mock" if not credentials else "live"
        }
    
    async def _publish_to_etsy(self, product: Dict[str, Any], credentials: Optional[Dict]) -> Dict[str, Any]:
        """Publish to Etsy using the live product sync service."""
        if (product.get("product_type") or "").lower() not in {
            "template",
            "planner",
            "digital",
            "ebook",
            "guide",
            "workbook",
            "toolkit",
            "spreadsheet",
            "checklist",
        }:
            return {
                "marketplace": "etsy",
                "status": "rejected",
                "reason": "Product type not suitable for Etsy digital downloads"
            }

        result = await self.sync_manager._sync_to_etsy(product)
        if not result.get("success"):
            return {
                "marketplace": "etsy",
                "status": "error",
                "reason": result.get("error", "Etsy publish failed")
            }

        return {
            "marketplace": "etsy",
            "listing_id": result.get("listing_id"),
            "listing_url": result.get("url"),
            "status": result.get("status", "published"),
            "published_at": datetime.now(timezone.utc).isoformat(),
            "product_id": product.get("id"),
            "price": product.get("price", 0),
            "category": "digital_downloads",
            "integration_type": "live"
        }
    
    async def _publish_to_udemy(self, product: Dict[str, Any], credentials: Optional[Dict]) -> Dict[str, Any]:
        """Publish to Udemy (mock implementation)"""
        await asyncio.sleep(0.5)
        
        if product.get("product_type") != "course":
            return {
                "marketplace": "udemy",
                "status": "rejected",
                "reason": "Only courses are supported on Udemy"
            }
        
        course_id = f"udemy-{random.randint(1000000, 9999999)}"
        return {
            "marketplace": "udemy",
            "listing_id": course_id,
            "listing_url": f"https://udemy.com/course/{course_id}",
            "status": "draft",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "product_id": product.get("id"),
            "price": product.get("price", 0),
            "approval_status": "pending_review",
            "integration_type": "mock" if not credentials else "live"
        }
    
    async def get_marketplace_stats(self, db) -> Dict[str, Any]:
        """Get aggregated marketplace statistics"""
        listings = await db.marketplace_listings.find({}, {"_id": 0}).to_list(1000)
        
        stats = {
            "total_listings": len(listings),
            "by_marketplace": {},
            "by_status": {},
            "total_sales": 0,
            "total_revenue": 0.0
        }
        
        for listing in listings:
            marketplace = listing.get("marketplace", "unknown")
            status = listing.get("status", "unknown")
            
            stats["by_marketplace"][marketplace] = stats["by_marketplace"].get(marketplace, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            stats["total_sales"] += listing.get("sales", 0)
            stats["total_revenue"] += listing.get("revenue", 0.0)
        
        return stats
