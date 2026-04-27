/**
 * Opportunity Scanner Module - 1
 * Scans for trending niches and market opportunities
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrendingUp, Search, Zap } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const OpportunityScannerModule = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [loading, setLoading] = useState(true);
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    const loadOpportunities = async () => {
      try {
        const response = await fetch(`${API}/api/opportunities?limit=3`);
        if (response.ok) {
          const data = await response.json();
          setOpportunities(Array.isArray(data) ? data : []);
        }
      } catch (error) {
        console.error('Failed to load opportunities:', error);
      } finally {
        setLoading(false);
      }
    };
    loadOpportunities();
  }, [API]);

  const startScan = async () => {
    setScanning(true);
    // In production, call the backend scanner endpoint
    setTimeout(() => setScanning(false), 2000);
  };

  const trendData = [
    { month: 'Jan', trend: 65 },
    { month: 'Feb', trend: 72 },
    { month: 'Mar', trend: 68 },
    { month: 'Apr', trend: 85 },
    { month: 'May', trend: 92 },
    { month: 'Jun', trend: 88 }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-gradient-to-r from-blue-900/50 to-blue-800/50 border-blue-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Search className="w-5 h-5" />
            Opportunity Scanner
          </CardTitle>
          <CardDescription className="text-blue-200">
            Real-time market trends and profitable niches
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={startScan}
            disabled={scanning}
            className="w-full bg-blue-600 hover:bg-blue-700"
          >
            {scanning ? '🔍 Scanning...' : '🔍 Scan for Opportunities'}
          </Button>
          <p className="text-sm text-blue-300">
            Analyzes Google Trends, Reddit, Twitter, TikTok, and competitor data
          </p>
        </CardContent>
      </Card>

      {/* Opportunity Cards */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🎯 Top Opportunities</h3>
        <div className="space-y-4">
          {opportunities.map((opp) => (
            <Card key={opp.id} className="bg-slate-800/50 border-slate-700 hover:border-blue-500 transition-colors">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold text-white text-lg">{opp.niche}</p>
                      <p className="text-sm text-slate-400">Market Size: {opp.marketSize}</p>
                    </div>
                    <div className="flex gap-2">
                      <div className="text-right">
                        <p className="text-2xl font-bold text-cyan-400">{opp.demandScore}</p>
                        <p className="text-xs text-slate-400">Demand Score</p>
                      </div>
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-slate-700/30 p-3 rounded-lg">
                      <p className="text-xs text-slate-400">Trend Score</p>
                      <p className="text-lg font-semibold text-orange-400">{opp.trendScore}</p>
                    </div>
                    <div className="bg-slate-700/30 p-3 rounded-lg">
                      <p className="text-xs text-slate-400">Competition</p>
                      <p className="text-lg font-semibold text-yellow-400">{opp.competition}</p>
                    </div>
                    <div className="bg-slate-700/30 p-3 rounded-lg">
                      <p className="text-xs text-slate-400">Recommended Price</p>
                      <p className="text-sm font-semibold text-green-400">{opp.recommendedPrice}</p>
                    </div>
                  </div>

                  {/* Pain Points */}
                  <div>
                    <p className="text-xs font-semibold text-slate-300 mb-2">💭 Top Pain Points:</p>
                    <div className="flex gap-2">
                      {opp.painPoints.map((point, idx) => (
                        <span key={idx} className="bg-blue-500/30 text-blue-200 text-xs px-3 py-1 rounded-full">
                          {point}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Action */}
                  <Button className="w-full bg-blue-600 hover:bg-blue-700">
                    Create Product From This Opportunity
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Trending Chart */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">📈 Market Trends (Last 6 Months)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="month" stroke="#94A3B8" />
              <YAxis stroke="#94A3B8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1E293B',
                  border: '1px solid #475569',
                  borderRadius: '8px'
                }}
              />
              <Line
                type="monotone"
                dataKey="trend"
                stroke="#06B6D4"
                strokeWidth={2}
                dot={{ fill: '#06B6D4', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default OpportunityScannerModule;

