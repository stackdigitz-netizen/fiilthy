import React, { useState, useEffect } from 'react';
import { TrendingUp, BarChart3, Zap, AlertCircle, RefreshCw } from 'lucide-react';
import './Pages.css';

const Dashboard = () => {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [paymentStats, setPaymentStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashResponse, paymentResponse] = await Promise.all([
        fetch('http://localhost:8000/api/dashboard/stats'),
        fetch('http://localhost:8000/api/payments/all-stats')
      ]);

      if (dashResponse.ok) {
        const dashData = await dashResponse.json();
        setDashboardStats(dashData);
      }
      if (paymentResponse.ok) {
        const payData = await paymentResponse.json();
        setPaymentStats(payData);
      }
    } catch (err) {
      setError(err.message);
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      label: 'Total Products',
      value: dashboardStats?.total_products || 0,
      change: `+${dashboardStats?.products_today || 0} today`
    },
    {
      label: 'Revenue Generated',
      value: `$${(paymentStats?.total_revenue || 0).toFixed(2)}`,
      change: `+$${(paymentStats?.today_revenue || 0).toFixed(2)} today`
    },
    {
      label: 'Total Sales',
      value: paymentStats?.total_sales || 0,
      change: `${paymentStats?.today_sales || 0} today`
    },
    {
      label: 'Pending Tasks',
      value: dashboardStats?.pending_tasks || 0,
      change: `${dashboardStats?.active_opportunities || 0} opportunities`
    }
  ];

  const recentActivity = [
    { time: 'Just now', action: 'Dashboard data updated', status: 'success' },
    { time: '1 min ago', action: 'Backend systems connected', status: 'success' },
    { time: '5 mins ago', action: 'Monitoring active', status: 'in-progress' },
    { time: 'Ready', action: 'All systems operational and synced', status: 'info' }
  ];

  return (
    <div className="page">
      <div className="page-header">
        <h1>📊 Factory Dashboard</h1>
        <p>Real-time overview of your autonomous product development system</p>
      </div>

      {error && (
        <div style={{
          padding: '16px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '6px',
          marginBottom: '20px',
          border: '1px solid #f5c6cb'
        }}>
          ⚠️ Error loading data: {error}
        </div>
      )}

      {/* Key Stats */}
      <div className="stats-grid">
        {stats.map((stat, idx) => (
          <div key={idx} className="stat-card" style={{ opacity: loading ? 0.5 : 1 }}>
            <h3>{stat.label}</h3>
            <p className="stat-value">{loading ? '...' : stat.value}</p>
            <p className="stat-change">{loading ? 'Loading...' : stat.change}</p>
          </div>
        ))}
      </div>

      {/* Factory Status */}
      <div className="content-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2>System Status</h2>
          <button
            onClick={loadDashboardData}
            disabled={loading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <RefreshCw size={16} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        <div className="status-box">
          <div className="status-content">
            <div className="status-indicator">
              <span className="status-dot active"></span>
              <span>{dashboardStats ? 'All systems operational & synced' : 'Connecting...'}</span>
            </div>
            <p>
              {dashboardStats ? (
                <>
                  {dashboardStats.total_products} products | {paymentStats?.total_sales || 0} sales |
                  ${(paymentStats?.total_revenue || 0).toFixed(2)} revenue
                </>
              ) : (
                'Loading system stats...'
              )}
            </p>
          </div>
          <button className="btn btn-primary">
            {dashboardStats ? '✓ System Ready' : 'Connecting...'}
          </button>
        </div>
      </div>

      {/* Revenue Breakdown */}
      {paymentStats && (
        <div className="content-section">
          <h2>💰 Revenue Summary</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
            <div style={{
              padding: '16px',
              backgroundColor: '#f0f9ff',
              borderRadius: '8px',
              borderLeft: '4px solid #007bff'
            }}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>Average Order Value</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                ${paymentStats.average_order_value?.toFixed(2) || '0.00'}
              </div>
            </div>
            <div style={{
              padding: '16px',
              backgroundColor: '#f0f9ff',
              borderRadius: '8px',
              borderLeft: '4px solid #28a745'
            }}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>Products With Sales</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                {paymentStats.products_with_sales || 0}
              </div>
            </div>
            <div style={{
              padding: '16px',
              backgroundColor: '#f0f9ff',
              borderRadius: '8px',
              borderLeft: '4px solid #ffc107'
            }}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>Today's Sales</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                ${(paymentStats.today_revenue || 0).toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="content-section">
        <h2>📋 Recent Activity</h2>
        <div className="activity-list">
          {recentActivity.map((item, idx) => (
            <div key={idx} className="activity-item">
              <div className="activity-time">{item.time}</div>
              <div className="activity-content">
                <p>{item.action}</p>
                <span className={`activity-badge ${item.status}`}>{item.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
