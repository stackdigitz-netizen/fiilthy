/**
 * Sales Funnel Builder Module - 5
 * Creates landing pages, checkout pages, email sequences, etc
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Zap } from 'lucide-react';

const SalesFunnelBuilderModule = () => {
  const [funnelPages, setFunnelPages] = useState([]);
  const [loading, setLoading] = useState(true);
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    const loadFunnelData = async () => {
      try {
        // Load funnel from backend
        const response = await fetch(`${API}/api/sales-funnel`);
        if (response.ok) {
          const data = await response.json();
          setFunnelPages(Array.isArray(data) ? data : []);
        } else {
          // Default structure if no funnel exists
          setFunnelPages([
            { name: 'Landing Page', icon: '🎯', status: 'Draft', ctr: '0%' },
            { name: 'Product Page', icon: '📦', status: 'Draft', ctr: '0%' },
            { name: 'Checkout', icon: '💳', status: 'Draft', ctr: '0%' },
            { name: 'Upsell', icon: '⬆️', status: 'Draft', ctr: '0%' },
            { name: 'Thank You', icon: '🎉', status: 'Draft', ctr: '0%' }
          ]);
        }
      } catch (error) {
        console.error('Failed to load funnel data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadFunnelData();
  }, [API]);

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-green-900/50 to-green-800/50 border-green-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Sales Funnel Builder
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Funnel Flow */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🛣️ Funnel Pages</h3>
        <div className="space-y-2">
          {funnelPages.map((page, idx) => (
            <div key={idx} className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500/30 rounded-lg flex items-center justify-center">
                <span className="text-lg">{page.icon}</span>
              </div>
              <div className="flex-1">
                <p className="font-semibold text-white">{page.name}</p>
              </div>
              <div className="text-right">
                <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">{page.status}</span>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-cyan-400">{page.ctr}</p>
                <p className="text-xs text-slate-400">CTR</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Email Sequences */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-sm">📧 Email Sequences</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {['Welcome (7 emails)', 'Abandoned Cart (3 emails)', 'Post-Purchase (5 emails)'].map((seq, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                <p className="text-white">{seq}</p>
                <Button variant="outline" size="sm" className="border-slate-600">
                  Edit
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="grid md:grid-cols-2 gap-3">
        <Button className="bg-green-600 hover:bg-green-700 h-12">Preview Funnel</Button>
        <Button className="bg-green-600 hover:bg-green-700 h-12">Regenerate Pages</Button>
      </div>
    </div>
  );
};

export default SalesFunnelBuilderModule;

