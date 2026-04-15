#!/usr/bin/env python3
"""
LAUNCH FIILTHY.AI - ONE COMMAND DEPLOYMENT
Automated GitHub + Vercel deployment
"""

import subprocess
import time
import sys
import json
import webbrowser

def cmd(command, silent=False):
    """Run command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if not silent:
            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(result.stderr)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        print(f"Error: {e}")
        return False, str(e)

print("\n" + "="*80)
print("LAUNCHING FIILTHY.AI PRODUCTION SYSTEM")
print("="*80 + "\n")

# Step 1: Verify git
print("1️⃣  Verifying Git Repository...")
success, _ = cmd("git status", silent=True)
if not success:
    print("❌ Not in git repository")
    sys.exit(1)
print("✅ Git repository ready")

# Step 2: Show deployment status
print("\n2️⃣  Current Deployment Status:")
success, output = cmd("git remote -v", silent=True)
if "github.com/stackdigitz-netizen/fiilthy" in output:
    print("✅ GitHub remote configured")
    print(f"   {output.strip()}")
else:
    print("⚠️  GitHub remote not configured yet")

# Step 3: Check commits
success, output = cmd("git log --oneline -1", silent=True)
print(f"\n3️⃣  Latest Commit: {output.strip()}")

# Step 4: Provide deployment instructions
print("\n" + "="*80)
print("MANUAL DEPLOYMENT STEPS (Copy & Paste)")
print("="*80 + "\n")

print("STEP 1️⃣  - CREATE GITHUB REPO (in your browser)")
print("""
1. You're at: https://github.com/login
2. Log in to GitHub
3. Go to: https://github.com/new
4. Fill in:
   - Repository name: fiilthy
   - Visibility: PUBLIC
5. Click "Create repository"
""")

print("\nSTEP 2️⃣  - PUSH CODE (copy paste this command)")
print("""
cd c:\\Users\\user\\fiilthy
git remote set-url origin https://github.com/stackdigitz-netizen/fiilthy.git
git branch -M main
git push -u origin main
""")

print("\nSTEP 3️⃣  - DEPLOY TO VERCEL (in your browser)")
print("""
1. Go to: https://vercel.com/new
2. Click "Import Project"
3. Select "GitHub"
4. Search: fiilthy
5. Click to select: stackdigitz-netizen/fiilthy
6. Add Environment Variables:
   - JWT_SECRET = (generate random)
   - MONGO_URI = (your MongoDB connection)
   - DB_NAME = ceo_ai
7. Click "Deploy"
8. Done! Your backend will be live in 2-5 minutes
""")

print("\n" + "="*80)
print("FAST TRACK: Copy-Paste Commands")
print("="*80 + "\n")

print("Terminal command (after creating GitHub repo):")
print("""
cd c:\\Users\\user\\fiilthy && git remote set-url origin https://github.com/stackdigitz-netizen/fiilthy.git && git branch -M main && git push -u origin main
""")

print("\n" + "="*80)
print("VERCEL DEPLOYMENT LINK")
print("="*80)
print("Go to: https://vercel.com/new")
print("\n")

# Option to open browser
print("Opening deployment links in browser...\n")
webbrowser.open("https://github.com/login")
time.sleep(1)
webbrowser.open("https://vercel.com/new")

print("✅ Browser windows opened")
print("\nFollow the steps above to deploy!")
print("Estimated time to live: 10 minutes\n")
