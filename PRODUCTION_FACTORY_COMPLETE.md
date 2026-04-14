# Complete Production Factory Setup & Integration Guide

**Date**: April 2026  
**Status**: ✅ Core Systems Overhauled & Functional

---

## 🎯 What's Been Fixed

### 1. ✅ Authentication (Fixed)
- **Issue**: JWT_SECRET env variable name mismatch between components
- **Fix**: 
  - `auth_utils.py` now accepts both `JWT_SECRET_KEY` and `JWT_SECRET`
  - `fiilthy_admin.py` now uses shared `decode_token()` from auth_utils
  - Both Flask and FastAPI backends use consistent secret handling

**Files Modified**:
- `backend/ai_services/auth_utils.py` — fallback env vars
- `backend/fiilthy_admin.py` — shared token decode

### 2. ✅ Post Scheduling System (New)
- **New File**: `backend/ai_services/post_scheduler.py`
- **Capabilities**:
  - Schedule posts across TikTok, Instagram, YouTube, Twitter, LinkedIn
  - Automatic platform-specific spacing (respects rate limits)
  - Flexible time slots (peak hour scheduling)
  - Pause/Resume/Reschedule support
  - Track posting status in real-time
  - Database persistence

**Key Classes**:
- `PostScheduler` — main scheduling engine
- `PostStatus` — draft, scheduled, queued, posting, posted, failed
- `PlatformPostConfig` — platform limits & rules

**API Endpoints** (see routes below)

### 3. ✅ Strict Quality Control (New)
- **New File**: `backend/ai_services/quality_control.py`
- **Validation Types**:
  - Product validation (title, description, price, cover, tags)
  - Video validation (duration, resolution, script quality)
  - Post validation (text, media, hashtags, platform specs)
  
**Quality Levels**:
- 🔴 **CRITICAL** — blocks publishing
- 🟠 **HIGH** — requires action
- 🟡 **MEDIUM** — warning
- ✅ **LOW** — informational

**Output**: 
- Quality score (0-100)
- Issues with fix suggestions
- Publishability status
- Recommendations

### 4. ✅ Real Video Generation (New)
- **New File**: `backend/ai_services/real_video_generator.py`
- **No Heavy Dependencies** — uses lightweight API integration
- **Integrations**:
  - **ElevenLabs** — AI voiceovers with natural speech
  - **Pexels/Pixabay** — stock background footage
  - **Replicate** — advanced video encoding (optional)

**Capabilities**:
- Generate multiple video variations
- Professional voiceover scripts
- Stock footage integration
- Platform-ready formats (vertical for TikTok/Shorts)
- QC integration (automatic quality checks)

### 5. ✅ AI Factory Overhaul
**Services Made Functional**:
- OpportunityHunter — finds real opportunities
- ProductGenerator — generates product concepts
- RevenueMaximizer — optimizes pricing & funnels
- MultiPlatformManager — coordinated publishing
- SocialMediaAI — creates platform-specific content

### 6. ✅ API Production Routes (New)
- **New File**: `backend/core/routes_v5_production_new.py`
- Comprehensive endpoints for all production features
- Integration-ready with database

---

## 🚀 Quick Start

###Step 1: Set Environment Variables

```bash
# JWT Authentication
export JWT_SECRET="your-super-secret-key-here"
export JWT_SECRET_KEY="same-key-for-compatibility"

# Video Generation
export ELEVENLABS_API_KEY="your-elevenlabs-key"
export PEXELS_API_KEY="your-pexels-key"
export PIXABAY_API_KEY="your-pixabay-key"
export REPLICATE_API_KEY="your-replicate-key"  # Optional

# Database
export MONGO_URI="your-mongodb-connection"
export DB_NAME="ceo_ai"

# Stripe (if using payments)
export STRIPE_SECRET_KEY="your-stripe-key"
```

### Step 2: Start Backend

```bash
cd ceo/backend

# Install new dependencies (if needed)
pip install elevenlabs httpx

# Start FastAPI server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Test Authentication

```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

---

## 📋 API Reference

### POST SCHEDULING

#### Create Schedule
```
POST /api/v5/schedule/create

{
  "product_id": "prod-123",
  "content_items": [
    {
      "id": "content-1",
      "text": "Check out our amazing product!",
      "media_urls": ["url-to-image.jpg"],
      "hashtags": ["productlaunch", "business"],
      "is_video": false
    }
  ],
  "platforms": ["tiktok", "instagram", "youtube"],
  "start_date": "2026-04-15T09:00:00Z",
  "spacing_minutes": 120,
  "schedule_times": ["09:00", "15:00", "21:00"]
}

Response:
{
  "success": true,
  "schedule_id": "schedule-abc123",
  "total_scheduled": 15,
  "message": "Successfully scheduled 15 posts"
}
```

#### Get Schedule
```
GET /api/v5/schedule/{schedule_id}

Response includes: posts, stats, status
```

#### Get Upcoming Posts
```
GET /api/v5/schedule/upcoming?limit=20

Returns next 20 posts (next 7 days)
```

#### Pause/Resume Schedule
```
POST /api/v5/schedule/{schedule_id}/pause
POST /api/v5/schedule/{schedule_id}/resume
```

#### Reschedule Single Post
```
POST /api/v5/schedule/{post_id}/reschedule?new_time=2026-04-15T14:00:00Z
```

---

### QUALITY CONTROL

#### Run Full QC Check
```
POST /api/v5/qc/check

{
  "content_type": "product",  // or "video" or "post"
  "data": {
    "title": "Amazing Product",
    "description": "This product will change your life...",
    "price": 29.99,
    "cover": "url-to-cover.jpg",
    "tags": ["productivity", "ai", "business"]
  }
}

Response:
{
  "is_publishable": true,
  "quality_score": 87,
  "issue_counts": {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 0
  },
  "issues": [
    {
      "level": "high",
      "category": "Cover",
      "message": "Cover image not optimized",
      "fix_suggestion": "Use 1200x630px images"
    }
  ],
  "recommendations": [...]
}
```

#### Quick Product Validation
```
POST /api/v5/qc/product-validation

{
  "title": "Product Name",
  "description": "Description...",
  "price": 29.99,
  ...
}
```

#### Quick Video Validation
```
POST /api/v5/qc/video-validation

{
  "title": "Video Title",
  "script": "Voiceover script...",
  "duration_seconds": 45,
  "resolution": {"width": 1080, "height": 1920}
}
```

#### Quick Post Validation
```
POST /api/v5/qc/post-validation

{
  "text": "Post content...",
  "media_urls": ["url"],
  "hashtags": ["tag1", "tag2"],
  "platform": "tiktok"
}
```

---

### VIDEO GENERATION

#### Generate Videos
```
POST /api/v5/videos/generate-real

{
  "product_id": "prod-123",
  "video_style": "promotional",  // promotional, educational, social_proof
  "count": 3,
  "run_qc": true
}

Response:
{
  "success": true,
  "total_generated": 3,
  "videos": [
    {
      "id": "vid-abc123",
      "status": "ready",
      "metadata": {
        "title": "Product Title",
        "script": "Generated script...",
        "voiceover_url": "path/to/audio.mp3",
        "background_urls": ["url1", "url2"]
      },
      "qc_result": {
        "quality_score": 92,
        "is_publishable": true
      }
    }
  ]
}
```

---

### OPPORTUNITY HUNTING

#### Hunt for Opportunities
```
POST /api/v5/opportunities/hunt

Response:
{
  "success": true,
  "opportunities_found": 10,
  "opportunities": [
    {
      "id": "opp-1",
      "niche": "AI Writing Tools",
      "trend_score": 0.92,
      "competition_level": "medium",
      "estimated_monthly_revenue": "$2500",
      "platforms": ["Gumroad", "Etsy"],
      "action_items": [...]
    }
  ]
}
```

#### List Opportunities
```
GET /api/v5/opportunities/list?status=discovered&limit=50
```

#### Create Team for Opportunity
```
POST /api/v5/opportunities/{opportunity_id}/team

Creates specialized agent team to execute opportunity
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              FastAPI Server (8000)                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │   API Routes (routes_v5_production_new.py)  │  │
│  │   - Scheduling                              │  │
│  │   - Quality Control                         │  │
│  │   - Video Generation                        │  │
│  │   - Opportunities                           │  │
│  └──────────────────────────────────────────────┘  │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐  │
│  │         AI Services Layer                    │  │
│  ├──────────────────────────────────────────────┤  │
│  │ PostScheduler │ VideoGenerator │ QC │ Hunter│  │
│  │ ─────────────────────────────────────────────│  │
│  │ product_generator │ revenue_maximizer │      │  │
│  │ social_media_ai │ multi_platform_manager    │  │
│  └──────────────────────────────────────────────┘  │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐  │
│  │         External APIs                        │  │
│  │ ─────────────────────────────────────────────│  │
│  │ ElevenLabs (voice) │ Pexels (video)         │  │
│  │ OpenAI/Claude (AI) │ MongoDB (persistence)  │  │
│  │ TikTok/IG/YT APIs (publishing)              │  │
│  └──────────────────────────────────────────────┘  │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐  │
│  │         MongoDB Database                     │  │
│  │ ─────────────────────────────────────────────│  │
│  │ post_schedules │ generated_videos │ products│  │
│  │ discovered_opportunities │ users             │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Checklist

- [ ] JWT Secret set (JWT_SECRET or JWT_SECRET_KEY)
- [ ] MongoDB connection string in MONGO_URI
- [ ] ElevenLabs API key set
- [ ] Pexels API key set (for stock footage)
- [ ] TikTok API credentials configured
- [ ] Instagram API credentials configured
- [ ] YouTube API credentials configured
- [ ] Stripe keys set (if using payments)
- [ ] CORS URLs configured for frontend
- [ ] Email service configured (SendGrid/SES)

---

## 🛠️ Troubleshooting

###Authentication Fails After Deploy
```
✓ Check JWT_SECRET env var is set in deployment platform
✓ Verify both JWT_SECRET and JWT_SECRET_KEY exist or one exists
✓ Check LOCAL `.venv/` uses same secret as production
```

### Scheduling Not Working
```
✓ Ensure MongoDB connection is active
✓ Check post_schedules collection exists in DB
✓ Verify start_date is in future
✓ Check platform names match (lowercase, exact)
```

### Videos Not Generating
```
✓ Confirm ElevenLabs API key is valid
✓ Check API rate limits not exceeded
✓ Ensure Pexels/Pixabay keys set for stock footage
✓ Verify product data includes title + description
```

### Quality Control Too Strict
```
✓ Customize validation rules in quality_control.py
✓ Adjust MIN/MAX constants per business needs
✓ Add/remove issue categories as needed
```

---

## 📈 Next Steps

1. **Integrate with Frontend** 
   - Connect scheduling UI to `/api/v5/schedule/create`
   - Add QC check before publishing
   - Show upcoming posts dashboard

2. **Production Deployment**
   - Configure environment variables in deployment platform
   - Set up MongoDB Atlas connection
   - Configure API credentials (ElevenLabs, Pexels, etc)
   - Deploy to Vercel/Render/Railway

3. **Advanced Features**
   - A/B testing different video styles
   - Automated reposting of top performers
   - Multi-language video generation
   - Analytics dashboard with performance metrics

---

## 📞 Support

**Endpoints Status**: ✅ Ready for use  
**Database Integration**: ✅ Complete  
**API Testing**: Use `/api/v5/` prefix for all new endpoints  
**Documentation**: Every endpoint includes detailed docstrings

---

**Last Updated**: April 14, 2026  
**Version**: 5.0 - Production Factory Complete
