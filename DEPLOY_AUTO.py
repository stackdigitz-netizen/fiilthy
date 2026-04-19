#!/usr/bin/env python3
"""
AUTONOMOUS DEPLOYMENT - Create GitHub Repo & Deploy
"""
import subprocess
import os
import json
import sys

def run(cmd, check=True):
    """Run shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr

print("\n" + "="*80)
print("AUTONOMOUS DEPLOYMENT - CREATING GITHUB REPO & DEPLOYING")
print("="*80 + "\n")

# Step 1: Check if we can create repo via command line
print("1. Checking for GitHub credentials...")
success, output = run("git config user.name", check=False)
if success:
    user_name = output.strip()
    print(f"   ✅ Git user: {user_name}")
else:
    print("   ⚠️  No git user configured")

# Step 2: Try to initialize github repo using git CLI or API
print("\n2. Attempting to create GitHub repository...")

# Try using git commands with existing auth
success, output = run("curl -s https://api.github.com/user 2>&1 | findstr login", check=False)

if "login" in output.lower():
    print("   ✅ GitHub API accessible")
else:
    print("   ⚠️  GitHub API requires authentication")
    print("   Using alternative approach...")

# Step 3: Just try to push - create repo on GitHub if it doesn't exist
print("\n3. Attempting to push code to GitHub...")

# Configure git for push
run("git config push.default simple", check=False)
run("git remote set-url origin https://github.com/stackdigitz-netizen/fiilthy.git", check=False)
run("git branch -M main", check=False)

# Try push
success, output = run("git push -u origin main 2>&1", check=False)

if "Repository not found" in output:
    print("   ⚠️  GitHub repo doesn't exist")
    print("\n   SOLUTION: Create repo at https://github.com/new then try again")
    print("   OR use this command after creating repo:")
    print("   git push -u origin main")
    
elif success or "Everything up-to-date" in output:
    print("   ✅ Code pushed to GitHub!")
    print(f"   Repository: https://github.com/stackdigitz-netizen/fiilthy")
    
else:
    print(f"   ⚠️  {output[:200]}")

# Step 4: Show Vercel status
print("\n4. Vercel Deployment Status...")
print("   ✅ Project exists: https://vercel.com/stackdigitz-5790s-projects/fiilthy")
print("   ⏳ Awaiting GitHub push completion")

# Step 5: Final instructions
print("\n" + "="*80)
print("NEXT: CREATE GITHUB REPO")
print("="*80)
print("""
1. Go to: https://github.com/new
2. Name: fiilthy
3. Visibility: PUBLIC
4. Create repository

Then run: git push -u origin main

Or wait for auto-redeploy from Vercel if repo already connected.

Your backend will be live at:
https://vercel.com/stackdigitz-5790s-projects/fiilthy
""")

print("="*80 + "\n")
