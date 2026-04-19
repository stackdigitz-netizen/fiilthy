# 🚀 DEPLOY TO VERCEL - WEB UI GUIDE

Your browser is already open. Follow these exact steps to deploy RIGHT NOW.

---

## STEP 1: Create GitHub Repo (3 minutes)

**In your browser**, go to: https://github.com/new

Fill in:
- **Repository name**: `fiilthy`
- **Owner**: `stackdigitz-netizen` (select from dropdown)
- **Visibility**: `PUBLIC` ⭐ **MUST BE PUBLIC**
- **Initialize repository**: Leave unchecked
- **Click**: "Create repository"

✅ You'll see a blank repo page. GOOD - this is expected.

---

## STEP 2: Push Your Code (1 minute)

**In your terminal**, run these commands:

```bash
cd c:\Users\user\fiilthy
git branch -M main
git remote set-url origin https://github.com/stackdigitz-netizen/fiilthy.git
git push -u origin main
```

Wait for it to finish. You should see:
```
Enumerating objects: XXX, done...
To github.com:stackdigitz-netizen/fiilthy.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

✅ Your code is now on GitHub!

---

## STEP 3: Deploy on Vercel (2 minutes)

**In your browser**, go to: https://vercel.com/new

1. **Click**: "Import Project"
2. **Click**: "GitHub" (or "Continue with GitHub")
3. **Search for**: `fiilthy`
4. **Select**: `stackdigitz-netizen/fiilthy`
5. **Next**: You'll see project settings

---

## STEP 4: Add Environment Variables (1 minute)

In the "Environment Variables" section, add these:

| Name | Value | Notes |
|------|-------|-------|
| `JWT_SECRET` | Generate random string | Use: `openssl rand -base64 32` |
| `MONGO_URI` | Your MongoDB Atlas connection | Format: `mongodb+srv://...` |
| `DB_NAME` | `ceo_ai` | Just copy this |

Example:
```
Key: JWT_SECRET
Value: K3n8Xp2Lq5Vf7Jmw9Yd4Rt6Us1Oa3Bc
```

**Click**: "Deploy"

---

## STEP 5: Wait for Deployment (2-5 minutes)

Vercel will:
1. Clone your GitHub repo
2. Install Python dependencies
3. Build your FastAPI app
4. Deploy to production

You'll see a progress bar. When it turns green and says **"Congratulations"**, you're LIVE! 🎉

---

## STEP 6: Get Your Live URL

At the top of the Vercel dashboard, you'll see:

```
✅ Production
https://fiilthy-abc123xyz.vercel.app
```

**This is your live backend!**

---

## STEP 7: Verify Deployment Works

Visit this URL in your browser:

```
https://fiilthy-abc123xyz.vercel.app/docs
```

You should see the **Swagger API documentation**. If you see it, you're LIVE! ✅

---

## QUICK CHECKLIST

- [ ] Created GitHub repo at https://github.com/stackdigitz-netizen/fiilthy
- [ ] Pushed code: `git push -u origin main`  
- [ ] Went to https://vercel.com/new
- [ ] Selected GitHub → fiilthy repo
- [ ] Added environment variables (JWT_SECRET, MONGO_URI, DB_NAME)
- [ ] Clicked "Deploy"
- [ ] Waited 2-5 minutes for build
- [ ] Got live URL: `https://fiilthy-*.vercel.app`
- [ ] Verified `/docs` works

---

## AFTER DEPLOYMENT

### Update Frontend

1. Go to your frontend repo
2. Update `.env` with:
   ```
   REACT_APP_API_URL=https://fiilthy-abc123xyz.vercel.app
   ```
3. Redeploy frontend

### Test Your APIs

Try these in Swagger at `/docs`:

- **Health Check**: `GET /api/fiilthy/health`
- **Schedule Post**: `POST /api/v5/schedule/create`
- **Run QC**: `POST /api/v5/qc/check`
- **Generate Video**: `POST /api/v5/videos/generate-real`

### Monitor Logs

Go to: https://vercel.com/dashboard → fiilthy → Deployments (tab) → Logs

---

## 🎯 THAT'S IT!

Your backend is now LIVE on Vercel. Total time: ~8-10 minutes.

Status:
- ✅ Backend deployed
- ⏳ Frontend awaits update
- 🚀 Ready for traffic

**Questions?** Check Vercel logs or visit your `/docs` endpoint for API reference.

