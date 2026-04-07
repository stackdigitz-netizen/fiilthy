"""
Test script for AI service endpoints
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_keys_status():
    """Test get keys status endpoint"""
    print("=" * 60)
    print("Testing GET /api/keys/status")
    print("=" * 60)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/keys/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def test_generate_product():
    """Test product generation endpoint"""
    print("=" * 60)
    print("Testing POST /api/ai/generate-product")
    print("=" * 60)
    payload = {
        "concept": "AI-powered project management tool for remote teams",
        "keywords": ["productivity", "collaboration", "remote work"],
        "tone": "professional"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/ai/generate-product",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def test_find_opportunities():
    """Test opportunity discovery endpoint"""
    print("=" * 60)
    print("Testing POST /api/ai/find-opportunities")
    print("=" * 60)
    payload = {
        "niche": "AI-powered email marketing",
        "market_size": "large",
        "keyword_focus": "email automation AI"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/ai/find-opportunities",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def test_generate_image():
    """Test image generation endpoint"""
    print("=" * 60)
    print("Testing POST /api/ai/generate-image")
    print("=" * 60)
    payload = {
        "description": "Professional project management dashboard with team collaboration features",
        "style": "professional UI design",
        "size": "1024x1024"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/ai/generate-image",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def test_full_product_generation():
    """Test complete product generation workflow"""
    print("=" * 60)
    print("Testing POST /api/ai/generate-full-product")
    print("=" * 60)
    payload = {
        "concept": "Email marketing automation platform with AI copywriting",
        "keywords": ["email marketing", "AI", "automation", "copywriting"],
        "generate_image": True,
        "save_to_db": True
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/ai/generate-full-product",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

async def main():
    print("\n🚀 AI Service Endpoints Test Suite")
    print("=" * 60)
    print("Note: Server must be running on http://localhost:8000\n")
    
    try:
        # Test keys status first
        await test_keys_status()
        
        # Test individual AI endpoints (only if keys are configured)
        print("⏳ Testing individual AI endpoints...")
        await test_generate_product()
        await test_find_opportunities()
        await test_generate_image()
        
        # Test full workflow
        print("⏳ Testing full product generation workflow...")
        await test_full_product_generation()
        
        print("✅ All tests completed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
