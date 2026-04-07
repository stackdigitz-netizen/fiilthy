"""
Sales Funnel Builder - Complete sales funnel generation
Creates landing pages, product pages, checkout pages, upsells, email sequences, etc.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class SalesFunnelBuilder:
    """
    Builds complete sales funnels with:
    - Landing pages
    - Product pages
    - Checkout pages
    - Upsell/downsell pages
    - Thank-you pages
    - Email sequences
    - Referral programs
    """
    
    def __init__(self):
        self.service_name = "Sales Funnel Builder"
    
    async def generate_complete_funnel(
        self,
        product_id: str,
        product_name: str,
        product_description: str,
        price: float,
        niche: str,
        target_audience: str,
        branding: Dict[str, Any],
        upsell_product: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a complete sales funnel"""
        
        logger.info(f"🔨 Building sales funnel for {product_name}")
        
        try:
            # Generate each funnel page
            landing_page = await self._generate_landing_page(
                product_name, product_description, niche, target_audience, branding
            )
            
            product_page = await self._generate_product_page(
                product_name, product_description, price, branding
            )
            
            checkout_page = await self._generate_checkout_page(
                product_name, price, branding
            )
            
            upsell_page = None
            if upsell_product:
                upsell_page = await self._generate_upsell_page(
                    product_name, upsell_product, branding
                )
            
            downsell_page = await self._generate_downsell_page(
                product_name, price * 0.5, branding
            )
            
            thank_you_page = await self._generate_thank_you_page(
                product_name, branding
            )
            
            # Generate email sequences
            welcome_sequence = await self._generate_email_sequence(
                "welcome", product_name, 7, branding
            )
            
            abandoned_cart_sequence = await self._generate_email_sequence(
                "abandoned_cart", product_name, 3, branding
            )
            
            # Generate referral program
            referral_program = await self._generate_referral_program(
                product_name, price
            )
            
            funnel = {
                "product_id": product_id,
                "funnel_name": f"{product_name} Sales Funnel",
                "created_at": datetime.utcnow().isoformat(),
                
                # Pages
                "landing_page": landing_page,
                "product_page": product_page,
                "checkout_page": checkout_page,
                "upsell_page": upsell_page,
                "downsell_page": downsell_page,
                "thank_you_page": thank_you_page,
                
                # Email sequences
                "welcome_sequence": welcome_sequence,
                "abandoned_cart_sequence": abandoned_cart_sequence,
                
                # Referral program
                "referral_program": referral_program,
                
                # Optimization settings
                "optimization": {
                    "split_test_enabled": True,
                    "conversion_target": 5.0,
                    "aov_target": price * 1.3,
                    "retention_target": 80.0
                },
                
                "status": "ready_to_publish"
            }
            
            logger.info(f"✅ Sales funnel generated successfully")
            return funnel
            
        except Exception as e:
            logger.error(f"❌ Error generating funnel: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    async def _generate_landing_page(
        self,
        product_name: str,
        description: str,
        niche: str,
        audience: str,
        branding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate high-converting landing page"""
        
        primary_color = branding.get("color_palette", {}).get("primary", "#6366F1")
        
        landing_page_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{product_name} - Limited Time Offer</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                
                .hero {{
                    background: linear-gradient(135deg, {primary_color} 0%, rgba(99, 102, 241, 0.8) 100%);
                    color: white;
                    padding: 60px 20px;
                    text-align: center;
                }}
                
                .hero h1 {{ font-size: 3em; margin-bottom: 20px; font-weight: bold; }}
                .hero p {{ font-size: 1.3em; margin-bottom: 30px; opacity: 0.95; }}
                
                .cta-button {{
                    background-color: #FF6B6B;
                    color: white;
                    border: none;
                    padding: 15px 40px;
                    font-size: 1.1em;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                
                .cta-button:hover {{ transform: scale(1.05); box-shadow: 0 10px 25px rgba(0,0,0,0.3); }}
                
                .section {{ padding: 60px 20px; max-width: 800px; margin: 0 auto; }}
                .section h2 {{ font-size: 2em; margin-bottom: 20px; color: {primary_color}; }}
                .section p {{ font-size: 1.1em; margin-bottom: 15px; line-height: 1.8; }}
                
                .benefits {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 40px 0;
                }}
                
                .benefit-card {{
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid {primary_color};
                }}
                
                .benefit-card h3 {{ color: {primary_color}; margin-bottom: 10px; }}
                
                .testimonial-section {{
                    background: #f0f0f0;
                    padding: 40px 20px;
                    border-radius: 8px;
                    margin: 40px 0;
                }}
                
                .testimonial {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid {primary_color};
                }}
                
                .pricing-section {{
                    background: {primary_color};
                    color: white;
                    padding: 40px;
                    border-radius: 8px;
                    text-align: center;
                    margin: 40px 0;
                }}
                
                .price {{ font-size: 3em; font-weight: bold; margin: 20px 0; }}
                .limited-time {{ background: #FF6B6B; padding: 10px 20px; border-radius: 4px; display: inline-block; margin: 10px 0; }}
                
                footer {{ background: #333; color: white; padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <!-- Hero Section -->
            <div class="hero">
                <h1>{product_name}</h1>
                <p>The Ultimate Solution for {niche}</p>
                <p style="font-size: 1em; opacity: 0.9;">Join thousands of {audience} who've transformed their {niche.lower()}...</p>
                <button class="cta-button">Get Instant Access Now</button>
                <p style="margin-top: 15px; font-size: 0.9em;">✓ 30-Day Money Back Guarantee</p>
            </div>
            
            <!-- Problem Section -->
            <div class="section">
                <h2>The Problem</h2>
                <p>Most {audience} struggle with {niche.lower()} because they:</p>
                <ul style="margin-left: 20px; margin-top: 15px;">
                    <li>Waste time on ineffective strategies</li>
                    <li>Don't have access to proven frameworks</li>
                    <li>Feel stuck and overwhelmed</li>
                    <li>Can't see real results</li>
                </ul>
            </div>
            
            <!-- Solution Section -->
            <div class="section">
                <h2>The Solution</h2>
                <p>{product_name} is the complete system that gives {audience} everything they need to succeed in {niche}.</p>
                
                <div class="benefits">
                    <div class="benefit-card">
                        <h3>✓ Proven Process</h3>
                        <p>Step-by-step framework that actually works</p>
                    </div>
                    <div class="benefit-card">
                        <h3>✓ Expert Knowledge</h3>
                        <p>Top strategies from industry leaders</p>
                    </div>
                    <div class="benefit-card">
                        <h3>✓ Real Results</h3>
                        <p>See measurable improvements</p>
                    </div>
                    <div class="benefit-card">
                        <h3>✓ Lifetime Access</h3>
                        <p>Never lose access to your purchase</p>
                    </div>
                </div>
            </div>
            
            <!-- Testimonials -->
            <div class="section testimonial-section">
                <h2>What Others Are Saying</h2>
                <div class="testimonial">
                    <p>"This product completely changed how I approach {niche}. Highly recommended!"</p>
                    <strong>- Sarah M., Verified Buyer</strong>
                </div>
                <div class="testimonial">
                    <p>"Best investment I've made. The ROI is incredible."</p>
                    <strong>- John D., Verified Buyer</strong>
                </div>
            </div>
            
            <!-- Pricing -->
            <div class="section pricing-section">
                <h2>Get {product_name} Today</h2>
                <p>Regular Price: $97</p>
                <div class="limited-time">⏰ LIMITED TIME: 70% OFF</div>
                <div class="price">$29</div>
                <button class="cta-button" style="background-color: white; color: {primary_color}; font-weight: bold;">
                    Claim Your Access Now
                </button>
                <p style="margin-top: 20px; font-size: 0.95em;">
                    ✓ Instant access • ✓ 30-day guarantee • ✓ Lifetime updates
                </p>
            </div>
            
            <!-- FAQ -->
            <div class="section">
                <h2>Frequently Asked Questions</h2>
                <div style="margin: 20px 0;">
                    <h3 style="color: {primary_color}; margin: 15px 0 10px 0;">Do I need prior experience?</h3>
                    <p>No! {product_name} is designed for beginners and experienced users alike.</p>
                </div>
                <div style="margin: 20px 0;">
                    <h3 style="color: {primary_color}; margin: 15px 0 10px 0;">Is there a money-back guarantee?</h3>
                    <p>Yes! 100% satisfaction guarantee. If you're not happy, we'll refund every penny.</p>
                </div>
                <div style="margin: 20px 0;">
                    <h3 style="color: {primary_color}; margin: 15px 0 10px 0;">How long do I have access?</h3>
                    <p>Forever! Once you purchase, it's yours for life.</p>
                </div>
            </div>
            
            <footer>
                <p>&copy; 2026 Your Brand. All rights reserved. | Privacy | Terms | Contact</p>
            </footer>
        </body>
        </html>
        """
        
        return {
            "page_type": "landing",
            "title": f"{product_name} - Hero Section",
            "html": landing_page_html,
            "conversion_focus": "email_capture",
            "cta_text": "Get Instant Access Now",
            "estimated_conversion_rate": 0.08
        }
    
    async def _generate_product_page(
        self,
        product_name: str,
        description: str,
        price: float,
        branding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate product details page"""
        
        primary_color = branding.get("color_palette", {}).get("primary", "#6366F1")
        
        product_page_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{product_name} - Product Details</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f9f9f9;">
            <div style="max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
                <h1 style="color: {primary_color};">{product_name}</h1>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 30px 0;">
                    <div>
                        <img src="{branding.get('cover_images', {}).get('main', 'https://via.placeholder.com/400x500')}" 
                             alt="{product_name}" style="width: 100%; border-radius: 8px;">
                    </div>
                    
                    <div>
                        <h2>You'll Get:</h2>
                        <ul style="line-height: 2; font-size: 1.1em;">
                            <li>✓ Complete {product_name} system</li>
                            <li>✓ Step-by-step guides</li>
                            <li>✓ Templates and resources</li>
                            <li>✓ Lifetime updates</li>
                            <li>✓ Email support</li>
                        </ul>
                        
                        <div style="background: {primary_color}; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin: 0 0 10px 0;">Only ${price}</h3>
                            <button style="background: #FF6B6B; color: white; border: none; padding: 12px 30px; 
                                          font-size: 1.1em; border-radius: 4px; cursor: pointer;">
                                Add to Cart
                            </button>
                        </div>
                    </div>
                </div>
                
                <h2 style="color: {primary_color};">What's Included</h2>
                <p>{description}</p>
                
                <h2 style="color: {primary_color};">Money-Back Guarantee</h2>
                <p>If you're not absolutely satisfied within 30 days, we'll refund 100% of your investment. No questions asked.</p>
            </div>
        </body>
        </html>
        """
        
        return {
            "page_type": "product",
            "title": f"{product_name} - Details",
            "html": product_page_html,
            "conversion_focus": "add_to_cart"
        }
    
    async def _generate_checkout_page(
        self,
        product_name: str,
        price: float,
        branding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate checkout page"""
        
        primary_color = branding.get("color_palette", {}).get("primary", "#6366F1")
        
        checkout_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Checkout - {product_name}</title>
        </head>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 500px; margin: 40px auto; background: white; padding: 30px; 
                        border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2>Complete Your Purchase</h2>
                
                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>{product_name}</strong></p>
                    <p style="margin: 10px 0 0 0; font-size: 1.3em; color: {primary_color};">${price}</p>
                </div>
                
                <form>
                    <h3>Billing Information</h3>
                    <input type="email" placeholder="Email" style="width: 100%; padding: 10px; margin: 10px 0; 
                                                                   border: 1px solid #ddd; border-radius: 4px;">
                    <input type="text" placeholder="Full Name" style="width: 100%; padding: 10px; margin: 10px 0; 
                                                                      border: 1px solid #ddd; border-radius: 4px;">
                    <input type="text" placeholder="Street Address" style="width: 100%; padding: 10px; margin: 10px 0; 
                                                                           border: 1px solid #ddd; border-radius: 4px;">
                    
                    <h3>Payment Information</h3>
                    <input type="text" placeholder="Card Number" style="width: 100%; padding: 10px; margin: 10px 0; 
                                                                        border: 1px solid #ddd; border-radius: 4px;">
                    <input type="text" placeholder="MM/YY" style="width: 48%; padding: 10px; margin: 10px 1% 10px 0; 
                                                                  border: 1px solid #ddd; border-radius: 4px;">
                    <input type="text" placeholder="CVC" style="width: 48%; padding: 10px; margin: 10px 0; 
                                                               border: 1px solid #ddd; border-radius: 4px;">
                    
                    <button type="submit" style="width: 100%; background: {primary_color}; color: white; 
                                                  padding: 12px; font-size: 1.1em; border: none; border-radius: 4px; 
                                                  cursor: pointer; margin-top: 20px;">
                        Complete Purchase - ${price}
                    </button>
                </form>
                
                <p style="text-align: center; font-size: 0.9em; color: #666; margin-top: 20px;">
                    ✓ Secure checkout powered by Stripe
                </p>
            </div>
        </body>
        </html>
        """
        
        return {
            "page_type": "checkout",
            "title": "Secure Checkout",
            "html": checkout_html,
            "conversion_focus": "payment_completion",
            "payment_gateway": "stripe"
        }
    
    async def _generate_upsell_page(
        self,
        product_name: str,
        upsell_product: Dict[str, Any],
        branding: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate upsell offer page"""
        
        primary_color = branding.get("color_palette", {}).get("primary", "#6366F1")
        upsell_price = upsell_product.get("price", 47)
        upsell_name = upsell_product.get("name", "Premium Package")
        
        upsell_html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial; background: linear-gradient(135deg, {primary_color}, #ff6b6b); 
                     padding: 40px 20px; text-align: center; color: white;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1>Wait! One More Thing...</h1>
                <h2>Limited Time Bundle Offer</h2>
                
                <div style="background: rgba(255,255,255,0.95); color: #333; padding: 30px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="color: {primary_color};">{upsell_name}</h3>
                    <p>Get everything in {product_name} PLUS premium bonuses</p>
                    
                    <ul style="text-align: left; display: inline-block;">
                        <li>✓ Everything above</li>
                        <li>✓ Advanced templates</li>
                        <li>✓ Private community access</li>
                        <li>✓ Monthly training calls</li>
                    </ul>
                    
                    <div style="margin: 30px 0;">
                        <span style="text-decoration: line-through; color: #999;">${upsell_price * 2}</span>
                        <div style="font-size: 2em; color: {primary_color}; font-weight: bold;">${upsell_price}</div>
                        <span style="background: #FF6B6B; color: white; padding: 5px 10px; border-radius: 4px;">SPECIAL OFFER</span>
                    </div>
                    
                    <button style="background: {primary_color}; color: white; padding: 15px 40px; 
                                   font-size: 1.2em; border: none; border-radius: 4px; cursor: pointer;">
                        YES! Add to my order
                    </button>
                    <br><br>
                    <button style="background: transparent; color: white; padding: 10px 20px; 
                                   border: 2px solid white; border-radius: 4px; cursor: pointer; font-size: 1em;">
                        No thanks, continue
                    </button>
                </div>
            </div>
        </body>
        </html>
        """
        
        return {
            "page_type": "upsell",
            "title": "Limited Time Upsell",
            "html": upsell_html,
            "upsell_product_name": upsell_name,
            "upsell_price": upsell_price,
            "conversion_focus": "upsell_acceptance"
        }
    
    async def _generate_downsell_page(
        self,
        product_name: str,
        downsell_price: float,
        branding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate downsell/one-click offer for after purchase"""
        
        primary_color = branding.get("color_palette", {}).get("primary", "#6366F1")
        
        downsell_html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial; text-align: center; padding: 40px 20px;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1>One Final Offer...</h1>
                <p style="font-size: 1.2em;">You're making a great choice with {product_name}!</p>
                
                <div style="background: #f9f9f9; padding: 30px; border-radius: 8px; border: 2px solid {primary_color};">
                    <h2>Limited Downsell: ${downsell_price}</h2>
                    <p>Professional implementation guide</p>
                    <p style="margin: 20px 0; font-size: 1.4em; color: {primary_color}; font-weight: bold;">Only ${downsell_price}</p>
                    <button style="background: {primary_color}; color: white; padding: 12px 30px; 
                                   border: none; border-radius: 4px; cursor: pointer; font-size: 1.1em;">
                        ONE CLICK - Add Now
                    </button>
                </div>
            </div>
        </body>
        </html>
        """
        
        return {
            "page_type": "downsell",
            "title": "Downsell Offer",
            "html": downsell_html,
            "downsell_price": downsell_price
        }
    
    async def _generate_thank_you_page(
        self,
        product_name: str,
        branding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate thank-you page after purchase"""
        
        primary_color = branding.get("color_palette", {}).get("primary", "#6366F1")
        
        thank_you_html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial; background: linear-gradient(135deg, {primary_color}, #10B981); 
                     color: white; padding: 40px 20px; text-align: center;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1 style="font-size: 3em;">🎉 Thank You!</h1>
                <h2>Your purchase is complete!</h2>
                
                <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 8px; margin: 30px 0;">
                    <p style="font-size: 1.2em;">Check your email for:</p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>✓ Your instant download link</li>
                        <li>✓ Access credentials</li>
                        <li>✓ Quick start guide</li>
                        <li>✓ Bonus resources</li>
                    </ul>
                </div>
                
                <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p>Need help? Email support@example.com</p>
                </div>
                
                <button style="background: white; color: {primary_color}; padding: 12px 40px; 
                              font-size: 1.1em; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                    Download Now
                </button>
            </div>
        </body>
        </html>
        """
        
        return {
            "page_type": "thank_you",
            "title": "Purchase Complete",
            "html": thank_you_html,
            "action_url": "/download/product"
        }
    
    async def _generate_email_sequence(
        self,
        sequence_type: str,
        product_name: str,
        duration_days: int,
        branding: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate email sequence"""
        
        sequences = {
            "welcome": [
                {
                    "day": 0,
                    "subject": f"Welcome to {product_name}! Here's Your Instant Access",
                    "preview": "Download your exclusive content now",
                    "body": f"Thank you for purchasing {product_name}! Here's everything you need to get started...",
                    "delay_hours": 0
                },
                {
                    "day": 1,
                    "subject": f"Quick Start Guide: Your First Steps with {product_name}",
                    "preview": "Complete first goal in the next 24 hours",
                    "body": "Here's the quickest way to see results with your new purchase...",
                    "delay_hours": 24
                },
                {
                    "day": 3,
                    "subject": f"Advanced {product_name} Techniques",
                    "preview": "Take your results to the next level",
                    "body": "Now that you've tried the basics, here's how to maximize your investment...",
                    "delay_hours": 72
                },
                {
                    "day": 7,
                    "subject": f"Exclusive Bonus: Bonus content for {product_name} customers",
                    "preview": "$50 value - Totally free",
                    "body": "As a valued customer, we're giving you exclusive access to...",
                    "delay_hours": 168
                }
            ],
            "abandoned_cart": [
                {
                    "day": 0,
                    "subject": "You left something in your cart",
                    "preview": "Claim your 5% discount now",
                    "body": "Your cart is waiting with exclusive products you were interested in...",
                    "delay_hours": 1
                },
                {
                    "day": 1,
                    "subject": "Last chance: Your items expire tomorrow",
                    "preview": "Limited inventory",
                    "body": "The items you wanted are selling fast. Complete your purchase now...",
                    "delay_hours": 24
                }
            ]
        }
        
        return sequences.get(sequence_type, [])
    
    async def _generate_referral_program(
        self,
        product_name: str,
        product_price: float
    ) -> Dict[str, Any]:
        """Generate referral program"""
        
        return {
            "enabled": True,
            "commission_type": "percentage",
            "commission_value": 30,
            "commission_currency": "USD",
            "referral_url_format": f"ref_{product_name.lower().replace(' ', '_')}_{{affiliate_id}}",
            "affiliate_dashboard_enabled": True,
            "payment_schedule": "monthly",
            "minimum_payout": 50,
            "tracking_expires_days": 30,
            "marketing_materials": {
                "social_posts": 10,
                "email_templates": 5,
                "banner_sizes": ["300x250", "728x90", "970x90"]
            }
        }


# Initialize the sales funnel builder
sales_funnel_builder = SalesFunnelBuilder()

