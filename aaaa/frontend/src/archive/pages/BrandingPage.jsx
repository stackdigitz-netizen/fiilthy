import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Palette, RefreshCw } from 'lucide-react';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

const paletteByType = {
  ebook: ['#0ea5e9', '#06b6d4', '#082f49'],
  course: ['#10b981', '#14b8a6', '#052e16'],
  template: ['#f59e0b', '#f97316', '#431407'],
  planner: ['#8b5cf6', '#ec4899', '#4a044e'],
  mini_app: ['#6366f1', '#3b82f6', '#172554'],
  default: ['#0ea5e9', '#10b981', '#111827']
};

const brandDeliverables = [
  {
    title: 'Logo Direction',
    description: 'Primary mark, icon mark, and inverted variants scoped to the selected product.'
  },
  {
    title: 'Cover Artwork',
    description: 'Hero imagery sized for storefronts, checkout, and preview pages.'
  },
  {
    title: 'Social Header Set',
    description: 'Reusable headers and thumbnails for campaign launches across major channels.'
  },
  {
    title: 'Email Visuals',
    description: 'Newsletter header, announcement banner, and product callout treatments.'
  },
  {
    title: 'Sales Visual Kit',
    description: 'Checkout accents, testimonial framing, and CTA graphic guidance.'
  },
  {
    title: 'Usage Guide',
    description: 'Short notes for consistent typography, color, and icon usage.'
  }
];

const titleCase = (value) =>
  String(value || 'unknown')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());

const BrandingPage = () => {
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    if (!selectedProductId && products.length > 0) {
      setSelectedProductId(products[0].id);
    }
  }, [products, selectedProductId]);

  const loadProducts = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API}/api/products?limit=100`);
      if (!response.ok) {
        throw new Error(`Failed to load products (${response.status})`);
      }

      const data = await response.json();
      setProducts(Array.isArray(data) ? data : []);
    } catch (loadError) {
      console.error('Failed to load products for branding:', loadError);
      setError(loadError.message);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const selectedProduct = useMemo(() => {
    return products.find((product) => product.id === selectedProductId) || null;
  }, [products, selectedProductId]);

  const palette = paletteByType[selectedProduct?.product_type] || paletteByType.default;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Branding Studio</h1>
        <p>Review live products and prepare branding work from real product records</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="content-section">
        <div className="section-header">
          <h2>Select Product</h2>
          <button className="btn btn-secondary" onClick={loadProducts} disabled={loading}>
            <RefreshCw size={16} /> {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {loading ? (
          <div className="empty-state">
            <p>Loading products from the backend...</p>
          </div>
        ) : products.length === 0 ? (
          <div className="empty-state">
            <p>No products exist yet. Create a product first to build a real branding brief.</p>
          </div>
        ) : (
          <div className="button-group">
            {products.map((product) => (
              <button
                key={product.id}
                className={`btn ${selectedProductId === product.id ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setSelectedProductId(product.id)}
              >
                {product.title}
              </button>
            ))}
          </div>
        )}
      </div>

      {selectedProduct && (
        <>
          <div className="grid-2">
            <div className="content-section">
              <h3>Product Brief</h3>
              <div className="stack-list">
                <div className="detail-row">
                  <span>Status</span>
                  <span className="badge badge-secondary">{titleCase(selectedProduct.status)}</span>
                </div>
                <div className="detail-row">
                  <span>Type</span>
                  <span className="metric-value">{titleCase(selectedProduct.product_type)}</span>
                </div>
                <div className="detail-row">
                  <span>Price</span>
                  <span className="metric-value">{currencyFormatter.format(selectedProduct.price || 0)}</span>
                </div>
                <div className="detail-row">
                  <span>Revenue</span>
                  <span className="metric-value">{currencyFormatter.format(selectedProduct.revenue || 0)}</span>
                </div>
                <div className="detail-row">
                  <span>Conversions</span>
                  <span className="metric-value">{selectedProduct.conversions || 0}</span>
                </div>
              </div>
              <p className="text-secondary mt-3">{selectedProduct.description}</p>
              {(selectedProduct.tags || []).length > 0 && (
                <div className="inline-tags mt-3">
                  {selectedProduct.tags.map((tag) => (
                    <span key={tag} className="badge badge-secondary">{tag}</span>
                  ))}
                </div>
              )}
            </div>

            <div className="content-section">
              <h3>Recommended Palette</h3>
              <p className="text-secondary mb-4">
                This palette is derived from the selected product type and can be refined when assets are generated.
              </p>
              <div className="color-palette">
                {palette.map((color) => (
                  <div key={color} className="color-swatch" style={{ backgroundColor: color }}>
                    <span>{color.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="content-section">
            <h2>Suggested Brand Outputs</h2>
            <div className="grid-3">
              {brandDeliverables.map((deliverable) => (
                <div key={deliverable.title} className="asset-card">
                  <div className="product-header">
                    <h3>{deliverable.title}</h3>
                    <span className="badge badge-secondary">Ready to plan</span>
                  </div>
                  <p>{deliverable.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid-2">
            <div className="content-section">
              <h3>Marketplace Links</h3>
              {(selectedProduct.marketplace_links || []).length === 0 ? (
                <div className="empty-state">
                  <p>No marketplace links have been published for this product yet.</p>
                </div>
              ) : (
                <div className="stack-list">
                  {selectedProduct.marketplace_links.map((link) => (
                    <div key={`${selectedProduct.id}-${link.platform}`} className="detail-row">
                      <span>{link.platform}</span>
                      <a href={link.url} target="_blank" rel="noreferrer" className="inline-code">
                        {link.status || 'ready'}
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="content-section">
              <h3>Messaging Anchors</h3>
              <div className="stack-list">
                <div className="detail-row">
                  <span>Core Offer</span>
                  <span className="metric-value">{selectedProduct.title}</span>
                </div>
                <div className="detail-row">
                  <span>Product Type</span>
                  <span className="metric-value">{titleCase(selectedProduct.product_type)}</span>
                </div>
                <div className="detail-row">
                  <span>Primary CTA</span>
                  <span className="metric-value">Lead with the transformation, then show the product.</span>
                </div>
              </div>
              <p className="text-secondary mt-3">
                Use the product description as the source of truth for copy tone and visual hierarchy:
                {' '}
                {selectedProduct.description}
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default BrandingPage;
