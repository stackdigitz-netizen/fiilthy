import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BrandLogo from '../components/BrandLogo';

export default function SuccessPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => navigate('/'), 4000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#0d1117',
      color: '#fff',
      fontFamily: 'sans-serif',
      textAlign: 'center',
      padding: '40px 20px',
    }}>
      <BrandLogo theme="light" size="lg" />
      <div style={{
        fontSize: '72px',
        margin: '24px 0 8px',
      }}>🎉</div>
      <h1 style={{
        fontSize: '36px',
        fontWeight: 800,
        background: 'linear-gradient(135deg, #b88924, #d4af37)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        marginBottom: '12px',
      }}>
        You're in, Empire Builder!
      </h1>
      <p style={{ fontSize: '18px', color: '#aaa', maxWidth: '480px', lineHeight: 1.6 }}>
        Your subscription is confirmed. Your FiiLTHY Empire is ready to generate income 24/7.
      </p>
      <p style={{ fontSize: '14px', color: '#555', marginTop: '32px' }}>
        Taking you to your dashboard...
      </p>
    </div>
  );
}
