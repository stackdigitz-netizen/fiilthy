"""
AI Assistant
Keeps users updated on everything happening in the CEO System
Provides guidance, notifications, and smart recommendations
"""
from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid

class AIAssistant:
    """Personal AI assistant that keeps you informed and guides you"""
    
    def __init__(self, db=None):
        self.db = db
        self.name = "Atlas"  # CEO System AI Assistant
    
    async def get_status_update(self) -> Dict[str, Any]:
        """Get a comprehensive status update on everything"""
        update = {
            "assistant": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "greeting": self._get_greeting(),
            "summary": {},
            "alerts": [],
            "recommendations": [],
            "recent_activity": [],
            "pending_actions": []
        }
        
        if self.db is not None:
            # Get counts
            products_count = await self.db.products.count_documents({})
            opportunities_count = await self.db.discovered_opportunities.count_documents({})
            teams_count = await self.db.agent_teams.count_documents({})
            
            # Get recent products
            recent_products = await self.db.products.find(
                {}, {"_id": 0, "id": 1, "title": 1, "status": 1, "created_at": 1}
            ).sort("created_at", -1).limit(5).to_list(5)
            
            # Get unpublished products
            unpublished = await self.db.products.count_documents({"status": {"$in": ["ready", "draft"]}})
            
            update["summary"] = {
                "total_products": products_count,
                "active_opportunities": opportunities_count,
                "agent_teams": teams_count,
                "unpublished_products": unpublished
            }
            
            update["recent_activity"] = [
                {
                    "type": "product",
                    "title": p.get("title", "Unknown"),
                    "status": p.get("status", "unknown"),
                    "time": p.get("created_at", "")
                }
                for p in recent_products
            ]
            
            # Generate alerts
            if unpublished > 0:
                update["alerts"].append({
                    "type": "info",
                    "icon": "📦",
                    "message": f"You have {unpublished} products ready to publish!",
                    "action": "View products and publish to marketplaces"
                })
            
            if opportunities_count > 0:
                update["alerts"].append({
                    "type": "opportunity",
                    "icon": "🎯",
                    "message": f"{opportunities_count} trending opportunities discovered!",
                    "action": "Review and create agent teams"
                })
        
        # Add recommendations
        update["recommendations"] = self._get_recommendations(update["summary"])
        
        # Pending actions
        update["pending_actions"] = self._get_pending_actions(update["summary"])
        
        return update
    
    def _get_greeting(self) -> str:
        """Get time-appropriate greeting"""
        hour = datetime.now().hour
        if hour < 12:
            return f"Good morning! I'm {self.name}, your AI assistant."
        elif hour < 17:
            return f"Good afternoon! I'm {self.name}, here to help."
        else:
            return f"Good evening! I'm {self.name}, at your service."
    
    def _get_recommendations(self, summary: Dict) -> List[Dict]:
        """Generate smart recommendations"""
        recs = []
        
        if summary.get("total_products", 0) == 0:
            recs.append({
                "priority": "high",
                "icon": "🚀",
                "title": "Launch Your First Product",
                "description": "Use the one-click Launch Product button to create and publish your first digital product!",
                "action": "launch_product"
            })
        
        if summary.get("unpublished_products", 0) > 0:
            recs.append({
                "priority": "high",
                "icon": "📢",
                "title": "Publish Your Products",
                "description": "You have products ready! Publish them to start making money.",
                "action": "view_products"
            })
        
        if summary.get("active_opportunities", 0) > 5:
            recs.append({
                "priority": "medium",
                "icon": "👥",
                "title": "Create Agent Teams",
                "description": "Assign AI teams to your top opportunities for automated execution.",
                "action": "open_hunter"
            })
        
        recs.append({
            "priority": "low",
            "icon": "🔐",
            "title": "Connect More Platforms",
            "description": "Add your social media and marketplace credentials for maximum reach.",
            "action": "open_vault"
        })
        
        return recs
    
    def _get_pending_actions(self, summary: Dict) -> List[Dict]:
        """Get list of pending actions user should take"""
        actions = []
        
        if summary.get("unpublished_products", 0) > 0:
            actions.append({
                "icon": "📤",
                "action": "Publish products to marketplaces",
                "count": summary.get("unpublished_products", 0)
            })
        
        return actions
    
    async def get_product_publishing_guide(self, product_id: str) -> Dict[str, Any]:
        """Get a detailed guide on where to publish a specific product"""
        if self.db is None:
            return {"error": "Database not available"}
        
        product = await self.db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            return {"error": "Product not found"}
        
        product_type = product.get("product_type", "ebook")
        
        # Import PublishingGuide
        from ai_services.project_manager import PublishingGuide
        guide = PublishingGuide()
        options = guide.get_publishing_options(product_type)
        
        return {
            "product": {
                "id": product_id,
                "title": product.get("title"),
                "type": product_type,
                "price": product.get("price")
            },
            "publishing_options": options,
            "message": self._generate_publishing_message(product, options)
        }
    
    def _generate_publishing_message(self, product: Dict, options: Dict) -> str:
        """Generate a helpful message about publishing options"""
        auto_count = len(options.get("automated", []))
        manual_count = len(options.get("manual", []))
        
        message = f"📚 **{product.get('title')}** can be published to {auto_count + manual_count} platforms!\n\n"
        
        if auto_count > 0:
            message += f"✅ **{auto_count} platforms** can be automated - I'll handle these for you!\n"
        
        if manual_count > 0:
            message += f"📝 **{manual_count} platforms** need manual upload - I'll guide you step by step.\n"
        
        return message
    
    async def add_notification(self, notification: Dict) -> Dict:
        """Add a notification for the user"""
        notif = {
            "id": f"notif-{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False,
            **notification
        }
        
        if self.db is not None:
            await self.db.notifications.insert_one(notif)
        
        return {"success": True, "notification": notif}
    
    async def get_notifications(self, unread_only: bool = False) -> List[Dict]:
        """Get user notifications"""
        if self.db is None:
            return []
        
        query = {}
        if unread_only:
            query["read"] = False
        
        notifications = await self.db.notifications.find(
            query, {"_id": 0}
        ).sort("timestamp", -1).limit(50).to_list(50)
        
        return notifications
    
    async def mark_notification_read(self, notification_id: str) -> Dict:
        """Mark a notification as read"""
        if self.db is not None:
            await self.db.notifications.update_one(
                {"id": notification_id},
                {"$set": {"read": True}}
            )
        return {"success": True}
    
    async def get_quick_stats(self) -> Dict[str, Any]:
        """Get quick stats for the assistant widget"""
        stats = {
            "products": 0,
            "revenue": 0,
            "opportunities": 0,
            "pending_tasks": 0
        }
        
        if self.db is not None:
            stats["products"] = await self.db.products.count_documents({})
            stats["opportunities"] = await self.db.discovered_opportunities.count_documents({})
            
            # Sum revenue
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$revenue"}}}]
            result = await self.db.products.aggregate(pipeline).to_list(1)
            if result:
                stats["revenue"] = result[0].get("total", 0)
        
        return stats
