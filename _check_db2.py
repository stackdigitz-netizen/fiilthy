import json, os, sys
sys.path.insert(0, 'ceo/backend')

from config.runtime_secrets import RuntimeSecrets
rs = RuntimeSecrets()
mk = rs.get_secret('MASTER_KEY')
print(f'MASTER_KEY available: {bool(mk)}')
print(f'MASTER_KEY length: {len(str(mk)) if mk else 0}')

if mk:
    from cryptography.fernet import Fernet
    try:
        key = mk.encode() if isinstance(mk, str) else mk
        f = Fernet(key)
        with open('ceo/backend/config/.secure_keys.json') as fh:
            data = json.load(fh)
        decrypted = f.decrypt(data['mongodb_url'].encode()).decode()
        print('Decryption: SUCCESS')
        is_mongo = decrypted.startswith('mongodb')
        print(f'URI starts with mongodb: {is_mongo}')
        
        # Now actually connect
        from pymongo import MongoClient
        import certifi
        client = MongoClient(decrypted, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        db = client['ceo_ai']
        product_count = db.products.count_documents({})
        published_count = db.products.count_documents({'status': 'published'})
        print(f'MONGO: CONNECTED')
        print(f'Total products: {product_count}')
        print(f'Published products: {published_count}')
        
        real_products = list(db.products.find(
            {'status': 'published'},
            {'title': 1, 'price': 1, 'product_type': 1}
        ).limit(5))
        for p in real_products:
            title = p.get('title', '?')
            price = p.get('price', 0)
            ptype = p.get('product_type', '?')
            print(f'  - {title} | ${price} | {ptype}')
        
        collections = db.list_collection_names()
        print(f'Collections: {collections}')
        
        for col_name in ['orders', 'purchases', 'transactions', 'analytics', 'tiktok_posts', 'campaigns']:
            if col_name in collections:
                count = db[col_name].count_documents({})
                print(f'{col_name}: {count} documents')
                
    except Exception as e:
        print(f'Error: {e}')
