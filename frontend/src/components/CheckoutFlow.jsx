import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/js';
import { CardElement, Elements, useStripe, useElements } from '@stripe/react-stripe-js';
import { ShoppingCart, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import './CheckoutFlow.css';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);

/**
 * CheckoutFlow - Complete purchase workflow
 * Handles payment processing and file delivery
 */
export const CheckoutFlow = ({ product, onClose, onSuccess }) => {
  const [step, setStep] = useState('confirm'); // confirm -> payment -> processing -> success
  const [customerEmail, setCustomerEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paymentIntent, setPaymentIntent] = useState(null);

  const handleStartPayment = async () => {
    if (!customerEmail) {
      setError('Please enter your email');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create payment intent
      const res = await fetch('/api/fiilthy/purchase/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: product.id,
          email: customerEmail
        })
      });

      if (!res.ok) throw new Error('Failed to start payment');

      const data = await res.json();
      setPaymentIntent(data);
      setStep('payment');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout-modal">
      <Elements stripe={stripePromise}>
        <CheckoutContent
          product={product}
          step={step}
          setStep={setStep}
          customerEmail={customerEmail}
          setCustomerEmail={setCustomerEmail}
          paymentIntent={paymentIntent}
          loading={loading}
          error={error}
          setError={setError}
          onStartPayment={handleStartPayment}
          onClose={onClose}
          onSuccess={onSuccess}
        />
      </Elements>
    </div>
  );
};

const CheckoutContent = ({
  product,
  step,
  setStep,
  customerEmail,
  setCustomerEmail,
  paymentIntent,
  loading,
  error,
  setError,
  onStartPayment,
  onClose,
  onSuccess
}) => {
  return (
    <div className="checkout-container">
      {/* Header */}
      <button className="checkout-close" onClick={onClose}>✕</button>

      <div className="checkout-header">
        <ShoppingCart size={28} />
        <h1>Complete Your Purchase</h1>
      </div>

      {/* Steps Indicator */}
      <div className="checkout-steps">
        <div className={`step ${step === 'confirm' || ['payment', 'processing', 'success'].includes(step) ? 'active' : ''}`}>
          <span>1</span> Confirm
        </div>
        <div className={`step ${step === 'payment' || ['processing', 'success'].includes(step) ? 'active' : ''}`}>
          <span>2</span> Payment
        </div>
        <div className={`step ${['processing', 'success'].includes(step) ? 'active' : ''}`}>
          <span>3</span> Process
        </div>
        <div className={`step ${step === 'success' ? 'active' : ''}`}>
          <span>4</span> Download
        </div>
      </div>

      {/* Content */}
      <div className="checkout-content">
        {step === 'confirm' && (
          <ConfirmStep
            product={product}
            customerEmail={customerEmail}
            setCustomerEmail={setCustomerEmail}
            loading={loading}
            error={error}
            onNext={onStartPayment}
            onCancel={onClose}
          />
        )}

        {step === 'payment' && paymentIntent && (
          <PaymentStep
            product={product}
            paymentIntent={paymentIntent}
            customerEmail={customerEmail}
            setStep={setStep}
            setError={setError}
            onSuccess={onSuccess}
          />
        )}

        {step === 'processing' && (
          <ProcessingStep />
        )}

        {step === 'success' && (
          <SuccessStep product={product} onClose={onClose} />
        )}
      </div>
    </div>
  );
};

/**
 * Step 1: Confirm Order
 */
const ConfirmStep = ({ product, customerEmail, setCustomerEmail, loading, error, onNext, onCancel }) => {
  return (
    <div className="step-content">
      <div className="product-summary">
        <img src={product.cover} alt={product.title} className="summary-image" />
        <div className="summary-info">
          <h3>{product.title}</h3>
          <p>{product.description.slice(0, 100)}...</p>
          <div className="summary-price">
            {product.originalPrice > product.price && (
              <span className="original-price">${product.originalPrice}</span>
            )}
            <span className="final-price">${product.price}</span>
          </div>
        </div>
      </div>

      <div className="order-breakdown">
        <h4>Order Summary</h4>
        <div className="breakdown-row">
          <span>Product</span>
          <span>${product.price}</span>
        </div>
        <div className="breakdown-row">
          <span>Tax</span>
          <span>$0.00</span>
        </div>
        <div className="breakdown-row total">
          <span>Total</span>
          <span>${product.price}</span>
        </div>
      </div>

      <div className="email-input">
        <label>Email Address</label>
        <input
          type="email"
          value={customerEmail}
          onChange={(e) => setCustomerEmail(e.target.value)}
          placeholder="your@email.com"
          required
        />
        <small>We'll send your download link here</small>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      <div className="actions">
        <button className="btn-secondary" onClick={onCancel} disabled={loading}>
          Cancel
        </button>
        <button
          className="btn-primary"
          onClick={onNext}
          disabled={loading || !customerEmail}
        >
          {loading ? (
            <>
              <Loader className="spinner" size={16} />
              Processing...
            </>
          ) : (
            'Continue to Payment'
          )}
        </button>
      </div>
    </div>
  );
};

/**
 * Step 2: Payment
 */
const PaymentStep = ({ product, paymentIntent, customerEmail, setStep, setError, onSuccess }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);

  const handlePayment = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) return;

    setProcessing(true);
    setError(null);

    try {
      // Confirm payment
      const { error, paymentIntent: pi } = await stripe.confirmCardPayment(
        paymentIntent.clientSecret,
        {
          payment_method: {
            card: elements.getElement(CardElement),
            billing_details: { email: customerEmail }
          }
        }
      );

      if (error) {
        setError(error.message);
        setProcessing(false);
        return;
      }

      if (pi.status === 'succeeded') {
        setStep('processing');

        // Confirm purchase on backend
        const res = await fetch('/api/fiilthy/purchase/complete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            paymentIntentId: pi.id,
            product_id: product.id,
            user_email: customerEmail
          })
        });

        if (!res.ok) throw new Error('Failed to complete purchase');

        const result = await res.json();
        setStep('success');
        onSuccess(result);
      }
    } catch (err) {
      setError(err.message);
      setProcessing(false);
    }
  };

  return (
    <form className="step-content" onSubmit={handlePayment}>
      <h3>Enter Payment Details</h3>

      <div className="card-element-wrapper">
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#fff',
                '::placeholder': {
                  color: '#aaa',
                },
              },
              invalid: {
                color: '#ef4444',
              },
            },
          }}
        />
      </div>

      <div className="trust-badges">
        <span>🔒 Secure payment by Stripe</span>
      </div>

      <button
        type="submit"
        disabled={processing}
        className="btn-primary btn-full"
      >
        {processing ? (
          <>
            <Loader className="spinner" size={16} />
            Processing Payment...
          </>
        ) : (
          `Pay $${product.price}`
        )}
      </button>
    </form>
  );
};

/**
 * Step 3: Processing
 */
const ProcessingStep = () => {
  return (
    <div className="step-content processing">
      <div className="processing-animation">
        <div className="spinner-circle"></div>
      </div>
      <h3>Processing Your Payment</h3>
      <p>Please wait while we process your purchase...</p>
    </div>
  );
};

/**
 * Step 4: Success
 */
const SuccessStep = ({ product, onClose }) => {
  return (
    <div className="step-content success">
      <CheckCircle className="success-icon" size={48} />
      <h3>Purchase Complete!</h3>

      <div className="success-message">
        <p>Thank you for your purchase!</p>
        <p>Your download link has been sent to your email.</p>
      </div>

      <div className="next-steps">
        <h4>Next Steps:</h4>
        <ol>
          <li>Check your email for the download link</li>
          <li>Download and extract the ZIP file</li>
          <li>Follow the included README for setup instructions</li>
          <li>Contact support@fiilthy.com if you have questions</li>
        </ol>
      </div>

      <button className="btn-primary btn-full" onClick={onClose}>
        Back to Store
      </button>
    </div>
  );
};

export default CheckoutFlow;
