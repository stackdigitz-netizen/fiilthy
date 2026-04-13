# CEO AI System - Environment Setup Guide

## STEP 1: Generate MASTER_KEY for Encryption
```bash
python -c "import base64, os; key = base64.urlsafe_b64encode(os.urandom(32)).decode(); print(f'MASTER_KEY={key}')"
```
Save this output to your `.env` file in the root directory

---

## STEP 2: Root .env Setup
Create or update `C:\Users\user\fiilthy\ceo\.env` with:

```env
# ENCRYPTION
MASTER_KEY=<paste-the-key-from-step-1>

# DATABASE
MONGO_URI=mongodb://atlas-sql-69c78f411fed5a34367cded3-srgqzg.z.query.mongodb.net/ceo_ai?ssl=true&authSource=admin
MONGO_DB_NAME=ceo_ai

# AI SERVICES
OPENAI_API_KEY=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
GEMINI_API_KEY=AIzaSyBI7DB5_rXb4JBUm__8PD88jgwyWOlw4l4

# MARKETPLACE
GUMROAD_CLIENT_ID=[REDACTED]
GUMROAD_CLIENT_SECRET=[REDACTED]
GUMROAD_ACCESS_TOKEN=[REDACTED]

# PAYMENTS
STRIPE_API_KEY=[REDACTED]
STRIPE_SECRET_KEY=[REDACTED]

# EMAIL
MAILCHIMP_API_KEY=[REDACTED]

# BACKEND
SUPABASE_URL=[REDACTED]
SUPABASE_ANON_KEY=[REDACTED]
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVkdnFub3NneHhyZmNrb25uaXh0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDUxNjY3NSwiZXhwIjoyMDkwMDkyNjc1fQ.BrfmdUgnNl41ZsV468olDNs3XIFpXnpGDubZc7GjfOo

# APP CONFIG
ENVIRONMENT=production
APP_ENVIRONMENT=production
```

---

## STEP 3: Run Key Encryption Setup
```bash
cd c:\Users\user\fiilthy\ceo
cd backend
python setup_secure_keys.py
```

This will:
- ✅ Read all keys from .env files
- ✅ Encrypt them with MASTER_KEY
- ✅ Store in `backend/config/.secure_keys.json` (git-ignored)
- ✅ Display which keys were encrypted

---

## STEP 4: Verify Keys Are Secure
```bash
# Check the file exists (should contain encrypted binary strings)
cat backend/config/.secure_keys.json

# You should see something like:
# {
#   "mongo_uri": "gAAAAABp1LSGVrpkF_64RSRFCxVVSdaUw-fqUqFml_gaZ_jL...",
#   "openai_api_key": "gAAAAABp1LiVwIOzA_krPIl6gfKpkyGCrRWa2n4isAOtehkd...",
#   ...
# }
```

---

## STEP 5: Start the Backend
```bash
cd backend
export MASTER_KEY=<your-master-key>
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

The backend will:
- ✅ Load MASTER_KEY from environment
- ✅ Decrypt keys from `.secure_keys.json`
- ✅ Initialize all AI services
- ✅ Connect to MongoDB
- ✅ Start FastAPI server

---

## STEP 6: Start the Frontend
```bash
cd frontend
npm install
export REACT_APP_BACKEND_URL=http://localhost:8000
npm start
```

Visit: **http://localhost:3000**

---

## 🔐 Security Checklist

- ✅ MASTER_KEY is in `.env` (never commit)
- ✅ `.secure_keys.json` is in `.gitignore`
- ✅ All API keys encrypted at rest
- ✅ Keys decrypted in memory only when needed
- ✅ Sensitive data never logged
- ✅ MongoDB connection secured with SSL

---

## 🚀 What's Working

- ✅ **MongoDB:** Connected to atlas-sql cluster0 (verified working)
- ✅ **OpenAI:** API key ready
- ✅ **Gemini:** API key ready  
- ✅ **Gumroad:** Auth tokens ready
- ✅ **Stripe:** Payment keys ready
- ✅ **Supabase:** All keys configured
- ✅ **Mailchimp:** Email API ready

---

## 🔧 Troubleshooting

**Error: "Failed to decrypt key"**
- Check MASTER_KEY matches the one used during setup
- Delete `.secure_keys.json` and rerun `setup_secure_keys.py`

**Error: "MongoDB connection refused"**
- Check MONGO_URI is correct and MongoDB is reachable
- Verify SSL certificate if using Atlas

**Error: "API key not found"**
- Rerun `setup_secure_keys.py` to re-encrypt all keys
- Check keys are in root `.env` file

---

## 📊 Keys Inventory

| Service | Status | Location |
|---------|--------|----------|
| MongoDB | ✅ | Encrypted in vault |
| OpenAI | ✅ | Encrypted in vault |
| Gemini | ✅ | Encrypted in vault |
| Gumroad | ✅ | Encrypted in vault |
| Stripe | ✅ | Encrypted in vault |
| Supabase | ✅ | Encrypted in vault |
| Mailchimp | ✅ | Encrypted in vault |

---

## 💡 Tips

- Keep MASTER_KEY in a password manager
- Rotate keys quarterly
- Never share `.secure_keys.json`
- Use different keys for dev/staging/production
- Monitor API usage in each service dashboard
