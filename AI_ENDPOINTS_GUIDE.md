# AI Service Endpoints Documentation

## Overview
The system now includes 4 new AI service endpoints that leverage OpenAI, Anthropic, and DALL-E APIs through the secure key management system.

## Architecture Flow

```
Frontend Settings Page
    ↓ (via localStorage)
Backend KeysManager
    ↓ (encrypted storage)
AI Service Endpoints
    ↓ (API calls)
OpenAI / Anthropic / DALL-E
    ↓ (responses)
MongoDB (optional persistence)
```

## Endpoints

### 1. GET `/api/keys/status`
**Purpose:** Check which API keys are configured

**Response:**
```json
{
  "api_keys_status": {
    "openai_key": "✅ Configured",
    "anthropic_key": "✅ Configured",
    "dalle_key": "❌ Not configured",
    "sendgrid_key": "✅ Configured",
    "stripe_key": "✅ Configured",
    "gumroad_key": "✅ Configured",
    "mongodb": "✅ Connected"
  }
}
```

### 2. POST `/api/ai/generate-product`
**Purpose:** Generate product description using OpenAI ChatGPT

**Request:**
```json
{
  "concept": "AI-powered project management tool for remote teams",
  "keywords": ["productivity", "collaboration", "remote work"],
  "tone": "professional"
}
```

**Response:**
```json
{
  "title": "TeamFlow: AI Project Management",
  "description": "Streamline remote team collaboration with AI-powered project management. Automatically organize tasks, track progress, and generate insights.",
  "keywords": ["project management", "remote teams", "AI", "collaboration", "productivity"],
  "price_range": "$29-$99",
  "target_audience": "Remote teams and distributed startups"
}
```

### 3. POST `/api/ai/find-opportunities`
**Purpose:** Find market opportunities using Anthropic Claude

**Request:**
```json
{
  "niche": "AI-powered email marketing",
  "market_size": "large",
  "keyword_focus": "email automation AI"
}
```

**Response:**
```json
{
  "opportunity_title": "AI Email Marketing Personalization Platform",
  "demand_level": "High",
  "competition_level": "Medium",
  "trend_direction": "Rising",
  "estimated_market_size": "$500M-$1B",
  "recommended_keywords": ["email AI", "automated copywriting", "personalization", "marketing automation"],
  "action_items": [
    "Research competing solutions",
    "Build beta with early adopters",
    "Create AI copywriting templates"
  ]
}
```

### 4. POST `/api/ai/generate-image`
**Purpose:** Generate product image using DALL-E

**Request:**
```json
{
  "description": "Professional project management dashboard with team collaboration features",
  "style": "professional UI design",
  "size": "1024x1024"
}
```

**Response:**
```json
{
  "image_url": "https://oaidalleapiprodscus.blob.core.windows.net/private/...",
  "prompt_used": "Professional project management dashboard with team collaboration features Style: professional UI design High quality product photography",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 5. POST `/api/ai/generate-full-product` (RECOMMENDED)
**Purpose:** Complete product generation workflow - concept → description → image → database

**Request:**
```json
{
  "concept": "Email marketing automation platform with AI copywriting",
  "keywords": ["email marketing", "AI", "automation", "copywriting"],
  "generate_image": true,
  "save_to_db": true
}
```

**Response:**
```json
{
  "product": {
    "title": "EmailGenius Pro",
    "description": "Automate your email marketing with AI-generated copy that converts...",
    "keywords": ["email marketing", "AI copywriting", "automation"],
    "price_range": "$49-$199",
    "target_audience": "E-commerce businesses and agencies"
  },
  "image": {
    "image_url": "https://oaidalleapiprodscus.blob.core.windows.net/private/...",
    "prompt_used": "...",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "database_id": "507f1f77bcf86cd799439011",
  "status": "success"
}
```

## Integration Requirements

### API Keys Required (in Settings/Frontend)
1. **OpenAI Key** - For product generation and DALL-E
   - Env variable: `OPENAI_API_KEY`
   - Frontend field: `openai_key`

2. **Anthropic Key** - For opportunity discovery
   - Env variable: `ANTHROPIC_API_KEY`
   - Frontend field: `anthropic_key`

3. **DALL-E Key** - For image generation (same as OpenAI)
   - Env variable: `DALLE_API_KEY` (or use `OPENAI_API_KEY`)
   - Frontend field: `dalle_key`

### Setup Steps

1. **Get API Keys:**
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - DALL-E: Use OpenAI key

2. **Store in Frontend Settings:**
   - Navigate to Settings page
   - Add each API key with category (AI)
   - Keys are encrypted via Fernet and stored in localStorage

3. **Send to Backend:**
   - POST `/api/keys/store` with all keys
   - Backend encrypts and caches them

4. **Use in Endpoints:**
   - Each endpoint retrieves key via `keys_manager.get_key()`
   - Key is passed to respective API client
   - Responses are processed and returned

## Error Handling

### Common Errors

**400 Bad Request - API key not configured**
```json
{
  "detail": "OpenAI API key not configured"
}
```
Solution: Add API key in Settings page, then POST to `/api/keys/store`

**500 Internal Server Error - API Error**
```json
{
  "detail": "OpenAI API error: Invalid API key provided"
}
```
Solution: Verify API key is correct in Settings page

**500 Internal Server Error - JSON Parsing**
- Fallback response is used with generic content
- Check logs for detailed error

## Usage Examples

### Python/HTTPX Example
```python
import httpx
import asyncio

async def generate_product():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:8000/api/ai/generate-product",
            json={
                "concept": "AI chatbot for customer support",
                "keywords": ["chatbot", "AI", "customer service"],
                "tone": "friendly"
            }
        )
        print(response.json())

asyncio.run(generate_product())
```

### JavaScript/Fetch Example
```javascript
async function generateProduct() {
  const response = await fetch("http://localhost:8000/api/ai/generate-product", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      concept: "AI chatbot for customer support",
      keywords: ["chatbot", "AI", "customer service"],
      tone: "friendly"
    })
  });
  const data = await response.json();
  console.log(data);
}

generateProduct();
```

### curl Example
```bash
curl -X POST http://localhost:8000/api/ai/generate-product \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "AI chatbot for customer support",
    "keywords": ["chatbot", "AI", "customer service"],
    "tone": "friendly"
  }'
```

## Data Flow

### Product Generation Flow
```
Frontend: Concept Input
    ↓
API: POST /ai/generate-product
    ↓
KeysManager: Retrieves OpenAI key
    ↓
OpenAI API: Generates description
    ↓
Response: AIProductResponse
    ↓
Frontend: Displays result
```

### Full Workflow Flow
```
Frontend: Submit concept + settings
    ↓
API: POST /ai/generate-full-product
    ├→ Generate product description (OpenAI)
    ├→ Generate image (DALL-E)
    └→ Save to MongoDB
    ↓
Response: Complete product with image and DB ID
    ↓
Frontend: Display with preview and status
```

## Status Indicators

Products in MongoDB will show:
- `status: "generated"` - AI generated product
- `source: "ai_generation"` - Source of product
- `created_at: ISO timestamp` - When created
- `image_url: URL or null` - Generated or stored image

## Next Steps

1. **Send keys from Settings to backend** (Frontend)
2. **Update dashboard to call `/ai/generate-full-product`** (Product generation flow)
3. **Add email integration with SendGrid** (Email notifications)
4. **Add autonomous product generation schedule** (Background tasks)
5. **Add product publishing workflow** (Gumroad integration)

## Testing

Run the test suite to verify all endpoints:

```bash
cd backend
python test_ai_endpoints.py
```

This tests all 5 endpoints with sample data.

## Performance Notes

- **Generate Product**: ~3-5 seconds (OpenAI request)
- **Find Opportunities**: ~4-7 seconds (Claude request)
- **Generate Image**: ~30 seconds (DALL-E processing)
- **Full Product**: ~40-50 seconds (all above combined)

Consider implementing background tasks for longer operations.
