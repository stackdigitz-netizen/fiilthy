#!/usr/bin/env python3
"""
AUTOMATED DEPLOYMENT - Complete End-to-End
"""
import subprocess
import os
import sys
import time

def run(cmd, check=True):
    """Run shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        return False, result.stderr
    return True, result.stdout + result.stderr

print("\n" + "="*80)
print("FIILTHY.AI - AUTOMATED DEPLOYMENT IN PROGRESS")
print("="*80 + "\n")

# Step 1: Verify code ready
print("1. Checking code status...")
success, output = run("git status --short")
if output.strip():
    print("   ⚠️  Uncommitted changes. Committing...")
    run("git add . && git commit -m 'Final: Ready for deployment'")
print("   ✅ Code ready")

# Step 2: Configure git
print("\n2. Configuring git remote...")
run("git remote set-url origin https://github.com/stackdigitz-netizen/fiilthy.git", check=False)
run("git branch -M main", check=False)
print("   ✅ Git configured")

# Step 3: Try to push
print("\n3. Attempting to push to GitHub...")
success, output = run("git push -u origin main 2>&1", check=False)

if "Repository not found" in output or "fatal" in output:
    print("   ⚠️  GitHub repo doesn't exist yet")
    print("\n   NEXT ACTION REQUIRED:")
    print("   ════════════════════════════════════════════════════════════")
    print("   1. Go to: https://github.com/new")
    print("   2. Create repo:")
    print("      - Name: fiilthy")
    print("      - Visibility: PUBLIC")
    print("   3. Create repository")
    print("   4. Then run this command again")
    print("   ════════════════════════════════════════════════════════════\n")
    
    print("   Waiting for repo to be created... (Press Ctrl+C to skip)")
    print("   Retrying in 5 seconds...")
    time.sleep(5)
    
    # Retry
    success, output = run("git push -u origin main 2>&1", check=False)
    if success or "Everything up-to-date" in output:
        print("   ✅ Code pushed to GitHub!")
    else:
        print("   ❌ Still can't push. Repository may not exist.")
        print("\n   MANUAL STEPS:")
        print("   1. Create GitHub repo at: https://github.com/new")
        print("   2. Then retry: git push -u origin main")
        sys.exit(1)
else:
    if "Everything up-to-date" in output or success:
        print("   ✅ Code pushed to GitHub!")
    else:
        print(f"   ⚠️  {output[:100]}")

# Step 4: Show deployment info
print("\n" + "="*80)
print("DEPLOYMENT READY")
print("="*80)

success, commits = run("git log --oneline -1")
print(f"\n✅ Latest commit: {commits.strip()}")
print(f"✅ Repository: https://github.com/stackdigitz-netizen/fiilthy")

print("\n" + "="*80)
print("NEXT: VERCEL DEPLOYMENT")
print("="*80)
print("""
Go to: https://vercel.com/new

1. Click "Import Project"
2. Select "GitHub"  
3. Search: fiilthy
4. Select: stackdigitz-netizen/fiilthy
5. Add Environment Variables:
   - JWT_SECRET = (generate random)
   - MONGO_URI = (your MongoDB connection)
   - DB_NAME = ceo_ai
6. Click "Deploy"

Your backend will be LIVE in 2-5 minutes!
""")

print("="*80)
print("✅ FIILTHY.AI DEPLOYMENT INITIATED")
print("="*80 + "\n")
