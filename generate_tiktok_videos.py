#!/usr/bin/env python3
"""
🎬 TikTok Video Generator

Automatically generates videos from your TikTok scripts using your app's AI video generator.

Usage:
python generate_tiktok_videos.py --script "AI Offer Engine" --style motivational
python generate_tiktok_videos.py --all  # Generate all scripts
"""

import json
import asyncio
import argparse
from pathlib import Path
import sys
import os

# Add the backend path to import the video generator
sys.path.append(str(Path(__file__).parent / "ceo" / "backend"))

try:
    from ai_services.faceless_video_generator import FacelessVideoGenerator, get_faceless_video_generator
    VIDEO_GENERATOR_AVAILABLE = True
except ImportError:
    VIDEO_GENERATOR_AVAILABLE = False
    print("❌ Video generator not available. Make sure you're in the right directory.")

# Sample products (fallback if API not available)
SAMPLE_PRODUCTS = [
    {
        "id": "flagship-ai-offer-engine",
        "title": "AI Offer Engine for Solo Operators",
        "subtitle": "Create a high-converting offer, even if you've never sold anything before.",
        "description": "Turn one skill into a premium digital offer, a fast checkout flow, and an AI-assisted sales engine you can run without a team.",
        "benefits": [
            "Turn an idea into something people will pay for",
            "Create offers that actually convert",
            "Launch faster without guessing"
        ],
        "includes": [
            "High-ticket offer design worksheet",
            "AI prompts for positioning and sales copy",
            "7-day launch sprint plan",
            "Delivery and fulfillment checklist",
            "Upsell and retention framework",
        ],
        "perfect_for": [
            "Solo operators",
            "Service providers",
            "Anyone wanting to create premium offers"
        ],
        "cta": "Start Building Your Offer Today",
        "price": 79.0,
        "originalPrice": 149.0,
        "type": "blueprint",
        "cover": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=600&q=80",
        "rating": 4.9,
        "reviews": 0,
        "downloads": 0,
        "tags": ["AI", "Offers", "Sales", "Solo Operator"],
        "fileSize": "14 MB",
        "updated": "2026-04-14",
        "product_type": "ebook",
        "status": "published",
        "featured": True,
    },
    {
        "id": "fiilthy-002",
        "title": "Digital Product Launch Playbook",
        "subtitle": "Launch profitable digital products in 7 days with AI.",
        "description": "Launch profitable digital products in 7 days with AI. The exact playbook used to generate $50K+ in launches.",
        "benefits": [
            "Launch products that actually sell",
            "Use AI to speed up your process",
            "Follow proven 7-day framework",
            "Generate $50K+ in revenue"
        ],
        "includes": [
            "127-point launch checklist",
            "5-part email funnel sequences",
            "40+ social media templates",
            "Pricing & positioning guide",
            "Competitor research framework",
        ],
        "perfect_for": [
            "New product creators",
            "Experienced sellers",
            "Anyone wanting faster launches"
        ],
        "cta": "Launch Your First Product Today",
        "price": 49.0,
        "originalPrice": 99.0,
        "type": "template",
        "cover": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80",
        "rating": 4.8,
        "reviews": 32,
        "downloads": 920,
        "tags": ["Digital Products", "Launch", "Marketing"],
        "fileSize": "12 MB",
        "updated": "2025-01-20",
        "product_type": "template",
        "status": "published",
    },
    {
        "id": "fiilthy-003",
        "title": "TikTok Affiliate Money Machine",
        "subtitle": "Earn $1K–$5K/month with TikTok affiliate marketing. No face, no followers, no experience needed.",
        "description": "Earn $1K–$5K/month with TikTok affiliate marketing. No face, no followers, no experience needed.",
        "benefits": [
            "Make money on TikTok without creating content",
            "No face or followers required",
            "Proven affiliate strategies",
            "Passive income potential"
        ],
        "includes": [
            "30 done-for-you video scripts",
            "Affiliate niche finder tool",
            "Analytics tracker template",
            "1,000 viral hashtag database",
            "Niche selection masterclass",
        ],
        "perfect_for": [
            "Side hustlers",
            "Stay-at-home parents",
            "Anyone wanting extra income"
        ],
        "cta": "Start Making Money on TikTok",
        "price": 37.0,
        "originalPrice": 77.0,
        "type": "course",
        "cover": "https://images.unsplash.com/photo-1611605698335-8441d6c83ddb?w=600&q=80",
        "rating": 4.7,
        "reviews": 89,
        "downloads": 2100,
        "tags": ["TikTok", "Affiliate", "Social Media"],
        "fileSize": "24 MB",
        "updated": "2025-01-10",
        "product_type": "course",
        "status": "published",
    },
    {
        "id": "fiilthy-004",
        "title": "ChatGPT Business Command Pack",
        "subtitle": "500+ battle-tested ChatGPT prompts for entrepreneurs. Create content, ads, emails and more in seconds.",
        "description": "500+ battle-tested ChatGPT prompts for entrepreneurs. Create content, ads, emails and more in seconds.",
        "benefits": [
            "Save hours on content creation",
            "Professional-quality copy instantly",
            "Categorized prompts for every business need",
            "Increase productivity 10x"
        ],
        "includes": [
            "500+ categorised prompts",
            "Prompt engineering guide",
            "Email marketing swipe file",
            "Social media caption pack",
            "Sales page template library",
        ],
        "perfect_for": [
            "Content creators",
            "Business owners",
            "Marketers",
            "Entrepreneurs"
        ],
        "cta": "Get Professional Copy Instantly",
        "price": 27.0,
        "originalPrice": 57.0,
        "type": "tool",
        "cover": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&q=80",
        "rating": 4.9,
        "reviews": 156,
        "downloads": 4200,
        "tags": ["ChatGPT", "AI", "Prompts", "Business"],
        "fileSize": "8 MB",
        "updated": "2025-01-25",
        "product_type": "template",
        "status": "published",
    },
]

# TikTok script mapping to products
SCRIPT_TO_PRODUCT = {
    "AI Offer Engine": "flagship-ai-offer-engine",
    "Digital Launch": "fiilthy-002",
    "TikTok Affiliate": "fiilthy-003",
    "ChatGPT Business": "fiilthy-004"
}

def get_product_by_id(product_id: str):
    """Get product data by ID"""
    for product in SAMPLE_PRODUCTS:
        if product["id"] == product_id:
            return product
    return None

async def generate_video_from_script(script_name: str, style: str = "motivational"):
    """Generate a video from a TikTok script"""

    if not VIDEO_GENERATOR_AVAILABLE:
        print("❌ Video generator not available")
        return

    if script_name not in SCRIPT_TO_PRODUCT:
        print(f"❌ Unknown script: {script_name}")
        print(f"Available: {list(SCRIPT_TO_PRODUCT.keys())}")
        return

    product_id = SCRIPT_TO_PRODUCT[script_name]
    product = get_product_by_id(product_id)

    if not product:
        print(f"❌ Product not found: {product_id}")
        return

    print(f"🎬 Generating video for: {script_name}")
    print(f"📦 Product: {product['title']}")
    print(f"🎨 Style: {style}")

    try:
        # Get video generator
        generator = await get_faceless_video_generator()

        # Generate video
        result = await generator.generate_full_video(
            product=product,
            video_style=style,
            duration=60
        )

        if result.get("success"):
            print("✅ Video generated successfully!")
            print(f"📹 Video ID: {result.get('video_id')}")
            print(f"📁 Path: {result.get('video_path')}")
            print(f"⏱️ Duration: {result.get('duration')}s")
            print(f"📱 Platforms: {list(result.get('platforms_ready', {}).keys())}")

            # Save result
            output_file = Path(f"generated_videos/{script_name.replace(' ', '_').lower()}_{style}.json")
            output_file.parent.mkdir(exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)

            print(f"💾 Saved result to: {output_file}")

            # Also save video path for easy access
            video_path = result.get('video_path')
            if video_path and os.path.exists(video_path):
                print(f"🎥 Video file: {video_path}")
                print(f"📏 Size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")

        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def generate_all_videos():
    """Generate videos for all scripts"""

    styles = ["motivational", "tutorial", "testimonial", "demo"]

    for script_name in SCRIPT_TO_PRODUCT.keys():
        for style in styles:
            print(f"\n{'='*60}")
            print(f"🎬 Generating: {script_name} - {style}")
            print(f"{'='*60}")
            await generate_video_from_script(script_name, style)

            # Small delay between generations
            await asyncio.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Generate TikTok videos from scripts")
    parser.add_argument("--script", help="Script name (e.g., 'AI Offer Engine')")
    parser.add_argument("--style", default="motivational",
                       choices=["motivational", "tutorial", "demo", "testimonial", "comparison"],
                       help="Video style")
    parser.add_argument("--all", action="store_true", help="Generate all scripts with all styles")

    args = parser.parse_args()

    if args.all:
        print("🚀 Generating ALL videos for ALL scripts...")
        print("This will take several minutes...")
        print("Make sure your ElevenLabs and Pexels API keys are set!")
        asyncio.run(generate_all_videos())
    elif args.script:
        asyncio.run(generate_video_from_script(args.script, args.style))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()