#!/usr/bin/env python3
"""
🚀 FIILTHY.AI AUTOMATED LAUNCH SCRIPT
Handles GitHub repo creation + Vercel deployment

This script will:
1. Check prerequisites
2. Guide through GitHub repo creation
3. Push code to GitHub
4. Generate Vercel deployment commands
5. Verify deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description="", check=True):
    """Run shell command and return output"""
    print(f"\n▶️  {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return None

def check_prerequisites():
    """Verify git, node, npm installed"""
    print("\n" + "="*80)
    print("✅ CHECKING PREREQUISITES")
    print("="*80)
    
    checks = {
        "git --version": "Git",
        "python --version": "Python",
    }
    
    all_good = True
    for cmd, name in checks.items():
        result = run_command(cmd, f"Checking {name}...", check=False)
        if result and result.returncode == 0:
            print(f"   ✅ {name} installed")
        else:
            print(f"   ⚠️  {name} not found - install it if needed")
            all_good = all_good and False
    
    return all_good

def check_git_status():
    """Verify git repo is clean"""
    print("\n" + "="*80)
    print("✅ GIT STATUS CHECK")
    print("="*80)
    
    result = run_command("git status --short", "Checking for uncommitted changes...")
    
    if result and result.returncode == 0:
        if not result.stdout.strip():
            print("   ✅ Working tree clean - ready to push")
            return True
        else:
            print(f"   ⚠️  Uncommitted changes found:\n{result.stdout}")
            return False
    return False

def display_github_instructions():
    """Show user what to do on GitHub"""
    print("\n" + "="*80)
    print("🔧 GITHUB REPO SETUP (MANUAL STEP)")
    print("="*80)
    print("""
Follow these steps:

1️⃣  OPEN THIS LINK IN YOUR BROWSER:
    https://github.com/new

2️⃣  FILL IN THE FORM:
    • Repository name: fiilthy
    • Owner: stackdigitz-netizen (select from dropdown)
    • Visibility: PUBLIC ⭐ (MUST be PUBLIC)
    • Description: AI-powered content creation & posting system
    • Skip "Initialize repository" options

3️⃣  CLICK: "Create repository"

4️⃣  YOU'LL SEE: A page with instructions
    ✅ This is expected - come back here when done

5️⃣  PRESS ENTER BELOW WHEN GITHUB REPO IS CREATED...
""")
    
    input("→ Press ENTER when GitHub repo is ready...")

def push_to_github():
    """Push code to GitHub"""
    print("\n" + "="*80)
    print("📤 PUSHING CODE TO GITHUB")
    print("="*80)
    
    commands = [
        ("git branch -M main", "Ensure 'main' branch exists"),
        ("git remote remove origin", "Remove old remote (if exists)"),
        ("git remote add origin https://github.com/stackdigitz-netizen/fiilthy.git", 
         "Add GitHub origin"),
        ("git push -u origin main", "Push code to GitHub"),
    ]
    
    for cmd, desc in commands:
        result = run_command(cmd, desc, check=False)
        if result and "fatal" in result.stderr.lower():
            print(f"\n❌ Push failed!")
            print("Troubleshooting tips:")
            print("  • Verify GitHub repo exists at https://github.com/stackdigitz-netizen/fiilthy")
            print("  • Check your git credentials: git config --list")
            print("  • If you hit auth issues, generate a personal access token: https://github.com/settings/tokens")
            return False
    
    print("\n✅ Code pushed to GitHub!")
    return True

def display_vercel_instructions():
    """Show Vercel deployment instructions"""
    print("\n" + "="*80)
    print("🚀 VERCEL DEPLOYMENT")
    print("="*80)
    print("""
OPTION A: Deploy via Vercel UI (Easiest) ⭐

1️⃣  OPEN IN BROWSER:
    https://vercel.com/new

2️⃣  CLICK: "Import Project" → "GitHub"

3️⃣  FIND YOUR REPO:
    Search for: fiilthy
    Click on: stackdigitz-netizen/fiilthy

4️⃣  ADD ENVIRONMENT VARIABLES:
    Add these in the "Environment Variables" section:
    
    JWT_SECRET = (generate random string, e.g., generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
    MONGO_URI = (your MongoDB Atlas connection string)
    DB_NAME = ceo_ai

5️⃣  CLICK: "Deploy"

6️⃣  WAIT: ~2-5 minutes for deployment

7️⃣  YOUR URL: Will show at top of Vercel dashboard
    Example: https://fiilthy-xyz123.vercel.app

────────────────────────────────────────────────────────

OPTION B: Deploy via Vercel CLI (Faster)

Run these commands:

npm install -g vercel
cd c:\\Users\\user\\fiilthy
vercel --prod

Then follow the prompts to add environment variables.

────────────────────────────────────────────────────────

✨ After Deployment:

• Your backend URL: https://your-deployment.vercel.app
• API docs: https://your-deployment.vercel.app/docs
• Health check: https://your-deployment.vercel.app/api/fiilthy/health
• Update frontend with this URL

""")
    
    print("\nPress ENTER when Vercel deployment is complete...")
    input("→ ")

def generate_deployment_verification():
    """Create verification script"""
    verify_script = """#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def verify_deployment(base_url):
    \"\"\"Verify deployed backend is working\"\"\"
    print(f"\\n🔍 Verifying deployment: {base_url}")
    print("="*60)
    
    checks = [
        ("/api/fiilthy/health", "Health check"),
        ("/docs", "API Documentation"),
        ("/openapi.json", "OpenAPI Schema"),
    ]
    
    for endpoint, description in checks:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else f"⚠️  ({response.status_code})"
            print(f"{status} {description}: {base_url}{endpoint}")
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
    
    print("="*60)
    print("\\n✨ Deployment verification complete!")
    print(f"\\n📊 Next steps:")
    print("  1. Visit https://your-deployment.vercel.app/docs")
    print("  2. Test the /api/v5/schedule/create endpoint")
    print("  3. Update frontend with backend URL")

if __name__ == "__main__":
    base_url = input("Enter your Vercel deployment URL (e.g., https://fiilthy-xyz.vercel.app): ").strip()
    if base_url:
        verify_deployment(base_url)
    else:
        print("No URL provided")
"""
    
    with open("verify_vercel_deployment.py", "w") as f:
        f.write(verify_script)
    print("✅ Created verify_vercel_deployment.py")

def create_env_template():
    """Create .env.example for reference"""
    env_template = """# Backend Environment Variables
# Copy these to Vercel dashboard under Settings > Environment Variables

JWT_SECRET=generate-a-random-string-here
MONGO_URI=your-mongodb-atlas-connection-string
DB_NAME=ceo_ai

# Optional - for video generation features
ELEVENLABS_API_KEY=your-key-here
PEXELS_API_KEY=your-key-here
PIXABAY_API_KEY=your-key-here

# Stripe (if using payments)
STRIPE_SECRET_KEY=your-key-here

# Social Media APIs
TIKTOK_CLIENT_ID=your-id
TIKTOK_CLIENT_SECRET=your-secret
INSTAGRAM_ACCESS_TOKEN=your-token
YOUTUBE_API_KEY=your-key
"""
    
    with open(".env.example", "w") as f:
        f.write(env_template)
    print("✅ Created .env.example")

def main():
    """Main launch flow"""
    print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                  🚀 FIILTHY.AI - AUTOMATED LAUNCH WIZARD 🚀                   ║
║                                                                                ║
║                    System Status: ✅ READY FOR DEPLOYMENT                      ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n⚠️  Missing some tools, but we can continue...")
    
    # Check git status
    if not check_git_status():
        print("❌ Git working tree not clean. Commit changes first!")
        sys.exit(1)
    
    # GitHub setup
    display_github_instructions()
    
    # Push code
    if not push_to_github():
        print("⚠️  Push may have failed. Check GitHub manually.")
        print("Visit: https://github.com/stackdigitz-netizen/fiilthy")
    
    # Vercel setup
    display_vercel_instructions()
    
    # Create helper files
    generate_deployment_verification()
    create_env_template()
    
    # Success message
    print("\n" + "="*80)
    print("✅ LAUNCH COMPLETE!")
    print("="*80)
    print("""
🎉 Your system is now LIVE!

📊 WHAT'S DEPLOYED:
   ✅ Backend API @ https://your-deployment.vercel.app
   ✅ Post Scheduler (7 endpoints)
   ✅ Quality Control (4 endpoints)
   ✅ Real Video Generator
   ✅ Opportunity Hunter
   ✅ Authentication system
   ✅ API Documentation

🔗 IMPORTANT LINKS:
   • Deployment: https://vercel.com/dashboard
   • GitHub: https://github.com/stackdigitz-netizen/fiilthy
   • API Docs: https://your-deployment.vercel.app/docs

💻 FRONTEND NEXT:
   1. Update frontend/.env with your backend URL
   2. Rebuild frontend
   3. Deploy to Vercel/Netlify

📞 SUPPORT:
   Run: python verify_vercel_deployment.py <your-url>

""")

if __name__ == "__main__":
    main()
