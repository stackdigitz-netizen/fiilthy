/**
 * Automation Control Center Module - 7
 * Manage all automations, workflows, and integrations
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Settings, Toggle2, AlertCircle } from 'lucide-react';

const AutomationControlModule = () => {
  const [automations, setAutomations] = useState([
    {
      id: 1,
      name: 'Auto-publish to Gumroad',
      status: 'active',
      lastRun: '2 hours ago',
      nextRun: 'Tomorrow 9 AM'
    },
    {
      id: 2,
      name: 'Daily TikTok posting',
      status: 'active',
      lastRun: '1 hour ago',
      nextRun: 'Today 3 PM'
    },
    {
      id: 3,
      name: 'Email sequence sender',
      status: 'active',
      lastRun: '30 mins ago',
      nextRun: 'Today 6 PM'
    },
    {
      id: 4,
      name: 'Revenue report',
      status: 'paused',
      lastRun: '3 days ago',
      nextRun: '-'
    }
  ]);

  const integrations = [
    { name: 'Gumroad', status: '✅ Connected', icon: '🛍️' },
    { name: 'Shopify', status: '❌ Not connected', icon: '🏪' },
    { name: 'Stripe', status: '✅ Connected', icon: '💳' },
    { name: 'TikTok API', status: '✅ Connected', icon: '🎵' },
    { name: 'Instagram', status: '✅ Connected', icon: '📷' },
    { name: 'Twitter', status: '❌ Needs refresh', icon: '𝕏' },
    { name: 'SendGrid', status: '✅ Connected', icon: '✉️' },
    { name: 'Google Trends', status: '✅ Connected', icon: '📊' }
  ];

  const toggleAutomation = (id) => {
    setAutomations(automations.map(a => 
      a.id === id ? { ...a, status: a.status === 'active' ? 'paused' : 'active' } : a
    ));
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-cyan-900/50 to-cyan-800/50 border-cyan-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Automation Control Center
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Automations */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🤖 Active Automations</h3>
        <div className="space-y-3">
          {automations.map((auto) => (
            <Card key={auto.id} className="bg-slate-800/50 border-slate-700">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-white">{auto.name}</p>
                    <p className="text-sm text-slate-400">Last: {auto.lastRun} • Next: {auto.nextRun}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      auto.status === 'active' 
                        ? 'bg-green-500/30 text-green-200'
                        : 'bg-slate-600/30 text-slate-300'
                    }`}>
                      {auto.status === 'active' ? '🟢' : '⚪'} {auto.status.toUpperCase()}
                    </span>
                    <Button
                      onClick={() => toggleAutomation(auto.id)}
                      variant="outline"
                      size="sm"
                      className="border-slate-600 hover:bg-slate-700/50"
                    >
                      <Toggle2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Integrations */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🔌 Platform Integrations</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {integrations.map((int, idx) => (
            <Card key={idx} className="bg-slate-800/50 border-slate-700 hover:border-cyan-500 transition-colors cursor-pointer">
              <CardContent className="pt-6 text-center">
                <p className="text-2xl mb-2">{int.icon}</p>
                <p className="font-semibold text-white text-sm">{int.name}</p>
                <p className={`text-xs mt-2 ${int.status.includes('Connected') ? 'text-green-400' : 'text-yellow-400'}`}>
                  {int.status}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Alerts */}
      <Card className="bg-yellow-900/30 border-yellow-700">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-yellow-100">⚠️ Twitter API token expiring soon</p>
              <p className="text-sm text-yellow-200 mt-1">Refresh your Twitter API credentials to keep automations running</p>
              <Button size="sm" className="mt-3 bg-yellow-600 hover:bg-yellow-700">
                Refresh Now
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AutomationControlModule;

