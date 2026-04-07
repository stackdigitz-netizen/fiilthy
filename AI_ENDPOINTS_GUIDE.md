# AI Service Endpoints Documentation

## Overview
The system includes comprehensive AI service endpoints and notification system:
- **5 AI Service Endpoints** for product generation, opportunity discovery, and image creation
- **6 Email & Notification Endpoints** for customer communication and task tracking
- **Secure Key Management** with Fernet encryption for all API keys

## Architecture Flow

```
Frontend Settings Page
    ↓ (via localStorage + POST /api/keys/store)
Backend KeysManager (Fernet encrypted)
    ↓ (retrieves keys as needed)
AI Service Endpoints / Email Service Endpoints
    ↓ (API calls to OpenAI / Anthropic / DALL-E / SendGrid)
MongoDB (stores products, notifications, metadata)
    ↓ (data persistence)
```

## Part 1: AI Service Endpoints

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

---

# Part 2: Email & Notification Endpoints

## Overview

The system includes 6 email and notification endpoints for sending automated communications and tracking notifications:

1. **Email Management** - Send direct emails and templated emails via SendGrid
2. **Notifications** - Create, retrieve, and manage in-app notifications
3. **Workflow Integration** - Automatic emails when products are ready

## Email Endpoints

### 1. POST `/api/email/send`
**Purpose:** Send email directly

**Request:**
```json
{
  "to_email": "customer@example.com",
  "subject": "Welcome to CEO Empire! 🚀",
  "body": "<h1>Welcome!</h1><p>Your account is ready...</p>",
  "template_type": "general"
}
```

**Response:**
```json
{
  "status": "success",
  "message_id": "unique-message-id",
  "message": "Email sent successfully",
  "sent_at": "2024-01-15T10:30:00Z"
}
```

**Error Scenarios:**
- `400` - SendGrid API key not configured
- `500` - SendGrid SDK not installed or API error

### 2. POST `/api/email/send-template`
**Purpose:** Send email using predefined templates

**Supported Templates:**
- `product_ready` - When AI-generated product is ready
- `opportunity_found` - When market opportunity is discovered
- `task_completed` - When background task completes
- `revenue_update` - Daily/weekly revenue report

**Request:**
```bash
POST /api/email/send-template?to_email=customer@example.com&template_type=product_ready

# With template data:
{
  "product_title": "Email Marketing Guide",
  "product_description": "Master email with AI",
  "price_range": "$29-$99"
}
```

**Example Responses:**

**Product Ready Email:**
```html
🚀 Your Product 'Email Marketing Guide' is Ready!
---
Description: Master email marketing with AI-generated copy...
Price Range: $29-$99
[Next Steps to publish]
```

**Opportunity Found Email:**
```html
💡 New Market Opportunity Identified!
---
Niche: AI-powered email marketing
Market Size: $500M-$1B
Demand Level: High
Top Keywords: email AI, personalization, marketing automation
```

### 3. POST `/api/email/send-product-notification`
**Purpose:** Send email when product is ready (recommended for workflow)

**Request:**
```bash
POST /api/email/send-product-notification
?product_id=prod_12345
&to_email=customer@example.com
```

**What it does:**
1. Retrieves product from database
2. Includes full product details in email
3. Shows product image if available
4. Provides next steps for publishing

**Response:**
```json
{
  "status": "success",
  "message": "Email sent successfully",
  "sent_at": "2024-01-15T10:30:00Z"
}
```

## Notification Endpoints

### 4. POST `/api/notifications`
**Purpose:** Create a notification

**Request:**
```json
{
  "recipient_id": "user_12345",
  "type": "product_ready",
  "title": "Product Ready!",
  "message": "Your AI-generated product is ready for publishing",
  "data": {
    "product_id": "prod_67890",
    "product_title": "Email Marketing Guide"
  }
}
```

**Response:**
```json
{
  "notification_id": "notif_abc123",
  "status": "created",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Notification Types:**
- `product_ready` - Product generated and ready
- `opportunity_found` - Market opportunity identified
- `task_completed` - Background AI task finished
- `revenue_update` - Revenue milestone reached
- `error` - System or task error occurred
- `general` - General notification

### 5. GET `/api/notifications/{recipient_id}`
**Purpose:** Retrieve notifications for a user

**Query Parameters:**
- `limit` (default: 20) - Number of notifications to return
- `unread_only` (default: false) - Only return unread notifications

**Request:**
```bash
GET /api/notifications/user_12345?limit=10&unread_only=false
```

**Response:**
```json
{
  "notifications": [
    {
      "notification_id": "notif_1",
      "recipient_id": "user_12345",
      "type": "product_ready",
      "title": "Product Ready!",
      "message": "...",
      "read": false,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "notification_id": "notif_2",
      "type": "opportunity_found",
      ...
    }
  ],
  "total": 2,
  "recipient_id": "user_12345"
}
```

### 6. POST `/api/notifications/{notification_id}/read`
**Purpose:** Mark notification as read

**Request:**
```bash
POST /api/notifications/notif_abc123/read
```

**Response:**
```json
{
  "status": "marked_read"
}
```

## Integration Workflow Example

### Complete Product Generation with Notification

```python
import httpx

async def create_and_notify():
    # Step 1: Generate product with AI
    product_response = await client.post(
        "/api/ai/generate-full-product",
        json={
            "concept": "Email marketing platform",
            "keywords": ["email", "marketing", "AI"],
            "generate_image": True,
            "save_to_db": True
        }
    )
    
    # Step 2: Send product ready email
    if product_response["status"] == "success":
        product_id = product_response["database_id"]
        await client.post(
            f"/api/email/send-product-notification",
            params={
                "product_id": product_id,
                "to_email": "user@example.com"
            }
        )
        
        # Step 3: Create notification for dashboard
        await client.post(
            "/api/notifications",
            json={
                "recipient_id": "user_12345",
                "type": "product_ready",
                "title": f"Product Ready: {product_response['product']['title']}",
                "message": "Your AI-generated product is ready to publish!",
                "data": {"product_id": product_id}
            }
        )
```

## Frontend Integration Example

```javascript
// Get unread notifications
async function loadNotifications() {
  const response = await fetch(
    `/api/notifications/user_12345?unread_only=true`
  );
  const data = await response.json();
  displayNotifications(data.notifications);
}

// Mark notification as read
async function markAsRead(notificationId) {
  await fetch(
    `/api/notifications/${notificationId}/read`,
    { method: "POST" }
  );
}

// Send email template with custom data
async function sendProductEmail() {
  const response = await fetch(
    `/api/email/send-template?to_email=customer@example.com&template_type=product_ready`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_title: "Email Marketing Guide",
        product_description: "Master email with AI",
        price_range: "$29-$99"
      })
    }
  );
  const result = await response.json();
  console.log("Email sent:", result);
}
```

## SendGrid Setup Required

### 1. Create SendGrid Account
- Go to https://sendgrid.com
- Sign up for free (limited emails)
- Create API key with "Mail Send" permissions

### 2. Add to Settings
- Go to Settings page in the application
- Paste SendGrid API key
- Save (will be encrypted)

### 3. Verify Sender Email
- SendGrid requires verified sender email
- Update the `from_email` in `/api/email/send` endpoint
- Or use the free verified domain

### 4. Test Deployment
```bash
cd backend
python test_email_notifications.py
```

## Database Schema

### notifications collection
```json
{
  "notification_id": "string",
  "recipient_id": "string",
  "type": "string",
  "title": "string",
  "message": "string",
  "data": {},
  "read": boolean,
  "read_at": "ISO timestamp (optional)",
  "created_at": "ISO timestamp"
}
```

## Error Handling

### Email Sending Errors

| Error | Solution |
|-------|----------|
| `400 - SendGrid key not configured` | Add SendGrid API key in Settings |
| `500 - SendGrid SDK not installed` | Run `pip install sendgrid` |
| `500 - Invalid API key` | Verify key in SendGrid dashboard |
| `500 - Email validation failed` | Check email address format |

### Notification Errors

| Error | Solution |
|-------|----------|
| `400 - Database not available` | Ensure MongoDB is connected |
| `404 - Notification not found` | Verify notification ID |
| `500 - Database error` | Check MongoDB connection |

## Best Practices

### Design Considerations

1. **Email Templates** - Keep HTML clean and responsive
2. **Personalization** - Always include customer name when possible
3. **Frequency** - Don't overwhelm users with notifications
4. **Transactions** - Use verified sender email for SendGrid
5. **Fallbacks** - Have plan if email service is down

### Common Workflows

1. **Product Ready Flow:**
   - Generate product (AI endpoint)
   - Create database notification
   - Send email notification
   - Update dashboard

2. **Opportunity Discovery Flow:**
   - Run opportunity scout (background)
   - Get results
   - Send opportunity email
   - Create dashboard notification

3. **Revenue Updates Flow:**
   - Aggregate daily sales
   - Calculate revenue
   - Send revenue email  
   - Create notification

## Testing Email Endpoints

Test suite includes all email and notification scenarios:

```bash
cd backend
python test_email_notifications.py
```

Tests:
- Direct email sending
- Template-based emails (all templates)
- Notification creation
- Notification retrieval
- Mark as read
- Product-specific notifications

## Performance Characteristics

- **Email Send**: ~2-3 seconds (API call to SendGrid)
- **Notification Create**: <100ms (direct database insert)
- **Notification Retrieve**: <50ms (single query)
- **Template Processing**: <100ms (string rendering)

## Rate Limiting

SendGrid free tier: 100 emails/day
SendGrid Pro: Unlimited (based on plan)

Keep track of email volume in production!
