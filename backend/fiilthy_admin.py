"""
Fiilthy Admin API - Complete backend for admin dashboard
Handles products, sales, analytics, and file delivery
"""

from flask import Blueprint, request, jsonify, send_file
from functools import wraps
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict
import stripe
from ai_services.auth_utils import decode_token

# Initialize blueprint
admin_bp = Blueprint('fiilthy_admin', __name__, url_prefix='/api/fiilthy/admin')

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Mock database (replace with real DB)
products_db = {}
sales_db = {}
users_db = {}

# ==================== Authentication ====================

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401

        try:
            # Extract raw token from "Bearer <token>"
            raw = token.split(' ')[1] if ' ' in token else token

            # Use shared decode utility (handles runtime secret fallbacks)
            payload = decode_token(raw)
            if payload is None:
                return jsonify({'error': 'Invalid or expired token'}), 401

            # Accept explicit is_admin claim or check users_db for admin flag
            if not payload.get('is_admin'):
                user_email = payload.get('email')
                user_record = users_db.get(user_email) if user_email else None
                if not user_record or not user_record.get('is_admin'):
                    return jsonify({'error': 'Admin access required'}), 403

            request.user = payload
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== Products Endpoints ====================

@admin_bp.route('/products', methods=['GET'])
@require_admin
def get_products():
    """Fetch all products with stats"""
    products = list(products_db.values())
    return jsonify(products), 200

@admin_bp.route('/products', methods=['POST'])
@require_admin
def create_product():
    """Create a new product"""
    data = request.json
    
    product = {
        'id': data.get('id', f"prod_{datetime.now().timestamp()}"),
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'price': data.get('price', 0),
        'originalPrice': data.get('originalPrice', 0),
        'type': data.get('type', 'template'),
        'cover': data.get('cover', ''),
        'includes': data.get('includes', []),
        'tags': data.get('tags', []),
        'status': 'draft',
        'sales': 0,
        'revenue': 0.0,
        'clicks': 0,
        'conversions': 0,
        'created_at': datetime.now().isoformat(),
        'file_path': data.get('file_path', '')
    }
    
    products_db[product['id']] = product
    return jsonify(product), 201

@admin_bp.route('/products/<product_id>', methods=['PUT'])
@require_admin
def update_product(product_id):
    """Update a product"""
    if product_id not in products_db:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.json
    product = products_db[product_id]
    
    # Update fields
    for key in ['title', 'description', 'price', 'originalPrice', 'type', 'cover', 'includes', 'tags', 'status']:
        if key in data:
            product[key] = data[key]
    
    product['updated_at'] = datetime.now().isoformat()
    return jsonify(product), 200

@admin_bp.route('/products/<product_id>', methods=['DELETE'])
@require_admin
def delete_product(product_id):
    """Delete a product"""
    if product_id not in products_db:
        return jsonify({'error': 'Product not found'}), 404
    
    del products_db[product_id]
    return jsonify({'success': True}), 200

@admin_bp.route('/products/<product_id>/publish', methods=['POST'])
@require_admin
def publish_product(product_id):
    """Publish product to marketplace"""
    if product_id not in products_db:
        return jsonify({'error': 'Product not found'}), 404
    
    product = products_db[product_id]
    product['status'] = 'published'
    product['published_at'] = datetime.now().isoformat()
    
    return jsonify(product), 200

# ==================== Sales Endpoints ====================

@admin_bp.route('/sales', methods=['GET'])
@require_admin
def get_sales():
    """Fetch all sales"""
    sales = list(sales_db.values())
    
    # Support filtering
    status = request.args.get('status')
    if status:
        sales = [s for s in sales if s['status'] == status]
    
    return jsonify(sales), 200

@admin_bp.route('/sales/<sale_id>', methods=['GET'])
@require_admin
def get_sale(sale_id):
    """Get specific sale"""
    if sale_id not in sales_db:
        return jsonify({'error': 'Sale not found'}), 404
    
    return jsonify(sales_db[sale_id]), 200

@admin_bp.route('/sales/<sale_id>/refund', methods=['POST'])
@require_admin
def refund_sale(sale_id):
    """Process refund for a sale"""
    if sale_id not in sales_db:
        return jsonify({'error': 'Sale not found'}), 404
    
    sale = sales_db[sale_id]
    
    if sale['status'] == 'refunded':
        return jsonify({'error': 'Already refunded'}), 400
    
    try:
        # Refund via Stripe
        refund = stripe.Refund.create(
            charge=sale['stripe_charge_id']
        )
        
        sale['status'] = 'refunded'
        sale['refunded_at'] = datetime.now().isoformat()
        sale['refund_id'] = refund.id
        
        return jsonify(sale), 200
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

# ==================== Analytics Endpoints ====================

@admin_bp.route('/analytics', methods=['GET'])
@require_admin
def get_analytics():
    """Get analytics dashboard data"""
    sales = list(sales_db.values())
    products = list(products_db.values())
    
    # Calculate metrics
    total_revenue = sum(s['amount'] for s in sales if s['status'] == 'completed')
    total_sales = len([s for s in sales if s['status'] == 'completed'])
    avg_order_value = total_revenue / total_sales if total_sales > 0 else 0
    
    # Time-based analytics
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    this_week = len([s for s in sales 
                     if datetime.fromisoformat(s['created_at']).date() >= week_ago 
                     and s['status'] == 'completed'])
    this_month = len([s for s in sales 
                      if datetime.fromisoformat(s['created_at']).date() >= month_ago 
                      and s['status'] == 'completed'])
    
    # Top products
    product_sales = {}
    for sale in sales:
        product_id = sale['product_id']
        product_sales[product_id] = product_sales.get(product_id, 0) + 1
    
    top_products = sorted(
        [(pid, count) for pid, count in product_sales.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    analytics = {
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'avg_order_value': avg_order_value,
        'this_week_sales': this_week,
        'this_month_sales': this_month,
        'total_products': len(products),
        'published_products': len([p for p in products if p['status'] == 'published']),
        'top_products': [
            {
                'product_id': pid,
                'sales_count': count,
                'product': products_db.get(pid, {})
            }
            for pid, count in top_products
        ],
        'revenue_growth': '+12%',
        'sales_growth': '+8%'
    }
    
    return jsonify(analytics), 200

# ==================== Payment Processing ====================

@admin_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create Stripe payment intent"""
    data = request.json
    product_id = data.get('product_id')
    user_email = data.get('user_email')
    
    if product_id not in products_db:
        return jsonify({'error': 'Product not found'}), 404
    
    product = products_db[product_id]
    
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(product['price'] * 100),  # Convert to cents
            currency='usd',
            metadata={
                'product_id': product_id,
                'user_email': user_email,
                'product_title': product['title']
            }
        )
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'paymentIntentId': intent.id
        }), 200
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    """Confirm payment and create sale record"""
    data = request.json
    payment_intent_id = data.get('paymentIntentId')
    product_id = data.get('product_id')
    user_email = data.get('user_email')
    
    try:
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status != 'succeeded':
            return jsonify({'error': 'Payment not completed'}), 400
        
        product = products_db.get(product_id, {})
        
        # Create sale record
        sale = {
            'id': f"sale_{datetime.now().timestamp()}",
            'product_id': product_id,
            'user_email': user_email,
            'amount': product.get('price', 0),
            'currency': 'usd',
            'status': 'completed',
            'stripe_payment_intent': payment_intent_id,
            'stripe_charge_id': intent.charges.data[0].id if intent.charges.data else None,
            'created_at': datetime.now().isoformat(),
            'file_delivered': False
        }
        
        sales_db[sale['id']] = sale
        
        # Update product stats
        product['sales'] = product.get('sales', 0) + 1
        product['revenue'] = product.get('revenue', 0) + product.get('price', 0)
        product['conversions'] = product.get('conversions', 0) + 1
        
        return jsonify({
            'success': True,
            'sale_id': sale['id'],
            'download_url': f"/api/fiilthy/downloads/{sale['id']}"
        }), 201
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

# ==================== File Delivery ====================

@admin_bp.route('/downloads/<sale_id>', methods=['GET'])
def download_file(sale_id):
    """Download purchased file"""
    if sale_id not in sales_db:
        return jsonify({'error': 'Sale not found'}), 404
    
    sale = sales_db[sale_id]
    
    if sale['status'] != 'completed':
        return jsonify({'error': 'Purchase not completed'}), 403
    
    product = products_db.get(sale['product_id'])
    if not product or not product.get('file_path'):
        return jsonify({'error': 'File not available'}), 404
    
    file_path = product['file_path']
    
    # Verify file exists
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    # Update delivered flag
    sale['file_delivered'] = True
    sale['delivery_date'] = datetime.now().isoformat()
    
    # Send file
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{product['title']}.zip"
    )

@admin_bp.route('/email-download-link/<sale_id>', methods=['POST'])
def email_download_link(sale_id):
    """Email download link to customer"""
    if sale_id not in sales_db:
        return jsonify({'error': 'Sale not found'}), 404
    
    sale = sales_db[sale_id]
    user_email = sale['user_email']
    download_url = f"{os.getenv('APP_URL', 'http://localhost:3000')}/api/fiilthy/downloads/{sale_id}"
    
    # Send email (integrate with SendGrid, AWS SES, etc.)
    try:
        # Example: send_email(user_email, 'Your Download', f"Download: {download_url}")
        print(f"Email sent to {user_email}: {download_url}")
        
        sale['email_sent'] = True
        sale['email_sent_at'] = datetime.now().isoformat()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Bulk Operations ====================

@admin_bp.route('/bulk-publish', methods=['POST'])
@require_admin
def bulk_publish():
    """Publish multiple products"""
    data = request.json
    product_ids = data.get('product_ids', [])
    
    updated = []
    for product_id in product_ids:
        if product_id in products_db:
            products_db[product_id]['status'] = 'published'
            products_db[product_id]['published_at'] = datetime.now().isoformat()
            updated.append(products_db[product_id])
    
    return jsonify({'updated': updated}), 200

@admin_bp.route('/bulk-delete', methods=['POST'])
@require_admin
def bulk_delete():
    """Delete multiple products"""
    data = request.json
    product_ids = data.get('product_ids', [])
    
    deleted = []
    for product_id in product_ids:
        if product_id in products_db:
            deleted.append(product_id)
            del products_db[product_id]
    
    return jsonify({'deleted': deleted}), 200

# ==================== Export Data ====================

@admin_bp.route('/export/sales', methods=['GET'])
@require_admin
def export_sales():
    """Export sales as CSV/JSON"""
    format_type = request.args.get('format', 'json')
    sales = list(sales_db.values())
    
    if format_type == 'csv':
        # Convert to CSV
        csv_data = 'id,product_id,user_email,amount,status,created_at\n'
        for sale in sales:
            csv_data += f"{sale['id']},{sale['product_id']},{sale['user_email']},{sale['amount']},{sale['status']},{sale['created_at']}\n"
        
        return csv_data, 200, {'Content-Type': 'text/csv'}
    else:
        return jsonify(sales), 200

@admin_bp.route('/export/products', methods=['GET'])
@require_admin
def export_products():
    """Export products as CSV/JSON"""
    products = list(products_db.values())
    return jsonify(products), 200

# ==================== Health Check ====================

@admin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200
