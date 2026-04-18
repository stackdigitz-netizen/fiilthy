import React, { useState, useEffect } from 'react';
import { Rocket, Zap, Mail, FileText, ChevronRight, Loader, Plus, Download } from 'lucide-react';
import { ProductFilesService } from '../services/ProductFilesService';
import './ProductsDashboard.css';

/**
 * ProductsDashboard - Integrated into CEO app
 * Shows all generated products and allows actions
 */
export const ProductsDashboard = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState('grid'); // grid or detail

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ProductFilesService.getAllProducts();
      setProducts(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
      console.error('Error loading products:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenProduct = (product) => {
    setSelectedProduct(product);
    setActiveTab('detail');
  };

  const handleGenerateMarketing = async (product) => {
    setIsGenerating(true);
    setSelectedProduct(product);
    try {
      const content = await ProductFilesService.generateMarketingContent(product.id);
      setGeneratedContent(content);
      setActiveTab('detail');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateEmail = async (product) => {
    setIsGenerating(true);
    setSelectedProduct(product);
    try {
      const content = await ProductFilesService.generateEmailCampaign(product.id);
      setGeneratedContent(content);
      setActiveTab('detail');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleOwnerDownload = async (product) => {
    try {
      await ProductFilesService.downloadOwnerBundle(product);
    } catch (err) {
      setError(err.message || 'Failed to download product bundle');
    }
  };

  return (
    <div className="products-dashboard">
      {/* Header */}
      <div className="products-header">
        <div>
          <h1>Your Products</h1>
          <p>Manage, view, and generate content for your digital products</p>
        </div>
        <button className="btn-new-product">
          <Plus size={18} />
          <span>Generate New Product</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="products-tabs">
        <button
          className={`tab ${activeTab === 'grid' ? 'active' : ''}`}
          onClick={() => setActiveTab('grid')}
        >
          📦 All Products ({products.length})
        </button>
        {selectedProduct && (
          <button
            className={`tab ${activeTab === 'detail' ? 'active' : ''}`}
            onClick={() => setActiveTab('detail')}
          >
            👁 {selectedProduct.title}
          </button>
        )}
      </div>

      {/* Grid View */}
      {activeTab === 'grid' && (
        <div className="products-grid-view">
          {loading ? (
            <div className="loading-state">
              <Loader size={48} />
              <p>Loading your products...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>⚠️ {error}</p>
              <button onClick={loadProducts}>Try Again</button>
            </div>
          ) : products.length === 0 ? (
            <div className="empty-state">
              <FileText size={64} opacity={0.3} />
              <p>No products yet. Generate your first product to get started!</p>
            </div>
          ) : (
            <div className="products-grid">
              {products.map((product) => (
                <ProductCardItem
                  key={product.id}
                  product={product}
                  onOpen={handleOpenProduct}
                  onGenerateMarketing={handleGenerateMarketing}
                  onGenerateEmail={handleGenerateEmail}
                  onDownloadBundle={handleOwnerDownload}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Detail View */}
      {activeTab === 'detail' && selectedProduct && (
        <ProductDetailView
          product={selectedProduct}
          generatedContent={generatedContent}
          isGenerating={isGenerating}
          onGenerateMarketing={() => handleGenerateMarketing(selectedProduct)}
          onGenerateEmail={() => handleGenerateEmail(selectedProduct)}
          onDownloadBundle={() => handleOwnerDownload(selectedProduct)}
          onBack={() => setActiveTab('grid')}
        />
      )}
    </div>
  );
};

/**
 * ProductCardItem - Individual product card
 */
const ProductCardItem = ({ product, onOpen, onGenerateMarketing, onGenerateEmail, onDownloadBundle }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState({});

  const handleAction = async (action) => {
    setIsLoading({ ...isLoading, [action]: true });
    try {
      switch (action) {
        case 'open':
          onOpen?.(product);
          break;
        case 'marketing':
          await onGenerateMarketing?.(product);
          break;
        case 'email':
          await onGenerateEmail?.(product);
          break;
        case 'download':
          await onDownloadBundle?.(product);
          break;
        default:
          break;
      }
    } finally {
      setIsLoading({ ...isLoading, [action]: false });
    }
  };

  return (
    <div
      className="product-card-item"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Card Header */}
      <div className="card-header">
        <div className="card-thumbnail">
          {product.thumbnail ? (
            <img src={product.thumbnail} alt={product.title} />
          ) : (
            <div className="thumbnail-placeholder">
              <FileText size={40} opacity={0.5} />
            </div>
          )}
        </div>
        <div className="card-meta">
          <h3 className="card-title">{product.title}</h3>
          <p className="card-type">{product.type || 'Digital Product'}</p>
          <p className="card-files">📦 {product.fileCount || 0} files</p>
        </div>
      </div>

      {/* Card Body */}
      <p className="card-description">{product.description}</p>

      {/* Action Buttons */}
      <div className={`card-actions ${isHovered ? 'visible' : ''}`}>
        <button
          className="action-btn primary"
          onClick={() => handleAction('open')}
          disabled={isLoading['open']}
        >
          <Rocket size={16} />
          <span>{isLoading['open'] ? 'Opening...' : 'Open Product'}</span>
        </button>

        <button
          className="action-btn secondary"
          onClick={() => handleAction('marketing')}
          disabled={isLoading['marketing']}
        >
          <Zap size={16} />
          <span>{isLoading['marketing'] ? 'Generating...' : '🎬 Marketing'}</span>
        </button>

        <button
          className="action-btn secondary"
          onClick={() => handleAction('email')}
          disabled={isLoading['email']}
        >
          <Mail size={16} />
          <span>{isLoading['email'] ? 'Generating...' : '📧 Email'}</span>
        </button>

        <button
          className="action-btn secondary"
          onClick={() => handleAction('download')}
          disabled={isLoading['download']}
        >
          <Download size={16} />
          <span>{isLoading['download'] ? 'Preparing...' : '⬇️ Download'}</span>
        </button>
      </div>

      {/* Tags */}
      {product.tags && product.tags.length > 0 && (
        <div className="card-tags">
          {product.tags.slice(0, 2).map((tag, idx) => (
            <span key={idx} className="tag">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * ProductDetailView - Full product details and generated content
 */
const ProductDetailView = ({
  product,
  generatedContent,
  isGenerating,
  onGenerateMarketing,
  onGenerateEmail,
  onDownloadBundle,
  onBack,
}) => {
  return (
    <div className="product-detail-view">
      {/* Back Button */}
      <button className="btn-back" onClick={onBack}>
        ← Back to Products
      </button>

      <div className="detail-content">
        {/* Product Info */}
        <div className="detail-section info-section">
          <div className="info-header">
            {product.thumbnail && <img src={product.thumbnail} alt={product.title} className="detail-thumbnail" />}
            <div className="info-text">
              <h2>{product.title}</h2>
              <p className="detail-description">{product.description}</p>
              <div className="detail-meta">
                <span>Type: {product.type || 'Digital'}</span>
                <span>Files: {product.fileCount || 0}</span>
                {product.price && <span>Price: ${product.price}</span>}
              </div>
            </div>
          </div>
        </div>

        {/* Generated Content */}
        {generatedContent && (
          <div className="detail-section generated-section">
            <h3>📺 Generated Marketing Content</h3>
            <GeneratedContentDisplay content={generatedContent} />
          </div>
        )}

        {/* Action Section */}
        <div className="detail-section action-section">
          <h3>Generate Content</h3>
          <div className="action-buttons">
            <button className="btn-action" onClick={onGenerateMarketing} disabled={isGenerating}>
              {isGenerating ? (
                <>
                  <Loader size={18} className="spinner" />
                  Generating Marketing...
                </>
              ) : (
                <>
                  <Zap size={18} />
                  Generate Marketing Videos & Scripts
                </>
              )}
            </button>

            <button className="btn-action" onClick={onGenerateEmail} disabled={isGenerating}>
              {isGenerating ? (
                <>
                  <Loader size={18} className="spinner" />
                  Generating Email...
                </>
              ) : (
                <>
                  <Mail size={18} />
                  Generate Email Campaign
                </>
              )}
            </button>

            <button className="btn-action" onClick={onDownloadBundle} disabled={isGenerating}>
              <Download size={18} />
              Download Product Bundle
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * GeneratedContentDisplay - Shows generated marketing content
 */
const GeneratedContentDisplay = ({ content }) => {
  if (!content) return null;

  return (
    <div className="generated-content">
      {content.videoScripts && content.videoScripts.length > 0 && (
        <div className="content-block">
          <h4>🎬 Video Scripts</h4>
          {content.videoScripts.map((script, idx) => (
            <div key={idx} className="content-item">
              <p>{script}</p>
            </div>
          ))}
        </div>
      )}

      {content.hooks && content.hooks.length > 0 && (
        <div className="content-block">
          <h4>🎣 Hooks</h4>
          {content.hooks.map((hook, idx) => (
            <div key={idx} className="content-item hook">
              "{hook}"
            </div>
          ))}
        </div>
      )}

      {content.captions && content.captions.length > 0 && (
        <div className="content-block">
          <h4>📱 Social Captions</h4>
          {content.captions.map((caption, idx) => (
            <div key={idx} className="content-item caption">
              {caption}
            </div>
          ))}
        </div>
      )}

      {content.ctas && content.ctas.length > 0 && (
        <div className="content-block">
          <h4>🎯 Call-to-Actions</h4>
          {content.ctas.map((cta, idx) => (
            <div key={idx} className="content-item cta">
              {cta}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductsDashboard;
