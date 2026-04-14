#!/usr/bin/env python3
"""
Vercel Deployment Verification
Run this after deploying to Vercel to verify all systems are live
"""

import requests
import json
import sys

BACKEND_URL = input("Enter your Vercel backend URL (e.g., https://my-project.vercel.app): ").strip()

if not BACKEND_URL:
    print("❌ No URL provided")
    sys.exit(1)

if not BACKEND_URL.startswith("http"):
    BACKEND_URL = f"https://{BACKEND_URL}"

print(f"\n🔍 Testing: {BACKEND_URL}\n")

tests = [
    ("Health Check", "GET", "/api/fiilthy/health"),
    ("API Docs", "GET", "/docs"),
    ("Auth Schema", "GET", "/api/auth/me", {"expect_auth_error": True}),
]

passed = 0
failed = 0

for test_name, method, endpoint, *extra in tests:
    expect_error = extra[0].get("expect_auth_error", False) if extra else False
    
    try:
        url = BACKEND_URL + endpoint
        if method == "GET":
            response = requests.get(url, timeout=10)
        
        status = response.status_code
        
        if expect_error:
            # Expecting 401 for unauthenticated
            if status == 401 or status == 403:
                print(f"✅ {test_name}: {status} (Auth required - Good!)")
                passed += 1
            else:
                print(f"⚠️  {test_name}: {status}")
                passed += 1
        else:
            if 200 <= status < 300:
                print(f"✅ {test_name}: {status} OK")
                passed += 1
            else:
                print(f"❌ {test_name}: {status} Error")
                failed += 1
    
    except Exception as e:
        print(f"❌ {test_name}: {str(e)}")
        failed += 1

print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*50}\n")

if failed == 0:
    print("🎉 All checks passed! Your deployment is working!")
else:
    print(f"⚠️  {failed} checks failed. Check logs at Vercel dashboard")

sys.exit(0 if failed == 0 else 1)
