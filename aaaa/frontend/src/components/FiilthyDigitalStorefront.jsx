import React, { useState, useEffect } from 'react';
import { ShoppingCart, Download, Eye, Star, ChevronRight, Lock, Zap } from 'lucide-react';
import './FiilthyDigitalStorefront.css';

/**
 * FiilthyDigitalStorefront - Complete digital product store
 * Displays Fiilthy digital products with purchase & delivery
 */
export const FiilthyDigitalStorefront = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [userPurchases, setUserPurchases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState([]);
  const [showCheckout, setShowCheckout] = useState(false);

  useEffect(() => {
    loadProducts();
    loadUserPurchases();
  }, []);

  const loadProducts = async () => {
    try {
      // Mock products - replace with API call
      const mockProducts = [
        {
          id: '6a472559-3ab9-4fd4-afec-9a4ed3316cb6',
          title: 'AI-Powered Content Strategy Mastery',
          description: 'Freelance marketers struggling to create consistent, high-quality content—meet your new best friend.',
          fullDescription: 'Transform your content creation process with AI-driven insights that save time and increase engagement. Discover proven strategies and tools that streamline your workflow, enabling you to produce compelling content that resonates with your audience and boosts your bottom line.',
          price: 149,
          originalPrice: 299,
          type: 'template',
          cover: 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-QbPOFuIwfINU4APXuftAIXAv/user-sDce6KMPZefHEaRP6CvLW3FO/img-gs0FHst9jCVhM9LlwpeNHBDJ.png',
          rating: 4.8,
          reviews: 24,
          downloads: 1200,
          includes: [
            'Step-by-step guides',
            'AI content calendars',
            'Actionable checklists',
            'Automation tools',
            'Email templates',
            'Video training'
          ],
          tags: ['AI', 'Content', 'Marketing', 'Templates'],
          fileSize: '245 MB',
          updated: '2026-04-12'
        }
      ];
      setProducts(mockProducts);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserPurchases = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (token) {
        // Mock purchases - replace with real API call
        setUserPurchases([]);
      }
    } catch (error) {
      console.error('Error loading purchases:', error);
    }
  };

  const handleAddToCart = (product) => {
    setCart([...cart, product]);
  };

  const hasPurchased = (productId) => {
    return userPurchases.some(p => p.id === productId);
  };

  return (
    <div className="fiilthy-storefront">
      {/* Hero Section */}
      <div className="storefront-hero">
        <div className="hero-content">
          <h1>🎯 Fiilthy Digital Products</h1>
          <p>Premium templates, guides & tools to scale your business</p>
          <div className="hero-stats">
            <div className="stat">
              <strong>{products.length}</strong>
              <span>Products</span>
            </div>
            <div className="stat">
              <strong>50K+</strong>
              <span>Downloads</span>
            </div>
            <div className="stat">
              <strong>4.9⭐</strong>
              <span>Rating</span>
            </div>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="storefront-grid">
        {loading ? (
          <div className="loading">Loading products...</div>
        ) : products.length === 0 ? (
          <div className="empty">No products yet</div>
        ) : (
          products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              hasPurchased={hasPurchased(product.id)}
              onSelect={() => setSelectedProduct(product)}
              onAddToCart={() => handleAddToCart(product)}
              onBuy={() => {
                setSelectedProduct(product);
                setShowCheckout(true);
              }}
            />
          ))
        )}
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <ProductDetailModal
          product={selectedProduct}
          hasPurchased={hasPurchased(selectedProduct.id)}
          onClose={() => setSelectedProduct(null)}
          onBuy={() => {
            setShowCheckout(true);
          }}
        />
      )}

      {/* Shopping Cart */}
      {cart.length > 0 && (
        <ShoppingCartWidget
          items={cart}
          onCheckout={() => setShowCheckout(true)}
          onRemove={(id) => setCart(cart.filter(item => item.id !== id))}
        />
      )}
    </div>
  );
};

/**
 * ProductCard - Individual product card in grid
 */
const ProductCard = ({ product, hasPurchased, onSelect, onAddToCart, onBuy }) => {
  const discount = Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100);

  return (
    <div className="product-card" onClick={onSelect}>
      <div className="card-image">
        <img src={product.cover} alt={product.title} />
        {discount > 0 && (
          <div className="discount-badge">
            Save {discount}%
          </div>
        )}
        {hasPurchased && (
          <div className="purchased-badge">
            ✓ Owned
          </div>
        )}
      </div>

      <div className="card-content">
        <h3>{product.title}</h3>
        <p className="description">{product.description}</p>

        <div className="card-meta">
          <div className="rating">
            <span className="stars">{'⭐'.repeat(Math.floor(product.rating))}</span>
            <span className="count">({product.reviews})</span>
          </div>
          <div className="downloads">📥 {product.downloads} downloads</div>
        </div>

        <div className="card-footer">
          <div className="price-section">
            {product.originalPrice > product.price && (
              <span className="original-price">${product.originalPrice}</span>
            )}
            <span className="price">${product.price}</span>
          </div>
          
          {hasPurchased ? (
            <button className="btn-download">
              <Download size={16} />
              Download
            </button>
          ) : (
            <button className="btn-buy" onClick={() => onBuy()}>
              <ShoppingCart size={16} />
              Buy Now
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * ProductDetailModal - Full product details
 */
const ProductDetailModal = ({ product, hasPurchased, onClose, onBuy }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>

        <div className="modal-grid">
          {/* Left: Image */}
          <div className="modal-image">
            <img src={product.cover} alt={product.title} />
            <div className="image-meta">
              <div className="meta-item">
                <strong>File Size:</strong> {product.fileSize}
              </div>
              <div className="meta-item">
                <strong>Last Updated:</strong> {product.updated}
              </div>
            </div>
          </div>

          {/* Right: Details */}
          <div className="modal-details">
            <h2>{product.title}</h2>
            <div className="rating-section">
              <div className="stars">{'⭐'.repeat(Math.floor(product.rating))}</div>
              <span>({product.reviews} reviews) • {product.downloads} downloads</span>
            </div>

            <p className="full-description">{product.fullDescription}</p>

            {/* What's Included */}
            <div className="includes-section">
              <h4>📦 What's Included:</h4>
              <ul>
                {product.includes.map((item, idx) => (
                  <li key={idx}>
                    <Zap size={14} />
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Tags */}
            <div className="tags-section">
              {product.tags.map((tag, idx) => (
                <span key={idx} className="tag">{tag}</span>
              ))}
            </div>

            {/* Price & CTA */}
            <div className="modal-footer">
              <div className="price-block">
                {product.originalPrice > product.price && (
                  <span className="original">${product.originalPrice}</span>
                )}
                <span className="current">${product.price}</span>
              </div>

              {hasPurchased ? (
                <button className="btn-primary download-btn">
                  <Download size={18} />
                  Download Product
                </button>
              ) : (
                <button className="btn-primary buy-btn" onClick={onBuy}>
                  <ShoppingCart size={18} />
                  Buy Now - ${product.price}
                </button>
              )}
            </div>

            {/* Guarantees */}
            <div className="guarantees">
              <div className="guarantee">
                <Lock size={14} />
                <span>Secure checkout with Stripe</span>
              </div>
              <div className="guarantee">
                <Eye size={14} />
                <span>30-day money-back guarantee</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * ShoppingCartWidget - Floating shopping cart
 */
const ShoppingCartWidget = ({ items, onCheckout, onRemove }) => {
  const total = items.reduce((sum, item) => sum + item.price, 0);

  return (
    <div className="cart-widget">
      <div className="cart-header">
        <ShoppingCart size={18} />
        <span className="cart-count">{items.length}</span>
      </div>

      <div className="cart-preview">
        {items.map((item) => (
          <div key={item.id} className="cart-item">
            <div className="item-info">
              <span className="item-title">{item.title}</span>
              <span className="item-price">${item.price}</span>
            </div>
            <button onClick={() => onRemove(item.id)} className="remove-btn">✕</button>
          </div>
        ))}
      </div>

      <div className="cart-footer">
        <div className="cart-total">
          Total: <strong>${total}</strong>
        </div>
        <button className="checkout-btn" onClick={onCheckout}>
          Checkout
        </button>
      </div>
    </div>
  );
};

export default FiilthyDigitalStorefront;
