import React from 'react';
import { Link } from 'react-router-dom';
import './AuthPages.css';

export default function LandingPage() {
  return (
    <div className="auth-container" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px', gap: '40px' }}>
      {/* Hero */}
      <div style={{ textAlign: 'center', maxWidth: '640px' }}>
        <h1 style={{ fontSize: '48px', fontWeight: 800, marginBottom: '16px', lineHeight: 1.1 }}>
          FiiLTHY<span style={{ color: '#e040fb' }}>.ai</span>
        </h1>
        <p style={{ fontSize: '20px', color: '#666', marginBottom: '8px' }}>
          Your AI-Powered Digital Empire
        </p>
        <p style={{ fontSize: '16px', color: '#888', marginBottom: '32px', lineHeight: 1.6 }}>
          Generate, launch, and sell digital products — eBooks, courses, templates, and more — powered by AI. From idea to revenue in minutes, not months.
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/signup" className="auth-button" style={{ display: 'inline-block', padding: '14px 32px', fontSize: '16px', textDecoration: 'none', textAlign: 'center' }}>
            Get Started Free
          </Link>
          <Link to="/login" style={{ display: 'inline-block', padding: '14px 32px', fontSize: '16px', textDecoration: 'none', color: '#333', border: '1px solid #ddd', borderRadius: '8px', textAlign: 'center' }}>
            Sign In
          </Link>
        </div>
      </div>

      {/* Features */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px', maxWidth: '900px', width: '100%' }}>
        {[
          { icon: '🔍', title: 'Opportunity Scout', desc: 'AI finds trending niches and high-demand product ideas' },
          { icon: '📦', title: 'Product Generation', desc: 'Generate complete eBooks, courses, and templates with one click' },
          { icon: '🚀', title: 'Auto-Launch', desc: 'Publish to Gumroad, create checkout links, and go live instantly' },
          { icon: '📣', title: 'Marketing AI', desc: 'Generate social posts, launch campaigns, and email sequences' },
          { icon: '💰', title: 'Revenue Tracking', desc: 'Track sales, payments, and conversion analytics in real time' },
          { icon: '🤖', title: 'Autonomous Mode', desc: 'Let the AI run 24/7 — scout, create, publish, and sell' },
        ].map((f, i) => (
          <div key={i} style={{ padding: '24px', border: '1px solid #eee', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>{f.icon}</div>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>{f.title}</h3>
            <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>{f.desc}</p>
          </div>
        ))}
      </div>

      {/* Pricing */}
      <div id="pricing" style={{ textAlign: 'center', maxWidth: '640px', width: '100%' }}>
        <h2 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>Simple Pricing</h2>
        <p style={{ color: '#666', marginBottom: '24px' }}>Start free. Upgrade when you're ready to scale.</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div style={{ padding: '32px 24px', border: '1px solid #eee', borderRadius: '12px' }}>
            <h3 style={{ fontSize: '20px', fontWeight: 700 }}>Starter</h3>
            <p style={{ fontSize: '36px', fontWeight: 800, margin: '12px 0' }}>Free</p>
            <ul style={{ listStyle: 'none', padding: 0, textAlign: 'left', fontSize: '14px', color: '#555' }}>
              <li style={{ padding: '6px 0' }}>&#10003; 5 products / month</li>
              <li style={{ padding: '6px 0' }}>&#10003; Opportunity scanning</li>
              <li style={{ padding: '6px 0' }}>&#10003; Stripe checkout links</li>
              <li style={{ padding: '6px 0' }}>&#10003; Basic analytics</li>
            </ul>
          </div>
          <div style={{ padding: '32px 24px', border: '2px solid #e040fb', borderRadius: '12px', position: 'relative' }}>
            <span style={{ position: 'absolute', top: '-12px', left: '50%', transform: 'translateX(-50%)', background: '#e040fb', color: '#fff', fontSize: '12px', fontWeight: 600, padding: '3px 12px', borderRadius: '10px' }}>POPULAR</span>
            <h3 style={{ fontSize: '20px', fontWeight: 700 }}>Empire</h3>
            <p style={{ fontSize: '36px', fontWeight: 800, margin: '12px 0' }}>$49<span style={{ fontSize: '16px', color: '#666' }}>/mo</span></p>
            <ul style={{ listStyle: 'none', padding: 0, textAlign: 'left', fontSize: '14px', color: '#555' }}>
              <li style={{ padding: '6px 0' }}>&#10003; Unlimited products</li>
              <li style={{ padding: '6px 0' }}>&#10003; Autonomous 24/7 mode</li>
              <li style={{ padding: '6px 0' }}>&#10003; Multi-platform publishing</li>
              <li style={{ padding: '6px 0' }}>&#10003; Advanced analytics</li>
              <li style={{ padding: '6px 0' }}>&#10003; Priority support</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={{ fontSize: '13px', color: '#999', textAlign: 'center', paddingTop: '20px', borderTop: '1px solid #eee', width: '100%', maxWidth: '900px' }}>
        <p>&copy; {new Date().getFullYear()} FiiLTHY.ai &mdash; All rights reserved.</p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '8px' }}>
          <Link to="/privacy" style={{ color: '#999' }}>Privacy Policy</Link>
          <Link to="/terms" style={{ color: '#999' }}>Terms of Service</Link>
          <Link to="/refund" style={{ color: '#999' }}>Refund Policy</Link>
          <a href="mailto:support@fiilthy.ai" style={{ color: '#999' }}>Support</a>
        </div>
      </footer>
    </div>
  );
}
