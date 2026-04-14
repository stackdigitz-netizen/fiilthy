"""
Fiilthy Backend Server - Main application entry point
Integrates admin, payments, and file delivery
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Import blueprints and services
from fiilthy_admin import admin_bp
from payment_processor import StripePaymentProcessor, PaymentReconciliation
from file_delivery import FileDeliveryManager, EmailNotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Security
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", os.getenv("FRONTEND_URL", "")]}})
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize services
file_delivery = FileDeliveryManager()
email_service = EmailNotificationService()

# Register blueprints
app.register_blueprint(admin_bp)

# ============== PURCHASE FLOW ==============

@app.route('/api/fiilthy/purchase/start', methods=['POST'])
def start_purchase():
    """Start purchase process - create payment intent"""
    try:
        data = request.json
        customer_email = data.get('email')
        product_id = data.get('product_id')
        
        # Create Stripe payment
        payment_data = StripePaymentProcessor.create_payment_intent(product_id, customer_email)
        
        return jsonify(payment_data), 200
    
    except Exception as e:
        logger.error(f"Purchase start error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/fiilthy/purchase/complete', methods=['POST'])
def complete_purchase():
    """Complete purchase and trigger delivery"""
    try:
        from fiilthy_admin import sales_db, products_db
        
        data = request.json
        payment_intent_id = data.get('paymentIntentId')
        product_id = data.get('product_id')
        user_email = data.get('user_email')
        
        # Verify payment with Stripe
        from payment_processor import StripePaymentProcessor
        payment_status = StripePaymentProcessor.get_payment_status(payment_intent_id)
        
        if payment_status['status'] != 'succeeded':
            return jsonify({'error': 'Payment not completed'}), 400
        
        product = products_db.get(product_id, {})
        
        # Create sale record
        sale_id = f"sale_{datetime.now().timestamp()}"
        sale = {
            'id': sale_id,
            'product_id': product_id,
            'user_email': user_email,
            'amount': product.get('price', 0),
            'status': 'completed',
            'payment_intent_id': payment_intent_id,
            'created_at': datetime.now().isoformat()
        }
        sales_db[sale_id] = sale
        
        # Update product stats
        product['sales'] = product.get('sales', 0) + 1
        product['revenue'] = product.get('revenue', 0) + product.get('price', 0)
        
        # Generate download link
        download_link = file_delivery.generate_download_link(sale_id, product_id)
        
        # Send confirmation email
        email_service.send_purchase_confirmation(
            user_email,
            product['title'],
            product.get('price', 0),
            download_link
        )
        
        # Log delivery
        file_delivery.log_delivery(sale_id, product_id, user_email, 'email_sent')
        
        return jsonify({
            'success': True,
            'sale_id': sale_id,
            'download_url': download_link
        }), 201
    
    except Exception as e:
        logger.error(f"Purchase completion error: {e}")
        return jsonify({'error': str(e)}), 400

# ============== STRIPE WEBHOOKS ==============

@app.route('/api/fiilthy/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        sig_header = request.headers.get('Stripe-Signature')
        webhook_result = StripePaymentProcessor.process_webhook(
            request.data,
            sig_header
        )
        
        logger.info(f"Webhook processed: {webhook_result['status']}")
        return jsonify({'received': True}), 200
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400

# ============== DOWNLOAD ENDPOINTS ==============

@app.route('/api/fiilthy/download/<sale_id>', methods=['GET'])
def download_product(sale_id):
    """Download purchased product"""
    try:
        from fiilthy_admin import sales_db, products_db
        
        token = request.args.get('token')
        
        if sale_id not in sales_db:
            return jsonify({'error': 'Sale not found'}), 404
        
        sale = sales_db[sale_id]
        product = products_db.get(sale['product_id'])
        
        if not product or sale['status'] != 'completed':
            return jsonify({'error': 'File not available'}), 403
        
        # Create package if not exists
        package_path = file_delivery.create_delivery_package(sale['product_id'], product)
        
        # Log download
        file_delivery.log_delivery(sale_id, sale['product_id'], sale['user_email'], 'downloaded')
        
        return send_file(
            package_path,
            as_attachment=True,
            download_name=f"{product['title']}.zip"
        )
    
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 400

# ============== RESEND EMAIL ==============

@app.route('/api/fiilthy/resend-download/<sale_id>', methods=['POST'])
def resend_download_email(sale_id):
    """Resend download email"""
    try:
        from fiilthy_admin import sales_db, products_db
        
        if sale_id not in sales_db:
            return jsonify({'error': 'Sale not found'}), 404
        
        sale = sales_db[sale_id]
        product = products_db.get(sale['product_id'])
        download_link = file_delivery.generate_download_link(sale_id, sale['product_id'])
        
        email_service.send_download_reminder(
            sale['user_email'],
            product['title'],
            download_link
        )
        
        file_delivery.log_delivery(sale_id, sale['product_id'], sale['user_email'], 'email_resent')
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        logger.error(f"Resend email error: {e}")
        return jsonify({'error': str(e)}), 400

# ============== REPORTING ==============

@app.route('/api/fiilthy/admin/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get complete dashboard data"""
    try:
        from fiilthy_admin import sales_db, products_db
        
        sales = list(sales_db.values())
        products = list(products_db.values())
        
        total_revenue = sum(s['amount'] for s in sales if s['status'] == 'completed')
        
        reconciliation = PaymentReconciliation.reconcile_balance()
        
        return jsonify({
            'products': products,
            'sales': sales,
            'total_revenue': total_revenue,
            'stripe_balance': reconciliation,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': str(e)}), 400

# ============== HEALTH CHECK ==============

@app.route('/api/fiilthy/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'environment': {
            'stripe_configured': bool(os.getenv('STRIPE_SECRET_KEY')),
            's3_configured': os.getenv('USE_S3') == 'true',
            'email_configured': bool(os.getenv('EMAIL_PASSWORD'))
        }
    }), 200

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

# ============== RUN APPLICATION ==============

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Fiilthy server on port {port}")
    logger.info(f"Environment: {'Development' if debug else 'Production'}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False
    )
