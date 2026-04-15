# Store Backend

Minimal Vercel-deployable FastAPI backend for the public FiiLTHY storefront.

## Endpoints

- `GET /api/system/health`
- `GET /api/store/products`
- `POST /api/store/checkout/{product_id}`
- `POST /api/payments/webhook`
- `POST /api/store/download-link/{session_id}`
- `GET /api/store/download/{token}`

## Required environment variables

- `MONGO_URL`
- `DB_NAME`
- `STRIPE_SECRET_KEY` or `STRIPE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `FRONTEND_URL`
