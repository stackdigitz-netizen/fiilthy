import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Lightbulb, RefreshCw, TrendingUp, Zap } from 'lucide-react';
import './Pages.css';
import API_URL from '../config/api';

const API = API_URL;

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

const normalizeTrendScore = (value) => {
  const numericValue = Number(value || 0);
  return numericValue <= 1 ? numericValue * 100 : numericValue;
};

const titleCase = (value) =>
  String(value || 'unknown')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());

const GrowthPage = () => {
  const [products, setProducts] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [paymentStats, setPaymentStats] = useState(null);
  const [revenueBreakdown, setRevenueBreakdown] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadGrowthData();
  }, []);

  const loadGrowthData = async () => {
    setLoading(true);
    setError(null);

    const results = await Promise.allSettled([
      fetch(`${API}/api/products?limit=100`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load products (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/opportunities?limit=50`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load opportunities (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/payments/all-stats`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load payment stats (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/analytics/revenue-breakdown`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load revenue breakdown (${response.status})`);
        }
        return response.json();
      })
    ]);

    const [productsResult, opportunitiesResult, paymentResult, revenueResult] = results;

    setProducts(productsResult.status === 'fulfilled' && Array.isArray(productsResult.value) ? productsResult.value : []);
    setOpportunities(
      opportunitiesResult.status === 'fulfilled' && Array.isArray(opportunitiesResult.value)
        ? opportunitiesResult.value
        : []
    );
    setPaymentStats(paymentResult.status === 'fulfilled' ? paymentResult.value : null);
    setRevenueBreakdown(revenueResult.status === 'fulfilled' ? revenueResult.value : null);

    const firstRejected = results.find((result) => result.status === 'rejected');
    if (firstRejected?.reason?.message) {
      setError(firstRejected.reason.message);
    }

    setLoading(false);
  };

  const sortedProducts = useMemo(() => {
    return [...products].sort(
      (left, right) => (right.revenue || 0) - (left.revenue || 0) || (right.conversions || 0) - (left.conversions || 0)
    );
  }, [products]);

  const normalizedOpportunities = useMemo(() => {
    return opportunities
      .map((opportunity) => ({
        ...opportunity,
        normalizedTrendScore: normalizeTrendScore(opportunity.trend_score)
      }))
      .sort((left, right) => right.normalizedTrendScore - left.normalizedTrendScore);
  }, [opportunities]);

  const publishedProducts = products.filter((product) => product.status === 'published').length;
  const readyProducts = products.filter((product) => product.status === 'ready').length;
  const highSignalOpportunities = normalizedOpportunities.filter(
    (opportunity) => opportunity.normalizedTrendScore >= 80
  );
  const productsWithoutLinks = products.filter((product) => (product.marketplace_links || []).length === 0);
  const forecast = revenueBreakdown?.projections || {};
  const revenueCategories = Object.keys(revenueBreakdown?.by_product_type || {}).length;

  const priorityActions = useMemo(() => {
    const actions = [];

    if (readyProducts > 0) {
      actions.push({
        icon: Zap,
        title: 'Publish ready inventory',
        message: `${readyProducts} products are marked ready and can be pushed into a live sales workflow.`
      });
    }

    if (highSignalOpportunities.length > 0) {
      actions.push({
        icon: TrendingUp,
        title: 'Validate top opportunities',
        message: `${highSignalOpportunities.length} opportunities are scoring 80+ and deserve execution review.`
      });
    }

    if (productsWithoutLinks.length > 0) {
      actions.push({
        icon: Lightbulb,
        title: 'Finish marketplace coverage',
        message: `${productsWithoutLinks.length} products still have no marketplace links, so they cannot convert yet.`
      });
    }

    if ((paymentStats?.total_sales || 0) === 0 && products.length > 0) {
      actions.push({
        icon: AlertCircle,
        title: 'Turn on first checkout path',
        message: 'Products exist, but no successful payments have been recorded yet.'
      });
    }

    if (actions.length === 0) {
      actions.push({
        icon: TrendingUp,
        title: 'Growth queue is clear',
        message: 'No obvious blockers are showing from products, opportunities, or revenue projections.'
      });
    }

    return actions.slice(0, 4);
  }, [highSignalOpportunities.length, paymentStats?.total_sales, products.length, productsWithoutLinks.length, readyProducts]);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Growth Lab</h1>
        <p>Prioritize real launch and revenue moves from current product, opportunity, and payment data</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="section-header mb-4">
        <h2>Growth Overview</h2>
        <button className="btn btn-secondary" onClick={loadGrowthData} disabled={loading}>
          <RefreshCw size={16} /> {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Published Products</h3>
          <p className="stat-value">{loading ? '...' : publishedProducts}</p>
          <p className="stat-change">Currently live inventory</p>
        </div>
        <div className="stat-card">
          <h3>Ready To Launch</h3>
          <p className="stat-value">{loading ? '...' : readyProducts}</p>
          <p className="stat-change">Products ready for publication</p>
        </div>
        <div className="stat-card">
          <h3>High-Signal Niches</h3>
          <p className="stat-value">{loading ? '...' : highSignalOpportunities.length}</p>
          <p className="stat-change">Opportunity score 80 and above</p>
        </div>
        <div className="stat-card">
          <h3>Next Month Projection</h3>
          <p className="stat-value">{loading ? '...' : currencyFormatter.format(forecast.next_month || 0)}</p>
          <p className="stat-change">Derived from tracked product revenue</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h3>Priority Actions</h3>
          {priorityActions.map((action) => {
            const Icon = action.icon;

            return (
              <div key={action.title} className="insight-box">
                <Icon size={20} />
                <div>
                  <p className="font-semibold">{action.title}</p>
                  <p className="text-secondary">{action.message}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="content-section">
          <h3>Forecast Snapshot</h3>
          <div className="stack-list">
            <div className="metric-row">
              <span>Next Week Revenue</span>
              <span className="metric-value">{currencyFormatter.format(forecast.next_week || 0)}</span>
            </div>
            <div className="metric-row">
              <span>Next Month Revenue</span>
              <span className="metric-value">{currencyFormatter.format(forecast.next_month || 0)}</span>
            </div>
            <div className="metric-row">
              <span>Next Quarter Revenue</span>
              <span className="metric-value">{currencyFormatter.format(forecast.next_quarter || 0)}</span>
            </div>
            <div className="metric-row">
              <span>Total Sales</span>
              <span className="metric-value">{paymentStats?.total_sales || 0}</span>
            </div>
            <div className="metric-row">
              <span>Average Order Value</span>
              <span className="metric-value">{currencyFormatter.format(paymentStats?.average_order_value || 0)}</span>
            </div>
            <div className="metric-row">
              <span>Tracked Revenue Categories</span>
              <span className="metric-value">{revenueCategories}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="content-section">
        <h2>Top Product Momentum</h2>
        {sortedProducts.length === 0 ? (
          <div className="empty-state">
            <p>No products are available yet, so growth prioritization is currently empty.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Status</th>
                  <th>Clicks</th>
                  <th>Conversions</th>
                  <th>Revenue</th>
                  <th>Marketplace Links</th>
                </tr>
              </thead>
              <tbody>
                {sortedProducts.slice(0, 6).map((product) => (
                  <tr key={product.id}>
                    <td className="font-semibold">{product.title}</td>
                    <td>
                      <span className="badge badge-secondary">{titleCase(product.status)}</span>
                    </td>
                    <td>{product.clicks || 0}</td>
                    <td>{product.conversions || 0}</td>
                    <td className="text-success font-semibold">{currencyFormatter.format(product.revenue || 0)}</td>
                    <td>{(product.marketplace_links || []).length}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="content-section">
        <h2>Opportunity Watchlist</h2>
        {normalizedOpportunities.length === 0 ? (
          <div className="empty-state">
            <p>No opportunities have been stored yet.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table small">
              <thead>
                <tr>
                  <th>Niche</th>
                  <th>Trend Score</th>
                  <th>Market Size</th>
                  <th>Keywords</th>
                  <th>Priority</th>
                </tr>
              </thead>
              <tbody>
                {normalizedOpportunities.slice(0, 6).map((opportunity) => {
                  const priority =
                    opportunity.normalizedTrendScore >= 80
                      ? 'high'
                      : opportunity.normalizedTrendScore >= 60
                        ? 'medium'
                        : 'low';

                  return (
                    <tr key={opportunity.id}>
                      <td className="font-semibold">{opportunity.niche}</td>
                      <td>
                        <div className="score-badge">{opportunity.normalizedTrendScore.toFixed(1)}</div>
                      </td>
                      <td>{opportunity.market_size || 'Unknown'}</td>
                      <td>{(opportunity.keywords || []).length}</td>
                      <td>
                        <span className={`badge badge-${priority}`}>{titleCase(priority)}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h3>Launch Constraints</h3>
          <div className="stack-list">
            <div className="detail-row">
              <span>Products without marketplace links</span>
              <span className="metric-value">{productsWithoutLinks.length}</span>
            </div>
            <div className="detail-row">
              <span>Draft products</span>
              <span className="metric-value">{products.filter((product) => product.status === 'draft').length}</span>
            </div>
            <div className="detail-row">
              <span>Tracked opportunities</span>
              <span className="metric-value">{normalizedOpportunities.length}</span>
            </div>
            <div className="detail-row">
              <span>Products with sales</span>
              <span className="metric-value">{paymentStats?.products_with_sales || 0}</span>
            </div>
          </div>
        </div>

        <div className="content-section">
          <h3>Recommended Next Moves</h3>
          {products.length === 0 && normalizedOpportunities.length === 0 ? (
            <div className="empty-state">
              <p>Create products or capture opportunities first so the growth queue has something real to optimize.</p>
            </div>
          ) : (
            <div className="stack-list">
              {readyProducts > 0 && (
                <div className="detail-row">
                  <span>Publish ready products</span>
                  <span className="metric-value">{readyProducts}</span>
                </div>
              )}
              {highSignalOpportunities.length > 0 && (
                <div className="detail-row">
                  <span>Review top-scoring opportunities</span>
                  <span className="metric-value">{highSignalOpportunities.length}</span>
                </div>
              )}
              <div className="detail-row">
                <span>Current total revenue</span>
                <span className="metric-value">{currencyFormatter.format(paymentStats?.total_revenue || 0)}</span>
              </div>
              <div className="detail-row">
                <span>Today revenue</span>
                <span className="metric-value">{currencyFormatter.format(paymentStats?.today_revenue || 0)}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GrowthPage;