import io
import json
import os
import secrets
import zipfile
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

import stripe
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pymongo import DESCENDING, MongoClient

app = FastAPI(title='FiiLTHY Store API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

SAMPLE_PRODUCTS: List[Dict[str, Any]] = [
    {
        'id': 'flagship-ai-offer-engine',
        'title': 'AI Offer Engine for Solo Operators',
        'description': 'Turn one skill into a premium digital offer, a fast checkout flow, and an AI-assisted sales engine you can run without a team.',
        'price': 79.0,
        'originalPrice': 149.0,
        'type': 'blueprint',
        'cover': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=600&q=80',
        'rating': 4.9,
        'reviews': 0,
        'downloads': 0,
        'includes': [
            'High-ticket offer design worksheet',
            'AI prompts for positioning and sales copy',
            '7-day launch sprint plan',
            'Delivery and fulfillment checklist',
            'Upsell and retention framework',
        ],
        'tags': ['AI', 'Offers', 'Sales', 'Solo Operator'],
        'fileSize': '14 MB',
        'updated': '2026-04-14',
        'product_type': 'ebook',
        'status': 'published',
        'featured': True,
    },
    {
        'id': 'fiilthy-002',
        'title': 'Digital Product Launch Playbook',
        'description': 'Launch profitable digital products in 7 days with AI. The exact playbook used to generate faster launches without a bloated team.',
        'price': 49.0,
        'originalPrice': 99.0,
        'type': 'template',
        'cover': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80',
        'rating': 4.8,
        'reviews': 0,
        'downloads': 0,
        'includes': [
            '127-point launch checklist',
            '5-part email funnel sequences',
            '40+ social media templates',
            'Pricing and positioning guide',
            'Competitor research framework',
        ],
        'tags': ['Digital Products', 'Launch', 'Marketing'],
        'fileSize': '12 MB',
        'updated': '2026-04-14',
        'product_type': 'template',
        'status': 'published',
    },
]


class CheckoutRequest(BaseModel):
    customer_email: str
    quantity: int = 1
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class DownloadLinkRequest(BaseModel):
    email: str


@lru_cache(maxsize=1)
def get_db():
    mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGO_URI') or os.environ.get('MONGODB_URL')
    if not mongo_url:
        raise RuntimeError('Missing Mongo connection string')
    client = MongoClient(mongo_url)
    return client[os.environ.get('DB_NAME', 'ceo_ai')]


@lru_cache(maxsize=1)
def get_stripe_key() -> str:
    stripe_key = os.environ.get('STRIPE_SECRET_KEY') or os.environ.get('STRIPE_KEY')
    if not stripe_key:
        raise RuntimeError('Missing Stripe secret key')
    return stripe_key


def public_product(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'id': doc.get('id'),
        'title': doc.get('title', ''),
        'description': doc.get('description', ''),
        'price': float(doc.get('price', 29.99)),
        'originalPrice': float(doc.get('originalPrice') or doc.get('price', 29.99)),
        'type': doc.get('product_type') or doc.get('type') or 'ebook',
        'cover': doc.get('cover_image') or doc.get('image_url') or doc.get('cover') or 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80',
        'rating': float(doc.get('rating', 4.8)),
        'reviews': int(doc.get('reviews', 0)),
        'downloads': int(doc.get('downloads', 0)),
        'conversions': int(doc.get('conversions', 0)),
        'includes': doc.get('includes') or doc.get('features') or [],
        'tags': doc.get('tags') or doc.get('keywords') or [],
        'fileSize': doc.get('fileSize', '5 MB'),
        'updated': str(doc.get('updated') or doc.get('created_at', ''))[:10],
        'status': doc.get('status'),
        'featured': bool(doc.get('featured')),
        'launch_score': float(doc.get('launch_score') or 0),
        'revenue': float(doc.get('revenue') or 0),
    }


def store_sort_key(product: Dict[str, Any]):
    return (
        1 if product.get('featured') else 0,
        float(product.get('launch_score') or 0),
        float(product.get('revenue') or 0),
        int(product.get('conversions') or product.get('downloads') or 0),
        str(product.get('updated') or ''),
    )


def lookup_product(product_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    product = db.products.find_one({'id': product_id}, {'_id': 0})
    if product:
        return product
    for sample in SAMPLE_PRODUCTS:
        if sample['id'] == product_id:
            return dict(sample)
    return None


def generate_product_content(product: Dict[str, Any]) -> str:
    title = product.get('title', 'Digital Product')
    description = product.get('description', '')
    includes = product.get('includes') or product.get('features') or []
    tags = product.get('tags') or product.get('keywords') or []
    includes_block = '\n'.join(f'- {item}' for item in includes) if includes else '- Complete digital product package'

    return f"""# {title}

## What This Helps You Do

{description}

## Included

{includes_block}

## 7-Day Execution Plan

Day 1: Choose the exact buyer and outcome.
Day 2: Refine the promise and pricing.
Day 3: Build the core delivery asset.
Day 4: Write the sales copy and offer bullets.
Day 5: Set up checkout and delivery.
Day 6: Launch with one clear call to action.
Day 7: Review buyer questions and tighten conversion.

## Positioning Angles

- Faster implementation with fewer moving parts
- Clear transformation instead of generic information
- Built for solo operators who need revenue without overhead

## Core Topics

{', '.join(tags) if tags else 'AI, offers, digital products'}

## Support

Email support@fiilthy.ai if you need help accessing the product.
""".strip()


@app.get('/api/system/health')
def health():
    return {'status': 'ok', 'service': 'store-backend', 'time': datetime.now(timezone.utc).isoformat()}


@app.get('/api/store/products')
def get_store_products(limit: int = 50):
    try:
        db = get_db()
        products = list(
            db.products.find({'status': {'$in': ['published', 'ready', 'approved']}}, {'_id': 0}).sort('created_at', DESCENDING).limit(limit)
        )
        result = sorted([public_product(product) for product in products], key=store_sort_key, reverse=True)
        featured_samples = [
            product for product in SAMPLE_PRODUCTS
            if product.get('featured') and not any(existing.get('id') == product.get('id') for existing in result)
        ]
        if result:
            return (featured_samples + result)[:limit]
    except Exception:
        pass
    return SAMPLE_PRODUCTS[:limit]


@app.post('/api/store/checkout/{product_id}')
def create_checkout(product_id: str, body: CheckoutRequest):
    product = lookup_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    stripe.api_key = get_stripe_key()
    frontend_url = os.environ.get('FRONTEND_URL', 'https://frontend-one-ashen-16.vercel.app')
    price_cents = int(float(product.get('price', 29.99)) * 100)
    cover = product.get('cover_image') or product.get('image_url') or product.get('cover') or ''
    images = [cover] if isinstance(cover, str) and cover.startswith('https://') else []

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product['title'],
                    'description': str(product.get('description', ''))[:500],
                    'images': images,
                },
                'unit_amount': price_cents,
            },
            'quantity': body.quantity,
        }],
        mode='payment',
        customer_email=body.customer_email,
        success_url=body.success_url or f"{frontend_url}/store?success=1&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=body.cancel_url or f'{frontend_url}/store',
        metadata={
            'product_id': product_id,
            'customer_email': body.customer_email,
            'store': 'fiilthy',
        },
    )

    db = get_db()
    db.payments.insert_one({
        'payment_id': secrets.token_hex(16),
        'product_id': product_id,
        'customer_email': body.customer_email,
        'amount_cents': price_cents * body.quantity,
        'currency': 'usd',
        'status': 'pending',
        'stripe_session_id': session.id,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'source': 'store-backend',
    })

    return {'checkout_url': session.url, 'session_id': session.id}


@app.post('/api/payments/webhook')
async def handle_webhook(request: Request):
    stripe.api_key = get_stripe_key()
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    if not webhook_secret:
        raise HTTPException(status_code=500, detail='Stripe webhook secret not configured')

    payload = await request.body()
    signature = request.headers.get('stripe-signature')
    if not signature:
        raise HTTPException(status_code=400, detail='Missing Stripe signature header')

    try:
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f'Invalid payload: {exc}')
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail='Invalid Stripe signature')

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        customer_email = session.get('customer_email')
        metadata = session.get('metadata', {})
        product_id = metadata.get('product_id')
        completed_at = datetime.now(timezone.utc).isoformat()
        amount = float(session.get('amount_total', 0)) / 100
        db = get_db()
        db.payments.update_one(
            {'stripe_session_id': session_id},
            {'$set': {'status': 'succeeded', 'completed_at': completed_at}},
        )
        db.downloads.update_one(
            {'stripe_session_id': session_id},
            {'$set': {
                'token': secrets.token_urlsafe(32),
                'product_id': product_id,
                'email': customer_email,
                'stripe_session_id': session_id,
                'created_at': completed_at,
                'expires_at': (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                'download_count': 0,
            }},
            upsert=True,
        )
        db.sales.update_one(
            {'stripe_session_id': session_id},
            {'$set': {
                'sale_id': secrets.token_hex(16),
                'product_id': product_id,
                'customer_email': customer_email,
                'amount': amount,
                'status': 'completed',
                'source': 'store-backend',
                'created_at': completed_at,
                'stripe_session_id': session_id,
            }},
            upsert=True,
        )
        if product_id:
            db.products.update_one(
                {'id': product_id},
                {'$inc': {'conversions': 1, 'revenue': amount}},
            )

    return {'status': 'received'}


@app.post('/api/store/download-link/{session_id}')
def get_download_link(session_id: str, body: DownloadLinkRequest, request: Request):
    db = get_db()
    record = db.downloads.find_one({'stripe_session_id': session_id})
    if not record:
        raise HTTPException(status_code=404, detail='Your download is not ready yet. Refresh this page in a few seconds.')

    request_email = body.email.lower().strip()
    record_email = str(record.get('email', '')).lower().strip()
    if not request_email:
        raise HTTPException(status_code=400, detail='Email is required')
    if record_email and record_email != request_email:
        raise HTTPException(status_code=403, detail='Email does not match this order')

    product = lookup_product(record.get('product_id')) or {}
    base_url = str(request.base_url).rstrip('/')
    return {
        'success': True,
        'product_title': product.get('title', 'Your Product'),
        'download_url': f"{base_url}/api/store/download/{record['token']}",
        'expires_at': record.get('expires_at'),
    }


@app.get('/api/store/download/{token}')
def download_product(token: str):
    db = get_db()
    record = db.downloads.find_one({'token': token})
    if not record:
        raise HTTPException(status_code=404, detail='Download link not found')

    expires_at = record.get('expires_at')
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
    if isinstance(expires_at, datetime) and datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=410, detail='This download link has expired')

    product = lookup_product(record.get('product_id'))
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    safe_title = ''.join(char if char.isalnum() or char in (' ', '-', '_') else '' for char in product.get('title', 'product')).strip().replace(' ', '_')
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f'{safe_title}.md', generate_product_content(product))
        archive.writestr('order_info.json', json.dumps({
            'product_id': record.get('product_id'),
            'title': product.get('title'),
            'customer_email': record.get('email'),
            'purchased_at': record.get('created_at'),
        }, indent=2))
    zip_buffer.seek(0)

    db.downloads.update_one(
        {'token': token},
        {'$inc': {'download_count': 1}, '$set': {'last_downloaded': datetime.now(timezone.utc).isoformat()}},
    )

    return StreamingResponse(
        zip_buffer,
        media_type='application/zip',
        headers={'Content-Disposition': f'attachment; filename="{safe_title}.zip"'},
    )
