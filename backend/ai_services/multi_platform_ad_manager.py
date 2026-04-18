"""
Multi-Platform Ad Campaign Manager
Orchestrates advertising campaigns across Google Ads, Facebook Ads, TikTok Ads, 
LinkedIn Ads, Pinterest Ads, Amazon Ads, and YouTube Ads
"""

import os
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from enum import Enum
import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class AdPlatform(Enum):
    """Supported ad platforms"""
    GOOGLE_ADS = "google_ads"
    FACEBOOK_ADS = "facebook_ads"
    TIKTOK_ADS = "tiktok_ads"
    LINKEDIN_ADS = "linkedin_ads"
    PINTEREST_ADS = "pinterest_ads"
    AMAZON_ADS = "amazon_ads"
    YOUTUBE_ADS = "youtube_ads"


class CampaignStatus(Enum):
    """Campaign status states"""
    DRAFT = "draft"
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class MultiPlatformAdCampaignManager:
    """Manage advertising campaigns across all platforms"""
    
    def __init__(self):
        self.db = None
        self.api_keys = {}
        self.platform_managers = {}
    
    async def set_db(self, database):
        """Set database connection"""
        self.db = database
        
        # Initialize platform managers
        self.platform_managers = {
            AdPlatform.GOOGLE_ADS: GoogleAdsManager(),
            AdPlatform.FACEBOOK_ADS: FacebookAdsManager(),
            AdPlatform.TIKTOK_ADS: TikTokAdsManager(),
            AdPlatform.LINKEDIN_ADS: LinkedInAdsManager(),
            AdPlatform.PINTEREST_ADS: PinterestAdsManager(),
            AdPlatform.AMAZON_ADS: AmazonAdsManager(),
            AdPlatform.YOUTUBE_ADS: YouTubeAdsManager()
        }

    @staticmethod
    def _resolve_platform(platform: str) -> Optional[AdPlatform]:
        """Resolve a platform string to its enum value."""
        try:
            return AdPlatform(platform.lower())
        except ValueError:
            return None
    
    async def create_campaign(self,
                              product_id: str,
                              platforms: List[str],
                              budget: float,
                              daily_budget: float,
                              duration_days: int = 30,
                              target_audience: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create and launch advertising campaigns across multiple platforms
        
        Args:
            product_id: Product to advertise
            platforms: List of platform names (google_ads, facebook_ads, etc)
            budget: Total campaign budget
            daily_budget: Daily budget per platform
            duration_days: Campaign duration
            target_audience: Audience targeting parameters
            
        Returns:
            Campaign creation result with platform-specific campaign IDs
        """
        
        try:
            if self.db is None:
                return {"error": "Database not configured"}
            
            # Get product
            product = await self.db.products.find_one(
                {"id": product_id},
                {"_id": 0}
            )
            
            if not product:
                return {"error": f"Product {product_id} not found"}
            
            # Create campaign record
            campaign_id = str(uuid.uuid4())
            campaign_record = {
                "campaign_id": campaign_id,
                "product_id": product_id,
                "product_title": product.get("title"),
                "platforms": platforms,
                "total_budget": budget,
                "daily_budget": daily_budget,
                "duration_days": duration_days,
                "status": CampaignStatus.PENDING.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "started_at": None,
                "ended_at": None,
                "target_audience": target_audience or {},
                "platform_campaigns": {},
                "total_spend": 0.0,
                "total_impressions": 0,
                "total_clicks": 0,
                "total_conversions": 0,
                "total_revenue": 0.0,
                "roi": 0.0
            }
            
            # Generate ad creative
            ad_creative = await self._generate_ad_creative(product)
            campaign_record["ad_creative"] = ad_creative
            
            # Launch campaigns on each platform
            results = {}
            successful_platforms = 0
            for platform in platforms:
                try:
                    platform_enum = self._resolve_platform(platform)
                    if platform_enum is None:
                        results[platform] = {
                            "status": "error",
                            "platform": platform,
                            "message": f"Platform '{platform}' is not supported"
                        }
                        continue

                    manager = self.platform_managers.get(platform_enum)
                    
                    if not manager:
                        results[platform] = {"status": "error", "message": "Platform not supported"}
                        continue
                    
                    platform_result = await manager.create_campaign(
                        product=product,
                        campaign_id=campaign_id,
                        daily_budget=daily_budget,
                        duration_days=duration_days,
                        ad_creative=ad_creative,
                        target_audience=target_audience
                    )
                    
                    results[platform] = platform_result
                    campaign_record["platform_campaigns"][platform] = platform_result
                    if platform_result.get("status") not in {"error", "failed"}:
                        successful_platforms += 1
                
                except Exception as e:
                    logger.error(f"Failed to create campaign on {platform}: {str(e)}")
                    results[platform] = {"status": "error", "message": str(e)}

            campaign_record["status"] = (
                CampaignStatus.PENDING.value if successful_platforms else CampaignStatus.FAILED.value
            )
            
            # Save campaign
            await self.db.campaigns.insert_one(campaign_record)
            
            return {
                "campaign_id": campaign_id,
                "status": "created" if successful_platforms else "failed",
                "product_id": product_id,
                "platforms_created": results,
                "successful_platforms": successful_platforms,
                "failed_platforms": [
                    platform
                    for platform, result in results.items()
                    if result.get("status") in {"error", "failed"}
                ],
                "total_budget": budget,
                "daily_budget": daily_budget
            }
        
        except Exception as e:
            logger.error(f"Failed to create campaign: {str(e)}")
            return {"error": str(e)}
    
    async def get_campaign_performance(self, campaign_id: str) -> Dict[str, Any]:
        """Get performance metrics for a campaign"""
        
        try:
            if self.db is None:
                return {"error": "Database not configured"}
            
            campaign = await self.db.campaigns.find_one(
                {"campaign_id": campaign_id},
                {"_id": 0}
            )
            
            if not campaign:
                return {"error": "Campaign not found"}
            
            # Aggregate performance from all platforms
            total_spend = 0.0
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            platform_metrics = {}
            
            for platform, platform_campaign in campaign.get("platform_campaigns", {}).items():
                try:
                    platform_enum = self._resolve_platform(platform)
                    if platform_enum is None:
                        continue

                    manager = self.platform_managers.get(platform_enum)
                    
                    if manager and "platform_id" in platform_campaign:
                        metrics = await manager.get_campaign_metrics(
                            campaign_id=platform_campaign.get("platform_id"),
                            campaign_name=f"{campaign_id}_{platform}"
                        )
                        
                        platform_metrics[platform] = metrics
                        total_spend += metrics.get("spend", 0)
                        total_impressions += metrics.get("impressions", 0)
                        total_clicks += metrics.get("clicks", 0)
                        total_conversions += metrics.get("conversions", 0)
                
                except Exception as e:
                    logger.warning(f"Failed to fetch metrics for {platform}: {str(e)}")
            
            # Calculate aggregates
            ctr = (total_clicks / max(total_impressions, 1)) * 100
            cpc = total_spend / max(total_clicks, 1)
            conversion_rate = (total_conversions / max(total_clicks, 1)) * 100
            cost_per_conversion = total_spend / max(total_conversions, 1)
            
            product = await self.db.products.find_one(
                {"id": campaign.get("product_id")},
                {"_id": 0}
            )
            
            roi = 0.0
            if cost_per_conversion > 0 and product:
                profit_per_sale = product.get("price", 0) - product.get("cost", 0)
                roi = ((profit_per_sale - cost_per_conversion) / max(cost_per_conversion, 1)) * 100
            
            return {
                "campaign_id": campaign_id,
                "product_id": campaign.get("product_id"),
                "product_title": campaign.get("product_title"),
                "status": campaign.get("status"),
                "created_at": campaign.get("created_at"),
                "total_budget": campaign.get("total_budget"),
                "platform_count": len(campaign.get("platform_campaigns", {})),
                "aggregated_metrics": {
                    "total_spend": total_spend,
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_conversions": total_conversions,
                    "ctr_percent": ctr,
                    "cpc": cpc,
                    "conversion_rate_percent": conversion_rate,
                    "cost_per_conversion": cost_per_conversion,
                    "estimated_roi_percent": roi,
                    "efficiency_score": self._calculate_efficiency_score(ctr, conversion_rate, roi)
                },
                "platform_metrics": platform_metrics
            }
        
        except Exception as e:
            logger.error(f"Failed to get campaign performance: {str(e)}")
            return {"error": str(e)}
    
    async def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Pause a campaign across all platforms"""
        
        try:
            if self.db is None:
                return {"error": "Database not configured"}
            
            campaign = await self.db.campaigns.find_one(
                {"campaign_id": campaign_id},
                {"_id": 0}
            )
            
            if not campaign:
                return {"error": "Campaign not found"}
            
            results = {}
            
            # Pause on each platform
            for platform, platform_campaign in campaign.get("platform_campaigns", {}).items():
                try:
                    platform_enum = self._resolve_platform(platform)
                    if platform_enum is None:
                        results[platform] = {"status": "error", "message": f"Unknown platform: {platform}"}
                        continue

                    manager = self.platform_managers.get(platform_enum)
                    
                    if manager and "platform_id" in platform_campaign:
                        result = await manager.pause_campaign(
                            campaign_id=platform_campaign.get("platform_id")
                        )
                        results[platform] = result
                except Exception as e:
                    results[platform] = {"status": "error", "message": str(e)}
            
            # Update campaign status
            await self.db.campaigns.update_one(
                {"campaign_id": campaign_id},
                {"$set": {"status": CampaignStatus.PAUSED.value}}
            )
            
            return {
                "campaign_id": campaign_id,
                "status": "paused",
                "platform_results": results
            }
        
        except Exception as e:
            logger.error(f"Failed to pause campaign: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Optimize campaign performance by adjusting bids/budgets"""
        
        try:
            if self.db is None:
                return {"error": "Database not configured"}
            
            performance = await self.get_campaign_performance(campaign_id)
            
            if "error" in performance:
                return performance
            
            campaign = await self.db.campaigns.find_one(
                {"campaign_id": campaign_id},
                {"_id": 0}
            )
            
            metrics = performance.get("aggregated_metrics", {})
            recommendations = []
            
            # Analyze performance and generate recommendations
            ctr = metrics.get("ctr_percent", 0)
            conversion_rate = metrics.get("conversion_rate_percent", 0)
            total_spend = metrics.get("total_spend", 0)
            
            # CTR analysis
            if ctr < 2.0:
                recommendations.append({
                    "type": "creative",
                    "action": "Refresh ad creative - CTR below 2%",
                    "expected_impact": "Increase CTR by 30-50%"
                })
            
            # Conversion rate analysis
            if conversion_rate < 1.0:
                recommendations.append({
                    "type": "audience",
                    "action": "Refine audience targeting - Conversion rate below 1%",
                    "expected_impact": "Increase conversion rate by 20-40%"
                })
            
            # Budget allocation
            if total_spend > 0:
                platform_metrics = performance.get("platform_metrics", {})
                best_performer = max(
                    platform_metrics.items(),
                    key=lambda x: x[1].get("roi", 0),
                    default=(None, {})
                )
                
                if best_performer[0]:
                    recommendations.append({
                        "type": "budget",
                        "action": f"Increase budget to {best_performer[0]} - Best ROI platform",
                        "expected_impact": f"Increase overall ROI by 10-20%"
                    })
            
            return {
                "campaign_id": campaign_id,
                "current_metrics": metrics,
                "recommendations": recommendations,
                "optimization_score": self._calculate_optimization_score(metrics)
            }
        
        except Exception as e:
            logger.error(f"Failed to optimize campaign: {str(e)}")
            return {"error": str(e)}
    
    async def list_campaigns(self,
                             product_id: Optional[str] = None,
                             status: Optional[str] = None,
                             limit: int = 20) -> List[Dict[str, Any]]:
        """List campaigns"""
        
        try:
            if self.db is None:
                return []
            
            query = {}
            if product_id:
                query["product_id"] = product_id
            if status:
                query["status"] = status
            
            campaigns = await self.db.campaigns.find(
                query,
                {"_id": 0}
            ).sort("created_at", -1).to_list(limit)
            
            return campaigns
        
        except Exception as e:
            logger.error(f"Failed to list campaigns: {str(e)}")
            return []
    
    async def _generate_ad_creative(self, product: Dict[str, Any]) -> Dict[str, str]:
        """Generate ad creative for the product"""
        
        return {
            "headline_short": product.get("title", "")[:30],
            "headline_long": product.get("title", ""),
            "description": product.get("description", "")[:120],
            "cta": "Shop Now",
            "images": product.get("images", [])[:5],
            "video_url": None,
            "estimated_ctr": 2.5,
            "estimated_conversion_rate": 1.2
        }
    
    def _calculate_efficiency_score(self,
                                   ctr: float,
                                   conversion_rate: float,
                                   roi: float) -> float:
        """Calculate overall campaign efficiency 0-100"""
        
        score = 0
        
        # CTR component (max 30 points)
        if ctr >= 5.0:
            score += 30
        elif ctr >= 3.0:
            score += 20
        elif ctr >= 2.0:
            score += 10
        
        # Conversion rate component (max 40 points)
        if conversion_rate >= 3.0:
            score += 40
        elif conversion_rate >= 2.0:
            score += 25
        elif conversion_rate >= 1.0:
            score += 15
        
        # ROI component (max 30 points)
        if roi >= 200:
            score += 30
        elif roi >= 100:
            score += 20
        elif roi >= 0:
            score += 10
        
        return min(score, 100)
    
    def _calculate_optimization_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate how much margin for optimization exists"""
        
        score = 100
        
        ctr = metrics.get("ctr_percent", 0)
        if ctr >= 3.0:
            score -= 10
        elif ctr >= 2.0:
            score -= 20
        
        conversion_rate = metrics.get("conversion_rate_percent", 0)
        if conversion_rate >= 2.0:
            score -= 10
        elif conversion_rate >= 1.0:
            score -= 20
        
        return max(score, 0)


# Platform-specific managers


class BaseHttpPlatformManager:
    """Shared helpers for live platform integrations."""

    async def _request(self,
                       method: str,
                       url: str,
                       *,
                       headers: Optional[Dict[str, str]] = None,
                       params: Optional[Dict[str, Any]] = None,
                       data: Optional[Dict[str, Any]] = None,
                       json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(
                method,
                url,
                headers=headers,
                params=params,
                data=data,
                json=json_body,
            ) as response:
                text = await response.text()
                payload: Dict[str, Any]
                try:
                    payload = json.loads(text) if text else {}
                except json.JSONDecodeError:
                    payload = {"raw": text}

                if response.status >= 400:
                    error_message = payload.get("error", {}).get("message") if isinstance(payload, dict) else None
                    if not error_message:
                        error_message = payload.get("message") if isinstance(payload, dict) else None
                    raise RuntimeError(error_message or f"HTTP {response.status}: {text}")

                return payload

    @staticmethod
    def _missing_config(platform: str, missing_fields: List[str]) -> Dict[str, Any]:
        return {
            "status": "not_configured",
            "platform": platform,
            "live": False,
            "message": f"Platform requires configuration. Missing: {', '.join(missing_fields)}"
        }

    @staticmethod
    def _minor_units(amount: float) -> int:
        return max(int(round(float(amount or 0) * 100)), 100)


class GoogleAdsManager(BaseHttpPlatformManager):
    """Google Ads API interface"""
    
    async def create_campaign(self, **kwargs) -> Dict[str, Any]:
        """Create Google Ads campaign"""
        # Mock implementation - replace with real Google Ads API calls
        return {
            "status": "created",
            "platform_id": f"google_{uuid.uuid4()}",
            "platform": "google_ads"
        }
    
    async def get_campaign_metrics(self, **kwargs) -> Dict[str, Any]:
        """Get campaign metrics"""
        return {
            "spend": 150.0,
            "impressions": 5000,
            "clicks": 125,
            "conversions": 15,
            "roi": 180.0
        }
    
    async def pause_campaign(self, **kwargs) -> Dict[str, Any]:
        """Pause campaign"""
        return {"status": "paused"}


class FacebookAdsManager(BaseHttpPlatformManager):
    """Facebook Ads API interface"""

    def __init__(self):
        self.access_token = os.getenv("FACEBOOK_ADS_ACCESS_TOKEN") or os.getenv("META_ACCESS_TOKEN")
        self.ad_account_id = os.getenv("FACEBOOK_ADS_ACCOUNT_ID") or os.getenv("META_AD_ACCOUNT_ID")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID") or os.getenv("META_PAGE_ID")
        self.instagram_actor_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        self.graph_version = os.getenv("META_GRAPH_VERSION", "v20.0")

    def _store_url(self, product: Dict[str, Any]) -> str:
        return (
            product.get("store_url")
            or product.get("product_url")
            or f"{os.getenv('FRONTEND_URL', 'http://localhost:3000').rstrip('/')}/store"
        )

    def _build_targeting(self, target_audience: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        audience = target_audience or {}
        targeting = {
            "geo_locations": {"countries": audience.get("countries") or ["US"]},
            "age_min": int(audience.get("age_min") or 18),
            "age_max": int(audience.get("age_max") or 65),
        }

        genders = audience.get("genders") or []
        if genders:
            gender_map = {"male": 1, "female": 2}
            targeting["genders"] = [gender_map[g] for g in genders if g in gender_map]

        return targeting

    def _build_story_spec(self, product: Dict[str, Any], ad_creative: Dict[str, Any]) -> Dict[str, Any]:
        destination_url = self._store_url(product)
        link_data = {
            "message": ad_creative.get("description") or product.get("description", "")[:200],
            "link": destination_url,
            "name": ad_creative.get("headline_long") or product.get("title", "Untitled Product"),
            "call_to_action": {
                "type": "SHOP_NOW",
                "value": {"link": destination_url}
            }
        }

        images = ad_creative.get("images") or product.get("images") or []
        if images:
            link_data["picture"] = images[0]

        story_spec = {
            "link_data": link_data,
        }
        
        # Use Instagram account if available, otherwise use Facebook Page
        if self.instagram_actor_id:
            story_spec["instagram_actor_id"] = self.instagram_actor_id
        elif self.page_id:
            story_spec["page_id"] = self.page_id
        else:
            # Fallback - this shouldn't happen due to validation above
            raise ValueError("Either page_id or instagram_actor_id must be configured")
            
        return story_spec
    
    async def create_campaign(self, **kwargs) -> Dict[str, Any]:
        missing = []
        if not self.access_token:
            missing.append("META_ACCESS_TOKEN")
        if not self.ad_account_id:
            missing.append("META_AD_ACCOUNT_ID")
        # Make page_id optional - can use Instagram account instead
        if not self.page_id and not self.instagram_actor_id:
            missing.append("META_PAGE_ID or INSTAGRAM_BUSINESS_ACCOUNT_ID")
        if missing:
            return self._missing_config("facebook_ads", missing)

        product = kwargs.get("product") or {}
        campaign_id = kwargs.get("campaign_id", str(uuid.uuid4()))
        daily_budget = kwargs.get("daily_budget", 10)
        ad_creative = kwargs.get("ad_creative") or {}
        target_audience = kwargs.get("target_audience") or {}
        campaign_name = f"{product.get('title', 'Product')} · {campaign_id[:8]}"
        base_url = f"https://graph.facebook.com/{self.graph_version}/act_{self.ad_account_id}"

        try:
            campaign_response = await self._request(
                "POST",
                f"{base_url}/campaigns",
                data={
                    "access_token": self.access_token,
                    "name": campaign_name,
                    "objective": "OUTCOME_TRAFFIC",
                    "status": "PAUSED",
                    "special_ad_categories": json.dumps([]),
                },
            )
            platform_campaign_id = campaign_response.get("id")

            adset_response = await self._request(
                "POST",
                f"{base_url}/adsets",
                data={
                    "access_token": self.access_token,
                    "name": f"{campaign_name} Ad Set",
                    "campaign_id": platform_campaign_id,
                    "daily_budget": str(self._minor_units(daily_budget)),
                    "billing_event": "IMPRESSIONS",
                    "optimization_goal": "LINK_CLICKS",
                    "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "destination_type": "WEBSITE",
                    "status": "PAUSED",
                    "targeting": json.dumps(self._build_targeting(target_audience)),
                },
            )

            creative_response = await self._request(
                "POST",
                f"{base_url}/adcreatives",
                data={
                    "access_token": self.access_token,
                    "name": f"{campaign_name} Creative",
                    "object_story_spec": json.dumps(self._build_story_spec(product, ad_creative)),
                },
            )

            ad_response = await self._request(
                "POST",
                f"{base_url}/ads",
                data={
                    "access_token": self.access_token,
                    "name": f"{campaign_name} Ad",
                    "adset_id": adset_response.get("id"),
                    "creative": json.dumps({"creative_id": creative_response.get("id")}),
                    "status": "PAUSED",
                },
            )

            return {
                "status": "created",
                "platform_id": platform_campaign_id,
                "platform": "facebook_ads",
                "adset_id": adset_response.get("id"),
                "creative_id": creative_response.get("id"),
                "ad_id": ad_response.get("id"),
                "live": True,
                "delivery_status": "paused",
                "review_url": f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={self.ad_account_id}&selected_campaign_ids={platform_campaign_id}",
            }
        except Exception as e:
            logger.error(f"Facebook Ads campaign creation failed: {str(e)}")
            return {
                "status": "error",
                "platform": "facebook_ads",
                "live": False,
                "message": str(e),
            }
    
    async def get_campaign_metrics(self, **kwargs) -> Dict[str, Any]:
        campaign_id = kwargs.get("campaign_id")
        if not self.access_token or not campaign_id:
            return {"spend": 0.0, "impressions": 0, "clicks": 0, "conversions": 0, "roi": 0.0}

        try:
            payload = await self._request(
                "GET",
                f"https://graph.facebook.com/{self.graph_version}/{campaign_id}/insights",
                params={
                    "access_token": self.access_token,
                    "fields": "spend,impressions,clicks,actions",
                },
            )
            insight = (payload.get("data") or [{}])[0]
            actions = insight.get("actions") or []
            conversions = 0
            for action in actions:
                if action.get("action_type") in {"purchase", "offsite_conversion.purchase", "omni_purchase"}:
                    conversions += int(float(action.get("value", 0) or 0))

            return {
                "spend": float(insight.get("spend", 0) or 0),
                "impressions": int(insight.get("impressions", 0) or 0),
                "clicks": int(insight.get("clicks", 0) or 0),
                "conversions": conversions,
                "roi": 0.0,
            }
        except Exception as e:
            logger.warning(f"Facebook Ads metrics lookup failed: {str(e)}")
            return {"spend": 0.0, "impressions": 0, "clicks": 0, "conversions": 0, "roi": 0.0}
    
    async def pause_campaign(self, **kwargs) -> Dict[str, Any]:
        campaign_id = kwargs.get("campaign_id")
        if not self.access_token or not campaign_id:
            return self._missing_config("facebook_ads", ["META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID"])

        try:
            await self._request(
                "POST",
                f"https://graph.facebook.com/{self.graph_version}/{campaign_id}",
                data={
                    "access_token": self.access_token,
                    "status": "PAUSED",
                },
            )
            return {"status": "paused", "platform": "facebook_ads", "platform_id": campaign_id, "live": True}
        except Exception as e:
            return {"status": "error", "platform": "facebook_ads", "live": False, "message": str(e)}


class TikTokAdsManager(BaseHttpPlatformManager):
    """TikTok Ads API interface"""

    def __init__(self):
        self.access_token = os.getenv("TIKTOK_ADS_ACCESS_TOKEN") or os.getenv("TIKTOK_ACCESS_TOKEN")
        self.advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
        self.base_url = os.getenv("TIKTOK_ADS_BASE_URL", "https://business-api.tiktok.com/open_api/v1.3")
    
    async def create_campaign(self, **kwargs) -> Dict[str, Any]:
        missing = []
        if not self.access_token:
            missing.append("TIKTOK_ADS_ACCESS_TOKEN")
        if not self.advertiser_id:
            missing.append("TIKTOK_ADVERTISER_ID")
        if missing:
            return self._missing_config("tiktok_ads", missing)

        product = kwargs.get("product") or {}
        campaign_id = kwargs.get("campaign_id", str(uuid.uuid4()))
        daily_budget = kwargs.get("daily_budget", 10)

        try:
            payload = await self._request(
                "POST",
                f"{self.base_url}/campaign/create/",
                headers={
                    "Access-Token": self.access_token,
                    "Content-Type": "application/json",
                },
                json_body={
                    "advertiser_id": self.advertiser_id,
                    "campaign_name": f"{product.get('title', 'Product')} · {campaign_id[:8]}",
                    "objective_type": "TRAFFIC",
                    "budget_mode": "BUDGET_MODE_DAY",
                    "budget": float(daily_budget),
                    "operation_status": "DISABLE",
                },
            )
            data = payload.get("data") or {}
            platform_campaign_id = data.get("campaign_id")
            if not platform_campaign_id:
                raise RuntimeError(payload.get("message") or "TikTok Ads did not return a campaign id")

            return {
                "status": "created",
                "platform_id": platform_campaign_id,
                "platform": "tiktok_ads",
                "live": True,
                "delivery_status": "paused",
            }
        except Exception as e:
            logger.error(f"TikTok Ads campaign creation failed: {str(e)}")
            return {
                "status": "error",
                "platform": "tiktok_ads",
                "live": False,
                "message": str(e),
            }
    
    async def get_campaign_metrics(self, **kwargs) -> Dict[str, Any]:
        return {
            "spend": 0.0,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "roi": 0.0
        }
    
    async def pause_campaign(self, **kwargs) -> Dict[str, Any]:
        campaign_id = kwargs.get("campaign_id")
        if not self.access_token or not self.advertiser_id:
            return self._missing_config("tiktok_ads", ["TIKTOK_ADS_ACCESS_TOKEN", "TIKTOK_ADVERTISER_ID"])

        try:
            await self._request(
                "POST",
                f"{self.base_url}/campaign/update/status/",
                headers={
                    "Access-Token": self.access_token,
                    "Content-Type": "application/json",
                },
                json_body={
                    "advertiser_id": self.advertiser_id,
                    "campaign_id": campaign_id,
                    "operation_status": "DISABLE",
                },
            )
            return {"status": "paused", "platform": "tiktok_ads", "platform_id": campaign_id, "live": True}
        except Exception as e:
            return {"status": "error", "platform": "tiktok_ads", "live": False, "message": str(e)}


class LinkedInAdsManager:
    """LinkedIn Ads API interface"""
    
    async def create_campaign(self, **kwargs) -> Dict[str, Any]:
        return {
            "status": "created",
            "platform_id": f"li_{uuid.uuid4()}",
            "platform": "linkedin_ads"
        }
    
    async def get_campaign_metrics(self, **kwargs) -> Dict[str, Any]:
        return {
            "spend": 250.0,
            "impressions": 3000,
            "clicks": 90,
            "conversions": 9,
            "roi": 120.0
        }
    
    async def pause_campaign(self, **kwargs) -> Dict[str, Any]:
        return {"status": "paused"}


class PinterestAdsManager:
    """Pinterest Ads API interface"""
    
    async def create_campaign(self, **kwargs) -> Dict[str, Any]:
        return {
            "status": "created",
            "platform_id": f"pin_{uuid.uuid4()}",
            "platform": "pinterest_ads"
        }
    
    async def get_campaign_metrics(self, **kwargs) -> Dict[str, Any]:
        return {
            "spend": 120.0,
            "impressions": 6000,
            "clicks": 150,
            "conversions": 18,
            "roi": 160.0
        }
    
    async def pause_campaign(self, **kwargs) -> Dict[str, Any]:
        return {"status": "paused"}


class AmazonAdsManager:
    """Amazon Ads API interface"""
    
    async def create_campaign(self, **kwargs) -> Dict[str, Any]:
        return {
            "status": "created",
            "platform_id": f"amz_{uuid.uuid4()}",
            "platform": "amazon_ads"
        }
    
    async def get_campaign_metrics(self, **kwargs) -> Dict[str, Any]:
        return {
            "spend": 180.0,
            "impressions": 9000,
            "clicks": 270,
            "conversions": 40,
            "roi": 280.0
        }
    
    async def pause_campaign(self, **kwargs) -> Dict[str, Any]:
        return {"status": "paused"}


class YouTubeAdsManager:
    """YouTube Ads API interface"""
    
    async def create_campaign(self, **kwargs) -> Dict[str, Any]:
        return {
            "status": "created",
            "platform_id": f"yt_{uuid.uuid4()}",
            "platform": "youtube_ads"
        }
    
    async def get_campaign_metrics(self, **kwargs) -> Dict[str, Any]:
        return {
            "spend": 170.0,
            "impressions": 15000,
            "clicks": 300,
            "conversions": 35,
            "roi": 200.0
        }
    
    async def pause_campaign(self, **kwargs) -> Dict[str, Any]:
        return {"status": "paused"}


async def get_campaign_manager() -> MultiPlatformAdCampaignManager:
    """Get or create campaign manager"""
    return MultiPlatformAdCampaignManager()
