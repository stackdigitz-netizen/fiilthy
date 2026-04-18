import React from 'react';
import { Link } from 'react-router-dom';
import BrandLogo from '../components/BrandLogo';
import './AuthPages.css';

const theme = {
  text: '#f8f4ea',
  muted: '#d8c48a',
  soft: '#a5966c',
  border: 'rgba(212, 175, 55, 0.22)',
  panel: 'rgba(255, 255, 255, 0.04)',
  panelStrong: 'linear-gradient(180deg, rgba(18, 18, 18, 0.96) 0%, rgba(7, 7, 7, 0.96) 100%)',
  gold: '#d4af37',
  goldLight: '#f4dd91',
  shadow: '0 24px 60px rgba(0, 0, 0, 0.34)',
};

const panelCard = {
  padding: '32px',
  border: `1px solid ${theme.border}`,
  borderRadius: '16px',
  textAlign: 'center',
  background: theme.panel,
  boxShadow: theme.shadow,
};

const quoteCard = {
  padding: '20px',
  background: 'rgba(255,255,255,0.05)',
  borderRadius: '12px',
  border: `1px solid ${theme.border}`,
  boxShadow: '0 16px 36px rgba(0,0,0,0.24)',
};

const secondaryCtaStyle = {
  display: 'inline-block',
  padding: '16px 40px',
  fontSize: '18px',
  textDecoration: 'none',
  color: theme.text,
  background: 'rgba(255,255,255,0.04)',
  border: `1px solid ${theme.border}`,
  borderRadius: '10px',
  textAlign: 'center',
  fontWeight: 700,
  boxShadow: '0 12px 32px rgba(0,0,0,0.24)',
};

export default function LandingPage() {
  return (
    <div className="auth-container" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px', gap: '40px' }}>
      <div style={{ width: '100%', maxWidth: '1120px', display: 'flex', flexDirection: 'column', gap: '40px' }}>
        <div style={{ textAlign: 'center', maxWidth: '840px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
          <BrandLogo theme="light" size="lg" />
          </div>
          <h1 style={{ fontSize: 'clamp(3rem, 7vw, 4.6rem)', fontWeight: 800, marginBottom: '18px', lineHeight: 1.05, color: theme.text, letterSpacing: '-0.04em' }}>
            Turn Your Ideas Into Digital Products That Sell Themselves
          </h1>
          <p style={{ fontSize: 'clamp(1.1rem, 2.6vw, 1.45rem)', color: theme.muted, marginBottom: '32px', lineHeight: 1.5 }}>
            AI-powered product creation, launch, and monetization with a cleaner luxury look built around black, gold, and white.
          </p>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/signup" className="auth-button" style={{ display: 'inline-block', padding: '16px 40px', fontSize: '18px', textDecoration: 'none', textAlign: 'center', fontWeight: 700 }}>
              Start Creating Now
            </Link>
            <Link to="/store" style={secondaryCtaStyle}>
              See Products In Action
            </Link>
          </div>
          <p style={{ fontSize: '16px', color: theme.soft, marginTop: '24px', marginBottom: 0 }}>
            Join 500+ creators who've generated $2M+ in digital product sales
          </p>
        </div>

        <div style={{ maxWidth: '1080px', width: '100%', textAlign: 'center', margin: '0 auto' }}>
          <h2 style={{ fontSize: '36px', fontWeight: 700, marginBottom: '16px', color: theme.text }}>What You Get</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '28px', marginTop: '40px' }}>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤖</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>AI Product Generator</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                Input any topic or niche, and the AI creates complete digital products: eBooks, courses, templates, printables, and more.
              </p>
            </div>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚀</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>One-Click Launch</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                Publish directly to Gumroad, Etsy, or your own website, then generate checkout links, sales pages, and launch assets instantly.
              </p>
            </div>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📈</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>Automated Marketing</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                The platform generates social posts, email sequences, TikTok scripts, and launch campaigns without the usual clutter.
              </p>
            </div>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>💰</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>Revenue Dashboard</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                Track sales, payments, and analytics in real time and keep the products that actually move revenue.
              </p>
            </div>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>Market Intelligence</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                Scan niches, analyze competitors, and identify high-demand opportunities with a cleaner signal-to-noise ratio.
              </p>
            </div>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚡</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>Autonomous Mode</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                Let the AI find opportunities, create products, publish, and market while you stay focused on the decisions that matter.
              </p>
            </div>
          </div>
        </div>

        <div style={{ maxWidth: '1080px', width: '100%', textAlign: 'center', margin: '0 auto' }}>
          <h2 style={{ fontSize: '36px', fontWeight: 700, marginBottom: '16px', color: theme.text }}>How It Works</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '28px', marginTop: '40px' }}>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>1️⃣</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>Choose Your Niche</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                Tell the system what topic interests you, or let it scan for trends and profit potential automatically.
              </p>
            </div>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>2️⃣</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>AI Generates Your Product</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                Watch the AI produce eBooks, courses, templates, or printables with a workflow designed for speed and polish.
              </p>
            </div>
            <div style={panelCard}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>3️⃣</div>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '16px', color: theme.text }}>Launch &amp; Sell</h3>
              <p style={{ fontSize: '16px', color: theme.muted, lineHeight: 1.6 }}>
                Publish to multiple platforms, generate marketing materials, and start collecting payments with a unified premium theme.
              </p>
            </div>
          </div>
        </div>

        <div style={{ maxWidth: '920px', width: '100%', textAlign: 'center', padding: '40px', background: theme.panelStrong, borderRadius: '18px', border: `1px solid ${theme.border}`, boxShadow: theme.shadow, margin: '0 auto' }}>
          <h2 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '24px', color: theme.text }}>Trusted By 500+ Creators</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px', marginBottom: '32px' }}>
            <div style={quoteCard}>
              <p style={{ fontSize: '16px', fontStyle: 'italic', color: theme.muted, margin: 0 }}>
                "Generated my first $10K product in 3 days. The AI did all the heavy lifting."
              </p>
              <p style={{ fontSize: '14px', fontWeight: 600, marginTop: '12px', color: theme.text }}>- Sarah M., Course Creator</p>
            </div>
            <div style={quoteCard}>
              <p style={{ fontSize: '16px', fontStyle: 'italic', color: theme.muted, margin: 0 }}>
                "From idea to Gumroad sales page in under an hour. Mind-blowing."
              </p>
              <p style={{ fontSize: '14px', fontWeight: 600, marginTop: '12px', color: theme.text }}>- Mike R., Entrepreneur</p>
            </div>
            <div style={quoteCard}>
              <p style={{ fontSize: '16px', fontStyle: 'italic', color: theme.muted, margin: 0 }}>
                "The autonomous mode runs my business while I sleep. Passive income finally real."
              </p>
              <p style={{ fontSize: '14px', fontWeight: 600, marginTop: '12px', color: theme.text }}>- Jessica L., Digital Marketer</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/signup" className="auth-button" style={{ display: 'inline-block', padding: '16px 40px', fontSize: '18px', textDecoration: 'none', textAlign: 'center', fontWeight: 700 }}>
              Join The Success Stories
            </Link>
          </div>
        </div>

        <div id="pricing" style={{ textAlign: 'center', maxWidth: '1080px', width: '100%', margin: '0 auto' }}>
          <h2 style={{ fontSize: '36px', fontWeight: 700, marginBottom: '16px', color: theme.text }}>Simple Pricing That Scales With You</h2>
          <p style={{ fontSize: '18px', color: theme.muted, marginBottom: '40px' }}>Start free. Upgrade when you're ready to scale.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '32px' }}>
            <div style={{ ...panelCard, textAlign: 'left' }}>
              <h3 style={{ fontSize: '24px', fontWeight: 700, color: theme.text }}>Starter</h3>
              <p style={{ fontSize: '48px', fontWeight: 800, margin: '16px 0', color: theme.text }}>Free</p>
              <ul style={{ listStyle: 'none', padding: 0, textAlign: 'left', fontSize: '16px', color: theme.muted }}>
                <li style={{ padding: '8px 0' }}>&#10003; 5 products / month</li>
                <li style={{ padding: '8px 0' }}>&#10003; Opportunity scanning</li>
                <li style={{ padding: '8px 0' }}>&#10003; Stripe checkout links</li>
                <li style={{ padding: '8px 0' }}>&#10003; Basic analytics</li>
              </ul>
              <Link to="/signup" style={{ display: 'inline-block', padding: '12px 24px', fontSize: '16px', textDecoration: 'none', color: theme.text, border: `1px solid ${theme.border}`, borderRadius: '10px', textAlign: 'center', marginTop: '20px', background: 'rgba(255,255,255,0.03)' }}>
                Get Started Free
              </Link>
            </div>
            <div style={{ ...panelCard, textAlign: 'left', border: `1px solid rgba(212, 175, 55, 0.45)`, position: 'relative', background: theme.panelStrong }}>
              <span style={{ position: 'absolute', top: '-16px', left: '50%', transform: 'translateX(-50%)', background: 'linear-gradient(135deg, #b88924 0%, #d4af37 60%, #f4dd91 100%)', color: '#050505', fontSize: '14px', fontWeight: 700, padding: '4px 16px', borderRadius: '999px' }}>MOST POPULAR</span>
              <h3 style={{ fontSize: '24px', fontWeight: 700, color: theme.text }}>Empire Builder</h3>
              <p style={{ fontSize: '48px', fontWeight: 800, margin: '16px 0', color: theme.text }}>$49<span style={{ fontSize: '20px', color: theme.muted }}>/mo</span></p>
              <ul style={{ listStyle: 'none', padding: 0, textAlign: 'left', fontSize: '16px', color: theme.muted }}>
                <li style={{ padding: '8px 0' }}>&#10003; Unlimited products</li>
                <li style={{ padding: '8px 0' }}>&#10003; Autonomous 24/7 mode</li>
                <li style={{ padding: '8px 0' }}>&#10003; Multi-platform publishing</li>
                <li style={{ padding: '8px 0' }}>&#10003; Advanced analytics</li>
                <li style={{ padding: '8px 0' }}>&#10003; Priority support</li>
              </ul>
              <Link to="/signup?plan=empire" className="auth-button" style={{ display: 'inline-block', padding: '12px 24px', fontSize: '16px', textDecoration: 'none', textAlign: 'center', marginTop: '20px' }}>
                Start Building Empire
              </Link>
            </div>
          </div>
        </div>

        <footer style={{ fontSize: '14px', color: theme.soft, textAlign: 'center', paddingTop: '40px', borderTop: `1px solid ${theme.border}`, width: '100%', maxWidth: '1080px', margin: '0 auto' }}>
          <p>&copy; {new Date().getFullYear()} FiiLTHY.ai | Turn Ideas Into Income</p>
          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginTop: '16px', flexWrap: 'wrap' }}>
            <Link to="/privacy" style={{ color: theme.soft }}>Privacy Policy</Link>
            <Link to="/terms" style={{ color: theme.soft }}>Terms of Service</Link>
            <Link to="/refund" style={{ color: theme.soft }}>Refund Policy</Link>
            <a href="mailto:support@fiilthy.ai" style={{ color: theme.soft }}>Support</a>
          </div>
        </footer>
      </div>
    </div>
  );
}
