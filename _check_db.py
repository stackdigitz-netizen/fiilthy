import sys, json, os
sys.path.insert(0, 'ceo/backend')
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

try:
    from pymongo import MongoClient
    import certifi
    from config.keys_manager import keys_manager
    
    mongo_uri = os.environ.get('MONGO_URI') or os.environ.get('MONGO_URL') or keys_manager.get_key('mongodb_url')
    
    if mongo_uri:
        client = MongoClient(mongo_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        db = client['ceo_ai']
        product_count = db.products.count_documents({})
        published_count = db.products.count_documents({'status': 'published'})
        print(f'MONGO: CONNECTED')
        print(f'Total products: {product_count}')
        print(f'Published products: {published_count}')
        
        real_products = list(db.products.find(
            {'status': 'published'},
            {'title': 1, 'price': 1, 'product_type': 1, 'tags': 1}
        ).limit(5))
        for p in real_products:
            title = p.get('title', '?')
            price = p.get('price', 0)
            ptype = p.get('product_type', '?')
            print(f'  - {title} | ${price} | {ptype}')
        
        # Check collections
        collections = db.list_collection_names()
        print(f'Collections: {collections}')
        
        # Check if any orders/purchases exist
        for col_name in ['orders', 'purchases', 'transactions', 'analytics']:
            if col_name in collections:
                count = db[col_name].count_documents({})
                print(f'{col_name}: {count} documents')
    else:
        print('MONGO: NO URI FOUND')
except Exception as e:
    print(f'MONGO ERROR: {e}')
