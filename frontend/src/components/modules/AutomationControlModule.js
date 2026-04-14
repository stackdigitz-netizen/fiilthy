/**
 * Automation Control Center Module - 7
 * Manage all automations, workflows, and integrations
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Settings, ToggleRight, AlertCircle } from 'lucide-react';

const AutomationControlModule = () => {
  const [automations, setAutomations] = useState([]);
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    const loadAutomations = async () => {
      try {
        // Load automations from backend
        const response = await fetch(`${API}/api/automations`);
        if (response.ok) {
          const data = await response.json();
          setAutomations(data || []);
        }
        
        // Load integrations/keys status
        const keysResponse = await fetch(`${API}/api/keys/status`);
        if (keysResponse.ok) {
          const keys = await keysResponse.json();
          // api_keys_status is nested under keys.api_keys_status
          const s = keys.api_keys_status || {};
          const isOk = (val) => val && String(val).includes('[OK]');
          const integrationStatus = [
            { name: 'Gumroad', status: isOk(s.gumroad_key) ? '✅ Connected' : '❌ Not connected', icon: '🛍️' },
            { name: 'Stripe', status: isOk(s.stripe_key) ? '✅ Connected' : '❌ Not connected', icon: '💳' },
            { name: 'SendGrid', status: isOk(s.sendgrid_key) ? '✅ Connected' : '❌ Not connected', icon: '✉️' },
            { name: 'OpenAI', status: isOk(s.openai_key) ? '✅ Connected' : '❌ Not connected', icon: '🤖' },
            { name: 'Anthropic', status: isOk(s.anthropic_key) ? '✅ Connected' : '❌ Not connected', icon: '🧠' },
            { name: 'Database', status: isOk(s.database_connection) ? '✅ Connected' : '❌ Not connected', icon: '🗄️' }
          ];
          setIntegrations(integrationStatus);
        }
      } catch (error) {
        console.error('Failed to load automations:', error);
      } finally {
        setLoading(false);
      }
    };
    loadAutomations();
  }, [API]);

  const handleToggleAutomation = (id) => {
    // In production, call backend to toggle automation
    console.log('Toggle automation:', id);
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
                      onClick={() => handleToggleAutomation(auto.id)}
                      variant="outline"
                      size="sm"
                      className="border-slate-600 hover:bg-slate-700/50"
                    >
                      <ToggleRight className="w-4 h-4" />
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

