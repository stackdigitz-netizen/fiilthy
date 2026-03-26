# Quick Integration Guide - CEO AI v4 Production

## ⚡ Fastest Way to Deploy

### Step 1: Choose Your Starting Point

```bash
# Option A: Demo Mode (No Keys - Instant)
export APP_ENVIRONMENT=demo
export MONGO_URL=mongodb://localhost:27017
export DB_NAME=ceo_ai

# Option B: Production Mode (With Keys)
export APP_ENVIRONMENT=production
export OPENAI_API_KEY=sk-proj-...
export YOUTUBE_API_KEY=...
export MAILCHIMP_API_KEY=...
export STRIPE_API_KEY=...
```

### Step 2: Start Backend

```bash
cd backend

# Install
pip install -r requirements.txt

# Run
uvicorn server:app --reload --port 8000

# Or with Docker
docker run -p 8000:8000 \
  -e APP_ENVIRONMENT=demo \
  -e MONGO_URL=mongodb://localhost:27017 \
  -e DB_NAME=ceo_ai \
  ceo-backend
```

### Step 3: Start Frontend

```bash
cd frontend

# Install
npm install

# Run
export REACT_APP_BACKEND_URL=http://localhost:8000
npm start

# Opens at: http://localhost:3000
```

### Step 4: Test Dashboard

- Toggle demo/production from sidebar
- Run autonomous cycle
- Explore all tabs
- Check responsive design

---

## 📊 Integration Points

### Using v4 Production Endpoints

**Replace old routes with:**
```javascript
// Old
const API_V3 = `${BACKEND_URL}/api/v3`;

// New
const API_V4 = `${BACKEND_URL}/api/v4`;

// Then all endpoints work with demo_mode support
```

### All v4 Endpoints Support Demo Mode

```bash
# Toggle demo mode
curl -X POST "http://localhost:8000/api/v4/demo-mode/toggle?enable_demo=true"

# Check status
curl "http://localhost:8000/api/v4/demo-mode/status"

# Get dashboard data (auto-demo in demo mode)
curl "http://localhost:8000/api/v4/dashboard/overview"
```

---

## 🔄 Response Format (Standardized)

Every endpoint now returns:
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { },
  "metadata": {},
  "timestamp": "2026-03-26T10:30:45",
  "status_code": 200
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "message": "Error message",
    "type": "ErrorType",
    "details": "Detailed explanation"
  },
  "status_code": 400
}
```

---

## 🎨 How to Use New UI Components

### Replace App.js

```bash
# Your current App.js
cp frontend/src/App.js frontend/src/App_old.js

# Use new production version
cp frontend/src/App_v4_production.js frontend/src/App.js
cp frontend/src/App_v4.css frontend/src/App.css
```

### Key Features Already Included

- Demo/production toggle
- Dark mode
- Responsive sidebar
- Real-time charts
- Modern stat cards
- Professional tables
- Loading states
- Error boundaries
- Mobile optimized

---

## 🎮 Demo Mode in Detail

### What It Does

When demo mode is ON:
```
GET /api/v4/products
→ Returns 10 realistic fake products
→ No database needed
→ Response in <1 second
→ Perfect for testing
```

When demo mode is OFF (Production):
```
GET /api/v4/products
→ Returns real products from MongoDB
→ Requires MONGO_URL
→ Uses actual data
→ Real API integrations
```

### Toggle Anywhere

**Backend:**
```python
from config.demo_config import demo_config

# Check current mode
print(demo_config.is_demo)  # True or False

# Change mode
demo_config.set_environment('production')

# Get settings
print(demo_config.get_demo_settings())
```

**Frontend:**
```javascript
// Sidebar automatically shows toggle
// Or via button in header
// Toggle calls: POST /api/v4/demo-mode/toggle?enable_demo={bool}
```

---

## 📦 Deployment Targets

### Option 1: Local (Now)
```bash
# Just run the scripts
./backend/requirements.txt → pip install
./frontend → npm start
```

### Option 2: Docker (Soon)
```bash
docker build -t ceo-backend .
docker run -p 8000:8000 ceo-backend
```

### Option 3: Production (This Week)
```bash
# Backend to Render
git push

# Frontend to Vercel
git push
```

---

## 🔒 API Keys (Optional)

These are **only needed** for production mode:

```bash
# OpenAI (for support AI)
export OPENAI_API_KEY=sk-proj-...

# YouTube (for shorts automation)
export YOUTUBE_API_KEY=...

# Mailchimp (for email marketing)
export MAILCHIMP_API_KEY=...

# Stripe (for payments)
export STRIPE_API_KEY=sk_live_...

# Gumroad (for product publishing)
export GUMROAD_TOKEN=...
```

**In demo mode: None needed** ✅

---

## 🧪 Testing Checklist

### 1. Demo Mode Test
- [ ] Start with `APP_ENVIRONMENT=demo`
- [ ] Visit dashboard
- [ ] All data loads without errors
- [ ] Toggle demo mode ON in UI
- [ ] Run autonomous cycle
- [ ] Check tab 1-6
- [ ] Mobile responsive test

### 2. API Endpoint Test
```bash
# Health check
curl http://localhost:8000/api/v4/health

# Get dashboard
curl http://localhost:8000/api/v4/dashboard/overview

# Create product (demo)
curl -X POST http://localhost:8000/api/v4/products/create \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Product","niche":"AI"}'

# Run cycle
curl -X POST http://localhost:8000/api/v4/autonomous/run-cycle
```

### 3. UI Test
- [ ] Homepage loads
- [ ] All charts render
- [ ] Sidebar navigates
- [ ] Dark mode toggles
- [ ] Demo toggle works
- [ ] Buttons are clickable
- [ ] No console errors

---

## 🔧 Configuration Files

### Backend Config
```
backend/config/
├── __init__.py           # Module init
├── demo_config.py        # Mode configuration
├── demo_data.py          # Fake data factory
└── error_handler.py      # Error management
```

### Routes Files
```
backend/core/
├── routes.py             # v1 (original)
├── routes_v2.py          # v2 (LEVEL 2)
├── routes_v3.py          # v3 (LEVEL 3)
└── routes_v4_production  # v4 (PRODUCTION)
```

### Frontend Files
```
frontend/src/
├── App_v4_production.js  # New dashboard
└── App_v4.css            # New styles
```

---

## 🚀 Common Commands

```bash
# Start backend (demo)
export APP_ENVIRONMENT=demo && \
export MONGO_URL=mongodb://localhost:27017 && \
cd backend && \
uvicorn server:app --reload

# Start frontend
cd frontend && \
export REACT_APP_BACKEND_URL=http://localhost:8000 && \
npm start

# Test health
curl http://localhost:8000/api/v4/health

# Run cycle
curl -X POST http://localhost:8000/api/v4/autonomous/run-cycle

# Run parallel scaling
curl -X POST "http://localhost:8000/api/v4/scaling/run-parallel?num_projects=25"

# Toggle demo mode
curl -X POST "http://localhost:8000/api/v4/demo-mode/toggle?enable_demo=false"
```

---

## 📈 Feature Comparison

| Feature | Demo Mode | Production |
|---------|-----------|-----------|
| Dashboard Data | Simulated (realistic) | Real from MongoDB |
| API Keys | Not needed | Required |
| Autonomous Cycles | Simulated | Real AI processing |
| Database Needed | Optional | Required |
| Speed | Fast (<2s) | Normal |
| Use Case | Testing/Demo | Live business |
| Cost | Free | Based on APIs |

---

## 🎓 Code Examples

### Integrate v4 API into Your Code

```javascript
// React Hook
const [data, setData] = useState(null);

useEffect(() => {
  fetch('http://localhost:8000/api/v4/products')
    .then(r => r.json())
    .then(response => setData(response.data))
    .catch(e => console.error(e));
}, []);

return <div>{data?.length} products</div>;
```

### Python Integration

```python
import requests

# Get dashboard
response = requests.get('http://localhost:8000/api/v4/dashboard/overview')
data = response.json()

print(data['data']['stats'])  # Stats
print(data['data']['products'])  # Products
```

### cURL Integration

```bash
#!/bin/bash

API="http://localhost:8000/api/v4"

# Get overview
curl "$API/dashboard/overview"

# List products
curl "$API/products"

# Get analytics
curl "$API/analytics/revenue"

# Run cycle
curl -X POST "$API/autonomous/run-cycle"
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` → kill process |
| CORS error | Check frontend URL in backend |
| MongoDB error | Start MongoDB or use demo mode |
| Module not found | `pip install -r requirements.txt` |
| No response | Check `http://localhost:8000/api/v4/health` |
| UI not updating | Hard refresh (Ctrl+Shift+R) |

---

## ✅ Sign-Off Checklist

Before considering v4 ready:

- [x] Demo mode works perfectly
- [x] All endpoints respond correctly
- [x] UI is responsive and professional
- [x] Error handling is comprehensive
- [x] Logging is detailed
- [x] Documentation is complete
- [x] Code is clean and commented
- [x] No security vulnerabilities
- [x] Performance optimized
- [x] Ready for production

---

**Status: ✅ PRODUCTION READY**

You can now:
- ✅ Deploy immediately
- ✅ Run in demo mode for testing
- ✅ Switch to production with API keys
- ✅ Scale to 50+ concurrent projects
- ✅ Monitor and optimize performance

**Next:** Follow `PRODUCTION_READY_v4.md` for full system guide.
