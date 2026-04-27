/**
 * Viral Content Engine Module - 4
 * Generates 100+ content pieces for marketing
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrendingUp } from 'lucide-react';

const ViralContentEngineModule = () => {
  const [contentStats, setContentStats] = useState({
    totalGenerated: 0,
    scheduled: 0,
    posted: 0,
    engagement: '0'
  });

  const [platforms, setPlatforms] = useState([
    { name: 'TikTok', icon: '🎵', pieces: 0, format: '60-sec videos' },
    { name: 'Instagram', icon: '📷', pieces: 0, format: 'Reels & Posts' },
    { name: 'Twitter', icon: '𝕏', pieces: 0, format: 'Threads' },
    { name: 'YouTube', icon: '▶️', pieces: 0, format: 'Shorts' },
    { name: 'Blog', icon: '📝', pieces: 0, format: 'SEO Posts' },
    { name: 'Email', icon: '✉️', pieces: 0, format: 'Sequences' }
  ]);

  const [loading, setLoading] = useState(true);
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    const loadContentStats = async () => {
      try {
        // Load content stats from backend
        const response = await fetch(`${API}/api/content/stats`);
        if (response.ok) {
          const data = await response.json();
          setContentStats(data || contentStats);
        }
      } catch (error) {
        console.error('Failed to load content stats:', error);
      } finally {
        setLoading(false);
      }
    };
    loadContentStats();
  }, [API, contentStats]);

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-orange-900/50 to-orange-800/50 border-orange-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Viral Content Engine
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-orange-200">Auto-generate 100+ content pieces for maximum reach</p>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="pt-4 text-center">
            <p className="text-2xl font-bold text-orange-400">{contentStats.totalGenerated}</p>
            <p className="text-xs text-slate-400">Total Pieces</p>
          </CardContent>
        </Card>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="pt-4 text-center">
            <p className="text-2xl font-bold text-cyan-400">{contentStats.scheduled}</p>
            <p className="text-xs text-slate-400">Scheduled</p>
          </CardContent>
        </Card>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="pt-4 text-center">
            <p className="text-2xl font-bold text-green-400">{contentStats.posted}</p>
            <p className="text-xs text-slate-400">Posted</p>
          </CardContent>
        </Card>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="pt-4 text-center">
            <p className="text-2xl font-bold text-pink-400">{contentStats.engagement}</p>
            <p className="text-xs text-slate-400">Engagement</p>
          </CardContent>
        </Card>
      </div>

      {/* Platforms */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">📱 Content by Platform</h3>
        <div className="space-y-3">
          {platforms.map((platform, idx) => (
            <Card key={idx} className="bg-slate-800/50 border-slate-700">
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{platform.icon}</span>
                    <div>
                      <p className="font-semibold text-white">{platform.name}</p>
                      <p className="text-sm text-slate-400">{platform.format}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-orange-400">{platform.pieces}</p>
                    <p className="text-xs text-slate-400">pieces</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="grid md:grid-cols-2 gap-3">
        <Button className="bg-orange-600 hover:bg-orange-700 h-12">
          Generate More Content
        </Button>
        <Button className="bg-orange-600 hover:bg-orange-700 h-12">
          View Content Calendar
        </Button>
      </div>
    </div>
  );
};

export default ViralContentEngineModule;

