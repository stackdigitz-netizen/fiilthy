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

const formatDateTime = (value) => {
  if (!value) {
    return 'Unavailable';
  }

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Unavailable' : date.toLocaleString();
};

const AnalyticsPage = () => {
  const [realtime, setRealtime] = useState(null);
  const [revenueBreakdown, setRevenueBreakdown] = useState(null);
  const [paymentStats, setPaymentStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    setLoading(true);
    setError(null);

    const results = await Promise.allSettled([
      fetch(`${API}/api/analytics/realtime`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load realtime analytics (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/analytics/revenue-breakdown`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load revenue breakdown (${response.status})`);
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

    const [realtimeResult, breakdownResult, paymentResult] = results;

    setRealtime(realtimeResult.status === 'fulfilled' ? realtimeResult.value : null);
    setRevenueBreakdown(breakdownResult.status === 'fulfilled' ? breakdownResult.value : null);
    setPaymentStats(paymentResult.status === 'fulfilled' ? paymentResult.value : null);

    const firstRejected = results.find((result) => result.status === 'rejected');
    if (firstRejected?.reason?.message) {
      setError(firstRejected.reason.message);
    }

    setLoading(false);
  };

  const revenueByType = useMemo(() => {
    return Object.entries(revenueBreakdown?.by_product_type || {})
      .map(([type, details]) => ({
        type,
        revenue: Number(details?.revenue || 0),
        count: Number(details?.count || 0)
      }))
      .sort((left, right) => right.revenue - left.revenue);
  }, [revenueBreakdown]);

  const totalTypeRevenue = revenueByType.reduce((sum, item) => sum + item.revenue, 0);
  const topProducts = realtime?.top_products || [];

  const notes = useMemo(() => {
    const entries = [];

    if ((realtime?.products?.total || 0) === 0) {
      entries.push('No products are stored yet, so the analytics baseline is still empty.');
    }

    if ((paymentStats?.total_sales || 0) === 0) {
      entries.push('No successful payments have been recorded yet.');
    }

    if (!realtime?.gumroad?.connected) {
      entries.push('Gumroad is not connected or did not return product data.');
    }

    if (entries.length === 0) {
      entries.push('Core analytics are coming from stored product and payment records.');
    }

    return entries;
  }, [paymentStats, realtime]);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Analytics & Revenue</h1>
        <p>Monitor live revenue, traffic, and product performance from backend records</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="section-header mb-4">
        <h2>Revenue Baseline</h2>
        <button className="btn btn-secondary" onClick={loadAnalyticsData} disabled={loading}>
          <RefreshCw size={16} /> {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Payment Revenue</h3>
          <p className="stat-value">
            {loading ? '...' : currencyFormatter.format(paymentStats?.total_revenue || 0)}
          </p>
          <p className="stat-change">Completed checkout revenue</p>
        </div>
        <div className="stat-card">
          <h3>Tracked Product Revenue</h3>
          <p className="stat-value">
            {loading ? '...' : currencyFormatter.format(realtime?.revenue?.total || 0)}
          </p>
          <p className="stat-change">Revenue stored on products</p>
        </div>
        <div className="stat-card">
          <h3>Total Sales</h3>
          <p className="stat-value">{loading ? '...' : paymentStats?.total_sales || 0}</p>
          <p className="stat-change">Successful payments recorded</p>
        </div>
        <div className="stat-card">
          <h3>Conversion Rate</h3>
          <p className="stat-value">{loading ? '...' : `${realtime?.traffic?.conversion_rate || 0}%`}</p>
          <p className="stat-change">From tracked clicks and conversions</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h3>KPI Baseline</h3>
          <div className="stack-list">
            <div className="metric-row">
              <span>Average Order Value</span>
              <span className="metric-value">{currencyFormatter.format(paymentStats?.average_order_value || 0)}</span>
            </div>
            <div className="metric-row">
              <span>Products With Sales</span>
              <span className="metric-value">{paymentStats?.products_with_sales || 0}</span>
            </div>
            <div className="metric-row">
              <span>Total Products</span>
              <span className="metric-value">{realtime?.products?.total || 0}</span>
            </div>
            <div className="metric-row">
              <span>Published Products</span>
              <span className="metric-value">{realtime?.products?.published || 0}</span>
            </div>
            <div className="metric-row">
              <span>Draft Products</span>
              <span className="metric-value">{realtime?.products?.draft || 0}</span>
            </div>
            <div className="metric-row">
              <span>Total Clicks</span>
              <span className="metric-value">{realtime?.traffic?.clicks || 0}</span>
            </div>
            <div className="metric-row">
              <span>Total Conversions</span>
              <span className="metric-value">{realtime?.traffic?.conversions || 0}</span>
            </div>
            <div className="metric-row">
              <span>Gumroad Products</span>
              <span className="metric-value">{realtime?.gumroad?.products || 0}</span>
            </div>
          </div>
        </div>

        <div className="content-section">
          <h3>Revenue by Product Type</h3>
          {revenueByType.length === 0 ? (
            <div className="empty-state">
              <p>No product-type revenue has been tracked yet.</p>
            </div>
          ) : (
            <div className="stack-list">
              {revenueByType.map((entry) => {
                const share = totalTypeRevenue > 0 ? (entry.revenue / totalTypeRevenue) * 100 : 0;

                return (
                  <div key={entry.type}>
                    <div className="detail-row">
                      <span>{titleCase(entry.type)}</span>
                      <span className="metric-value">{currencyFormatter.format(entry.revenue)}</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${share}%` }}></div>
                    </div>
                    <p className="text-secondary text-xs mt-2 mb-3">
                      {entry.count} products • {share.toFixed(1)}% of tracked product revenue
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <div className="content-section">
        <h2>Top Revenue Products</h2>
        {topProducts.length === 0 ? (
          <div className="empty-state">
            <p>No product revenue data is available yet.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table small">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Conversions</th>
                  <th>Revenue</th>
                  <th>Revenue Share</th>
                </tr>
              </thead>
              <tbody>
                {topProducts.map((product) => {
                  const revenue = Number(product.revenue || 0);
                  const revenueShare = (realtime?.revenue?.total || 0) > 0
                    ? (revenue / realtime.revenue.total) * 100
                    : 0;

                  return (
                    <tr key={product.id || product.title}>
                      <td className="font-semibold">{product.title || 'Untitled product'}</td>
                      <td>{product.conversions || 0}</td>
                      <td className="text-success font-semibold">{currencyFormatter.format(revenue)}</td>
                      <td>{revenueShare.toFixed(1)}%</td>
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
          <h3>Daily Snapshot</h3>
          <div className="stack-list">
            <div className="metric-row">
              <span>Today Revenue</span>
              <span className="metric-value">{currencyFormatter.format(paymentStats?.today_revenue || 0)}</span>
            </div>
            <div className="metric-row">
              <span>Today Sales</span>
              <span className="metric-value">{paymentStats?.today_sales || 0}</span>
            </div>
            <div className="metric-row">
              <span>Last Analytics Update</span>
              <span className="metric-value">{formatDateTime(realtime?.timestamp)}</span>
            </div>
            <div className="metric-row">
              <span>Gumroad Connection</span>
              <span className="metric-value">{realtime?.gumroad?.connected ? 'Connected' : 'Not connected'}</span>
            </div>
          </div>
        </div>

        <div className="content-section">
          <h3>Operational Notes</h3>
          {notes.map((note) => (
            <div key={note} className="insight-box">
              <AlertCircle size={18} />
              <p>{note}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
