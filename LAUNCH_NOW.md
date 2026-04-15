# 🚀 LIVE LAUNCH GUIDE - FIILTHY.AI

**Status**: ✅ All systems ready  
**Date**: April 14, 2026  
**Target**: Vercel Deployment

---

## 📋 LAUNCH OPTIONS

### **OPTION 1: Auto-Deploy via GitHub (Recommended)**

**Step 1: Ensure GitHub repo exists**
```bash
# Your GitHub repo URL:
https://github.com/stackdigitz-netizen/fiilthy

# Verify local repo is clean
git status
# Should show: "nothing to commit, working tree clean"
```

**Step 2: Push to GitHub**
```bash
git push origin main
```

**Step 3: Connect to Vercel**
1. Go to: https://vercel.com/new
2. Click "Import Project"
3. Select GitHub → Connect GitHub account
4. Find & select: `stackdigitz-netizen/fiilthy`
5. Click "Import"

**Step 4: Configure Environment Variables in Vercel**
```
PROJECT SETTINGS → ENVIRONMENT VARIABLES

JWT_SECRET = your-secure-random-string-here
MONGO_URI = your-mongodb-atlas-connection-string
DB_NAME = ceo_ai

# Optional (for features):
ELEVENLABS_API_KEY = your-key
PEXELS_API_KEY = your-key
PIXABAY_API_KEY = your-key
```

**Step 5: Deploy**
- Click "Deploy"
- Watch build logs (should take 2-5 minutes)
- Get live URL when complete

---

### **OPTION 2: Deploy via Vercel CLI**

**Prerequisites**: Install Vercel CLI
```bash
npm i -g vercel
```

**Deploy Steps**:
```bash
cd c:\Users\user\fiilthy

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Follow prompts and set environment variables
```

---

### **OPTION 3: Manual GitHub Push (If repo exists)**

```bash
# Verify all changes committed
git status

# Push to your GitHub repo
git push origin main

# Then in Vercel dashboard:
# New Project → Import from Git → Select fiilthy repo
```

---

## ✅ PRE-LAUNCH CHECKLIST

Before clicking deploy, verify:

- [ ] Git repo is clean: `git status`
- [ ] Latest commit is there: `git log --oneline -1`
- [ ] All files committed: `git diff --cached` (empty)
- [ ] GitHub account created
- [ ] Vercel account created
- [ ] MongoDB Atlas account ready with connection string
- [ ] Environment variables ready

---

## 📊 DEPLOYMENT TIMELINE

```
T+0min:   Push to GitHub / Click Deploy on Vercel
T+1-2min: Build process starts (Python dependencies install)
T+2-4min: FastAPI server starts, routes registered
T+5min:   ✅ LIVE - Get your .vercel.app URL
```

---

## 🔍 VERIFY AFTER DEPLOYMENT

Once you get your Vercel URL (e.g., `https://fiilthy-123.vercel.app`):

**Check 1: API is live**
```bash
curl https://YOUR_URL/api/fiilthy/health
```
Expected: `{"status": "ok", ...}`

**Check 2: API docs accessible**
```
https://YOUR_URL/docs
```
Should show Swagger UI with all endpoints

**Check 3: Authentication works**
```bash
curl -X POST https://YOUR_URL/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","first_name":"Test","last_name":"User"}'
```

**Check 4: Run verification script**
```bash
python verify_deployment.py
# Enter your Vercel URL when prompted
```

---

## 🚨 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| "Build failed - Python not found" | Check `vercel.json` exists & has correct build config |
| "Auth fails on Vercel" | Verify `JWT_SECRET` env var is set |
| "502 Bad Gateway" | Check Vercel build logs for Python errors |
| "MongoDB timeout" | Add Vercel IPs to MongoDB whitelist (0.0.0.0/0) |

---

## 📞 YOUR GITHUB REPO

```
Owner: stackdigitz-netizen
Repo: fiilthy
URL: https://github.com/stackdigitz-netizen/fiilthy
```

---

## 🎯 WHAT'S DEPLOYED

✅ FastAPI backend with all production services  
✅ Post scheduling across 5+ platforms  
✅ Quality control engine with strict validation  
✅ Real video generation (API integration)  
✅ Opportunity hunter system  
✅ MongoDB integration  
✅ JWT authentication  
✅ Full API documentation at `/docs`  

---

## ⏱️ NEXT 5 MINUTES

1. **Create/verify GitHub repo** (1 min)
2. **Push code to GitHub** (1 min)
3. **Import project on Vercel** (1 min)
4. **Set environment variables** (1 min)
5. **Click Deploy & wait** (2-3 min)

**Total: ~7 minutes to LIVE** 🚀

---

## 📱 FINAL STEP

Once deployed and verified, update your frontend `.env`:

```
REACT_APP_API_URL=https://YOUR_VERCEL_URL/api
REACT_APP_BACKEND_URL=https://YOUR_VERCEL_URL
```

Then redeploy frontend.

---

**Ready? Go here:** https://vercel.com/new

🚀 **LET'S LAUNCH!** 🚀
