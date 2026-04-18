import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  BarChart, Bar,
  LineChart, Line,
  PieChart, Pie, Cell,
  XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';
import {
  Zap, TrendingUp, DollarSign, Package,
  AlertCircle, CheckCircle, Clock,
  Menu, X, Moon, Sun, Settings,
  RotateCw, Play, Pause, Maximize2,
  Download, Share2, RefreshCw, Home,
  BarChart3, LineChart as LineChartIcon,
  Mail, Radio, Target, Users
} from 'lucide-react';
import './App.css';

// ============================================================================
// Configuration
// ============================================================================

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API_V4 = `${BACKEND_URL}/api/v4`;

// Colors for charts
const CHART_COLORS = {
  primary: '#8b5cf6',
  secondary: '#ec4899',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
};

// ============================================================================
// Utility Functions
// ============================================================================

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value || 0);
};

const formatNumber = (value) => {
  return new Intl.NumberFormat('en-US').format(value || 0);
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

// ============================================================================
// Stat Card Component
// ============================================================================

const StatCard = ({ icon: Icon, label, value, trend, color = 'primary', loading = false }) => (
  <div className={`stat-card stat-card-${color}`}>
    <div className="stat-header">
      <div className="stat-icon">
        <Icon size={24} />
      </div>
      <span className="stat-label">{label}</span>
    </div>
    <div className="stat-value">
      {loading ? (
        <div className="skeleton-line skeleton-value"></div>
      ) : (
        <>
          <div className="value">{value}</div>
          {trend && (
            <div className={`trend trend-${trend > 0 ? 'up' : 'down'}`}>
              <TrendingUp size={16} />
              {Math.abs(trend)}%
            </div>
          )}
        </>
      )}
    </div>
  </div>
);

// ============================================================================
// Data Table Component
// ============================================================================

const DataTable = ({ title, data, columns, loading = false, onAction }) => {
  if (loading) {
    return (
      <div className="data-table-container loading">
        <h3>{title}</h3>
        <div className="skeleton-lines">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton-line"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="data-table-container">
      <div className="table-header">
        <h3>{title}</h3>
        <button className="btn-icon" title="Refresh">
          <RefreshCw size={18} />
        </button>
      </div>

      {data && data.length > 0 ? (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col.key}>{col.label}</th>
                ))}
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {data.slice(0, 8).map((row, idx) => (
                <tr key={idx} className={row.status ? `status-${row.status}` : ''}>
                  {columns.map((col) => (
                    <td key={col.key}>
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </td>
                  ))}
                  <td>
                    <button
                      className="btn-sm btn-secondary"
                      onClick={() => onAction && onAction(row)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <Package size={40} />
          <p>No data available</p>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// Chart Component
// ============================================================================

const ChartContainer = ({ title, children, loading = false }) => (
  <div className="chart-container">
    <div className="chart-header">
      <h3>{title}</h3>
      <button className="btn-icon" title="Download">
        <Download size={18} />
      </button>
    </div>
    {loading ? (
      <div className="skeleton-chart"></div>
    ) : (
      <div className="chart-content">{children}</div>
    )}
  </div>
);

// ============================================================================
// Modal Component
// ============================================================================

const Modal = ({ title, isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={onClose}></div>
      <div className="modal">
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="btn-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </>
  );
};

// ============================================================================
// Demo Mode Toggle Component
// ============================================================================

const DemoModeToggle = ({ isDemoMode, onToggle, loading }) => (
  <div className="demo-mode-control">
    <label className="toggle-label">
      <input
        type="checkbox"
        checked={isDemoMode}
        onChange={(e) => onToggle(e.target.checked)}
        disabled={loading}
      />
      <span className="toggle-slider"></span>
      <span className="toggle-text">
        {isDemoMode ? '🎮 Demo Mode' : '🚀 Production Mode'}
      </span>
    </label>
    <p className="toggle-hint">
      {isDemoMode
        ? 'Using simulated data - no API keys required'
        : 'Using live production APIs - requires credentials'}
    </p>
  </div>
);

// ============================================================================
// Main Dashboard Component
// ============================================================================

const Dashboard = () => {
  // State Management
  const [demoMode, setDemoMode] = useState(true);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [aiRunning, setAiRunning] = useState(false);

  // Data State
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [socialPosts, setSocialPosts] = useState([]);
  const [emailSequences, setEmailSequences] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  // Modal State
  const [showSettings, setShowSettings] = useState(false);
  const [showAiModal, setShowAiModal] = useState(false);

  // ============================================================================
  // API Calls
  // ============================================================================

  const toggleDemoMode = useCallback(async (newMode) => {
    try {
      const endpoint = `${API_V4}/demo-mode/toggle?enable_demo=${newMode}`;
      const response = await axios.post(endpoint);
      setDemoMode(newMode);
      
      // Refresh data
      setTimeout(() => fetchDashboardData(), 500);
    } catch (error) {
      console.error('Error toggling demo mode:', error);
      alert('Failed to toggle demo mode');
    }
  }, []);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      
      const [overviewRes, statsRes, productsRes, oppsRes, analyticsRes] = await Promise.all([
        axios.get(`${API_V4}/dashboard/overview`),
        axios.get(`${API_V4}/dashboard/stats`),
        axios.get(`${API_V4}/products?limit=10`),
        axios.get(`${API_V4}/opportunities?limit=8`),
        axios.get(`${API_V4}/analytics/full`),
      ]);

      const overview = overviewRes.data.data || {};
      
      setStats(overview.stats || {});
      setProducts(productsRes.data.data?.products || []);
      setOpportunities(oppsRes.data.data?.opportunities || []);
      setRevenueData(overviewRes.data.data?.revenue_metrics?.events || []);
      setSocialPosts(overviewRes.data.data?.social_posts || []);
      setEmailSequences(overviewRes.data.data?.email_sequences || []);
      setAnalytics(analyticsRes.data.data || {});

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  }, []);

  const runAutonomousCycle = useCallback(async () => {
    try {
      setAiRunning(true);
      setShowAiModal(true);

      const response = await axios.post(`${API_V4}/autonomous/run-cycle`, null, {
        params: {
          enable_publishing: true,
          enable_marketing: true,
        },
      });

      await new Promise((resolve) => setTimeout(resolve, 2000));
      await fetchDashboardData();
    } catch (error) {
      console.error('Error running autonomous cycle:', error);
      alert('Failed to run autonomous cycle');
    } finally {
      setAiRunning(false);
    }
  }, [fetchDashboardData]);

  // ============================================================================
  // Effects
  // ============================================================================

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <div className={`app-container ${sidebarOpen ? 'sidebar-open' : ''}`}>
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <Zap size={28} />
            <span>CEO AI</span>
          </div>
          <button
            className="btn-close md-only"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={24} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {[
            { id: 'overview', label: 'Overview', icon: Home },
            { id: 'products', label: 'Products', icon: Package },
            { id: 'analytics', label: 'Analytics', icon: BarChart3 },
            { id: 'marketing', label: 'Marketing', icon: Target },
            { id: 'scaling', label: 'Scaling', icon: TrendingUp },
            { id: 'settings', label: 'Settings', icon: Settings },
          ].map((tab) => (
            <button
              key={tab.id}
              className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => {
                setActiveTab(tab.id);
                setSidebarOpen(false);
              }}
            >
              <tab.icon size={20} />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <DemoModeToggle
            isDemoMode={demoMode}
            onToggle={toggleDemoMode}
            loading={loading}
          />
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="header">
          <div className="header-left">
            <button
              className="btn-menu md-only"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={24} />
            </button>
            <h1>Dashboard</h1>
          </div>

          <div className="header-right">
            <button
              className="btn-icon"
              onClick={() => setDarkMode(!darkMode)}
              title={darkMode ? 'Light Mode' : 'Dark Mode'}
            >
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <button className="btn-primary" onClick={runAutonomousCycle} disabled={aiRunning}>
              <Zap size={18} />
              {aiRunning ? 'Running...' : 'Run AI Cycle'}
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="content">
          {activeTab === 'overview' && (
            <div className="tab-content">
              {/* Top Stats */}
              <section className="stats-grid">
                <StatCard
                  icon={Package}
                  label="Total Products"
                  value={formatNumber(stats?.total_products || 0)}
                  trend={15}
                  color="primary"
                  loading={loading}
                />
                <StatCard
                  icon={DollarSign}
                  label="Total Revenue"
                  value={formatCurrency(stats?.total_revenue || 0)}
                  trend={42}
                  color="success"
                  loading={loading}
                />
                <StatCard
                  icon={Target}
                  label="Opportunities"
                  value={formatNumber(stats?.opportunities_found || 0)}
                  trend={28}
                  color="warning"
                  loading={loading}
                />
                <StatCard
                  icon={TrendingUp}
                  label="Active Campaigns"
                  value={formatNumber(stats?.active_campaigns || 0)}
                  trend={9}
                  color="info"
                  loading={loading}
                />
              </section>

              {/* Charts */}
              <div className="charts-grid">
                <ChartContainer title="Revenue Trend" loading={loading}>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={revenueData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="revenue"
                        stroke={CHART_COLORS.primary}
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>

                <ChartContainer title="Conversions" loading={loading}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={revenueData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="conversions" fill={CHART_COLORS.secondary} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </div>

              {/* Data Tables */}
              <div className="tables-grid">
                <DataTable
                  title="Recent Products"
                  data={products}
                  columns={[
                    { key: 'title', label: 'Title' },
                    { key: 'type', label: 'Type' },
                    {
                      key: 'price',
                      label: 'Price',
                      render: (value) => formatCurrency(value),
                    },
                    {
                      key: 'status',
                      label: 'Status',
                      render: (value) => (
                        <span className={`badge badge-${value}`}>{value}</span>
                      ),
                    },
                  ]}
                  loading={loading}
                />

                <DataTable
                  title="Opportunities"
                  data={opportunities}
                  columns={[
                    { key: 'title', label: 'Opportunity' },
                    {
                      key: 'demand_score',
                      label: 'Demand',
                      render: (value) => `${value}%`,
                    },
                    {
                      key: 'profitability_score',
                      label: 'Profit',
                      render: (value) => `${value}%`,
                    },
                  ]}
                  loading={loading}
                />
              </div>
            </div>
          )}

          {activeTab === 'products' && (
            <div className="tab-content">
              <h2>Products</h2>
              <div className="action-bar">
                <button className="btn-primary">+ Create Product</button>
              </div>
              <DataTable
                title="All Products"
                data={products}
                columns={[
                  { key: 'title', label: 'Product' },
                  { key: 'niche', label: 'Niche' },
                  { key: 'sales', label: 'Sales' },
                  {
                    key: 'revenue',
                    label: 'Revenue',
                    render: (value) => formatCurrency(value),
                  },
                ]}
                loading={loading}
              />
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="tab-content">
              <h2>Analytics</h2>
              <ChartContainer title="Comprehensive Analytics">
                <div className="analytics-grid">
                  <div className="analytics-stat">
                    <span className="label">Total Visitors</span>
                    <span className="value">
                      {formatNumber(analytics?.total_visitors)}
                    </span>
                  </div>
                  <div className="analytics-stat">
                    <span className="label">Conversion Rate</span>
                    <span className="value">{analytics?.conversion_rate}</span>
                  </div>
                  <div className="analytics-stat">
                    <span className="label">Bounce Rate</span>
                    <span className="value">{analytics?.bounce_rate}</span>
                  </div>
                </div>
              </ChartContainer>
            </div>
          )}

          {activeTab === 'marketing' && (
            <div className="tab-content">
              <h2>Marketing</h2>
              <div className="marketing-cards">
                <div className="marketing-card">
                  <Radio size={32} />
                  <h3>Social Media</h3>
                  <p>{socialPosts.length} posts scheduled</p>
                </div>
                <div className="marketing-card">
                  <Mail size={32} />
                  <h3>Email Campaigns</h3>
                  <p>{emailSequences.length} sequences</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="tab-content">
              <h2>Settings</h2>
              <div className="settings-section">
                <h3>Environment</h3>
                <DemoModeToggle
                  isDemoMode={demoMode}
                  onToggle={toggleDemoMode}
                  loading={loading}
                />
              </div>
            </div>
          )}
        </div>
      </main>

      {/* AI Modal */}
      <Modal
        title="Running Autonomous AI Cycle"
        isOpen={showAiModal}
        onClose={() => setShowAiModal(false)}
      >
        <div className="ai-modal-content">
          <div className="ai-progress">
            <div className="spinner"></div>
            <p>Processing...</p>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Dashboard;
