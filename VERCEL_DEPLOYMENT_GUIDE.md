# Vercel Deployment Guide - FiiLTHY.ai

**Status**: ✅ Ready for Launch  
**Date**: April 14, 2026

---

## 🚀 Deploy in 2 Minutes

### Step 1: Click Deploy Button
```
👉 https://vercel.com/new
```
- Select your GitHub repo (fiilthy)
- Click "Import Project"
- Vercel auto-detects FastAPI backend

### Step 2: Add Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

**Critical (Must Have)**:
```
JWT_SECRET = your-secure-random-string
MONGO_URI = your-mongodb-atlas-url
DB_NAME = ceo_ai
```

**Optional (For Features)**:
```
ELEVENLABS_API_KEY = your-key
PEXELS_API_KEY = your-key
PIXABAY_API_KEY = your-key
STRIPE_SECRET_KEY = your-key
```

### Step 3: Deploy
```bash
git push origin main
```
Vercel auto-deploys. Done! 🎉

---

## ✅ Verify Deployment

Once live, check these:

```bash
# Your backend URL
https://your-project.vercel.app

# API Docs (Swagger)
https://your-project.vercel.app/docs

# Health Check
curl https://your-project.vercel.app/api/fiilthy/health

# Test Auth
curl -X POST https://your-project.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

## 🔧 Troubleshooting

### "Build failed - Python not found"
✓ Ensure `ceo/backend/requirements.txt` exists  
✓ Check `vercel.json` points to correct path

### "Authentication fails"
✓ Verify `JWT_SECRET` is set in Vercel env vars  
✓ Backend needs same secret as frontend expects

### "Database connection timeout"
✓ Check MongoDB URI in env vars  
✓ Whitelist Vercel IP: Settings → IP Whitelist → 0.0.0.0/0

### "API returns 502"
✓ Check Vercel build logs
✓ Ensure all imports work (run `python -m py_compile ceo/backend/server.py` locally)

---

## 📊 What's Deployed

✅ FastAPI Backend  
✅ Post Scheduling System  
✅ Quality Control Engine  
✅ Video Generation (API-ready)  
✅ Opportunity Hunter  
✅ JWT Authentication  
✅ MongoDB Integration  

---

## 🔗 Connect Frontend

Update frontend `.env`:
```
REACT_APP_API_URL=https://your-project.vercel.app/api
REACT_APP_BACKEND_URL=https://your-project.vercel.app
```

Then redeploy frontend.

---

## 📡 Monitoring

Vercel Dashboard shows:
- Real-time logs
- Build history
- Performance metrics
- Error reports

Check logs: Deployments → [Latest] → Logs

---

**Ready to launch?** Push to main and watch it deploy! 🚀
