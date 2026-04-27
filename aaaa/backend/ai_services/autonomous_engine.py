"""
Fully Autonomous Product Empire Engine
Generates, publishes, markets, and monetizes products without human intervention
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone
import random

from .real_product_generator import RealProductGenerator
from .opportunity_scout import OpportunityScout
from .compliance_checker import ComplianceChecker
from .marketplace_integrations import MarketplaceIntegrations
from .revenue_maximizer import RevenueMaximizer
from .social_media_ai import SocialMediaAI

class AutonomousEngine:
    def __init__(self, db):
        self.db = db
        self.product_generator = RealProductGenerator()
        self.opportunity_scout = OpportunityScout()
        self.compliance_checker = ComplianceChecker()
        self.marketplace = MarketplaceIntegrations()
        self.revenue_optimizer = RevenueMaximizer()
        self.social_media = SocialMediaAI()
        
        self.running = False
    
    async def run_autonomous_product_cycle(self) -> Dict[str, Any]:
        """
        Complete autonomous cycle:
        1. Scout opportunity
        2. Generate REAL product
        3. Run compliance checks
        4. Publish to marketplace
        5. Create marketing posts
        6. Track analytics
        
        Returns complete product with all links and files
        """
        
        results = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "steps_completed": [],
            "product": None,
            "marketplace_listing": None,
            "social_posts": [],
            "status": "running"
        }
        
        try:
            # STEP 1: Scout best opportunity
            print("\n🔍 STEP 1: Scouting opportunities...")
            opportunities = await self.opportunity_scout.scout_opportunities()
            
            # Select highest-scoring opportunity
            top_opportunity = max(opportunities, key=lambda x: x.get('trend_score', 0))
            print(f"✓ Selected: {top_opportunity['niche']} (Score: {top_opportunity['trend_score']})")
            results["steps_completed"].append("opportunity_scouting")
            results["opportunity"] = top_opportunity
            
            # STEP 2: Generate REAL, complete product
            print("\n📦 STEP 2: Generating complete product...")
            
            # Determine best product type for this niche
            if any(keyword in top_opportunity['niche'].lower() for keyword in ['course', 'learn', 'training', 'masterclass']):
                product_type = 'course'
                product = await self.product_generator.generate_complete_course(
                    topic=top_opportunity['niche'],
                    target_audience='beginners',
                    duration_hours=3
                )
            else:
                product_type = 'ebook'
                product = await self.product_generator.generate_complete_ebook(
                    niche=top_opportunity['niche'],
                    keywords=top_opportunity['keywords'],
                    target_audience='general'
                )
            
            # Add ID and pricing
            product['id'] = f"prod-{random.randint(100000, 999999)}"
            
            # Optimize pricing
            price_ranges = {'ebook': (19.99, 49.99), 'course': (39.99, 99.99)}
            min_price, max_price = price_ranges.get(product_type, (19.99, 49.99))
            product['price'] = round(random.uniform(min_price, max_price), 2)
            
            print(f"✓ Product created: {product['title']}")
            print(f"  Type: {product['product_type']}")
            print(f"  Quality Score: {product['quality_score']}/100")
            print(f"  Price: ${product['price']}")
            
            results["steps_completed"].append("product_generation")
            results["product"] = {
                "id": product['id'],
                "title": product['title'],
                "type": product['product_type'],
                "price": product['price'],
                "quality_score": product['quality_score']
            }
            
            # STEP 3: Compliance checks
            print("\n✅ STEP 3: Running compliance checks...")
            compliance = await self.compliance_checker.check_product_compliance(product)
            
            if compliance['overall_status'] == 'failed':
                print(f"❌ Compliance failed: {compliance['issues']}")
                results["status"] = "failed_compliance"
                results["compliance_issues"] = compliance['issues']
                return results
            
            print(f"✓ Compliance: {compliance['overall_status']}")
            if compliance.get('warnings'):
                print(f"  Warnings: {', '.join(compliance['warnings'])}")
            
            results["steps_completed"].append("compliance_check")
            results["compliance"] = compliance['overall_status']
            
            # STEP 4: Select best marketplace
            print("\n🛒 STEP 4: Publishing to marketplace...")
            
            # Select marketplace based on product type
            marketplace_map = {
                'ebook': 'gumroad',  # Easy to start
                'course': 'udemy',
                'template': 'gumroad',
                'planner': 'etsy'
            }
            
            target_marketplace = marketplace_map.get(product['product_type'], 'gumroad')
            
            # Publish (currently mock, but ready for real API)
            listing = await self.marketplace.publish_to_marketplace(
                product=product,
                marketplace=target_marketplace,
                credentials=None  # Will use real credentials when provided
            )
            
            print(f"✓ Published to {target_marketplace}")
            print(f"  Listing URL: {listing['listing_url']}")
            print(f"  Status: {listing['status']}")
            
            # Save listing to database
            listing_doc = listing.copy()
            listing_doc.pop('_id', None)
            listing_doc['sales'] = 0
            listing_doc['revenue'] = 0.0
            await self.db.marketplace_listings.insert_one(listing_doc)
            
            results["steps_completed"].append("marketplace_publish")
            results["marketplace_listing"] = listing
            
            # STEP 5: Generate social media posts
            print("\n📱 STEP 5: Creating social media marketing...")
            
            social_posts = await self.social_media.generate_posts(product, num_posts=5)
            
            print(f"✓ Created {len(social_posts)} social media posts")
            for post in social_posts[:3]:
                print(f"  - {post['platform']}: {post['content'][:50]}...")
            
            # Save posts to database
            for post in social_posts:
                post_doc = post.copy()
                post_doc.pop('_id', None)
                await self.db.social_media_posts.insert_one(post_doc)
            
            results["steps_completed"].append("social_media_creation")
            results["social_posts"] = social_posts
            
            # STEP 6: Save complete product to database
            print("\n💾 STEP 6: Saving product to database...")
            
            # Add marketplace links
            product['marketplace_links'] = [{
                "platform": target_marketplace.title(),
                "url": listing['listing_url'],
                "status": listing['status']
            }]
            
            product['revenue'] = 0.0
            product['conversions'] = 0
            product['clicks'] = 0
            product['status'] = 'published' if listing['status'] == 'published' else 'ready'
            product['created_at'] = datetime.now(timezone.utc).isoformat()
            
            product_doc = product.copy()
            product_doc.pop('_id', None)
            await self.db.products.insert_one(product_doc)
            
            print(f"✓ Product saved to database")
            
            results["steps_completed"].append("database_save")
            
            # STEP 7: Export product file
            print("\n📄 STEP 7: Exporting product file...")
            
            file_path = await self.product_generator.export_to_file(product, format='json')
            markdown_path = await self.product_generator.export_to_file(product, format='markdown')
            
            print(f"✓ Exported to: {file_path}")
            print(f"✓ Markdown: {markdown_path}")
            
            results["steps_completed"].append("file_export")
            results["files"] = {
                "json": file_path,
                "markdown": markdown_path
            }
            
            # Complete!
            results["status"] = "success"
            results["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            print("\n" + "="*60)
            print("🎉 AUTONOMOUS CYCLE COMPLETE!")
            print("="*60)
            print(f"Product: {product['title']}")
            print(f"Price: ${product['price']}")
            print(f"Marketplace: {target_marketplace}")
            print(f"Quality Score: {product['quality_score']}/100")
            print(f"Social Posts: {len(social_posts)}")
            print(f"Status: Ready for sales!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error in autonomous cycle: {str(e)}")
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def continuous_autonomous_mode(self, products_per_day: int = 3):
        """
        Run continuously, generating products on schedule
        
        Args:
            products_per_day: How many products to generate daily
        """
        
        print("\n" + "="*60)
        print("🚀 STARTING CONTINUOUS AUTONOMOUS MODE")
        print("="*60)
        print(f"Target: {products_per_day} products per day")
        print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        self.running = True
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                print(f"\n{'='*60}")
                print(f"AUTONOMOUS CYCLE #{cycle_count}")
                print(f"{'='*60}\n")
                
                # Run complete product cycle
                result = await self.run_autonomous_product_cycle()
                
                if result['status'] == 'success':
                    print(f"\n✅ Cycle #{cycle_count} successful!")
                else:
                    print(f"\n⚠️  Cycle #{cycle_count} completed with status: {result['status']}")
                
                # Wait before next cycle (space them throughout the day)
                wait_hours = 24 / products_per_day
                wait_seconds = wait_hours * 3600
                
                print(f"\n⏳ Waiting {wait_hours:.1f} hours until next cycle...")
                
                # For demo/testing, use much shorter wait
                # Remove this in production
                await asyncio.sleep(10)  # 10 seconds for demo
                # await asyncio.sleep(wait_seconds)  # Use this in production
                
            except Exception as e:
                print(f"\n❌ Error in cycle #{cycle_count}: {str(e)}")
                print("Continuing to next cycle...")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop(self):
        """Stop continuous autonomous mode"""
        self.running = False
        print("\n🛑 Stopping autonomous mode...")
