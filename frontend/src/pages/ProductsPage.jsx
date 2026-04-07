import React, { useState, useEffect } from 'react';
import { Package, Clock, TrendingUp, Zap, Image, Loader, Check, X } from 'lucide-react';
import './Pages.css';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generatedProduct, setGeneratedProduct] = useState(null);
  const [concept, setConcept] = useState('');
  const [keywords, setKeywords] = useState('');
  const [generateImage, setGenerateImage] = useState(true);
  const [generationError, setGenerationError] = useState(null);
  const [fetchingProducts, setFetchingProducts] = useState(false);
  const [checkoutModal, setCheckoutModal] = useState(null);
  const [checkoutEmail, setCheckoutEmail] = useState('');
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  // Load products from backend on mount
  useEffect(() => {
    loadProductsFromBackend();
  }, []);

  const loadProductsFromBackend = async () => {
    setFetchingProducts(true);
    try {
      const response = await fetch('http://localhost:8000/api/products');
      if (response.ok) {
        const data = await response.json();
        setProducts(data);
      }
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setFetchingProducts(false);
    }
  };

  const generateProduct = async (e) => {
    e.preventDefault();
    setLoading(true);
    setGenerationError(null);
    setGeneratedProduct(null);

    try {
      if (!concept.trim()) {
        throw new Error('Please enter a product concept');
      }

      const keywordArray = keywords.split(',').map(k => k.trim()).filter(k => k);

      const response = await fetch('http://localhost:8000/api/ai/generate-full-product', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept: concept.trim(),
          keywords: keywordArray,
          generate_image: generateImage,
          save_to_db: true
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }

      const result = await response.json();
      setGeneratedProduct(result);
      setConcept('');
      setKeywords('');
      
      // Reload products list
      loadProductsFromBackend();
    } catch (error) {
      setGenerationError(error.message);
      console.error('Generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const addProductToList = () => {
    if (generatedProduct) {
      loadProductsFromBackend();
      setGeneratedProduct(null);
    }
  };

  const handleCheckout = async (productId) => {
    if (!checkoutEmail) {
      alert('Please enter an email address');
      return;
    }

    setCheckoutLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/payments/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: productId,
          customer_email: checkoutEmail,
          quantity: 1
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout');
      }

      const result = await response.json();
      // Redirect to Stripe checkout
      window.location.href = result.checkout_url;
    } catch (error) {
      alert(`Error: ${error.message}`);
      console.error('Checkout error:', error);
    } finally {
      setCheckoutLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>🚀 Product Factory</h1>
        <p>AI-powered product generation and management</p>
      </div>

      {/* AI Product Generator Section */}
      <div className="content-section" style={{ backgroundColor: '#f8f9ff', border: '2px solid #007bff' }}>
        <div className="section-header">
          <h2>⚡ Generate Product with AI</h2>
          <p className="text-secondary">Describe your product idea and let AI create everything</p>
        </div>

        <form onSubmit={generateProduct} style={{ maxWidth: '600px' }}>
          <div className="form-group">
            <label>Product Concept *</label>
            <textarea
              placeholder="e.g., AI-powered email marketing course with copywriting templates"
              value={concept}
              onChange={(e) => setConcept(e.target.value)}
              rows="3"
              style={{
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontFamily: 'inherit'
              }}
            />
          </div>

          <div className="form-group">
            <label>Keywords (Optional)</label>
            <input
              type="text"
              placeholder="e.g., email marketing, AI, automation, copywriting"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              style={{
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '6px'
              }}
            />
            <small style={{ color: '#666', marginTop: '4px', display: 'block' }}>Separate with commas</small>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={generateImage}
                onChange={(e) => setGenerateImage(e.target.checked)}
                style={{ marginRight: '8px', width: '16px', height: '16px' }}
              />
              <span>Generate product image with AI</span>
            </label>
          </div>

          {generationError && (
            <div style={{
              padding: '12px',
              backgroundColor: '#f8d7da',
              color: '#721c24',
              borderRadius: '6px',
              marginBottom: '16px',
              border: '1px solid #f5c6cb'
            }}>
              {generationError}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '12px 24px',
              backgroundColor: loading ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            {loading ? '🔄 Generating...' : '⚡ Generate Product'}
          </button>
        </form>
      </div>

      {/* Generated Product Preview */}
      {generatedProduct && (
        <div className="content-section" style={{ backgroundColor: '#f0f9ff', border: '2px solid #28a745' }}>
          <div className="section-header">
            <h2>✨ Generated Product Preview</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', alignItems: 'start' }}>
            {/* Product Info */}
            <div>
              <h3>{generatedProduct.product.title}</h3>
              <p style={{ color: '#555', marginBottom: '16px', lineHeight: '1.6' }}>
                {generatedProduct.product.description}
              </p>

              <div style={{ marginBottom: '16px' }}>
                <strong>Price Range:</strong> {generatedProduct.product.price_range}
              </div>

              <div style={{ marginBottom: '16px' }}>
                <strong>Target Audience:</strong><br />
                {generatedProduct.product.target_audience}
              </div>

              <div style={{ marginBottom: '16px' }}>
                <strong>Keywords:</strong><br />
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                  {generatedProduct.product.keywords.map((kw, idx) => (
                    <span
                      key={idx}
                      style={{
                        backgroundColor: '#e7f3ff',
                        color: '#0066cc',
                        padding: '4px 12px',
                        borderRadius: '16px',
                        fontSize: '12px'
                      }}
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              <div style={{ marginTop: '20px', display: 'flex', gap: '12px' }}>
                <button
                  onClick={addProductToList}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  ✓ Product Saved
                </button>
              </div>
            </div>

            {/* Product Image */}
            {generatedProduct.image && (
              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <div style={{ maxWidth: '300px' }}>
                  <img
                    src={generatedProduct.image.image_url}
                    alt={generatedProduct.product.title}
                    style={{
                      width: '100%',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                  />
                  <p style={{ fontSize: '12px', color: '#999', marginTop: '8px', textAlign: 'center' }}>
                    Generated with DALL-E
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Products List */}
      <div className="content-section">
        <div className="section-header">
          <h2>📦 All Products ({products.length})</h2>
          <button
            onClick={loadProductsFromBackend}
            disabled={fetchingProducts}
            style={{
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: fetchingProducts ? 'not-allowed' : 'pointer',
              fontSize: '14px'
            }}
          >
            {fetchingProducts ? 'Loading...' : '🔄 Refresh'}
          </button>
        </div>

        {products.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            <p>No products yet. Generate your first product above!</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #ddd' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Product</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Price Range</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Target Audience</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Created</th>
                  <th style={{ padding: '12px', textAlign: 'center' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {products.slice(0, 10).map((product, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '12px' }}>
                      <div>
                        <strong>{product.title}</strong>
                      </div>
                    </td>
                    <td style={{ padding: '12px' }}>{product.price_range || 'TBD'}</td>
                    <td style={{ padding: '12px' }}>{product.target_audience || 'General'}</td>
                    <td style={{ padding: '12px', fontSize: '12px', color: '#999' }}>
                      {new Date(product.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <button
                        onClick={() => setCheckoutModal(products[idx])}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        💳 Sell
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Checkout Modal */}
      {checkoutModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '32px',
            borderRadius: '12px',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
          }}>
            <h2>💳 Create Checkout</h2>
            <p style={{ color: '#666', marginBottom: '24px' }}>
              Product: <strong>{checkoutModal.title}</strong>
            </p>

            <div className="form-group">
              <label>Customer Email *</label>
              <input
                type="email"
                placeholder="customer@example.com"
                value={checkoutEmail}
                onChange={(e) => setCheckoutEmail(e.target.value)}
                style={{
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  width: '100%',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div style={{
              padding: '16px',
              backgroundColor: '#f0f9ff',
              borderRadius: '6px',
              marginBottom: '24px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>Price Range:</span>
                <strong>{checkoutModal.price_range || '$29.99'}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Customer Email:</span>
                <strong>{checkoutEmail || 'TBD'}</strong>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => handleCheckout(checkoutModal.id)}
                disabled={checkoutLoading}
                style={{
                  flex: 1,
                  padding: '12px',
                  backgroundColor: checkoutLoading ? '#ccc' : '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: checkoutLoading ? 'not-allowed' : 'pointer',
                  fontWeight: '600'
                }}
              >
                {checkoutLoading ? 'Creating...' : '→ Proceed to Stripe'}
              </button>
              <button
                onClick={() => {
                  setCheckoutModal(null);
                  setCheckoutEmail('');
                }}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#f0f0f0',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductsPage;
