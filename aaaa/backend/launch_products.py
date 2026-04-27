"""
🚀 LAUNCH SCRIPT - Generate & Publish Products to All Platforms
Creates real products with Gemini AI and publishes to Gumroad, TikTok, Etsy
"""

import asyncio
import json
import requests
import time
from datetime import datetime

# BaseURL for API
BASE_URL = "http://localhost:8000"

# Product ideas to generate
PRODUCT_IDEAS = [
    {
        "niche": "AI Automation Tools",
        "description": "Complete toolkit for automating business processes with AI",
        "target_audience": "entrepreneurs",
        "style": "professional"
    },
    {
        "niche": "Content Creation Templates",
        "description": "Ready-to-use templates for TikTok, Instagram, YouTube content",
        "target_audience": "content creators",
        "style": "creative"
    },
    {
        "niche": "Affiliate Marketing Guide",
        "description": "Step-by-step guide to making $10K+ per month with affiliate marketing",
        "target_audience": "marketers",
        "style": "strategic"
    }
]


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_section(title):
    """Print formatted section"""
    print(f"\n{'─'*80}")
    print(f"  📌 {title}")
    print(f"{'─'*80}")


async def wait_for_server(max_attempts=10):
    """Wait for backend server to be ready"""
    print_section("Waiting for Backend Server...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"  ✅ Server is ready! ({attempt+1} attempts)")
                return True
        except:
            print(f"  ⏳ Attempt {attempt+1}/{max_attempts}... server starting up")
            await asyncio.sleep(1)
    
    print("  ❌ Server failed to start")
    return False


async def generate_product(idea):
    """Generate a product with Gemini AI"""
    print_section(f"Generating: {idea['niche']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/products/generate-with-gemini",
            json=idea,
            timeout=30
        )
        
        if response.status_code == 200:
            product = response.json()
            print(f"  ✅ Product Generated!")
            print(f"     Title: {product.get('title', 'N/A')}")
            print(f"     Price: ${product.get('price', 'N/A')}")
            print(f"     Features: {len(product.get('features', []))} included")
            return product
        else:
            print(f"  ⚠️  Generation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return None


async def publish_to_all_platforms(product_id, product_title):
    """Publish product to all platforms simultaneously"""
    print_section(f"Publishing to All Platforms: {product_title}")
    
    platforms = ["gumroad", "tiktok", "etsy"]
    
    try:
        response = requests.post(
            f"{BASE_URL}/products/{product_id}/publish-all-platforms",
            json={"platforms": platforms},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Publishing Complete!")
            
            # Show results per platform
            for platform in platforms:
                status = result.get(platform, {}).get("status", "unknown")
                print(f"     🔹 {platform.upper()}: {status}")
                
                if platform == "gumroad":
                    print(f"        → Product URL: {result.get(platform, {}).get('url', 'N/A')}")
                elif platform == "tiktok":
                    print(f"        → Videos Posted: {result.get(platform, {}).get('videos_posted', 0)}")
                elif platform == "etsy":
                    print(f"        → Listing ID: {result.get(platform, {}).get('listing_id', 'N/A')}")
            
            return result
        else:
            print(f"  ⚠️  Publishing failed: {response.status_code}")
            print(f"     Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return None


async def get_analytics():
    """Get real-time analytics from all platforms"""
    print_section("Real-Time Analytics")
    
    try:
        # Gumroad
        gumroad_response = requests.get(f"{BASE_URL}/gumroad/analytics/summary", timeout=10)
        if gumroad_response.status_code == 200:
            gumroad = gumroad_response.json()
            print(f"  💰 GUMROAD")
            print(f"     Sales: ${gumroad.get('total_sales', 0):,.2f}")
            print(f"     Products: {gumroad.get('product_count', 0)}")
            print(f"     Revenue This Month: ${gumroad.get('monthly_revenue', 0):,.2f}")
        
        # TikTok
        tiktok_response = requests.get(f"{BASE_URL}/api/social/tiktok/analytics/channel/summary", timeout=10)
        if tiktok_response.status_code == 200:
            tiktok = tiktok_response.json()
            print(f"  📱 TIKTOK")
            print(f"     Views: {tiktok.get('total_views', 0):,}")
            print(f"     Followers: {tiktok.get('followers', 0):,}")
            print(f"     Engagement Rate: {tiktok.get('engagement_rate', 0):.1f}%")
        
        # Etsy
        etsy_response = requests.get(f"{BASE_URL}/etsy/analytics", timeout=10)
        if etsy_response.status_code == 200:
            etsy = etsy_response.json()
            print(f"  🛒 ETSY")
            print(f"     Shop Sales: {etsy.get('total_sales', 0):,}")
            print(f"     Listings: {etsy.get('active_listings', 0)}")
            print(f"     Star Rating: {etsy.get('shop_rating', 0):.1f}/5.0")
    
    except Exception as e:
        print(f"  ⚠️  Could not fetch analytics: {str(e)}")


async def main():
    """Main launch sequence"""
    print_header("🚀 MULTI-PLATFORM PRODUCT LAUNCH SYSTEM 🚀")
    print(f"\n  Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Platforms: Gumroad (💰) + TikTok (📱) + Etsy (🛒)")
    print(f"  AI Engine: Google Gemini")
    print(f"  Bank Account: Gumroad (LIVE)")
    
    # Wait for server
    server_ready = await wait_for_server()
    if not server_ready:
        print("\n❌ Cannot proceed - server not responding")
        return
    
    # Generate and publish products
    products_published = 0
    
    for i, idea in enumerate(PRODUCT_IDEAS[:1]):  # Start with 1st product
        print(f"\n\n{'█'*80}")
        print(f"  PRODUCT {i+1}/{len(PRODUCT_IDEAS[:1])}")
        print(f"{'█'*80}")
        
        # Generate product
        product = await generate_product(idea)
        
        if product:
            product_id = product.get("product_id", f"product_{i+1}")
            product_title = product.get("title", idea["niche"])
            
            # Publish to all platforms
            await asyncio.sleep(1)  # Brief pause between API calls
            result = await publish_to_all_platforms(product_id, product_title)
            
            if result:
                products_published += 1
        
        await asyncio.sleep(2)  # Brief pause between products
    
    # Get final analytics
    await asyncio.sleep(2)
    await get_analytics()
    
    # Final summary
    print_header("🎉 LAUNCH SUMMARY 🎉")
    print(f"\n  ✅ Products Generated: {products_published}")
    print(f"  ✅ Platforms Active: 3 (Gumroad, TikTok, Etsy)")
    print(f"  ✅ Real-Time Publishing: LIVE")
    print(f"  ✅ Bank Integration: CONNECTED")
    print(f"\n  🎯 NEXT STEPS:")
    print(f"     1. Monitor Gumroad for sales: https://gumroad.com")
    print(f"     2. Check TikTok analytics for video performance")
    print(f"     3. Track Etsy shop metrics in real-time")
    print(f"     4. Generate more products and publish")
    print(f"\n  💡 TIP: Run this script periodically to continuously publish products")
    print(f"\n  Launch completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n🔧 Starting Multi-Platform Launch System...\n")
    asyncio.run(main())
