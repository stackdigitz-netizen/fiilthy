/**
 * Analytics & Revenue Module - 6
 * Real-time revenue tracking and performance metrics
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { BarChart3 } from 'lucide-react';

const AnalyticsRevenueModule = () => {
  const [revenueData, setRevenueData] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    const loadAnalyticsData = async () => {
      try {
        // Load real data from backend
        const [revenueResponse, productsResponse] = await Promise.all([
          fetch(`${API}/api/analytics/realtime`),
          fetch(`${API}/api/products?limit=3`)
        ]);

        if (revenueResponse.ok) {
          // Format revenue data from backend
          const data = await revenueResponse.json();
          setRevenueData(data.daily_breakdown || []);
        }

        if (productsResponse.ok) {
          const products = await productsResponse.json();
          // Transform products to match the expected format
          setTopProducts(products.slice(0, 3).map(p => ({
            name: p.title,
            revenue: p.revenue || 0,
            sales: p.sales || 0
          })));
        }
      } catch (error) {
        console.error('Failed to load analytics data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadAnalyticsData();
  }, [API]);

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-indigo-900/50 to-indigo-800/50 border-indigo-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Analytics & Revenue
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="pt-4 text-center">
            <p className="text-sm text-slate-400 mb-2">Total Revenue</p>
            <p className="text-2xl font-bold text-green-400">$12,456</p>
            <p className="text-xs text-green-500 mt-1">↑ 32% MoM</p>
          </CardContent>
        </Card>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="pt-4 text-center">
            <p className="text-sm text-slate-400 mb-2">Total Sales</p>
            <p className="text-2xl font-bold text-blue-400">345</p>
            <p className="text-xs text-blue-500 mt-1">↑ 18% WoW</p>
          </CardContent>
        </Card>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="pt-4 text-center">
            <p className="text-sm text-slate-400 mb-2">Conversion Rate</p>
            <p className="text-2xl font-bold text-cyan-400">5.8%</p>
            <p className="text-xs text-cyan-500 mt-1">↑ 1.2%</p>
          </CardContent>
        </Card>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="pt-4 text-center">
            <p className="text-sm text-slate-400 mb-2">Avg Order Value</p>
            <p className="text-2xl font-bold text-purple-400">$36.13</p>
            <p className="text-xs text-purple-500 mt-1">↑ 5% WoW</p>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Chart */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">📊 Revenue This Week</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="day" stroke="#94A3B8" />
              <YAxis stroke="#94A3B8" />
              <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #475569' }} />
              <Bar dataKey="revenue" fill="#06B6D4" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Top Products */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">🏆 Top Products</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {topProducts.map((product, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                <div>
                  <p className="font-semibold text-white">{product.name}</p>
                  <p className="text-sm text-slate-400">{product.sales} sales</p>
                </div>
                <p className="text-lg font-bold text-green-400">${product.revenue}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsRevenueModule;

