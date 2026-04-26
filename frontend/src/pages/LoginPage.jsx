import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import API_URL from '../config/api';
import BrandLogo from '../components/BrandLogo';
import './AuthPages.css';

const sanitizeNextPath = (candidate) => {
  if (!candidate || typeof candidate !== 'string') {
    return '/';
  }

  if (!candidate.startsWith('/') || candidate.startsWith('//')) {
    return '/';
  }

  return candidate;
};

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const nextPath = sanitizeNextPath(searchParams.get('next'));
  const signupHref = nextPath === '/' ? '/signup' : `/signup?next=${encodeURIComponent(nextPath)}`;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/auth/login`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        }
      );

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      const { access_token, user } = data;
      login(access_token, user);
      navigate(nextPath);
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
          <p>Sign In to Your Digital Empire</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
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
            <label htmlFor="password">Password</label>
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
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={{ margin: '16px 0', textAlign: 'center' }}>
          <span>or</span>
        </div>

        <button
          className="auth-button google-auth-button"
          style={{ background: '#fff', color: '#333', border: '1px solid #ccc', marginBottom: 16 }}
          onClick={() => {
            window.location.href = `${API_URL}/api/auth/google/login`;
          }}
        >
          Sign in with Google
        </button>

        <div className="auth-footer">
          <p>Don't have an account? <Link to={signupHref}>Sign Up</Link></p>
        </div>
      </div>
    </div>
  );
}
