import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import API_URL from '../config/api';
import BrandLogo from '../components/BrandLogo';
import './AuthPages.css';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();

  const plan = searchParams.get('plan') || 'free';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/auth/signup`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            password,
            first_name: firstName || null,
            last_name: lastName || null
          })
        }
      );

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }

      const { access_token, user } = data;
      login(access_token, user);

      // Redirect to Stripe if the user selected a paid plan
      if (plan === 'empire') {
        try {
          const subRes = await fetch(`${API_URL}/api/payments/subscribe`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${access_token}`,
            },
            body: JSON.stringify({
              customer_email: email,
              plan: 'empire',
              success_url: `${window.location.origin}/success`,
              cancel_url: `${window.location.origin}/#pricing`,
            }),
          });
          const subData = await subRes.json();
          if (subData.checkout_url) {
            window.location.href = subData.checkout_url;
            return;
          }
        } catch (subErr) {
          console.warn('Subscription redirect failed, going to dashboard:', subErr);
        }
      }

      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <BrandLogo theme="light" size="md" />
          {plan === 'empire' ? (
            <>
              <p>Create Your Account</p>
              <div style={{ display: 'inline-block', background: 'linear-gradient(135deg, #b88924, #d4af37)', color: '#050505', fontWeight: 700, fontSize: '14px', padding: '4px 14px', borderRadius: '999px', marginTop: '8px' }}>
                Empire Builder — $49/mo
              </div>
              <p style={{ fontSize: '13px', color: '#888', marginTop: '8px' }}>After signup you'll complete your subscription securely via Stripe.</p>
            </>
          ) : (
            <p>Create Your Digital Empire Account</p>
          )}
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="firstName">First Name (optional)</label>
              <input
                id="firstName"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="First"
              />
            </div>
            <div className="form-group">
              <label htmlFor="lastName">Last Name (optional)</label>
              <input
                id="lastName"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="Last"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password (min 6 characters)</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="auth-button">
            {loading
              ? (plan === 'empire' ? 'Creating Account...' : 'Creating Account...')
              : (plan === 'empire' ? 'Create Account & Start Subscription →' : 'Create Account')}
          </button>
        </form>

        <div className="auth-footer">
          <p>Already have an account? <Link to="/login">Sign In</Link></p>
        </div>
      </div>
    </div>
  );
}
