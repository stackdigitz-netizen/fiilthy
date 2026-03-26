import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';
import { 
  TrendingUp, DollarSign, Package, AlertCircle, 
  CheckCircle, Clock, ExternalLink, Sparkles, Activity 
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [revenueMetrics, setRevenueMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiRunning, setAiRunning] = useState(false);
  const [aiMessage, setAiMessage] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [revenueRecs, setRevenueRecs] = useState(null);
  const [socialPosts, setSocialPosts] = useState([]);
  const [affiliateProgram, setAffiliateProgram] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, productsRes, opportunitiesRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/products?limit=10`),
        axios.get(`${API}/opportunities?limit=5`)
      ]);

      setStats(statsRes.data);
      setProducts(productsRes.data);
      setOpportunities(opportunitiesRes.data);
      
      // Generate mock revenue data for chart
      const mockRevenue = Array.from({ length: 7 }, (_, i) => ({
        date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        revenue: Math.floor(Math.random() * 5000) + 1000,
        conversions: Math.floor(Math.random() * 50) + 10
      }));
      setRevenueMetrics(mockRevenue);
      
      setLoading(false);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setLoading(false);
    }
  };

  const handlePublish = async (productId) => {
    try {
      await axios.put(`${API}/products/${productId}/status`, null, {
        params: { status: 'published' }
      });
      fetchDashboardData();
    } catch (error) {
      console.error("Error publishing product:", error);
    }
  };

  const runAutonomousCycle = async () => {
    setAiRunning(true);
    setAiMessage('🤖 Starting autonomous AI cycle...');
    
    try {
      const response = await axios.post(`${API}/ai/run-autonomous-cycle`);
      const results = response.data.results;
      
      setAiMessage(`✅ Cycle complete! Found ${results.opportunities_found} opportunities, created ${results.products_created} products`);
      
      setTimeout(() => {
        fetchDashboardData();
        setAiRunning(false);
        setAiMessage('');
      }, 3000);
    } catch (error) {
      console.error("Error running autonomous cycle:", error);
      setAiMessage('❌ Error running autonomous cycle');
      setAiRunning(false);
    }
  };

  const scoutOpportunities = async () => {
    setAiRunning(true);
    setAiMessage('🔍 Scouting new opportunities...');
    
    try {
      const response = await axios.post(`${API}/ai/scout-opportunities`);
      setAiMessage(`✅ Found ${response.data.opportunities_found} new opportunities!`);
      
      setTimeout(() => {
        fetchDashboardData();
        setAiRunning(false);
        setAiMessage('');
      }, 2000);
    } catch (error) {
      console.error("Error scouting opportunities:", error);
      setAiMessage('❌ Error scouting opportunities');
      setAiRunning(false);
    }
  };

  const generateProduct = async (opportunity) => {
    setAiRunning(true);
    setAiMessage(`📚 Generating product for: ${opportunity.niche}...`);
    
    try {
      const response = await axios.post(`${API}/ai/generate-book`, {
        niche: opportunity.niche,
        keywords: opportunity.keywords,
        book_length: "medium",
        target_audience: "general"
      });
      
      setAiMessage(`✅ Created: ${response.data.product.title}!`);
      
      setTimeout(() => {
        fetchDashboardData();
        setAiRunning(false);
        setAiMessage('');
      }, 3000);
    } catch (error) {
      console.error("Error generating product:", error);
      setAiMessage('❌ Error generating product');
      setAiRunning(false);
    }
  };

  const optimizeRevenue = async () => {
    setAiRunning(true);
    setAiMessage('💰 Optimizing pricing and creating bundles...');
    
    try {
      const response = await axios.post(`${API}/ai/optimize-revenue`);
      setRevenueRecs(response.data.recommendations);
      setAiMessage('✅ Revenue optimization complete!');
      
      setTimeout(() => {
        setAiRunning(false);
        setAiMessage('');
        setActiveTab('marketing');
      }, 2000);
    } catch (error) {
      console.error("Error optimizing revenue:", error);
      setAiMessage('❌ Error optimizing revenue');
      setAiRunning(false);
    }
  };

  const generateAffiliateProgram = async () => {
    setAiRunning(true);
    setAiMessage('🤝 Creating affiliate program...');
    
    try {
      const response = await axios.post(`${API}/ai/generate-affiliate-program`);
      setAffiliateProgram(response.data.program);
      setAiMessage('✅ Affiliate program created!');
      
      setTimeout(() => {
        setAiRunning(false);
        setAiMessage('');
        setActiveTab('marketing');
      }, 2000);
    } catch (error) {
      console.error("Error creating affiliate program:", error);
      setAiMessage('❌ Error creating affiliate program');
      setAiRunning(false);
    }
  };

  const generateSocialPosts = async (productId) => {
    setAiRunning(true);
    setAiMessage('📱 Generating social media posts...');
    
    try {
      const response = await axios.post(`${API}/ai/generate-social-posts`, {
        product_id: productId,
        num_posts: 5
      });
      setSocialPosts(response.data.posts);
      setAiMessage(`✅ Generated ${response.data.posts_generated} social posts!`);
      
      setTimeout(() => {
        setAiRunning(false);
        setAiMessage('');
        setActiveTab('marketing');
      }, 2000);
    } catch (error) {
      console.error("Error generating social posts:", error);
      setAiMessage('❌ Error generating social posts');
      setAiRunning(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'bg-gray-500',
      ready: 'bg-blue-500',
      published: 'bg-green-500',
      retired: 'bg-red-500'
    };
    return colors[status] || 'bg-gray-500';
  };

  const getProductTypeIcon = (type) => {
    const icons = {
      ebook: '📚',
      course: '🎓',
      template: '📄',
      planner: '📅',
      mini_app: '⚡'
    };
    return icons[type] || '📦';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-2xl flex items-center gap-3">
          <Activity className="animate-spin" size={32} />
          Loading CEO Dashboard...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6" data-testid="ceo-dashboard">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold flex items-center gap-3" data-testid="dashboard-title">
              <Sparkles className="text-purple-400" size={40} />
              AI Empire CEO Dashboard
            </h1>
            <p className="text-gray-400 mt-2">Fully Autonomous Product Generation System</p>
          </div>
          <div className="flex items-center gap-2 bg-green-500/20 text-green-400 px-4 py-2 rounded-lg">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            System Autonomous
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="stat-total-products">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Products</p>
                <p className="text-3xl font-bold mt-1">{stats?.total_products || 0}</p>
                <p className="text-purple-400 text-sm mt-2">+{stats?.products_today || 0} today</p>
              </div>
              <Package className="text-purple-400" size={40} />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="stat-total-revenue">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Revenue</p>
                <p className="text-3xl font-bold mt-1">${stats?.total_revenue?.toFixed(2) || '0.00'}</p>
                <p className="text-green-400 text-sm mt-2">+${stats?.revenue_today?.toFixed(2) || '0.00'} today</p>
              </div>
              <DollarSign className="text-green-400" size={40} />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="stat-pending-tasks">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Pending AI Tasks</p>
                <p className="text-3xl font-bold mt-1">{stats?.pending_tasks || 0}</p>
                <p className="text-yellow-400 text-sm mt-2">In queue</p>
              </div>
              <Clock className="text-yellow-400" size={40} />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="stat-opportunities">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Opportunities</p>
                <p className="text-3xl font-bold mt-1">{stats?.active_opportunities || 0}</p>
                <p className="text-blue-400 text-sm mt-2">Trending niches</p>
              </div>
              <TrendingUp className="text-blue-400" size={40} />
            </div>
          </div>
        </div>
      </div>

      {/* AI Control Panel */}
      {aiMessage && (
        <div className="mb-6 bg-blue-500/20 border border-blue-500/50 rounded-xl p-4">
          <p className="text-white text-center font-medium">{aiMessage}</p>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="mb-6 bg-white/10 backdrop-blur-lg rounded-xl p-2 border border-white/20">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex-1 px-4 py-2 rounded-lg transition-all ${
              activeTab === 'overview' 
                ? 'bg-purple-600 text-white' 
                : 'text-gray-300 hover:bg-white/5'
            }`}
            data-testid="tab-overview"
          >
            📊 Overview
          </button>
          <button
            onClick={() => setActiveTab('marketing')}
            className={`flex-1 px-4 py-2 rounded-lg transition-all ${
              activeTab === 'marketing' 
                ? 'bg-purple-600 text-white' 
                : 'text-gray-300 hover:bg-white/5'
            }`}
            data-testid="tab-marketing"
          >
            📈 Marketing & Revenue
          </button>
        </div>
      </div>

      <div className="mb-6 bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="ai-control-panel">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Sparkles size={24} className="text-purple-400" />
          AI Team Controls
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Master Control */}
          <button
            onClick={runAutonomousCycle}
            disabled={aiRunning}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-700 px-6 py-4 rounded-lg transition-all flex items-center gap-3 justify-center font-semibold"
            data-testid="run-autonomous-cycle-btn"
          >
            <Activity className={aiRunning ? "animate-spin" : ""} size={20} />
            {aiRunning ? 'AI Teams Running...' : 'Run Autonomous Cycle'}
          </button>

          {/* Scout Opportunities */}
          <button
            onClick={scoutOpportunities}
            disabled={aiRunning}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 px-6 py-4 rounded-lg transition-all flex items-center gap-3 justify-center font-semibold"
            data-testid="scout-opportunities-btn"
          >
            <TrendingUp size={20} />
            Scout Opportunities
          </button>

          {/* Generate Product (Quick) */}
          <button
            onClick={() => opportunities.length > 0 && generateProduct(opportunities[0])}
            disabled={aiRunning || opportunities.length === 0}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-700 px-6 py-4 rounded-lg transition-all flex items-center gap-3 justify-center font-semibold"
            data-testid="quick-generate-btn"
          >
            <Package size={20} />
            Generate Product
          </button>

          {/* Revenue Optimizer */}
          <button
            onClick={optimizeRevenue}
            disabled={aiRunning}
            className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-700 px-6 py-4 rounded-lg transition-all flex items-center gap-3 justify-center font-semibold"
            data-testid="optimize-revenue-btn"
          >
            <DollarSign size={20} />
            Optimize Revenue
          </button>

          {/* Social Media Posts */}
          <button
            onClick={() => products.length > 0 && generateSocialPosts(products[0].id)}
            disabled={aiRunning || products.length === 0}
            className="bg-pink-600 hover:bg-pink-700 disabled:bg-gray-700 px-6 py-4 rounded-lg transition-all flex items-center gap-3 justify-center font-semibold"
            data-testid="generate-social-btn"
          >
            <Sparkles size={20} />
            Social Media Posts
          </button>

          {/* Affiliate Program */}
          <button
            onClick={generateAffiliateProgram}
            disabled={aiRunning}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-700 px-6 py-4 rounded-lg transition-all flex items-center gap-3 justify-center font-semibold"
            data-testid="affiliate-program-btn"
          >
            <CheckCircle size={20} />
            Affiliate Program
          </button>
        </div>

        <div className="mt-4 text-sm text-gray-400">
          <p>💡 <strong>Autonomous Cycle:</strong> Scouts opportunities → Generates 2 products → Updates dashboard</p>
        </div>
      </div>

      {/* Conditional Tab Content */}
      {activeTab === 'overview' && (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Products & Opportunities */}
        <div className="lg:col-span-2 space-y-6">
          {/* Daily Product Feed */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="daily-product-feed">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <Package size={24} className="text-purple-400" />
              Daily Product Feed
            </h2>
            
            <div className="space-y-4">
              {products.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <Package size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No products generated yet. The AI teams will start creating products automatically.</p>
                </div>
              ) : (
                products.map((product) => (
                  <div 
                    key={product.id} 
                    className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-purple-400/50 transition-all"
                    data-testid={`product-card-${product.id}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <div className="text-4xl">{getProductTypeIcon(product.product_type)}</div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-lg">{product.title}</h3>
                            <span className={`px-2 py-1 rounded text-xs ${getStatusColor(product.status)} text-white`}>
                              {product.status}
                            </span>
                          </div>
                          <p className="text-gray-400 text-sm mt-1">{product.description}</p>
                          
                          <div className="flex items-center gap-4 mt-3 text-sm">
                            <span className="text-green-400">${product.revenue.toFixed(2)} revenue</span>
                            <span className="text-blue-400">{product.conversions} conversions</span>
                            <span className="text-purple-400">${product.price} price</span>
                          </div>

                          {/* Marketplace Links */}
                          <div className="flex gap-2 mt-3">
                            {product.marketplace_links?.map((link, idx) => (
                              <a
                                key={idx}
                                href={link.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full hover:bg-purple-500/30 transition-all flex items-center gap-1"
                                data-testid={`marketplace-link-${link.platform.toLowerCase().replace(' ', '-')}`}
                              >
                                {link.platform}
                                <ExternalLink size={12} />
                              </a>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Publish Control */}
                      {product.status === 'ready' && (
                        <button
                          onClick={() => handlePublish(product.id)}
                          className="bg-green-500 hover:bg-green-600 px-4 py-2 rounded-lg flex items-center gap-2 transition-all"
                          data-testid={`publish-btn-${product.id}`}
                        >
                          <CheckCircle size={16} />
                          Publish
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Revenue Metrics Chart */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="revenue-chart">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <DollarSign size={24} className="text-green-400" />
              Revenue Metrics (7 Days)
            </h2>
            
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueMetrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                <XAxis dataKey="date" stroke="#ffffff60" />
                <YAxis stroke="#ffffff60" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e1e2e', border: '1px solid #ffffff30', borderRadius: '8px' }}
                />
                <Legend />
                <Line type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} name="Revenue ($)" />
                <Line type="monotone" dataKey="conversions" stroke="#8b5cf6" strokeWidth={2} name="Conversions" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Column - Opportunities & Alerts */}
        <div className="space-y-6">
          {/* Trending Opportunities */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="opportunities-panel">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingUp size={20} className="text-blue-400" />
              Trending Opportunities
            </h2>
            
            <div className="space-y-3">
              {opportunities.length === 0 ? (
                <p className="text-gray-400 text-sm text-center py-8">
                  Opportunity Scout AI will identify trending niches automatically.
                </p>
              ) : (
                opportunities.map((opp) => (
                  <div 
                    key={opp.id} 
                    className="bg-white/5 rounded-lg p-3 border border-white/10 hover:border-purple-400/50 transition-all"
                    data-testid={`opportunity-${opp.id}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold">{opp.niche}</h3>
                      <span className="text-yellow-400 text-sm font-bold">
                        {(opp.trend_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {opp.keywords?.slice(0, 3).map((keyword, idx) => (
                        <span 
                          key={idx}
                          className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                    <button
                      onClick={() => generateProduct(opp)}
                      disabled={aiRunning}
                      className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-3 py-1.5 rounded text-xs transition-all mt-2"
                      data-testid={`generate-from-opp-${opp.id}`}
                    >
                      Generate Product
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Optimization Alerts */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="optimization-alerts">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <AlertCircle size={20} className="text-yellow-400" />
              Optimization Alerts
            </h2>
            
            <div className="space-y-3">
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-400 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-green-400">All Systems Operational</p>
                    <p className="text-xs text-gray-400 mt-1">All AI teams running autonomously</p>
                  </div>
                </div>
              </div>

              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <AlertCircle size={16} className="text-blue-400 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-blue-400">Revenue Optimizer Active</p>
                    <p className="text-xs text-gray-400 mt-1">Analyzing pricing and campaigns</p>
                  </div>
                </div>
              </div>

              <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <Sparkles size={16} className="text-purple-400 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-purple-400">AI Teams Coordinating</p>
                    <p className="text-xs text-gray-400 mt-1">Micro-taskforce orchestrating workflows</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Product Type Distribution */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20" data-testid="product-distribution">
            <h2 className="text-xl font-bold mb-4">Product Distribution</h2>
            
            <div className="space-y-2">
              {['ebook', 'course', 'template', 'planner', 'mini_app'].map((type, idx) => {
                const count = products.filter(p => p.product_type === type).length;
                const percentage = products.length > 0 ? (count / products.length * 100).toFixed(0) : 0;
                return (
                  <div key={type}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="capitalize">{type.replace('_', ' ')}</span>
                      <span>{count} ({percentage}%)</span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full transition-all" 
                        style={{ 
                          width: `${percentage}%`,
                          backgroundColor: COLORS[idx % COLORS.length]
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      )}

      {/* Marketing & Revenue Tab */}
      {activeTab === 'marketing' && (
        <div className="space-y-6">
          {/* Revenue Optimization */}
          {revenueRecs && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <DollarSign size={24} className="text-green-400" />
                Revenue Optimization Recommendations
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                {revenueRecs.pricing_recommendations?.slice(0, 6).map((rec, idx) => (
                  <div key={idx} className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <h3 className="font-semibold mb-2">{rec.product_title}</h3>
                    <div className="flex items-center gap-4 mb-2">
                      <span className="text-gray-400">${rec.current_price}</span>
                      <span className="text-green-400">→ ${rec.recommended_price}</span>
                      <span className="text-yellow-400 text-sm">{rec.estimated_revenue_increase}</span>
                    </div>
                    <p className="text-sm text-gray-400">{rec.reasoning}</p>
                  </div>
                ))}
              </div>

              <h3 className="text-xl font-bold mb-3">Recommended Bundles</h3>
              <div className="space-y-3">
                {revenueRecs.bundles?.slice(0, 3).map((bundle, idx) => (
                  <div key={idx} className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold text-lg">{bundle.bundle_name}</h4>
                      <span className="text-green-400 font-bold">${bundle.bundle_price}</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{bundle.appeal}</p>
                    <div className="flex flex-wrap gap-2">
                      {bundle.products.map((product, pidx) => (
                        <span key={pidx} className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded">
                          {product}
                        </span>
                      ))}
                    </div>
                    <p className="text-sm text-yellow-400 mt-2">Savings: {bundle.savings}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Social Media Posts */}
          {socialPosts.length > 0 && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Sparkles size={24} className="text-pink-400" />
                Social Media Posts ({socialPosts.length})
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {socialPosts.map((post) => (
                  <div key={post.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-sm">{post.platform}</span>
                      <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">{post.status}</span>
                    </div>
                    <p className="text-sm text-gray-300 mb-2">{post.content}</p>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {post.hashtags?.map((tag, idx) => (
                        <span key={idx} className="text-xs text-blue-400">{tag}</span>
                      ))}
                    </div>
                    <div className="text-xs text-gray-500">
                      {post.post_time} • {post.cta}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Affiliate Program */}
          {affiliateProgram && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <CheckCircle size={24} className="text-indigo-400" />
                Affiliate Program
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
                <div className="bg-white/5 rounded-lg p-4">
                  <h3 className="text-sm text-gray-400">Active Affiliates</h3>
                  <p className="text-3xl font-bold text-indigo-400">{affiliateProgram.active_affiliates}</p>
                </div>
                <div className="bg-white/5 rounded-lg p-4">
                  <h3 className="text-sm text-gray-400">Total Sales</h3>
                  <p className="text-3xl font-bold text-green-400">{affiliateProgram.total_sales}</p>
                </div>
                <div className="bg-white/5 rounded-lg p-4">
                  <h3 className="text-sm text-gray-400">Total Revenue</h3>
                  <p className="text-3xl font-bold text-yellow-400">${affiliateProgram.total_revenue?.toFixed(2)}</p>
                </div>
              </div>

              <h3 className="text-xl font-bold mb-3">Top Affiliates</h3>
              <div className="space-y-2">
                {affiliateProgram.top_affiliates?.map((affiliate, idx) => (
                  <div key={affiliate.id} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{affiliate.name}</p>
                      <p className="text-sm text-gray-400">{affiliate.email}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm">
                        <span className="text-yellow-400 font-bold">{affiliate.tier}</span>
                        {' • '}
                        {affiliate.sales} sales
                      </p>
                      <p className="text-green-400 font-semibold">${affiliate.commission_earned.toFixed(2)}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 bg-indigo-500/10 border border-indigo-500/30 rounded-lg p-4">
                <h4 className="font-semibold mb-2">Commission Structure</h4>
                <div className="flex gap-4">
                  {affiliateProgram.commission_structure?.tiers?.map((tier, idx) => (
                    <div key={idx} className="flex-1 text-center">
                      <p className="text-sm text-gray-400">{tier.level}</p>
                      <p className="font-bold text-lg">{tier.rate}%</p>
                      <p className="text-xs text-gray-500">{tier.sales_required}+ sales</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!revenueRecs && !socialPosts.length && !affiliateProgram && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-12 border border-white/20 text-center">
              <DollarSign size={64} className="mx-auto mb-4 opacity-50" />
              <h2 className="text-2xl font-bold mb-2">Marketing & Revenue Optimization</h2>
              <p className="text-gray-400 mb-6">
                Use the AI Team Controls to generate marketing materials and optimize revenue
              </p>
              <div className="flex gap-3 justify-center">
                <button
                  onClick={optimizeRevenue}
                  className="bg-yellow-600 hover:bg-yellow-700 px-6 py-3 rounded-lg"
                >
                  Optimize Revenue
                </button>
                <button
                  onClick={generateAffiliateProgram}
                  className="bg-indigo-600 hover:bg-indigo-700 px-6 py-3 rounded-lg"
                >
                  Create Affiliate Program
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
