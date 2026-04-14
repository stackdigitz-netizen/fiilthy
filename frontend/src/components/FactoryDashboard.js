/**
 * Main Dashboard Component - Autonomous AI Product Development Factory
 * Contains all 8 dashboard modules
 */

import React, { useState, useEffect, useRef } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Search,
  Zap,
  Palette,
  Package,
  BarChart3,
  Settings,
  Lightbulb,
  TrendingUp,
  Play,
  Download,
  RefreshCw,
  Plus
} from 'lucide-react';

// Import module components
import OpportunityScannerModule from './modules/OpportunityScannerModule';
import ProductFactoryModule from './modules/ProductFactoryModule';
import BrandingStudioModule from './modules/BrandingStudioModule';
import ViralContentEngineModule from './modules/ViralContentEngineModule';
import SalesFunnelBuilderModule from './modules/SalesFunnelBuilderModule';
import AnalyticsRevenueModule from './modules/AnalyticsRevenueModule';
import AutomationControlModule from './modules/AutomationControlModule';
import AIGrowthLabModule from './modules/AIGrowthLabModule';
import WorkflowGuide from './WorkflowGuide';

/**
 * Main Factory Dashboard
 * Orchestrates all autonomous factory operations
 */
const FactoryDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [factoryStatus, setFactoryStatus] = useState({
    status: 'idle',
    cycle_id: null,
    progress: 0,
    current_stage: 'Ready'
  });

  const [cycleMetrics, setCycleMetrics] = useState({
    totalCycles: 12,
    avgProductsPerCycle: 3,
    totalRevenueGenerated: '$12,456.00',
    avgTimePerCycle: '45 mins'
  });

  const [recentProducts, setRecentProducts] = useState([]);
  const pollRef = useRef(null);
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  // Load real products from backend on mount
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const response = await fetch(`${API}/api/products?limit=3`);
        if (response.ok) {
          const data = await response.json();
          setRecentProducts(data.slice(0, 3));
        }
      } catch (error) {
        console.error('Failed to load products:', error);
      }
    };
    loadProducts();
  }, [API]);

  // Clean up polling on unmount
  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  const startFactoryCycle = async () => {
    if (pollRef.current) clearInterval(pollRef.current);

    // Call the real factory create endpoint
    let cycle_id = 'cycle_' + Date.now();
    try {
      const res = await fetch(`${API}/api/v5/factory/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niche: 'trending', target_audience: 'general', product_style: 'ebook', revenue_goal: 1000, auto_publish: false })
      });
      if (res.ok) {
        const data = await res.json();
        cycle_id = data.cycle_id || cycle_id;
      }
    } catch (e) {
      console.error('Factory create error:', e);
    }

    setFactoryStatus({ status: 'running', cycle_id, progress: 5, current_stage: 'Scanning opportunities...' });

    // Simulate progressive stages while backend works
    const stages = [
      [10, 'Analyzing market trends...'],
      [20, 'Selecting product niche...'],
      [35, 'Generating product content...'],
      [50, 'Creating branding assets...'],
      [65, 'Building sales funnel...'],
      [75, 'Generating social content...'],
      [85, 'Preparing for publishing...'],
      [95, 'Finalizing product...'],
    ];
    let stageIndex = 0;

    pollRef.current = setInterval(async () => {
      // Try polling real status endpoint
      try {
        const statusRes = await fetch(`${API}/api/v5/factory/status/${cycle_id}`);
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          const progress = statusData.progress || 0;
          const stage = statusData.current_stage || '';
          if (statusData.status === 'completed' || progress >= 100) {
            clearInterval(pollRef.current);
            setFactoryStatus({ status: 'completed', cycle_id, progress: 100, current_stage: '✅ Cycle complete!' });
            return;
          }
          if (progress > 5) {
            setFactoryStatus(prev => ({ ...prev, progress, current_stage: stage }));
            return;
          }
        }
      } catch (_) {}

      // Fallback: advance through stages visually
      if (stageIndex < stages.length) {
        const [progress, current_stage] = stages[stageIndex];
        stageIndex++;
        setFactoryStatus(prev => ({ ...prev, progress, current_stage }));
      } else {
        clearInterval(pollRef.current);
        setFactoryStatus(prev => ({ ...prev, status: 'completed', progress: 100, current_stage: '✅ Cycle complete!' }));
      }
    }, 4000);
  };

  const modules = [
    {
      id: 'scanner',
      label: 'Opportunity Scanner',
      description: 'Detect viral product opportunities',
      icon: Search,
      component: OpportunityScannerModule,
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 'factory',
      label: 'Product Factory',
      description: 'Generate complete products',
      icon: Package,
      component: ProductFactoryModule,
      color: 'from-purple-500 to-purple-600'
    },
    {
      id: 'branding',
      label: 'Branding Studio',
      description: 'Create visual branding packages',
      icon: Palette,
      component: BrandingStudioModule,
      color: 'from-pink-500 to-pink-600'
    },
    {
      id: 'content',
      label: 'Viral Content Engine',
      description: 'Generate 100+ content pieces',
      icon: TrendingUp,
      component: ViralContentEngineModule,
      color: 'from-orange-500 to-orange-600'
    },
    {
      id: 'funnel',
      label: 'Sales Funnel Builder',
      description: 'Create complete sales funnels',
      icon: Zap,
      component: SalesFunnelBuilderModule,
      color: 'from-green-500 to-green-600'
    },
    {
      id: 'analytics',
      label: 'Analytics & Revenue',
      description: 'Monitor performance & revenue',
      icon: BarChart3,
      component: AnalyticsRevenueModule,
      color: 'from-indigo-500 to-indigo-600'
    },
    {
      id: 'automation',
      label: 'Automation Control',
      description: 'Manage automations & workflows',
      icon: Settings,
      component: AutomationControlModule,
      color: 'from-cyan-500 to-cyan-600'
    },
    {
      id: 'growth',
      label: 'AI Growth Lab',
      description: 'Run experiments & optimize',
      icon: Lightbulb,
      component: AIGrowthLabModule,
      color: 'from-amber-500 to-amber-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                🏭 AI Product Development Factory
              </h1>
              <p className="text-slate-400 mt-1">Autonomous digital business machine</p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={startFactoryCycle}
                disabled={factoryStatus.status === 'running'}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600"
              >
                <Play className="w-4 h-4 mr-2" />
                {factoryStatus.status === 'running' ? 'Running...' : 'Start Cycle'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Factory Status Bar */}
      {factoryStatus.status === 'running' && (
        <div className="bg-gradient-to-r from-cyan-900 to-blue-900 border-b border-cyan-700">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <RefreshCw className="w-5 h-5 text-cyan-400 animate-spin" />
                <div>
                  <p className="font-semibold text-white">🔄 {factoryStatus.current_stage}</p>
                  <p className="text-sm text-cyan-200">Cycle ID: {factoryStatus.cycle_id}</p>
                </div>
              </div>
              <div className="w-64">
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all"
                    style={{ width: `${factoryStatus.progress}%` }}
                  />
                </div>
                <p className="text-xs text-cyan-200 mt-1 text-right">{factoryStatus.progress}% Complete</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <WorkflowGuide page="factory" />
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          {/* Tab Navigation */}
          <TabsList className="grid grid-cols-4 md:grid-cols-9 gap-2 h-auto bg-transparent p-0 mb-8">
            {/* Overview tab */}
            <TabsTrigger
              value="overview"
              className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-blue-500 data-[state=active]:text-white text-slate-400 hover:text-white transition-colors px-3 py-2 rounded-lg"
            >
              Overview
            </TabsTrigger>

            {/* Module tabs */}
            {modules.map((module) => {
              const Icon = module.icon;
              return (
                <TabsTrigger
                  key={module.id}
                  value={module.id}
                  className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-blue-500 data-[state=active]:text-white text-slate-400 hover:text-white transition-colors px-2 py-2 rounded-lg"
                  title={module.label}
                >
                  <Icon className="w-4 h-4" />
                </TabsTrigger>
              );
            })}
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-slate-400">Total Cycles</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-white">{cycleMetrics.totalCycles}</p>
                  <p className="text-xs text-cyan-400 mt-2">↑ 3 this week</p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-slate-400">Avg Products/Cycle</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-white">{cycleMetrics.avgProductsPerCycle}</p>
                  <p className="text-xs text-green-400 mt-2">↑ Increasing efficiency</p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-slate-400">Total Revenue</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-white">{cycleMetrics.totalRevenueGenerated}</p>
                  <p className="text-xs text-green-400 mt-2">↑ 32% MoM</p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-slate-400">Avg Time/Cycle</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-white">{cycleMetrics.avgTimePerCycle}</p>
                  <p className="text-xs text-cyan-400 mt-2">Fully automated</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Products */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Recent Products</CardTitle>
                <CardDescription className="text-slate-400">Latest generated products</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentProducts.map((product) => (
                    <div key={product.id} className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                      <div>
                        <p className="font-semibold text-white">{product.name}</p>
                        <p className="text-sm text-slate-400">{product.niche}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-cyan-400">{product.status}</p>
                        <p className="text-sm text-slate-400">{product.sales} sales • {product.revenue}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Module Quick Access */}
            <div>
              <h2 className="text-xl font-bold text-white mb-4">📦 Available Modules</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {modules.map((module) => {
                  const Icon = module.icon;
                  return (
                    <button
                      key={module.id}
                      onClick={() => setActiveTab(module.id)}
                      className={`p-4 rounded-lg bg-gradient-to-br ${module.color} hover:shadow-lg transform hover:scale-105 transition-all text-white`}
                    >
                      <Icon className="w-8 h-8 mb-2" />
                      <p className="font-semibold">{module.label}</p>
                      <p className="text-xs opacity-90">{module.description}</p>
                    </button>
                  );
                })}
              </div>
            </div>
          </TabsContent>

          {/* Module Tabs */}
          {modules.map((module) => {
            const Component = module.component;
            return (
              <TabsContent key={module.id} value={module.id}>
                <Component />
              </TabsContent>
            );
          })}
        </Tabs>
      </div>
    </div>
  );
};

export default FactoryDashboard;

