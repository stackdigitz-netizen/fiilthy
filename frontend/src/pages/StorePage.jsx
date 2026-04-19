import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import {
  ShoppingCart, Download, Star, Check, Zap, Lock, Mail, X,
  ArrowLeft, Package, Crown, Repeat,
} from 'lucide-react';
import BrandLogo from '../components/BrandLogo';
import API_URL from '../config/api';

const API = API_URL;

const CACHE_KEY = 'store_products_v4';
const CACHE_TIME = 5 * 60 * 1000; // 5 minutes
const MEMBERSHIP_FALLBACK_PLANS = [
  {
    id: 'monthly',
    name: 'FiiLTHY Monthly Membership',
    description: 'Full access to every product, blueprint and template. New drops every month.',
    price_cents: 2900,
    interval: 'month',
    label: '$29/month',
    perks: [
      'Instant access to ALL products',
      'New product drops every month',
      'Priority support',
      'Members-only templates & bonuses',
      'Cancel any time',
    ],
  },
  {
    id: 'annual',
    name: 'FiiLTHY Annual Membership',
    description: 'Everything in Monthly, billed annually. Save $99 vs monthly.',
    price_cents: 24900,
    interval: 'year',
    label: '$249/year',
    perks: [
      'Everything in Monthly',
      'Saves $99 vs monthly billing',
      'Bonus: Private strategy vault',
      'Annual member badge',
      'Cancel any time',
    ],
  },
];

function normalizePlans(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.value)) {
    return payload.value;
  }

  return [];
}

function sortPlans(plans) {
  const rank = { monthly: 0, annual: 1 };
  return [...plans].sort((left, right) => {
    const leftRank = rank[left.id] ?? 99;
    const rightRank = rank[right.id] ?? 99;
    return leftRank - rightRank;
  });
}

function formatPlanPrice(plan) {
  const amount = Number(plan.price_cents || 0) / 100;
  const suffix = plan.interval === 'year' ? '/yr' : '/mo';
  return {
    amount: `$${Number.isInteger(amount) ? amount.toFixed(0) : amount.toFixed(2)}`,
    suffix,
  };
}

function normalizeProductText(value) {
  return String(value || '').trim().toLowerCase().replace(/\s+/g, ' ');
}

function dedupeProducts(products) {
  const seen = new Set();

  return products.filter((product) => {
    const dedupeKey = [
      normalizeProductText(product.title),
      normalizeProductText(product.type || product.product_type),
      Number(product.price || 0).toFixed(2),
    ].join('::');

    if (seen.has(dedupeKey)) {
      return false;
    }

    seen.add(dedupeKey);
    return true;
  });
}

async function requestDownloadLink(sessionId, customerEmail) {
  const res = await fetch(`${API}/api/store/download-link/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: customerEmail }),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(payload.detail || 'Download link is not ready yet');
  }
  return payload;
}

// ─── Main Page ──────────────────────────────────────────────────────────────

export default function StorePage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [email, setEmail] = useState(() => {
    if (typeof window === 'undefined') return '';
    return window.localStorage.getItem('storeCheckoutEmail') || '';
  });
  const [emailError, setEmailError] = useState('');
  const [checkoutLoading, setCheckoutLoading] = useState(null); // holds product id
  const [subscribeLoading, setSubscribeLoading] = useState(null); // holds plan id
  const [membershipPlans, setMembershipPlans] = useState([]);
  const [plansLoading, setPlansLoading] = useState(true);
  const [plansError, setPlansError] = useState('');
  const emailInputRef = useRef(null);
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const isSuccess = params.get('success') === '1';
  const sessionId = params.get('session_id');
  const normalizedEmail = email.trim();
  const hasValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail);

  const focusEmailField = useCallback(() => {
    if (!emailInputRef.current) return;
    emailInputRef.current.focus();
    emailInputRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, []);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError('');
    
    // Check cache first
    if (typeof window !== 'undefined') {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        try {
          const { data, timestamp } = JSON.parse(cached);
          if (Date.now() - timestamp < CACHE_TIME) {
            setProducts(dedupeProducts(data));
            setLoading(false);
            return;
          }
        } catch (e) {
          // Invalid cache, ignore
        }
      }
    }
    
    try {
      const response = await fetch(`${API}/api/store/products`);
      if (!response.ok) throw new Error('Failed to load products');
      const data = await response.json();
      const productsData = dedupeProducts(Array.isArray(data) ? data : []);
      setProducts(productsData);
      
      // Cache the data
      if (typeof window !== 'undefined') {
        localStorage.setItem(CACHE_KEY, JSON.stringify({ data: productsData, timestamp: Date.now() }));
      }
    } catch (err) {
      setError(err.message || 'Failed to load products. Please check your connection.');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadPlans = useCallback(async () => {
    setPlansLoading(true);
    setPlansError('');

    try {
      const response = await fetch(`${API}/api/store/plans`);
      if (!response.ok) {
        throw new Error('Failed to load membership plans');
      }

      const data = await response.json();
      const normalizedPlans = normalizePlans(data);

      if (normalizedPlans.length > 0) {
        setMembershipPlans(sortPlans(normalizedPlans));
      } else {
        setPlansError('Using fallback membership plans while the backend returns no plans.');
      }
    } catch (err) {
      setPlansError(err.message || 'Using fallback membership plans.');
      setMembershipPlans([]);
    } finally {
      setPlansLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  useEffect(() => {
    loadPlans();
  }, [loadPlans]);

  const handleBuy = async (product) => {
    const checkoutEmail = email.trim();
    if (!checkoutEmail) {
      setEmailError('Enter your email to continue');
      focusEmailField();
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(checkoutEmail)) {
      setEmailError('Please enter a valid email address');
      focusEmailField();
      return;
    }
    setEmailError('');
    setCheckoutLoading(product.id);
    try {
      window.localStorage.setItem('storeCheckoutEmail', checkoutEmail);
      const res = await fetch(`${API}/api/store/checkout/${product.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_email: checkoutEmail, quantity: 1 }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Checkout failed');
      }
      const { checkout_url } = await res.json();
      window.location.href = checkout_url;
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setCheckoutLoading(null);
    }
  };

  const isSubscribed = params.get('subscribed') === '1';
  const subscribedPlan = params.get('plan');
  const displayPlans = sortPlans(membershipPlans.length > 0 ? membershipPlans : MEMBERSHIP_FALLBACK_PLANS);

  const handleSubscribe = async (plan) => {
    const checkoutEmail = email.trim();
    if (!checkoutEmail) {
      setEmailError('Enter your email to continue');
      focusEmailField();
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(checkoutEmail)) {
      setEmailError('Please enter a valid email address');
      focusEmailField();
      return;
    }
    setEmailError('');
    setSubscribeLoading(plan);
    try {
      window.localStorage.setItem('storeCheckoutEmail', checkoutEmail);
      const res = await fetch(`${API}/api/store/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_email: checkoutEmail, plan }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Checkout failed');
      }
      const { checkout_url } = await res.json();
      window.location.href = checkout_url;
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setSubscribeLoading(null);
    }
  };

  if (isSubscribed) return <SubscribedPage plan={subscribedPlan} />;
  if (isSuccess) return <SuccessPage sessionId={sessionId} />;

  return (
    <div style={s.page}>
      {/* Header */}
      <div style={s.header}>
        <div style={s.headerInner}>
          <BrandLogo theme="dark" size="sm" />
          <span style={s.tagline}>Digital Products</span>
        </div>
      </div>

      {/* Hero */}
      <div style={s.hero}>
        <h1 style={s.heroTitle}>AI-Powered Income Systems</h1>
        <p style={s.heroSub}>
          Premium blueprints, guides & templates to build real income with AI.
          <br />Instant download — no subscription, yours forever.
        </p>
        <div style={s.heroStats}>
          <StatBadge value={`${products.length || '4'}+`} label="Products" />
          <StatBadge value="50K+" label="Downloads" />
          <StatBadge value="4.9★" label="Rating" />
          <StatBadge value="30-day" label="Refund" />
        </div>
      </div>

      {/* Email capture */}
      <div style={s.emailSection}>
        <div style={s.emailCard}>
          <Mail size={20} style={{ color: '#6b7280', flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <p style={s.emailLabel}>Your download is sent here after purchase</p>
            <input
              ref={emailInputRef}
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={e => { setEmail(e.target.value); setEmailError(''); }}
              style={s.emailInput}
            />
            <p style={s.emailHint}>Required before Buy Now opens Stripe checkout.</p>
            {emailError && <p style={s.emailError}>{emailError}</p>}
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div style={s.sectionWrap}>
        <h2 style={s.sectionTitle}>Featured Products</h2>
        {loading && <div style={s.loadingBox}>Loading products…</div>}
        {error && <div style={s.errorBox}><p>{error}</p><button onClick={loadProducts} style={s.retryButton}>Retry</button></div>}
        {!loading && !error && (
          <div style={s.grid}>
            {products.length === 0 ? <p style={{ color: '#9ca3af', textAlign: 'center', padding: '60px 0' }}>No products available</p> : products.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onSelect={() => setSelectedProduct(product)}
                onBuy={() => handleBuy(product)}
                isLoading={checkoutLoading === product.id}
                hasValidEmail={hasValidEmail}
              />
            ))}
          </div>
        )}
      </div>

      {/* Membership Plans */}
      <div style={{ background: '#111111', padding: '70px 24px', marginBottom: 0 }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(255,255,255,0.08)', borderRadius: 20, padding: '6px 16px', marginBottom: 16 }}>
              <Crown size={14} style={{ color: '#f59e0b' }} />
              <span style={{ color: '#f59e0b', fontSize: 12, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase' }}>Membership</span>
            </div>
            <h2 style={{ color: '#ffffff', fontSize: 'clamp(26px, 4vw, 42px)', fontWeight: 900, margin: '0 0 12px', letterSpacing: '-1px' }}>Get Everything. Every Month.</h2>
            <p style={{ color: '#9ca3af', fontSize: 16, maxWidth: 520, margin: '0 auto' }}>One membership unlocks every product we've ever made and every new drop going forward.</p>
            {plansLoading && (
              <p style={{ color: '#6b7280', fontSize: 13, margin: '14px 0 0' }}>Syncing live membership plans…</p>
            )}
            {!plansLoading && plansError && (
              <p style={{ color: '#fbbf24', fontSize: 13, margin: '14px 0 0' }}>{plansError}</p>
            )}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
            {displayPlans.map((plan) => {
              const isFeatured = plan.id === 'annual';
              const pricing = formatPlanPrice(plan);
              const buttonIcon = isFeatured ? <Crown size={15} /> : <Repeat size={15} />;
              const buttonLabel = isFeatured ? 'Subscribe Annual' : 'Subscribe Monthly';

              return (
                <div
                  key={plan.id}
                  style={{
                    background: '#1f2937',
                    border: isFeatured ? '2px solid #f59e0b' : '1px solid #374151',
                    borderRadius: 16,
                    padding: '32px 28px',
                    position: 'relative',
                  }}
                >
                  {isFeatured && (
                    <div style={{ position: 'absolute', top: -13, left: '50%', transform: 'translateX(-50%)', background: '#f59e0b', color: '#000', fontSize: 11, fontWeight: 900, padding: '4px 14px', borderRadius: 20, whiteSpace: 'nowrap' }}>
                      BEST VALUE
                    </div>
                  )}
                  <div style={{ color: isFeatured ? '#f59e0b' : '#9ca3af', fontSize: 12, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 8 }}>
                    {plan.interval === 'year' ? 'Annual' : 'Monthly'}
                  </div>
                  <div style={{ color: '#ffffff', fontSize: 42, fontWeight: 900, marginBottom: 4 }}>
                    {pricing.amount}
                    <span style={{ fontSize: 18, fontWeight: 400, color: '#6b7280' }}>{pricing.suffix}</span>
                  </div>
                  <p style={{ color: '#ffffff', fontSize: 18, fontWeight: 700, margin: '0 0 10px' }}>{plan.name}</p>
                  <p style={{ color: '#9ca3af', fontSize: 14, margin: '0 0 24px', lineHeight: 1.6 }}>{plan.description}</p>
                  <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 28px' }}>
                    {(plan.perks || []).map((perk) => (
                      <li key={perk} style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#d1d5db', fontSize: 14, marginBottom: 10 }}>
                        <Check size={14} style={{ color: isFeatured ? '#f59e0b' : '#22c55e', flexShrink: 0 }} />{perk}
                      </li>
                    ))}
                  </ul>
                  <button
                    onClick={() => handleSubscribe(plan.id)}
                    disabled={subscribeLoading === plan.id}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 8,
                      padding: '13px 20px',
                      background: isFeatured ? '#f59e0b' : '#ffffff',
                      color: isFeatured ? '#000000' : '#111111',
                      border: 'none',
                      borderRadius: 8,
                      fontWeight: 800,
                      fontSize: 15,
                      cursor: 'pointer',
                      opacity: subscribeLoading === plan.id ? 0.7 : 1,
                    }}
                  >
                    {buttonIcon}
                    {subscribeLoading === plan.id ? 'Loading…' : hasValidEmail ? buttonLabel : 'Enter Email First'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Trust bar */}
      <div style={s.trustBar}>
        {[
          { icon: <Lock size={16} />, text: 'Secure Stripe Checkout' },
          { icon: <Download size={16} />, text: 'Instant Download Link' },
          { icon: <Check size={16} />, text: '30-Day Money-Back Guarantee' },
          { icon: <Zap size={16} />, text: 'AI-Powered Products' },
        ].map(({ icon, text }) => (
          <div key={text} style={s.trustItem}>{icon}<span>{text}</span></div>
        ))}
      </div>

      {/* Product modal */}
      {selectedProduct && (
        <ProductModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
          onBuy={() => { setSelectedProduct(null); handleBuy(selectedProduct); }}
          isLoading={checkoutLoading === selectedProduct.id}
          checkoutEmail={normalizedEmail}
          hasValidEmail={hasValidEmail}
        />
      )}
    </div>
  );
}

// ─── Subscribed Page ──────────────────────────────────────────────────────────

function SubscribedPage({ plan }) {
  const planLabel = plan === 'annual' ? 'Annual' : 'Monthly';
  return (
    <div style={{ ...s.page, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div style={s.successBox}>
        <div style={{ fontSize: 72, lineHeight: 1, marginBottom: 16 }}>🎉</div>
        <h1 style={{ color: '#111111', fontSize: 28, fontWeight: 800, margin: '0 0 12px' }}>
          You're a Member!
        </h1>
        <p style={{ color: '#6b7280', fontSize: 16, lineHeight: 1.6, marginBottom: 24 }}>
          Your <strong>{planLabel} Membership</strong> is active.<br />
          Check your email for your receipt and access details.
        </p>
        <div style={s.successNote}>
          <Crown size={18} style={{ color: '#f59e0b' }} />
          <span>Full access to all products unlocked</span>
        </div>
        <button
          style={{ ...s.buyBtn, width: '100%', justifyContent: 'center', marginTop: 18, padding: '14px 18px' }}
          onClick={() => window.location.href = '/store'}
        >
          <ShoppingCart size={16} /> Browse All Products
        </button>
      </div>
    </div>
  );
}

// ─── Success Page ────────────────────────────────────────────────────────────

function SuccessPage({ sessionId }) {
  const [email, setEmail] = useState(() => window.localStorage.getItem('storeCheckoutEmail') || '');
  const [downloadData, setDownloadData] = useState(null);
  const [loading, setLoading] = useState(Boolean(sessionId));
  const [error, setError] = useState('');

  const unlockDownload = async () => {
    if (!sessionId) {
      setError('Missing checkout session. Contact support if you were charged.');
      return;
    }
    if (!email.trim()) {
      setError('Enter the purchase email to unlock your download.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const payload = await requestDownloadLink(sessionId, email.trim());
      window.localStorage.setItem('storeCheckoutEmail', email.trim());
      setDownloadData(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    if (!sessionId || !email.trim()) {
      setLoading(false);
      return undefined;
    }

    setLoading(true);
    setError('');

    requestDownloadLink(sessionId, email.trim())
      .then((payload) => {
        if (cancelled) return;
        window.localStorage.setItem('storeCheckoutEmail', email.trim());
        setDownloadData(payload);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message);
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [email, sessionId]);

  return (
    <div style={{ ...s.page, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div style={s.successBox}>
        <div style={{ fontSize: 72, lineHeight: 1, marginBottom: 16 }}>🎉</div>
        <h1 style={{ color: '#111111', fontSize: 28, fontWeight: 800, margin: '0 0 12px' }}>
          Payment Successful!
        </h1>
        <p style={{ color: '#6b7280', fontSize: 16, lineHeight: 1.6, marginBottom: 24 }}>
          Your purchase is confirmed.
          <br />
          Your download can be unlocked right here, and we'll email it when delivery is configured.
        </p>
        <div style={{ marginBottom: 16, textAlign: 'left' }}>
          <p style={{ color: '#374151', fontSize: 13, marginBottom: 8 }}>Purchase email</p>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={event => {
              setEmail(event.target.value);
              setError('');
            }}
            style={{
              width: '100%',
              background: '#f9fafb',
              color: '#111827',
              border: '1px solid #e5e7eb',
              borderRadius: 10,
              padding: '12px 14px',
              outline: 'none',
              fontSize: 14,
              boxSizing: 'border-box',
            }}
          />
        </div>
        <div style={s.successNote}>
          <Mail size={18} style={{ color: '#00e5ff' }} />
          <span>Download link stays valid for 7 days from purchase</span>
        </div>
        {downloadData ? (
          <button
            style={{ ...s.buyBtn, width: '100%', justifyContent: 'center', marginTop: 18, padding: '14px 18px' }}
            onClick={() => { window.location.href = downloadData.download_url; }}
          >
            <Download size={16} /> Download {downloadData.product_title}
          </button>
        ) : (
          <button
            style={{ ...s.buyBtn, width: '100%', justifyContent: 'center', marginTop: 18, padding: '14px 18px', opacity: loading ? 0.75 : 1 }}
            onClick={unlockDownload}
            disabled={loading}
          >
            <Lock size={16} /> {loading ? 'Unlocking…' : 'Unlock My Download'}
          </button>
        )}
        {error && (
          <p style={{ color: '#fca5a5', fontSize: 13, lineHeight: 1.5, marginTop: 12 }}>
            {error}
          </p>
        )}
        <button
          style={{ ...s.backBtn, marginTop: 14 }}
          onClick={() => window.location.href = '/store'}
        >
          <ArrowLeft size={14} /> Browse More Products
        </button>
      </div>
    </div>
  );
}

// ─── Product Card ─────────────────────────────────────────────────────────────

function ProductCard({ product, onSelect, onBuy, isLoading, hasValidEmail }) {
  const discount =
    product.originalPrice > product.price
      ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
      : 0;

  return (
    <div style={s.card} onClick={onSelect}>
      <div style={s.cardImgWrap}>
        <img src={product.cover} alt={product.title} style={s.cardImg} loading="lazy" />
        {discount > 0 && <div style={s.badge}>−{discount}%</div>}
        <div style={s.cardTypePill}>{product.type || 'guide'}</div>
      </div>
      <div style={s.cardBody}>
        <h3 style={s.cardTitle}>{product.title}</h3>
        <p style={s.cardDesc}>{product.description}</p>
        <div style={s.cardMeta}>
          <span style={{ color: '#f59e0b' }}>
            {'★'.repeat(Math.floor(product.rating || 4.8))}
            <span style={{ color: '#666', marginLeft: 4 }}>({product.reviews || 0})</span>
          </span>
          <span style={{ color: '#555' }}>📥 {(product.downloads || 0).toLocaleString()}</span>
        </div>
        <div style={s.cardFooter}>
          <div style={s.priceRow}>
            {discount > 0 && (
              <span style={s.origPrice}>${product.originalPrice}</span>
            )}
            <span style={s.price}>${product.price}</span>
          </div>
          <button
            style={{ ...s.buyBtn, opacity: isLoading ? 0.7 : 1 }}
            onClick={e => { e.stopPropagation(); onBuy(); }}
            disabled={isLoading}
            title={hasValidEmail ? 'Go to secure Stripe checkout' : 'Enter your email above to continue to checkout'}
          >
            <ShoppingCart size={14} />
            {isLoading ? 'Loading…' : hasValidEmail ? 'Buy Now' : 'Enter Email First'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Product Modal ────────────────────────────────────────────────────────────

function ProductModal({ product, onClose, onBuy, isLoading, checkoutEmail, hasValidEmail }) {
  const discount =
    product.originalPrice > product.price
      ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
      : 0;

  return (
    <div style={s.overlay} onClick={onClose}>
      <div style={{ ...s.modal, maxWidth: '900px', maxHeight: '90vh', overflowY: 'auto' }} onClick={e => e.stopPropagation()}>
        <button style={s.closeBtn} onClick={onClose}>
          <X size={18} />
        </button>

        <div style={{ padding: '40px' }}>
          {/* Product Title */}
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: 800, marginBottom: '8px', lineHeight: 1.2, color: '#111111' }}>
              {product.title}
            </h1>
            <p style={{ fontSize: '18px', color: '#6b7280', margin: 0 }}>
              {product.subtitle || 'Create a high-converting offer, even if you\'ve never sold anything before.'}
            </p>
          </div>

          {/* Price Section */}
          <div style={{ textAlign: 'center', marginBottom: '32px', padding: '24px', background: '#f9fafb', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Launch Price</div>
            {discount > 0 && (
              <div style={{ fontSize: '24px', color: '#9ca3af', textDecoration: 'line-through', marginBottom: '4px' }}>
                ${product.originalPrice}
              </div>
            )}
            <div style={{ fontSize: '48px', fontWeight: 800, color: '#111111', marginBottom: '8px' }}>
              ${product.price}
            </div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>Instant download included</div>
          </div>

          {/* CTA Button */}
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <button
              style={{ ...s.buyBtn, padding: '16px 40px', fontSize: '18px', fontWeight: 700 }}
              onClick={onBuy}
              disabled={isLoading || !hasValidEmail}
            >
              {isLoading ? 'Processing...' : 'Get Instant Access'}
            </button>
            {!hasValidEmail && (
              <p style={{ color: '#fca5a5', fontSize: '14px', marginTop: '8px' }}>
                Enter your email above to continue
              </p>
            )}
          </div>

          {/* What This Does */}
          <div style={{ marginBottom: '40px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '16px', color: '#111111' }}>🎯 What This Does</h2>
            <p style={{ color: '#374151', fontSize: '16px', lineHeight: 1.6, marginBottom: '16px' }}>
              {product.description}
            </p>
            <ul style={{ color: '#374151', fontSize: '16px', lineHeight: 1.8, paddingLeft: '20px' }}>
              {(product.benefits || [
                'Turn an idea into something people will pay for',
                'Create offers that actually convert',
                'Launch faster without guessing'
              ]).map((benefit, i) => (
                <li key={i} style={{ marginBottom: '8px' }}>✅ {benefit}</li>
              ))}
            </ul>
          </div>

          {/* What You Get */}
          <div style={{ marginBottom: '40px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '16px', color: '#111111' }}>📦 What You Get</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
              {(product.includes || [
                'Full step-by-step guide',
                'Offer creation worksheet',
                '25 AI prompts',
                '7-day launch sprint plan',
                'Fulfillment checklist',
                'Upsell framework'
              ]).map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', background: '#f9fafb', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                  <Check size={16} style={{ color: '#22c55e', flexShrink: 0 }} />
                  <span style={{ color: '#374151', fontSize: '14px' }}>{item}</span>
                </div>
              ))}
            </div>
            <p style={{ color: '#9ca3af', fontSize: '14px', marginTop: '16px', textAlign: 'center' }}>
              👉 Everything is ready to use
            </p>
          </div>

          {/* How To Use It */}
          <div style={{ marginBottom: '40px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '16px', color: '#111111' }}>⚙️ How To Use It</h2>
            <ol style={{ color: '#374151', fontSize: '16px', lineHeight: 1.8, paddingLeft: '20px' }}>
              <li style={{ marginBottom: '8px' }}>Open the files</li>
              <li style={{ marginBottom: '8px' }}>Follow the steps</li>
              <li style={{ marginBottom: '8px' }}>Launch your product</li>
            </ol>
            <p style={{ color: '#9ca3af', fontSize: '14px', marginTop: '16px', textAlign: 'center' }}>
              👉 No experience needed
            </p>
          </div>

          {/* Real Value */}
          <div style={{ marginBottom: '40px', padding: '24px', background: '#f9fafb', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '16px', color: '#111111' }}>🔥 Real Value</h2>
            <p style={{ color: '#374151', fontSize: '16px', lineHeight: 1.6, marginBottom: '16px' }}>
              Most people struggle because:
            </p>
            <ul style={{ color: '#374151', fontSize: '16px', lineHeight: 1.8, paddingLeft: '20px' }}>
              <li style={{ marginBottom: '8px' }}>They don't know what to sell</li>
              <li style={{ marginBottom: '8px' }}>Their offer is weak</li>
              <li style={{ marginBottom: '8px' }}>They overthink everything</li>
            </ul>
            <p style={{ color: '#111111', fontSize: '16px', fontWeight: 600, textAlign: 'center', marginTop: '16px' }}>
              👉 This removes all of that.
            </p>
          </div>

          {/* Perfect For */}
          <div style={{ marginBottom: '40px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '16px', color: '#111111' }}>💡 Perfect For</h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
              {(product.perfectFor || [
                'Beginners',
                'Side hustlers',
                'Anyone who wants to make money online'
              ]).map((audience, i) => (
                <span key={i} style={{ background: '#111111', color: '#ffffff', padding: '8px 16px', borderRadius: '20px', fontSize: '14px', fontWeight: 600 }}>
                  {audience}
                </span>
              ))}
            </div>
          </div>

          {/* Guarantee + Trust */}
          <div style={{ marginBottom: '40px', padding: '24px', background: '#f9fafb', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '16px', color: '#111111' }}>🔒 Guarantee + Trust</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Download size={20} style={{ color: '#22c55e' }} />
                <span style={{ color: '#374151', fontSize: '14px' }}>Instant download after purchase</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Check size={20} style={{ color: '#22c55e' }} />
                <span style={{ color: '#374151', fontSize: '14px' }}>7-day simple guarantee</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Lock size={20} style={{ color: '#22c55e' }} />
                <span style={{ color: '#374151', fontSize: '14px' }}>Secure Stripe checkout</span>
              </div>
            </div>
            <p style={{ color: '#9ca3af', fontSize: '14px', marginTop: '16px', textAlign: 'center' }}>
              Support available if you need help
            </p>
          </div>

          {/* Urgency */}
          <div style={{ textAlign: 'center', marginBottom: '32px', padding: '20px', background: 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)', borderRadius: '12px' }}>
            <p style={{ color: '#fff', fontSize: '18px', fontWeight: 700, margin: 0 }}>
              🔥 Launch pricing — limited time only
            </p>
          </div>

          {/* Final CTA */}
          <div style={{ textAlign: 'center' }}>
            <button
              style={{ ...s.buyBtn, padding: '18px 48px', fontSize: '20px', fontWeight: 800 }}
              onClick={onBuy}
              disabled={isLoading || !hasValidEmail}
            >
              {isLoading ? 'Processing...' : `Start Now — ${product.cta || 'Build Your First Offer Today'}`}
            </button>
            {!hasValidEmail && (
              <p style={{ color: '#fca5a5', fontSize: '14px', marginTop: '12px' }}>
                Enter your email above to unlock your purchase
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── StatBadge ────────────────────────────────────────────────────────────────

function StatBadge({ value, label }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ color: '#111111', fontWeight: 800, fontSize: 22 }}>{value}</div>
      <div style={{ color: '#6b7280', fontSize: 12, marginTop: 2 }}>{label}</div>
    </div>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const s = {
  page: {
    background: '#f9fafb',
    minHeight: '100vh',
    color: '#111827',
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
  },
  header: {
    borderBottom: '1px solid #e5e7eb',
    padding: '14px 24px',
    background: '#ffffff',
  },
  headerInner: {
    maxWidth: 1200,
    margin: '0 auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logo: {
    fontSize: 22,
    fontWeight: 900,
    letterSpacing: '-1px',
    color: '#111111',
  },
  tagline: {
    color: '#9ca3af',
    fontSize: 14,
  },
  hero: {
    textAlign: 'center',
    padding: '70px 20px 50px',
    background: '#ffffff',
    borderBottom: '1px solid #e5e7eb',
  },
  heroTitle: {
    fontSize: 'clamp(30px, 5vw, 56px)',
    fontWeight: 900,
    color: '#111111',
    margin: '0 0 14px',
    letterSpacing: '-2px',
    lineHeight: 1.1,
  },
  heroSub: {
    color: '#6b7280',
    fontSize: 'clamp(14px, 2vw, 18px)',
    lineHeight: 1.7,
    margin: '0 0 36px',
  },
  heroStats: {
    display: 'flex',
    justifyContent: 'center',
    gap: 40,
    flexWrap: 'wrap',
  },
  emailSection: {
    maxWidth: 640,
    margin: '0 auto 52px',
    padding: '0 20px',
  },
  emailCard: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 14,
    background: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: 12,
    padding: '18px 20px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
  },
  emailLabel: {
    color: '#374151',
    fontSize: 13,
    margin: '0 0 8px',
  },
  emailInput: {
    width: '100%',
    padding: '11px 14px',
    background: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: 8,
    color: '#111827',
    fontSize: 15,
    outline: 'none',
    boxSizing: 'border-box',
  },
  emailHint: {
    color: '#9ca3af',
    fontSize: 12,
    margin: '8px 0 0',
  },
  emailError: {
    color: '#ef4444',
    fontSize: 12,
    margin: '6px 0 0',
  },
  sectionWrap: {
    maxWidth: 1200,
    margin: '0 auto',
    padding: '0 24px 60px',
  },
  sectionTitle: {
    color: '#111111',
    fontSize: 22,
    fontWeight: 800,
    marginBottom: 24,
    letterSpacing: '-0.5px',
  },
  loadingBox: {
    color: '#9ca3af',
    textAlign: 'center',
    padding: '60px 0',
  },
  errorBox: {
    textAlign: 'center',
    padding: '60px 0',
    color: '#ef4444',
  },
  retryButton: {
    background: '#111111',
    color: '#ffffff',
    border: 'none',
    padding: '8px 16px',
    borderRadius: 6,
    cursor: 'pointer',
    fontWeight: 700,
    marginTop: 10,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(270px, 1fr))',
    gap: 20,
  },
  card: {
    background: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: 12,
    overflow: 'hidden',
    cursor: 'pointer',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    transition: 'border-color 0.15s, transform 0.15s, box-shadow 0.15s',
  },
  cardImgWrap: {
    height: 186,
    position: 'relative',
    overflow: 'hidden',
    background: '#f3f4f6',
  },
  cardImg: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  badge: {
    position: 'absolute',
    top: 10,
    right: 10,
    background: '#111111',
    color: '#ffffff',
    fontSize: 11,
    fontWeight: 800,
    padding: '3px 8px',
    borderRadius: 4,
  },
  cardTypePill: {
    display: 'inline-block',
    background: '#f3f4f6',
    color: '#374151',
    fontSize: 10,
    fontWeight: 700,
    letterSpacing: 1,
    textTransform: 'uppercase',
    padding: '3px 8px',
    borderRadius: 4,
    marginBottom: 8,
  },
  cardBody: {
    padding: '14px 16px 16px',
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: 700,
    margin: '0 0 7px',
    color: '#111111',
    lineHeight: 1.3,
  },
  cardDesc: {
    color: '#6b7280',
    fontSize: 13,
    margin: '0 0 10px',
    lineHeight: 1.5,
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  cardMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 12,
    marginBottom: 12,
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  priceRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
  },
  origPrice: {
    color: '#9ca3af',
    fontSize: 13,
    textDecoration: 'line-through',
  },
  price: {
    color: '#111111',
    fontSize: 22,
    fontWeight: 800,
  },
  buyBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '8px 14px',
    background: '#111111',
    color: '#ffffff',
    border: 'none',
    borderRadius: 7,
    fontWeight: 800,
    fontSize: 13,
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  },
  // Modal
  overlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.6)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: 20,
  },
  modal: {
    background: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: 16,
    maxWidth: 820,
    width: '100%',
    maxHeight: '92vh',
    overflowY: 'auto',
    position: 'relative',
    boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
  },
  closeBtn: {
    position: 'absolute',
    top: 12,
    right: 12,
    background: '#f3f4f6',
    border: 'none',
    color: '#6b7280',
    borderRadius: 6,
    padding: '6px 8px',
    cursor: 'pointer',
    zIndex: 1,
    display: 'flex',
    alignItems: 'center',
  },
  modalInner: {
    display: 'grid',
    gridTemplateColumns: '1fr 1.5fr',
  },
  modalImgWrap: {
    position: 'relative',
  },
  modalImg: {
    width: '100%',
    height: 300,
    objectFit: 'cover',
    borderRadius: '16px 0 0 0',
    display: 'block',
  },
  fileInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '10px 14px',
    background: '#f9fafb',
    color: '#9ca3af',
    fontSize: 12,
    borderRadius: '0 0 0 16px',
  },
  modalDetails: {
    padding: '28px 28px 24px',
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 800,
    margin: '0 0 8px',
    color: '#111111',
    lineHeight: 1.25,
  },
  includesList: {
    marginBottom: 14,
  },
  includeItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 8,
    color: '#374151',
    fontSize: 13,
    marginBottom: 5,
  },
  tagRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 20,
  },
  tag: {
    background: '#f3f4f6',
    color: '#374151',
    fontSize: 11,
    fontWeight: 700,
    padding: '3px 8px',
    borderRadius: 4,
  },
  modalCheckoutHint: {
    color: '#6b7280',
    fontSize: 13,
    lineHeight: 1.5,
    margin: '0 0 14px',
  },
  modalFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  guarantees: {
    display: 'flex',
    gap: 16,
    color: '#9ca3af',
    fontSize: 12,
    flexWrap: 'wrap',
  },
  // Trust bar
  trustBar: {
    display: 'flex',
    justifyContent: 'center',
    gap: 36,
    flexWrap: 'wrap',
    padding: '32px 24px',
    borderTop: '1px solid #e5e7eb',
    color: '#9ca3af',
    fontSize: 13,
    background: '#ffffff',
  },
  trustItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  // Success page
  successBox: {
    maxWidth: 520,
    margin: '0 auto',
    padding: '60px 40px',
    textAlign: 'center',
    background: '#ffffff',
    borderRadius: 20,
    border: '1px solid #e5e7eb',
    boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
  },
  successNote: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    background: '#f0fdf4',
    border: '1px solid #bbf7d0',
    color: '#16a34a',
    padding: '12px 20px',
    borderRadius: 8,
    marginBottom: 28,
    fontSize: 14,
  },
  backBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    background: 'transparent',
    border: '1px solid #e5e7eb',
    color: '#6b7280',
    padding: '10px 20px',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: 14,
  },
};
