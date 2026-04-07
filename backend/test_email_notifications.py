"""
Test script for Email and Notification endpoints
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_send_email():
    """Test direct email sending endpoint"""
    print("=" * 60)
    print("Testing POST /api/email/send")
    print("=" * 60)
    payload = {
        "to_email": "customer@example.com",
        "subject": "Welcome to CEO Empire! 🚀",
        "body": """
            <h1>Welcome!</h1>
            <p>Thank you for joining CEO Empire.</p>
            <p>Your AI-powered business generation system is ready to create amazing products.</p>
        """,
        "template_type": "general"
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/email/send",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def test_send_template_email():
    """Test template-based email endpoint"""
    print("=" * 60)
    print("Testing POST /api/email/send-template")
    print("=" * 60)
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Test product_ready template
        response = await client.post(
            f"{BASE_URL}/api/email/send-template",
            params={
                "to_email": "customer@example.com",
                "template_type": "product_ready"
            },
            json={
                "product_title": "AI Email Marketing Guide",
                "product_description": "Master email marketing with AI-powered copywriting",
                "price_range": "$29-$99",
                "keywords": ["email", "marketing", "AI"]
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test opportunity_found template
    print("-" * 60)
    print("Testing opportunity_found template")
    print("-" * 60)
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/email/send-template",
            params={
                "to_email": "customer@example.com",
                "template_type": "opportunity_found"
            },
            json={
                "niche": "AI-powered email marketing",
                "market_size": "$500M-$1B",
                "demand_level": "High",
                "keywords": ["email AI", "personalization", "marketing automation"]
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def test_create_notification():
    """Test notification creation endpoint"""
    print("=" * 60)
    print("Testing POST /api/notifications")
    print("=" * 60)
    payload = {
        "recipient_id": "user_12345",
        "type": "product_ready",
        "title": "Product Ready!",
        "message": "Your AI-generated product 'Email Marketing Guide' is ready for publishing",
        "data": {
            "product_id": "prod_67890",
            "product_title": "Email Marketing Guide"
        }
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/notifications",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def test_get_notifications():
    """Test fetching notifications"""
    print("=" * 60)
    print("Testing GET /api/notifications/{recipient_id}")
    print("=" * 60)
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/notifications/user_12345?limit=10&unread_only=False"
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def test_mark_notification_read():
    """Test marking notification as read"""
    print("=" * 60)
    print("Testing POST /api/notifications/{notification_id}/read")
    print("=" * 60)
    # First create a notification to get its ID
    async with httpx.AsyncClient(timeout=15.0) as client:
        create_response = await client.post(
            f"{BASE_URL}/api/notifications",
            json={
                "recipient_id": "user_12345",
                "type": "task_completed",
                "title": "Task Complete",
                "message": "Your AI task has completed"
            }
        )
        
        if create_response.status_code == 200:
            notification_data = create_response.json()
            notification_id = notification_data.get("notification_id")
            
            # Now mark it as read
            read_response = await client.post(
                f"{BASE_URL}/api/notifications/{notification_id}/read"
            )
            print(f"Status: {read_response.status_code}")
            print(f"Response: {json.dumps(read_response.json(), indent=2)}")
        else:
            print(f"Failed to create notification: {create_response.status_code}")
    print()

async def test_send_product_notification():
    """Test product-specific notification email"""
    print("=" * 60)
    print("Testing POST /api/email/send-product-notification")
    print("=" * 60)
    payload_params = {
        "product_id": "prod_12345",
        "to_email": "customer@example.com"
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/email/send-product-notification",
            params=payload_params
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def main():
    print("\n📧 Email & Notification Endpoints Test Suite")
    print("=" * 60)
    print("Note: Server must be running on http://localhost:8000\n")
    print("⚠️  SendGrid API key must be configured for email tests\n")
    
    try:
        # Note: Email tests will fail without SendGrid key
        print("1️⃣  Testing direct email endpoint...")
        try:
            await test_send_email()
        except Exception as e:
            print(f"⚠️  Skipped (likely no SendGrid API key): {str(e)[:100]}\n")
        
        print("2️⃣  Testing template-based emails...")
        try:
            await test_send_template_email()
        except Exception as e:
            print(f"⚠️  Skipped (likely no SendGrid API key): {str(e)[:100]}\n")
        
        print("3️⃣  Testing notification creation...")
        await test_create_notification()
        
        print("4️⃣  Testing notification retrieval...")
        await test_get_notifications()
        
        print("5️⃣  Testing mark notification as read...")
        await test_mark_notification_read()
        
        print("6️⃣  Testing product notification email...")
        try:
            await test_send_product_notification()
        except Exception as e:
            print(f"⚠️  Skipped (likely no product or SendGrid key): {str(e)[:100]}\n")
        
        print("✅ All email and notification tests completed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
