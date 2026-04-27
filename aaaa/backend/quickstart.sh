#!/bin/bash
# Quick Start - All Integrations
# This script starts your complete multi-platform automation system

echo "======================================================================"
echo "🚀 STARTING COMPLETE INTEGRATION SYSTEM"
echo "======================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo "❌ Error: server.py not found"
    echo "Make sure you're in the backend directory: cd backend"
    exit 1
fi

echo "✅ Python environment check..."
python --version

echo ""
echo "✅ Checking dependencies..."
python -c "import fastapi; import pymongo; import aiohttp; print('All dependencies ready!')"

if [ $? -ne 0 ]; then
    echo "⚠️  Installing missing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "======================================================================"
echo "📊 CONFIGURED INTEGRATIONS"
echo "======================================================================"
echo ""
echo "  📱 TikTok:     14 endpoints (post, schedule, analytics, trending)"
echo "  🛍️  Gumroad:    14 endpoints (CRUD, files, variants, analytics)"
echo "  🤖 Gemini AI:   7 endpoints (generate, brainstorm, validate, analyze)"
echo "  🛒 Etsy:        9 endpoints (listings, shop, orders, analytics)"
echo "  🌐 Multi-Plat:  3 endpoints (publish all platforms simultaneously)"
echo ""
echo "  TOTAL: 44 API endpoints ready"
echo ""

echo "======================================================================"
echo "🎯 QUICK WORKFLOWS"
echo "======================================================================"
echo ""
echo "1️⃣  Create & Publish to All Platforms:"
echo "    POST /products/generate-with-gemini"
echo "    POST /products/{id}/publish-all-platforms"
echo ""
echo "2️⃣  Generate TikTok Video Series:"
echo "    POST /api/products/{id}/post-tiktok-series"
echo ""
echo "3️⃣  Publish to Gumroad with Files:"
echo "    POST /gumroad/create-product"
echo "    POST /gumroad/{id}/upload-file"
echo ""
echo "4️⃣  Analyze Market & Brainstorm:"
echo "    POST /products/analyze-market-gemini"
echo "    POST /products/{id}/brainstorm-gemini"
echo ""

echo "======================================================================"
echo "🔧 ENVIRONMENT VARIABLES REQUIRED"
echo "======================================================================"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << 'EOF'
# Gemini API Keys
GEMINI_API_KEY=your_key_here
GEMINI_API_KEY_2=backup_key_1
GEMINI_API_KEY_3=backup_key_2

# TikTok
TIKTOK_CREATOR_TOKEN=your_token_here
TIKTOK_OAUTH_TOKEN=your_oauth_token

# Gumroad
GUMROAD_API_TOKEN=your_token_here

# Etsy
ETSY_API_KEY=your_key_here
ETSY_API_SECRET=your_secret_here
ETSY_SHOP_ID=your_shop_id

# Stripe (for payments)
STRIPE_API_KEY=your_key_here
STRIPE_WEBHOOK_SECRET=your_secret_here

# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/database
EOF
    echo "✅ Template created at .env"
    echo "⚠️  Please update .env with your API keys"
fi

echo ""
echo "✅ Checking for critical API keys..."
if grep -q "your_" .env; then
    echo "⚠️  .env contains placeholder values"
    echo "Please update your API keys before testing live endpoints"
fi

echo ""
echo "======================================================================"
echo "🚀 STARTING FASTAPI SERVER"
echo "======================================================================"
echo ""
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Alternative Docs: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python server.py
