import React, { useState } from 'react';
import { Rocket, Zap, Mail, FileText, ChevronRight } from 'lucide-react';
import './ProductCard.css';

/**
 * ProductCard - Clean, clickable card for each product
 * Shows product info and action buttons
 */
export const ProductCard = ({ product, onOpen, onGenerateMarketing, onGenerateEmail, onViewDetails }) => {
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
        case 'details':
          onViewDetails?.(product);
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
      className="product-card"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Card Header */}
      <div className="product-card-header">
        <div className="product-thumbnail">
          {product.thumbnail ? (
            <img src={product.thumbnail} alt={product.title} />
          ) : (
            <div className="thumbnail-placeholder">
              <FileText size={40} opacity={0.5} />
            </div>
          )}
        </div>
        <div className="product-meta">
          <h3 className="product-title">{product.title}</h3>
          <p className="product-type">{product.type}</p>
          <p className="product-files">📦 {product.fileCount} files included</p>
        </div>
      </div>

      {/* Card Body */}
      <p className="product-description">{product.description}</p>

      {/* Action Buttons */}
      <div className={`product-actions ${isHovered ? 'visible' : ''}`}>
        <button
          className="action-btn btn-primary"
          onClick={() => handleAction('open')}
          disabled={isLoading['open']}
          title="Open and explore this product"
        >
          <Rocket size={16} />
          <span>{isLoading['open'] ? 'Opening...' : 'Open Product'}</span>
          <ChevronRight size={14} />
        </button>

        <button
          className="action-btn btn-secondary"
          onClick={() => handleAction('marketing')}
          disabled={isLoading['marketing']}
          title="Generate video marketing scripts"
        >
          <Zap size={16} />
          <span>{isLoading['marketing'] ? 'Generating...' : 'Generate Marketing'}</span>
        </button>

        <button
          className="action-btn btn-secondary"
          onClick={() => handleAction('email')}
          disabled={isLoading['email']}
          title="Generate email campaign"
        >
          <Mail size={16} />
          <span>{isLoading['email'] ? 'Generating...' : 'Generate Email'}</span>
        </button>

        <button
          className="action-btn btn-tertiary"
          onClick={() => handleAction('details')}
          disabled={isLoading['details']}
          title="View full product details"
        >
          <FileText size={16} />
          <span>{isLoading['details'] ? 'Loading...' : 'View Details'}</span>
        </button>
      </div>

      {/* Tags */}
      {product.tags && product.tags.length > 0 && (
        <div className="product-tags">
          {product.tags.slice(0, 3).map((tag, idx) => (
            <span key={idx} className="tag">
              {tag}
            </span>
          ))}
          {product.tags.length > 3 && <span className="tag-more">+{product.tags.length - 3}</span>}
        </div>
      )}
    </div>
  );
};

export default ProductCard;
