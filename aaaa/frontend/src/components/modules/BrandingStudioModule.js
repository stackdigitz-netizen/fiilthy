/**
 * Branding Studio Module - 3
 * Generates logos, covers, thumbnails, brand guidelines
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Palette, RefreshCw } from 'lucide-react';

const BrandingStudioModule = () => {
  const [branding, setBranding] = useState({
    logo: 'https://via.placeholder.com/200x200?text=Logo',
    colors: {
      primary: '#6366F1',
      secondary: '#EC4899',
      accent: '#F97316'
    },
    generated: 0
  });

  const [brandingAssets, setBrandingAssets] = useState([
    { name: 'Logo', icon: '📿', count: 0 },
    { name: 'Covers', icon: '📕', count: 0 },
    { name: 'Thumbnails', icon: '🖼️', count: 0 },
    { name: 'Ad Creatives', icon: '📢', count: 0 },
    { name: 'Social Templates', icon: '📱', count: 0 },
    { name: 'Email Headers', icon: '✉️', count: 0 }
  ]);

  const [loading, setLoading] = useState(true);
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    const loadBrandingData = async () => {
      try {
        // Load branding data from backend
        const response = await fetch(`${API}/api/branding`);
        if (response.ok) {
          const data = await response.json();
          setBranding(data || branding);
        }
      } catch (error) {
        console.error('Failed to load branding data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadBrandingData();
  }, [API, branding]);

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-pink-900/50 to-pink-800/50 border-pink-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Palette className="w-5 h-5" />
            Branding Studio
          </CardTitle>
        </CardHeader>
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Logo Preview */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm">Logo Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-slate-900 p-12 rounded-lg flex items-center justify-center mb-4">
              <img src={branding.logo} alt="Logo" className="h-32" />
            </div>
            <Button className="w-full bg-pink-600 hover:bg-pink-700">
              <RefreshCw className="w-4 h-4 mr-2" /> Regenerate Logo
            </Button>
          </CardContent>
        </Card>

        {/* Color Palette */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm">Color Palette</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(branding.colors).map(([key, value]) => (
                <div key={key} className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-lg border-2 border-slate-600"
                    style={{ backgroundColor: value }}
                  ></div>
                  <div>
                    <p className="capitalize font-semibold text-white">{key}</p>
                    <p className="text-sm text-slate-400">{value}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Assets Grid */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🎨 Generated Assets</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {brandingAssets.map((asset, idx) => (
            <Card key={idx} className="bg-slate-800/50 border-slate-700 hover:border-pink-500 transition-colors cursor-pointer">
              <CardContent className="pt-6 text-center">
                <p className="text-3xl mb-2">{asset.icon}</p>
                <p className="font-semibold text-white">{asset.name}</p>
                <p className="text-lg font-bold text-pink-400">{asset.count}</p>
                <p className="text-xs text-slate-400">variations</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BrandingStudioModule;

