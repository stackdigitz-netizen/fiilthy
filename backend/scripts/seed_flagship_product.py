from datetime import datetime, timezone
from pathlib import Path
import os

from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGO_URI') or os.environ.get('MONGODB_URL')
db_name = os.environ.get('DB_NAME', 'ceo_ai')

if not mongo_url:
    raise SystemExit('Missing Mongo connection string')

client = MongoClient(mongo_url)
db = client[db_name]

now = datetime.now(timezone.utc).isoformat()
product = {
    'id': 'flagship-ai-offer-engine',
    'title': 'AI Offer Engine for Solo Operators',
    'description': 'The flagship FiiLTHY system for turning one expertise into a packaged offer, checkout flow, and repeatable AI-assisted sales engine.',
    'fullDescription': 'Build one high-value digital offer, position it clearly, price it correctly, launch it fast, and fulfill it with AI-assisted systems. This package is designed for founders, freelancers, and solo operators who need revenue fast without a bloated team.',
    'product_type': 'ebook',
    'type': 'blueprint',
    'status': 'published',
    'price': 79.0,
    'originalPrice': 149.0,
    'rating': 0,
    'reviews': 0,
    'downloads': 0,
    'cover_image': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80',
    'cover': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80',
    'includes': [
        'Offer design worksheet for high-conversion digital products',
        'AI prompt pack for positioning, headlines, and checkout copy',
        '7-day launch sprint plan',
        'Customer delivery and fulfillment checklist',
        'Post-purchase upsell and retention framework',
    ],
    'tags': ['AI', 'Offers', 'Digital Products', 'Sales', 'Solo Operator'],
    'fileSize': '14 MB',
    'updated': now[:10],
    'featured': True,
    'created_at': now,
    'updated_at': now,
    'source': 'seed_flagship_product',
}

result = db.products.update_one(
    {'id': product['id']},
    {'$set': product, '$setOnInsert': {'created_at': now}},
    upsert=True,
)

if result.upserted_id:
    print('Inserted flagship product')
else:
    print('Updated flagship product')
