import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Search, Zap, Target, Users, TrendingUp, 
  Plus, Play, Pause, RefreshCw, ChevronRight,
  Sparkles, AlertCircle, CheckCircle, Clock
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const OpportunityHunter = ({ onClose }) => {
  const [opportunities, setOpportunities] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hunting, setHunting] = useState(false);
  const [message, setMessage] = useState(null);
  const [activeTab, setActiveTab] = useState('opportunities');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [oppsRes, teamsRes] = await Promise.all([
        axios.get(`${API}/hunter/opportunities`),
        axios.get(`${API}/hunter/teams`)
      ]);
      setOpportunities(oppsRes.data.opportunities || []);
      setTeams(teamsRes.data.teams || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const startHunting = async () => {
    setHunting(true);
    setMessage({ type: 'info', text: '🔍 Hunting for new opportunities...' });
    
    try {
      const response = await axios.post(`${API}/hunter/hunt`);
      setMessage({
        type: 'success',
        text: `🎯 Found ${response.data.opportunities_found} new opportunities!`
      });
      setOpportunities(response.data.opportunities || []);
    } catch (error) {
      setMessage({ type: 'error', text: 'Hunting failed' });
    }
    setHunting(false);
  };

  const createTeam = async (opportunityId) => {
    setLoading(true);
    try {
      // Create team
      const response = await axios.post(`${API}/hunter/team?opportunity_id=${opportunityId}`);
      if (response.data.success) {
        const teamId = response.data.team.id;
        
        // Activate team immediately
        setMessage({ type: 'info', text: '🤖 Activating agent team...' });
        const activateRes = await axios.post(`${API}/teams/${teamId}/activate`);
        
        if (activateRes.data.success) {
          setMessage({ type: 'success', text: '🚀 Team created and working! Check Teams tab for progress.' });
        } else {
          setMessage({ type: 'success', text: '🤖 Team created! Activate it in Teams tab.' });
        }
        
        fetchData();
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create team' });
    }
    setLoading(false);
  };

  const activateTeam = async (teamId) => {
    setLoading(true);
    setMessage({ type: 'info', text: '🚀 Activating team...' });
    try {
      const response = await axios.post(`${API}/teams/${teamId}/activate`);
      if (response.data.success) {
        setMessage({ type: 'success', text: '⚡ Team is now working!' });
        fetchData();
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to activate team' });
    }
    setLoading(false);
  };

  const advanceTeam = async (teamId) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/teams/${teamId}/advance`);
      if (response.data.success) {
        if (response.data.status === 'completed') {
          setMessage({ type: 'success', text: '🎉 Team completed all phases!' });
        } else {
          setMessage({ type: 'success', text: `✅ Advanced to ${response.data.new_phase} phase!` });
        }
        fetchData();
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to advance team' });
    }
    setLoading(false);
  };

  const getRevenueBadge = (potential) => {
    const colors = {
      'very_high': 'bg-green-500',
      'high': 'bg-emerald-500',
      'medium-high': 'bg-blue-500',
      'medium': 'bg-yellow-500',
      'recurring': 'bg-purple-500'
    };
    return colors[potential] || 'bg-gray-500';
  };

  const getCompetitionColor = (level) => {
    const colors = { low: 'text-green-400', medium: 'text-yellow-400', high: 'text-red-400' };
    return colors[level] || 'text-gray-400';
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden border border-white/20">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-600 to-red-600 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Target size={32} className="text-white" />
              <div>
                <h2 className="text-2xl font-bold text-white">Opportunity Hunter</h2>
                <p className="text-white/70 text-sm">AI agents continuously finding income opportunities</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={startHunting}
                disabled={hunting}
                className="bg-white/20 hover:bg-white/30 px-6 py-2 rounded-lg flex items-center gap-2 transition-all font-semibold"
              >
                {hunting ? (
                  <>
                    <RefreshCw size={20} className="animate-spin" />
                    Hunting...
                  </>
                ) : (
                  <>
                    <Search size={20} />
                    Hunt Now
                  </>
                )}
              </button>
              <button
                onClick={onClose}
                className="text-white/70 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-white/10 px-6">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('opportunities')}
              className={`py-4 px-4 border-b-2 transition-all ${
                activeTab === 'opportunities'
                  ? 'border-orange-500 text-orange-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-2">
                <TrendingUp size={18} />
                Opportunities ({opportunities.length})
              </div>
            </button>
            <button
              onClick={() => setActiveTab('teams')}
              className={`py-4 px-4 border-b-2 transition-all ${
                activeTab === 'teams'
                  ? 'border-orange-500 text-orange-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-2">
                <Users size={18} />
                Agent Teams ({teams.length})
              </div>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-220px)]">
          {/* Message */}
          {message && (
            <div className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${
              message.type === 'success' ? 'bg-green-500/20 text-green-400' :
              message.type === 'error' ? 'bg-red-500/20 text-red-400' :
              'bg-blue-500/20 text-blue-400'
            }`}>
              {message.type === 'success' ? <CheckCircle size={20} /> :
               message.type === 'error' ? <AlertCircle size={20} /> :
               <RefreshCw size={20} className="animate-spin" />}
              {message.text}
            </div>
          )}

          {activeTab === 'opportunities' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {opportunities.map(opp => (
                <div
                  key={opp.id}
                  className="bg-white/5 border border-white/10 rounded-xl p-5 hover:border-white/20 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-lg">{opp.title}</h4>
                      <p className="text-sm text-gray-400">{opp.category_name}</p>
                    </div>
                    <span className={`${getRevenueBadge(opp.revenue_potential)} px-2 py-1 rounded text-xs font-semibold`}>
                      {opp.revenue_potential?.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 mb-4 text-sm">
                    <div className="bg-black/20 rounded-lg p-2">
                      <p className="text-gray-500 text-xs">Trend Score</p>
                      <p className="font-bold text-green-400">{Math.round(opp.trend_score * 100)}%</p>
                    </div>
                    <div className="bg-black/20 rounded-lg p-2">
                      <p className="text-gray-500 text-xs">Competition</p>
                      <p className={`font-bold capitalize ${getCompetitionColor(opp.competition_level)}`}>
                        {opp.competition_level}
                      </p>
                    </div>
                    <div className="bg-black/20 rounded-lg p-2">
                      <p className="text-gray-500 text-xs">Est. Revenue</p>
                      <p className="font-bold text-blue-400">{opp.estimated_monthly_revenue}/mo</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock size={14} />
                      {opp.estimated_time_to_market}
                    </div>
                    {opp.status === 'discovered' ? (
                      <button
                        onClick={() => createTeam(opp.id)}
                        disabled={loading}
                        className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-semibold transition-all"
                      >
                        <Zap size={16} />
                        Create Team
                      </button>
                    ) : (
                      <span className="text-green-400 text-sm flex items-center gap-1">
                        <CheckCircle size={16} />
                        Team Assigned
                      </span>
                    )}
                  </div>
                </div>
              ))}

              {opportunities.length === 0 && (
                <div className="col-span-2 text-center py-12 text-gray-500">
                  <Search size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No opportunities found yet.</p>
                  <p className="text-sm">Click "Hunt Now" to discover new opportunities!</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'teams' && (
            <div className="space-y-4">
              {teams.map(team => (
                <div
                  key={team.id}
                  className="bg-white/5 border border-white/10 rounded-xl p-5"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-semibold text-lg">{team.opportunity_title}</h4>
                      <p className="text-sm text-gray-400">Team ID: {team.id}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      team.status === 'working' ? 'bg-green-500/20 text-green-400 animate-pulse' :
                      team.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
                      team.status === 'active' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {team.status === 'working' ? '⚡ Working' : team.status}
                    </span>
                  </div>

                  {/* Work Plan Progress */}
                  {team.work_plan && (
                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-gray-400">Phase: <span className="text-white font-medium capitalize">{team.current_phase || 'starting'}</span></span>
                        <span className="text-gray-400">{team.tasks_completed || 0} tasks done</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full transition-all"
                          style={{ width: `${Math.min(((team.tasks_completed || 0) / 15) * 100, 100)}%` }}
                        />
                      </div>
                      {team.work_plan.phases && (
                        <div className="flex gap-1 mt-2">
                          {team.work_plan.phases.map((phase, idx) => (
                            <span 
                              key={idx}
                              className={`text-xs px-2 py-1 rounded ${
                                team.current_phase === phase.phase 
                                  ? 'bg-green-500/30 text-green-400' 
                                  : 'bg-white/5 text-gray-500'
                              }`}
                            >
                              {phase.phase}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Agent Outputs */}
                  {team.outputs && team.outputs.length > 0 && (
                    <div className="mb-4 bg-black/20 rounded-lg p-3 max-h-40 overflow-y-auto">
                      <p className="text-xs text-gray-400 mb-2">Recent Activity:</p>
                      {team.outputs.slice(-3).map((output, idx) => (
                        <div key={idx} className="text-xs mb-2 border-l-2 border-purple-500 pl-2">
                          <span className="text-purple-400 font-medium">{output.agent}:</span>
                          <span className="text-gray-300 ml-1">{output.output}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mb-4">
                    <p className="text-sm text-gray-400 mb-2">Agents ({team.agents?.length || 0})</p>
                    <div className="flex flex-wrap gap-2">
                      {team.agents?.map((agent, idx) => (
                        <span
                          key={idx}
                          className={`px-3 py-1 rounded-full text-xs flex items-center gap-1 ${
                            agent.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-white/10'
                          }`}
                        >
                          <Sparkles size={12} className="text-purple-400" />
                          {agent.name}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-center mb-4">
                    <div className="bg-black/20 rounded-lg p-3">
                      <p className="text-2xl font-bold">{team.tasks_completed || 0}</p>
                      <p className="text-xs text-gray-400">Tasks Done</p>
                    </div>
                    <div className="bg-black/20 rounded-lg p-3">
                      <p className="text-2xl font-bold">{team.products_created || 0}</p>
                      <p className="text-xs text-gray-400">Products</p>
                    </div>
                    <div className="bg-black/20 rounded-lg p-3">
                      <p className="text-2xl font-bold text-green-400">${team.revenue_generated || 0}</p>
                      <p className="text-xs text-gray-400">Revenue</p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    {team.status !== 'working' && (
                      <button
                        onClick={() => activateTeam(team.id)}
                        disabled={loading}
                        className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2"
                      >
                        <Play size={16} />
                        Activate Team
                      </button>
                    )}
                    {team.status === 'working' && (
                      <button
                        onClick={() => advanceTeam(team.id)}
                        disabled={loading}
                        className="flex-1 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2"
                      >
                        <ChevronRight size={16} />
                        Advance Phase
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {teams.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <Users size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No agent teams created yet.</p>
                  <p className="text-sm">Create a team from the Opportunities tab!</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OpportunityHunter;
