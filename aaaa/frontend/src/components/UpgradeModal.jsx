import React, { useState } from 'react';
import { X, Zap, Crown, Rocket } from 'lucide-react';
import API_URL from '../config/api';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: '$29/mo',
    limit: 50,
    icon: Zap,
    color: '#00bcd4',
    description: 'Perfect for solo creators getting started'
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$79/mo',
    limit: 500,
    icon: Crown,
    color: '#ff6d00',
    description: 'For serious creators scaling fast'
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: '$299/mo',
    limit: 'Unlimited',
    icon: Rocket,
    color: '#7c4dff',
    description: 'For teams and power users'
  }
];

export default function UpgradeModal({ isOpen, onClose, currentPlan = 'free' }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleUpgrade = async (planId) => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_URL}/api/billing/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan: planId,
          success_url: `${window.location.origin}/billing/success`,
          cancel_url: `${window.location.origin}/billing/cancel`
        })
      });

      const data = await response.json();
      if (response.ok && data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        setError(data.detail || 'Failed to create checkout session');
      }
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      background: 'rgba(0,0,0,0.7)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 16
    }}>
      <div style={{
        background: '#0d1117',
        border: '1px solid #30363d',
        borderRadius: 16,
        width: '100%', maxWidth: 720,
        maxHeight: '90vh', overflow: 'auto',
        padding: '28px 24px'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <h2 style={{ margin: 0, fontSize: 22, color: '#fff' }}>Upgrade Your Plan</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#8b949e', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>
        <p style={{ color: '#8b949e', margin: '0 0 20px 0' }}>
          You have reached your <strong>{currentPlan}</strong> plan limit. Upgrade to continue generating.
        </p>

        {error && (
          <div style={{
            background: 'rgba(255,0,0,0.1)', border: '1px solid #ff4444',
            color: '#ff6b6b', padding: 10, borderRadius: 8, marginBottom: 16
          }}>
            {error}
          </div>
        )}

        {/* Plan Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14 }}>
          {PLANS.map((plan) => {
            const Icon = plan.icon;
            const isCurrent = currentPlan === plan.id;
            return (
              <div key={plan.id} style={{
                border: `2px solid ${isCurrent ? plan.color : '#30363d'}`,
                borderRadius: 12,
                padding: 18,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                background: isCurrent ? `${plan.color}10` : 'transparent'
              }}>
                <Icon size={28} color={plan.color} style={{ marginBottom: 10 }} />
                <h3 style={{ margin: '0 0 4px 0', color: '#fff', fontSize: 16 }}>{plan.name}</h3>
                <div style={{ color: plan.color, fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
                  {plan.price}
                </div>
                <div style={{ color: '#8b949e', fontSize: 12, marginBottom: 12 }}>
                  {plan.limit === 'Unlimited' ? 'Unlimited generations' : `${plan.limit} generations/mo`}
                </div>
                <p style={{ color: '#8b949e', fontSize: 11, marginBottom: 14, flex: 1 }}>
                  {plan.description}
                </p>
                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={loading || isCurrent}
                  style={{
                    width: '100%',
                    padding: '10px 0',
                    borderRadius: 8,
                    border: 'none',
                    background: isCurrent ? '#30363d' : plan.color,
                    color: '#fff',
                    fontWeight: 600,
                    cursor: isCurrent ? 'default' : 'pointer',
                    opacity: loading ? 0.7 : 1
                  }}
                >
                  {isCurrent ? 'Current Plan' : loading ? 'Loading...' : 'Upgrade'}
                </button>
              </div>
            );
          })}
        </div>

        <p style={{ color: '#6e7681', fontSize: 11, textAlign: 'center', marginTop: 16 }}>
          Secure checkout powered by Stripe. Cancel anytime.
        </p>
      </div>
    </div>
  );
}
