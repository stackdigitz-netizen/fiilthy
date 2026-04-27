"""
Real Payment Processing with Stripe
Handles complete payment lifecycle, webhooks, and reconciliation
"""

import stripe
import os
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

class StripePaymentProcessor:
    """Handle all Stripe payment operations"""
    
    @staticmethod
    def create_customer(email: str, name: str = None) -> str:
        """Create Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name or email,
                description=f"Fiilthy customer - {email}"
            )
            logger.info(f"Customer created: {customer.id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Error creating customer: {e}")
            raise

    @staticmethod
    def create_product(title: str, description: str, price: float) -> dict:
        """Create Stripe product and price"""
        try:
            # Create product
            product = stripe.Product.create(
                name=title,
                description=description,
                type='digital'
            )
            
            # Create price
            price_obj = stripe.Price.create(
                product=product.id,
                unit_amount=int(price * 100),  # Convert to cents
                currency='usd'
            )
            
            logger.info(f"Product created: {product.id}")
            
            return {
                'product_id': product.id,
                'price_id': price_obj.id,
                'amount': int(price * 100)
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error creating product: {e}")
            raise

    @staticmethod
    def create_checkout_session(price_id: str, customer_id: str, success_url: str, cancel_url: str) -> str:
        """Create Stripe checkout session"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
            )
            logger.info(f"Checkout session created: {session.id}")
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout: {e}")
            raise

    @staticmethod
    def create_subscription(price_id: str, customer_id: str) -> str:
        """Create recurring subscription"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {'price': price_id},
                ],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )
            logger.info(f"Subscription created: {subscription.id}")
            return subscription.id
        except stripe.error.StripeError as e:
            logger.error(f"Error creating subscription: {e}")
            raise

    @staticmethod
    def process_webhook(request_body: bytes, sig_header: str) -> dict:
        """Process Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(
                request_body, sig_header, STRIPE_WEBHOOK_SECRET
            )
            logger.info(f"Webhook received: {event['type']}")
            
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                logger.info(f"Payment succeeded: {payment_intent['id']}")
                return {'status': 'success', 'payment_intent': payment_intent}
            
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                logger.warning(f"Payment failed: {payment_intent['id']}")
                return {'status': 'failed', 'payment_intent': payment_intent}
            
            elif event['type'] == 'charge.refunded':
                charge = event['data']['object']
                logger.info(f"Charge refunded: {charge['id']}")
                return {'status': 'refunded', 'charge': charge}
            
            elif event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                logger.info(f"Subscription updated: {subscription['id']}")
                return {'status': 'subscription_updated', 'subscription': subscription}
            
            elif event['type'] == 'invoice.payment_succeeded':
                invoice = event['data']['object']
                logger.info(f"Invoice paid: {invoice['id']}")
                return {'status': 'invoice_paid', 'invoice': invoice}
            
            return {'status': 'unhandled', 'type': event['type']}
        
        except ValueError as e:
            logger.error(f"Webhook error: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Signature verification failed: {e}")
            raise

    @staticmethod
    def refund_payment(charge_id: str, amount: int = None) -> dict:
        """Refund a charge"""
        try:
            refund = stripe.Refund.create(
                charge=charge_id,
                amount=amount  # Optional: partial refund
            )
            logger.info(f"Refund created: {refund.id}")
            return {'refund_id': refund.id, 'status': refund.status}
        except stripe.error.StripeError as e:
            logger.error(f"Refund error: {e}")
            raise

    @staticmethod
    def get_payment_status(payment_intent_id: str) -> dict:
        """Get payment status"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'status': payment_intent.status,
                'amount': payment_intent.amount,
                'charges': [
                    {
                        'id': charge.id,
                        'amount': charge.amount,
                        'status': charge.status
                    }
                    for charge in payment_intent.charges.data
                ]
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving payment: {e}")
            raise

    @staticmethod
    def list_transactions(customer_id: str = None, limit: int = 10) -> list:
        """List customer transactions"""
        try:
            if customer_id:
                charges = stripe.Charge.list(customer=customer_id, limit=limit)
            else:
                charges = stripe.Charge.list(limit=limit)
            
            return [
                {
                    'id': charge.id,
                    'customer': charge.customer,
                    'amount': charge.amount,
                    'currency': charge.currency,
                    'status': charge.status,
                    'created': datetime.fromtimestamp(charge.created).isoformat()
                }
                for charge in charges.data
            ]
        except stripe.error.StripeError as e:
            logger.error(f"Error listing transactions: {e}")
            raise

class PaymentReconciliation:
    """Handle payment reconciliation and reconciliation"""
    
    @staticmethod
    def reconcile_balance() -> dict:
        """Reconcile account balance"""
        try:
            balance = stripe.Balance.retrieve()
            
            return {
                'available': [
                    {
                        'amount': amt['amount'],
                        'currency': amt['currency']
                    }
                    for amt in balance.available
                ],
                'pending': [
                    {
                        'amount': amt['amount'],
                        'currency': amt['currency']
                    }
                    for amt in balance.pending
                ]
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving balance: {e}")
            raise

    @staticmethod
    def get_recent_disputes() -> list:
        """Get recent disputes"""
        try:
            disputes = stripe.Dispute.list(limit=10)
            
            return [
                {
                    'id': dispute.id,
                    'amount': dispute.amount,
                    'reason': dispute.reason,
                    'status': dispute.status,
                    'created': datetime.fromtimestamp(dispute.created).isoformat()
                }
                for dispute in disputes.data
            ]
        except stripe.error.StripeError as e:
            logger.error(f"Error listing disputes: {e}")
            raise

    @staticmethod
    def generate_payout_report() -> dict:
        """Generate payout report"""
        try:
            payouts = stripe.Payout.list(limit=30, status='paid')
            
            total_amount = sum(p.amount for p in payouts.data)
            
            return {
                'total_payouts': len(payouts.data),
                'total_amount': total_amount,
                'payouts': [
                    {
                        'id': payout.id,
                        'amount': payout.amount,
                        'arrival_date': datetime.fromtimestamp(payout.arrival_date).isoformat() if payout.arrival_date else None,
                        'status': payout.status
                    }
                    for payout in payouts.data
                ]
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error generating report: {e}")
            raise
