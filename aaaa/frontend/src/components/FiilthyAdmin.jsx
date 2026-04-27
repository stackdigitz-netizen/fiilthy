import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Eye, DollarSign, Download, Users } from 'lucide-react';
import './FiilthyAdmin.css';

/**
 * FiilthyAdmin - Complete admin dashboard for Fiilthy storefront
 * Manage products, sales, downloads, and analytics
 */
export const FiilthyAdmin = () => {
  const [activeTab, setActiveTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [sales, setSales] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [productsRes, salesRes, analyticsRes] = await Promise.all([
        fetch('/api/fiilthy/admin/products', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        }),
        fetch('/api/fiilthy/admin/sales', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        }),
        fetch('/api/fiilthy/admin/analytics', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        })
      ]);

      if (productsRes.ok) setProducts(await productsRes.json());
      if (salesRes.ok) setSales(await salesRes.json());
      if (analyticsRes.ok) setAnalytics(await analyticsRes.json());
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fiilthy-admin">
      {/* Header */}
      <div className="admin-header">
        <h1>🎛️ Fiilthy Admin Dashboard</h1>
        <p>Manage products, sales, and analytics</p>
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        <button
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          📊 Analytics
        </button>
        <button
          className={`tab ${activeTab === 'products' ? 'active' : ''}`}
          onClick={() => setActiveTab('products')}
        >
          📦 Products ({products.length})
        </button>
        <button
          className={`tab ${activeTab === 'sales' ? 'active' : ''}`}
          onClick={() => setActiveTab('sales')}
        >
          💳 Sales ({sales.length})
        </button>
      </div>

      {/* Content */}
      <div className="admin-content">
        {activeTab === 'analytics' && (
          <AnalyticsTab analytics={analytics} sales={sales} products={products} />
        )}
        {activeTab === 'products' && (
          <ProductsTab
            products={products}
            onAdd={() => {
              setEditingProduct(null);
              setShowProductForm(true);
            }}
            onEdit={(product) => {
              setEditingProduct(product);
              setShowProductForm(true);
            }}
            onRefresh={loadAdminData}
          />
        )}
        {activeTab === 'sales' && (
          <SalesTab sales={sales} />
        )}
      </div>

      {/* Product Form Modal */}
      {showProductForm && (
        <ProductFormModal
          product={editingProduct}
          onClose={() => {
            setShowProductForm(false);
            setEditingProduct(null);
          }}
          onSave={() => {
            setShowProductForm(false);
            loadAdminData();
          }}
        />
      )}
    </div>
  );
};

/**
 * AnalyticsTab - Dashboard analytics
 */
const AnalyticsTab = ({ analytics, sales, products }) => {
  const totalRevenue = sales.reduce((sum, sale) => sum + sale.amount, 0);
  const totalSales = sales.length;
  const avgOrderValue = totalSales > 0 ? totalRevenue / totalSales : 0;

  return (
    <div className="analytics-section">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <div className="stat-label">Total Revenue</div>
            <div className="stat-value">${totalRevenue.toFixed(2)}</div>
            <div className="stat-change">+12% this month</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">Total Sales</div>
            <div className="stat-value">{totalSales}</div>
            <div className="stat-change">+8 this week</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💵</div>
          <div className="stat-content">
            <div className="stat-label">Avg Order Value</div>
            <div className="stat-value">${avgOrderValue.toFixed(2)}</div>
            <div className="stat-change">+5% vs last month</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <div className="stat-label">Active Products</div>
            <div className="stat-value">{products.length}</div>
            <div className="stat-change">+2 this week</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-card">
          <h3>Sales Over Time</h3>
          <div className="chart-placeholder">
            <p>Chart visualization (integrate Chart.js or Recharts)</p>
          </div>
        </div>

        <div className="chart-card">
          <h3>Top Products</h3>
          <div className="top-products">
            {products.slice(0, 5).map((product, idx) => (
              <div key={idx} className="top-product-row">
                <span className="rank">#{idx + 1}</span>
                <span className="name">{product.title}</span>
                <span className="sales">{product.sales || 0} sales</span>
                <span className="revenue">${product.revenue || 0}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * ProductsTab - Manage products
 */
const ProductsTab = ({ products, onAdd, onEdit, onRefresh }) => {
  return (
    <div className="products-section">
      <div className="section-header">
        <h2>📦 Manage Products</h2>
        <button className="btn-primary" onClick={onAdd}>
          <Plus size={18} />
          Add Product
        </button>
      </div>

      <div className="products-list">
        {products.length === 0 ? (
          <div className="empty-state">No products yet</div>
        ) : (
          products.map((product) => (
            <div key={product.id} className="product-row">
              <div className="product-info">
                <img src={product.cover} alt={product.title} className="product-thumb" />
                <div className="product-details">
                  <h4>{product.title}</h4>
                  <p>{product.description.slice(0, 60)}...</p>
                  <div className="product-meta">
                    <span>Price: ${product.price}</span>
                    <span>Sales: {product.sales || 0}</span>
                    <span>Revenue: ${product.revenue || 0}</span>
                  </div>
                </div>
              </div>

              <div className="product-actions">
                <button className="btn-icon" title="View">
                  <Eye size={18} />
                </button>
                <button className="btn-icon" onClick={() => onEdit(product)} title="Edit">
                  <Edit2 size={18} />
                </button>
                <button className="btn-icon danger" title="Delete">
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

/**
 * SalesTab - View all sales
 */
const SalesTab = ({ sales }) => {
  return (
    <div className="sales-section">
      <div className="section-header">
        <h2>💳 Recent Sales</h2>
        <div className="sales-filters">
          <input type="text" placeholder="Search customer..." className="search-input" />
          <select className="status-filter">
            <option>All Status</option>
            <option>Completed</option>
            <option>Pending</option>
            <option>Refunded</option>
          </select>
        </div>
      </div>

      <div className="sales-list">
        {sales.length === 0 ? (
          <div className="empty-state">No sales yet</div>
        ) : (
          <table className="sales-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Product</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Status</th>
                <th>Download</th>
              </tr>
            </thead>
            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td>{sale.user_email}</td>
                  <td>{sale.product_id}</td>
                  <td>${sale.amount.toFixed(2)}</td>
                  <td>{new Date(sale.created_at).toLocaleDateString()}</td>
                  <td>
                    <span className={`status ${sale.status}`}>
                      {sale.status}
                    </span>
                  </td>
                  <td>
                    <button className="btn-download">
                      <Download size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

/**
 * ProductFormModal - Add/edit product
 */
const ProductFormModal = ({ product, onClose, onSave }) => {
  const [formData, setFormData] = useState(product || {
    title: '',
    description: '',
    price: 0,
    originalPrice: 0,
    type: 'template',
    cover: '',
    includes: [],
    tags: []
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const method = product ? 'PUT' : 'POST';
      const endpoint = product ? `/api/fiilthy/admin/products/${product.id}` : '/api/fiilthy/admin/products';
      
      const res = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(formData)
      });

      if (res.ok) {
        onSave();
      }
    } catch (error) {
      console.error('Error saving product:', error);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>

        <h2>{product ? 'Edit Product' : 'Add New Product'}</h2>

        <form onSubmit={handleSubmit} className="product-form">
          <div className="form-group">
            <label>Product Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Price</label>
              <input
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                step="0.01"
              />
            </div>

            <div className="form-group">
              <label>Original Price</label>
              <input
                type="number"
                value={formData.originalPrice}
                onChange={(e) => setFormData({ ...formData, originalPrice: parseFloat(e.target.value) })}
                step="0.01"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Type</label>
            <select value={formData.type} onChange={(e) => setFormData({ ...formData, type: e.target.value })}>
              <option value="template">Template</option>
              <option value="course">Course</option>
              <option value="guide">Guide</option>
              <option value="tool">Tool</option>
            </select>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary">Save Product</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FiilthyAdmin;
