import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import './Pages.css';
import API_URL from '../config/api';

const API = API_URL;

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

const titleCase = (value) =>
  String(value || 'unknown')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());

const SalesPage = () => {
  const [products, setProducts] = useState([]);
  const [paymentStats, setPaymentStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSalesData();
  }, []);

  const loadSalesData = async () => {
    setLoading(true);
    setError(null);

    const results = await Promise.allSettled([
      fetch(`${API}/api/products?limit=100`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load products (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/payments/all-stats`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load payment stats (${response.status})`);
        }
        return response.json();
      })
    ]);

    const [productsResult, paymentResult] = results;

    setProducts(productsResult.status === 'fulfilled' && Array.isArray(productsResult.value) ? productsResult.value : []);
    setPaymentStats(paymentResult.status === 'fulfilled' ? paymentResult.value : null);

    const firstRejected = results.find((result) => result.status === 'rejected');
    if (firstRejected?.reason?.message) {
      setError(firstRejected.reason.message);
    }

    setLoading(false);
  };

  const sortedProducts = useMemo(() => {
    return [...products].sort((left, right) => (right.revenue || 0) - (left.revenue || 0));
  }, [products]);

  const totalClicks = products.reduce((sum, product) => sum + (product.clicks || 0), 0);
  const totalConversions = products.reduce((sum, product) => sum + (product.conversions || 0), 0);
  const overallConversionRate = totalClicks > 0 ? (totalConversions / totalClicks) * 100 : 0;
  const publishedProducts = products.filter((product) => product.status === 'published').length;
  const readyProducts = products.filter((product) => product.status === 'ready').length;
  const productsWithLinks = products.filter((product) => (product.marketplace_links || []).length > 0).length;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Sales Operations</h1>
        <p>Review real checkout, revenue, and marketplace readiness across your products</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="section-header mb-4">
        <h2>Revenue Overview</h2>
        <button className="btn btn-secondary" onClick={loadSalesData} disabled={loading}>
          <RefreshCw size={16} /> {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Sellable Products</h3>
          <p className="stat-value">{loading ? '...' : publishedProducts + readyProducts}</p>
          <p className="stat-change">Published plus ready inventory</p>
        </div>
        <div className="stat-card">
          <h3>Total Sales</h3>
          <p className="stat-value">{loading ? '...' : paymentStats?.total_sales || 0}</p>
          <p className="stat-change">Recorded payments</p>
        </div>
        <div className="stat-card">
          <h3>Avg Order Value</h3>
          <p className="stat-value">
            {loading ? '...' : currencyFormatter.format(paymentStats?.average_order_value || 0)}
          </p>
          <p className="stat-change">Across completed checkouts</p>
        </div>
        <div className="stat-card">
          <h3>Total Revenue</h3>
          <p className="stat-value">
            {loading ? '...' : currencyFormatter.format(paymentStats?.total_revenue || 0)}
          </p>
          <p className="stat-change">Live payment aggregate</p>
        </div>
      </div>

      <div className="content-section">
        <div className="section-header">
          <h2>Product Sales Snapshot</h2>
        </div>

        {sortedProducts.length === 0 ? (
          <div className="empty-state">
            <p>No products exist yet, so there is no live sales data to summarize.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Price</th>
                  <th>Conversions</th>
                  <th>Revenue</th>
                </tr>
              </thead>
              <tbody>
                {sortedProducts.map((product) => (
                  <tr key={product.id}>
                    <td className="font-semibold">{product.title}</td>
                    <td>{titleCase(product.product_type)}</td>
                    <td>
                      <span className="badge badge-secondary">{titleCase(product.status)}</span>
                    </td>
                    <td>{currencyFormatter.format(product.price || 0)}</td>
                    <td>{product.conversions || 0}</td>
                    <td className="text-success font-semibold">{currencyFormatter.format(product.revenue || 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h3>Launch Readiness</h3>
          <div className="stack-list">
            <div className="metric-row">
              <span>Published products</span>
              <span className="metric-value">{publishedProducts}</span>
            </div>
            <div className="metric-row">
              <span>Ready products</span>
              <span className="metric-value">{readyProducts}</span>
            </div>
            <div className="metric-row">
              <span>Products with marketplace links</span>
              <span className="metric-value">{productsWithLinks}</span>
            </div>
            <div className="metric-row">
              <span>Products with sales</span>
              <span className="metric-value">{paymentStats?.products_with_sales || 0}</span>
            </div>
          </div>
        </div>

        <div className="content-section">
          <h3>Checkout Performance</h3>
          <div className="stack-list">
            <div className="metric-row">
              <span>Total clicks</span>
              <span className="metric-value">{totalClicks}</span>
            </div>
            <div className="metric-row">
              <span>Total conversions</span>
              <span className="metric-value">{totalConversions}</span>
            </div>
            <div className="metric-row">
              <span>Overall conversion rate</span>
              <span className="metric-value">{overallConversionRate.toFixed(2)}%</span>
            </div>
            <div className="metric-row">
              <span>Today revenue</span>
              <span className="metric-value">{currencyFormatter.format(paymentStats?.today_revenue || 0)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="content-section">
        <h3>Marketplace Coverage</h3>
        {productsWithLinks === 0 ? (
          <div className="empty-state">
            <p>No marketplace links have been published yet.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table small">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Status</th>
                  <th>Marketplace Links</th>
                </tr>
              </thead>
              <tbody>
                {products
                  .filter((product) => (product.marketplace_links || []).length > 0)
                  .map((product) => (
                    <tr key={product.id}>
                      <td className="font-semibold">{product.title}</td>
                      <td>{titleCase(product.status)}</td>
                      <td>{product.marketplace_links.length}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default SalesPage;
