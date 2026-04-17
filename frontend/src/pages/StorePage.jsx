import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
  ShoppingCart, Download, Star, Check, Zap, Lock, Mail, X,
  ArrowLeft, Package,
} from 'lucide-react';

const API = typeof window !== 'undefined' && window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://backend-seven-beta-88.vercel.app';

const CACHE_KEY = 'store_products_v3';
const CACHE_TIME = 5 * 60 * 1000; // 5 minutes

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
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [checkoutLoading, setCheckoutLoading] = useState(null); // holds product id
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const isSuccess = params.get('success') === '1';
  const sessionId = params.get('session_id');

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

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const handleBuy = async (product) => {
    const normalizedEmail = email.trim();
    if (!normalizedEmail) {
      setEmailError('Enter your email to continue');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
      setEmailError('Please enter a valid email address');
      return;
    }
    setEmailError('');
    setCheckoutLoading(product.id);
    try {
      window.localStorage.setItem('storeCheckoutEmail', normalizedEmail);
      const res = await fetch(`${API}/api/store/checkout/${product.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_email: normalizedEmail, quantity: 1 }),
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

  if (isSuccess) return <SuccessPage sessionId={sessionId} />;

  return (
    <div style={s.page}>
      {/* Header */}
      <div style={s.header}>
        <div style={s.headerInner}>
          <span style={s.logo}>FiiLTHY<span style={{ color: '#00e5ff' }}>.ai</span></span>
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
          <Mail size={20} style={{ color: '#00e5ff', flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <p style={s.emailLabel}>Your download is sent here after purchase</p>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={e => { setEmail(e.target.value); setEmailError(''); }}
              style={s.emailInput}
            />
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
            {products.length === 0 ? <p style={{ color: '#555', textAlign: 'center', padding: '60px 0' }}>No products available</p> : products.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onSelect={() => setSelectedProduct(product)}
                onBuy={() => handleBuy(product)}
                isLoading={checkoutLoading === product.id}
              />
            ))}
          </div>
        )}
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
        />
      )}
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
        <h1 style={{ color: '#00e5ff', fontSize: 28, fontWeight: 800, margin: '0 0 12px' }}>
          Payment Successful!
        </h1>
        <p style={{ color: '#aaa', fontSize: 16, lineHeight: 1.6, marginBottom: 24 }}>
          Your purchase is confirmed.
          <br />
          Your download can be unlocked right here, and we'll email it when delivery is configured.
        </p>
        <div style={{ marginBottom: 16, textAlign: 'left' }}>
          <p style={{ color: '#d1d5db', fontSize: 13, marginBottom: 8 }}>Purchase email</p>
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
              background: '#111827',
              color: '#fff',
              border: '1px solid #223047',
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

function ProductCard({ product, onSelect, onBuy, isLoading }) {
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
          >
            <ShoppingCart size={14} />
            {isLoading ? 'Loading…' : 'Buy Now'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Product Modal ────────────────────────────────────────────────────────────

function ProductModal({ product, onClose, onBuy, isLoading }) {
  const discount =
    product.originalPrice > product.price
      ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
      : 0;

  return (
    <div style={s.overlay} onClick={onClose}>
      <div style={s.modal} onClick={e => e.stopPropagation()}>
        <button style={s.closeBtn} onClick={onClose}>
          <X size={18} />
        </button>
        <div style={s.modalInner}>
          {/* Left image */}
          <div style={s.modalImgWrap}>
            <img src={product.cover} alt={product.title} style={s.modalImg} />
            <div style={s.fileInfo}>
              <Package size={14} />
              <span>{product.fileSize || '—'} · Updated {(product.updated || '').slice(0,10)}</span>
            </div>
          </div>

          {/* Right details */}
          <div style={s.modalDetails}>
            <div style={s.cardTypePill}>{product.type || 'guide'}</div>
            <h2 style={s.modalTitle}>{product.title}</h2>
            <div style={{ color: '#f59e0b', marginBottom: 8 }}>
              {'★'.repeat(Math.floor(product.rating || 4.8))}
              <span style={{ color: '#666', marginLeft: 6, fontSize: 13 }}>
                {product.reviews || 0} reviews · {(product.downloads || 0).toLocaleString()} downloads
              </span>
            </div>
            <p style={{ color: '#aaa', fontSize: 14, lineHeight: 1.6, marginBottom: 16 }}>
              {product.description}
            </p>

            {/* Includes */}
            {(product.includes || []).length > 0 && (
              <div style={s.includesList}>
                <p style={{ color: '#fff', fontWeight: 700, marginBottom: 8 }}>📦 What's Included:</p>
                {product.includes.map((item, i) => (
                  <div key={i} style={s.includeItem}>
                    <Check size={14} style={{ color: '#00e5ff', flexShrink: 0 }} />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Tags */}
            {(product.tags || []).length > 0 && (
              <div style={s.tagRow}>
                {product.tags.map((t, i) => <span key={i} style={s.tag}>{t}</span>)}
              </div>
            )}

            {/* Price + CTA */}
            <div style={s.modalFooter}>
              <div style={s.priceRow}>
                {discount > 0 && <span style={s.origPrice}>${product.originalPrice}</span>}
                <span style={{ ...s.price, fontSize: 30 }}>${product.price}</span>
              </div>
              <button
                style={{ ...s.buyBtn, padding: '12px 22px', fontSize: 15, opacity: isLoading ? 0.7 : 1 }}
                onClick={onBuy}
                disabled={isLoading}
              >
                <ShoppingCart size={16} />
                {isLoading ? 'Loading…' : `Buy Now — $${product.price}`}
              </button>
            </div>

            {/* Guarantees */}
            <div style={s.guarantees}>
              <span><Lock size={12} style={{ marginRight: 4 }} />Secure Stripe</span>
              <span><Check size={12} style={{ marginRight: 4 }} />30-day refund</span>
              <span><Download size={12} style={{ marginRight: 4 }} />Instant download</span>
            </div>
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
      <div style={{ color: '#00e5ff', fontWeight: 800, fontSize: 22 }}>{value}</div>
      <div style={{ color: '#555', fontSize: 12, marginTop: 2 }}>{label}</div>
    </div>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const s = {
  page: {
    background: '#07080f',
    minHeight: '100vh',
    color: '#fff',
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
  },
  header: {
    borderBottom: '1px solid #1a2a3a',
    padding: '14px 24px',
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
    color: '#fff',
  },
  tagline: {
    color: '#555',
    fontSize: 14,
  },
  hero: {
    textAlign: 'center',
    padding: '70px 20px 50px',
    background: 'radial-gradient(ellipse 80% 60% at 50% 0%, #0a1628 0%, #07080f 100%)',
  },
  heroTitle: {
    fontSize: 'clamp(30px, 5vw, 56px)',
    fontWeight: 900,
    color: '#fff',
    margin: '0 0 14px',
    letterSpacing: '-2px',
    lineHeight: 1.1,
  },
  heroSub: {
    color: '#888',
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
    background: '#0d1117',
    border: '1px solid #1a2a3a',
    borderRadius: 12,
    padding: '18px 20px',
  },
  emailLabel: {
    color: '#aaa',
    fontSize: 13,
    margin: '0 0 8px',
  },
  emailInput: {
    width: '100%',
    padding: '11px 14px',
    background: '#07080f',
    border: '1px solid #1a2a3a',
    borderRadius: 8,
    color: '#fff',
    fontSize: 15,
    outline: 'none',
    boxSizing: 'border-box',
  },
  emailError: {
    color: '#f87171',
    fontSize: 12,
    margin: '6px 0 0',
  },
  sectionWrap: {
    maxWidth: 1200,
    margin: '0 auto',
    padding: '0 24px 60px',
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 800,
    marginBottom: 24,
    letterSpacing: '-0.5px',
  },
  loadingBox: {
    color: '#555',
    textAlign: 'center',
    padding: '60px 0',
  },
  errorBox: {
    textAlign: 'center',
    padding: '60px 0',
    color: '#f87171',
  },
  retryButton: {
    background: '#00e5ff',
    color: '#000',
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
    background: '#0d1117',
    border: '1px solid #1a2a3a',
    borderRadius: 12,
    overflow: 'hidden',
    cursor: 'pointer',
    transition: 'border-color 0.15s, transform 0.15s',
  },
  cardImgWrap: {
    height: 186,
    position: 'relative',
    overflow: 'hidden',
    background: '#1a2a3a',
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
    background: '#00e5ff',
    color: '#000',
    fontSize: 11,
    fontWeight: 800,
    padding: '3px 8px',
    borderRadius: 4,
  },
  cardTypePill: {
    display: 'inline-block',
    background: 'rgba(0,229,255,0.12)',
    color: '#00e5ff',
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
    color: '#fff',
    lineHeight: 1.3,
  },
  cardDesc: {
    color: '#777',
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
    color: '#444',
    fontSize: 13,
    textDecoration: 'line-through',
  },
  price: {
    color: '#00e5ff',
    fontSize: 22,
    fontWeight: 800,
  },
  buyBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '8px 14px',
    background: '#00e5ff',
    color: '#000',
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
    background: 'rgba(0,0,0,0.88)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: 20,
  },
  modal: {
    background: '#0d1117',
    border: '1px solid #1a2a3a',
    borderRadius: 16,
    maxWidth: 820,
    width: '100%',
    maxHeight: '92vh',
    overflowY: 'auto',
    position: 'relative',
  },
  closeBtn: {
    position: 'absolute',
    top: 12,
    right: 12,
    background: '#1a2a3a',
    border: 'none',
    color: '#aaa',
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
    background: '#07080f',
    color: '#555',
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
    color: '#fff',
    lineHeight: 1.25,
  },
  includesList: {
    marginBottom: 14,
  },
  includeItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 8,
    color: '#aaa',
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
    background: '#1a2a3a',
    color: '#00e5ff',
    fontSize: 11,
    fontWeight: 700,
    padding: '3px 8px',
    borderRadius: 4,
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
    color: '#444',
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
    borderTop: '1px solid #111',
    color: '#444',
    fontSize: 13,
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
    background: '#0d1117',
    borderRadius: 20,
    border: '1px solid #00e5ff33',
  },
  successNote: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    background: '#001a22',
    border: '1px solid #00e5ff44',
    color: '#00e5ff',
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
    border: '1px solid #1a2a3a',
    color: '#aaa',
    padding: '10px 20px',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: 14,
  },
};
