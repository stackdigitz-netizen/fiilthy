/**
 * AI Growth Lab Module - 8
 * Run A/B tests, experiments, and growth optimization
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lightbulb, Plus, TrendingUp } from 'lucide-react';

const AIGrowthLabModule = () => {
  const [experiments, setExperiments] = useState([
    {
      id: 1,
      type: 'Price Test',
      variants: ['$19', '$27', '$37', '$47'],
      winner: '$27',
      uplift: '24%',
      status: 'completed',
      duration: '7 days'
    },
    {
      id: 2,
      type: 'Landing Page Copy',
      variants: ['Version A', 'Version B', 'Version C'],
      winner: 'Version B',
      uplift: '18%',
      status: 'running',
      duration: '5 days remaining'
    },
    {
      id: 3,
      type: 'Ad Creative',
      variants: ['Design 1', 'Design 2'],
      winner: null,
      uplift: null,
      status: 'paused',
      duration: '3 days'
    }
  ]);

  const growthStrategies = [
    { icon: '📋', name: 'Duplicate Winners', desc: 'Clone high-performing products' },
    { icon: '📦', name: 'Create Bundles', desc: 'Combine products for upsells' },
    { icon: '🔄', name: 'Product Variations', desc: 'Create niche variations' },
    { icon: '📈', name: 'Subscription Tier', desc: 'Convert to recurring revenue' },
    { icon: '💎', name: 'Premium Tier', desc: 'Create higher-ticket offers' },
    { icon: '🎁', name: 'Affiliate Program', desc: 'Launch commission-based sales' }
  ];

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-amber-900/50 to-amber-800/50 border-amber-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            AI Growth Lab
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-amber-200">Run experiments and automatically optimize your products</p>
        </CardContent>
      </Card>

      {/* Active Experiments */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🧪 Active Experiments</h3>
        <div className="space-y-3">
          {experiments.map((exp) => (
            <Card key={exp.id} className="bg-slate-800/50 border-slate-700">
              <CardContent className="pt-6">
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-semibold text-white">{exp.type}</p>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      exp.status === 'running' ? 'bg-blue-500/30 text-blue-200' :
                      exp.status === 'completed' ? 'bg-green-500/30 text-green-200' :
                      'bg-slate-600/30 text-slate-300'
                    }`}>
                      {exp.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-slate-400">{exp.duration}</p>
                </div>

                {/* Variants */}
                <div className="mb-4">
                  <p className="text-xs font-semibold text-slate-400 mb-2">Variants:</p>
                  <div className="flex flex-wrap gap-2">
                    {exp.variants.map((v, idx) => (
                      <span key={idx} className={`px-2 py-1 text-xs rounded ${
                        v === exp.winner
                          ? 'bg-green-500/30 text-green-200 font-semibold'
                          : 'bg-slate-700/50 text-slate-300'
                      }`}>
                        {v} {v === exp.winner && '👑'}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Results */}
                {exp.uplift && (
                  <div className="pt-4 border-t border-slate-700">
                    <p className="text-sm text-slate-400 mb-2">Winner: <span className="text-green-400 font-semibold">{exp.winner}</span></p>
                    <p className="text-lg font-bold text-green-400">↑ {exp.uplift} Improvement</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 mt-4">
                  {exp.status === 'running' && (
                    <>
                      <Button size="sm" variant="outline" className="flex-1 border-slate-600">Pause</Button>
                      <Button size="sm" variant="outline" className="flex-1 border-slate-600">View Results</Button>
                    </>
                  )}
                  {exp.status === 'completed' && (
                    <>
                      <Button size="sm" className="flex-1 bg-green-600 hover:bg-green-700">Apply Winner</Button>
                      <Button size="sm" variant="outline" className="flex-1 border-slate-600">Run Again</Button>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Start New Experiment */}
      <Card className="bg-slate-800/50 border-slate-700 border-dashed">
        <CardContent className="pt-6">
          <Button className="w-full bg-amber-600 hover:bg-amber-700 h-12">
            <Plus className="w-4 h-4 mr-2" /> Start New Experiment
          </Button>
        </CardContent>
      </Card>

      {/* Growth Strategies */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🚀 Growth Strategies</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {growthStrategies.map((strategy, idx) => (
            <Button
              key={idx}
              variant="outline"
              className="h-auto py-4 flex flex-col gap-2 border-slate-700 hover:border-amber-500 hover:bg-amber-900/30"
            >
              <span className="text-2xl">{strategy.icon}</span>
              <p className="font-semibold text-white text-sm">{strategy.name}</p>
              <p className="text-xs text-slate-400">{strategy.desc}</p>
            </Button>
          ))}
        </div>
      </div>

      {/* Growth Insights */}
      <Card className="bg-gradient-to-r from-green-900/30 to-emerald-900/30 border-green-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="p-3 bg-slate-700/30 rounded-lg">
            <p className="text-sm text-slate-300">
              💡 Your top-performing product "AI Writing Tool" has 45% higher conversion than average. 
              Consider creating 2-3 variations targeting different audiences.
            </p>
          </div>
          <div className="p-3 bg-slate-700/30 rounded-lg">
            <p className="text-sm text-slate-300">
              💡 Price test shows $27 is optimal for your niche, but could test $37 bundle in 14 days for higher AOV.
            </p>
          </div>
          <div className="p-3 bg-slate-700/30 rounded-lg">
            <p className="text-sm text-slate-300">
              💡 Email sequences have 32% open rate. Consider adding SMS follow-up for 18% improvement potential.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIGrowthLabModule;

