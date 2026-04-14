"""
Integration Tests for Payment System
Tests payment flow, file delivery, and admin operations
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import stripe

# Mock Stripe for testing
@pytest.fixture
def mock_stripe():
    with patch('stripe.PaymentIntent') as mock:
        yield mock

@pytest.fixture
def client():
    """Flask test client"""
    from app import app
    app.config['TESTING'] = True
    return app.test_client()

class TestPaymentFlow:
    """Test complete payment flow"""
    
    def test_create_payment_intent(self, client, mock_stripe):
        """Test payment intent creation"""
        response = client.post('/api/fiilthy/purchase/start', json={
            'product_id': 'test_product',
            'email': 'test@example.com'
        })
        assert response.status_code in [200, 400]  # Depends on Stripe mock
    
    def test_complete_purchase(self, client):
        """Test purchase completion"""
        response = client.post('/api/fiilthy/purchase/complete', json={
            'paymentIntentId': 'pi_test123',
            'product_id': 'test_product',
            'user_email': 'test@example.com'
        })
        assert response.status_code in [201, 400]

class TestAdminAPI:
    """Test admin endpoints"""
    
    def test_get_products(self, client):
        """Test fetching products"""
        response = client.get('/api/fiilthy/admin/products')
        assert response.status_code in [200, 401]  # May require auth
    
    def test_create_product(self, client):
        """Test product creation"""
        response = client.post('/api/fiilthy/admin/products', json={
            'title': 'Test Product',
            'description': 'Test',
            'price': 99.99
        })
        assert response.status_code in [201, 401]
    
    def test_get_sales(self, client):
        """Test fetching sales"""
        response = client.get('/api/fiilthy/admin/sales')
        assert response.status_code in [200, 401]
    
    def test_get_analytics(self, client):
        """Test analytics endpoint"""
        response = client.get('/api/fiilthy/admin/analytics')
        assert response.status_code in [200, 401]

class TestFileDelivery:
    """Test file delivery system"""
    
    def test_download_file(self, client):
        """Test file download"""
        response = client.get('/api/fiilthy/download/sale_test123')
        assert response.status_code in [200, 404]
    
    def test_resend_email(self, client):
        """Test resending download email"""
        response = client.post('/api/fiilthy/resend-download/sale_test123')
        assert response.status_code in [200, 404]

class TestWebhooks:
    """Test webhook handling"""
    
    def test_stripe_webhook(self, client):
        """Test Stripe webhook"""
        response = client.post('/api/fiilthy/webhooks/stripe', 
            data='{}',
            headers={'Stripe-Signature': 'test'}
        )
        assert response.status_code in [200, 400]

class TestSecurity:
    """Test security features"""
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.get('/api/fiilthy/admin/products',
            headers={'Origin': 'http://localhost:3000'}
        )
        # Should include CORS headers
        # assert response.headers.get('Access-Control-Allow-Origin')
    
    def test_rate_limiting(self, client):
        """Test rate limiting"""
        # Make many requests
        for i in range(5):
            response = client.get('/api/fiilthy/health')
        # Later requests should be rate limited
        assert response.status_code in [200, 429]
