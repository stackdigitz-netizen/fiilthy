import React, { useState, useEffect, useCallback } from 'react';
import { Radar, Users, Zap, TrendingUp, RefreshCw, Play, FastForward, ChevronRight } from 'lucide-react';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const REVENUE_COLORS = {
  very_high: { bg: '#28a74520', color: '#28a745' },
  high: { bg: '#17a2b820', color: '#17a2b8' },
  'medium-high': { bg: '#ffc10720', color: '#ffc107' },
  medium: { bg: '#fd7e1420', color: '#fd7e14' },
  recurring: { bg: '#7c3aed20', color: '#7c3aed' },
};

const COMPETITION_COLORS = {
  low: '#28a745',
  medium: '#ffc107',
  high: '#dc3545',
};

const HunterPage = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [teams, setTeams] = useState([]);
  const [teamsSummary, setTeamsSummary] = useState(null);
  const [hunting, setHunting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [creatingTeam, setCreatingTeam] = useState(null);
  const [activeTab, setActiveTab] = useState('opportunities');
  const [advancingTeam, setAdvancingTeam] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [oppRes, teamsRes, summaryRes] = await Promise.all([
        fetch(`${API}/api/hunter/opportunities?limit=50`),
        fetch(`${API}/api/hunter/teams`),
        fetch(`${API}/api/teams/summary`),
      ]);
      if (oppRes.ok) {
        const d = await oppRes.json();
        setOpportunities(d.opportunities || []);
      }
      if (teamsRes.ok) {
        const d = await teamsRes.json();
        setTeams(d.teams || []);
      }
      if (summaryRes.ok) {
        setTeamsSummary(await summaryRes.json());
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const hunt = async () => {
    setHunting(true);
    try {
      const r = await fetch(`${API}/api/hunter/hunt`, { method: 'POST' });
      const data = await r.json();
      if (data.success) {
        await load();
        alert(`Hunt complete! ${data.opportunities_found} new opportunities found.`);
      }
    } catch (e) {
      alert(e.message);
    } finally {
      setHunting(false);
    }
  };

  const createTeam = async (oppId) => {
    setCreatingTeam(oppId);
    try {
      const r = await fetch(`${API}/api/hunter/team?opportunity_id=${oppId}`, { method: 'POST' });
      const data = await r.json();
      if (data.success) {
        await load();
      } else {
        alert(data.message || data.detail || 'Failed to create team');
      }
    } catch (e) {
      alert(e.message);
    } finally {
      setCreatingTeam(null);
    }
  };

  const advanceTeam = async (teamId) => {
    setAdvancingTeam(teamId);
    try {
      const r = await fetch(`${API}/api/teams/${teamId}/advance`, { method: 'POST' });
      const data = await r.json();
      if (!data.success) alert(data.message || 'Could not advance team');
      await load();
    } catch (e) {
      alert(e.message);
    } finally {
      setAdvancingTeam(null);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1><Radar size={28} style={{ marginRight: 8, verticalAlign: 'middle' }} />Opportunity Hunter</h1>
        <p>AI scouts trending niches and deploys specialized agent teams to execute them</p>
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {/* Summary tiles */}
      {teamsSummary && (
        <div className="stats-grid" style={{ marginBottom: 24 }}>
          <div className="stat-card">
            <h3>Opportunities</h3>
            <p className="stat-value">{opportunities.length}</p>
            <p className="stat-change">discovered</p>
          </div>
          <div className="stat-card">
            <h3>Agent Teams</h3>
            <p className="stat-value">{teamsSummary.total_teams || teams.length}</p>
            <p className="stat-change">{teamsSummary.active_teams || 0} active</p>
          </div>
          <div className="stat-card">
            <h3>Tasks Done</h3>
            <p className="stat-value">{teamsSummary.total_tasks_completed || 0}</p>
            <p className="stat-change">completed</p>
          </div>
          <div className="stat-card">
            <h3>Revenue</h3>
            <p className="stat-value">${(teamsSummary.total_revenue_generated || 0).toFixed(2)}</p>
            <p className="stat-change">from teams</p>
          </div>
        </div>
      )}

      {/* Action bar */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        <button
          className="btn btn-primary"
          onClick={hunt}
          disabled={hunting}
          style={{ display: 'flex', alignItems: 'center', gap: 6 }}
        >
          <Radar size={16} style={{ animation: hunting ? 'spin 1s linear infinite' : 'none' }} />
          {hunting ? 'Hunting...' : 'Hunt New Opportunities'}
        </button>
        <button className="btn btn-outline" onClick={load} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <RefreshCw size={14} />Refresh
        </button>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          {['opportunities', 'teams'].map((tab) => (
            <button
              key={tab}
              className={`btn ${activeTab === tab ? 'btn-primary' : 'btn-outline'}`}
              style={{ padding: '6px 16px', fontSize: 13, textTransform: 'capitalize' }}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'opportunities' ? <><Target size={14} style={{ marginRight: 4 }} />{opportunities.length} Opportunities</> : <><Users size={14} style={{ marginRight: 4 }} />{teams.length} Teams</>}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loading-state">Loading...</div>
      ) : activeTab === 'opportunities' ? (
        <div className="content-section">
          <h2>🎯 Discovered Opportunities ({opportunities.length})</h2>
          {opportunities.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '48px 0', color: '#555' }}>
              <Radar size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
              <p>No opportunities yet. Click "Hunt New Opportunities" to start.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
              {opportunities.map((opp) => {
                const revColor = REVENUE_COLORS[opp.revenue_potential] || REVENUE_COLORS.medium;
                const compColor = COMPETITION_COLORS[opp.competition_level] || '#888';
                const hasTeam = opp.status === 'team_assigned';
                return (
                  <div key={opp.id} style={{
                    background: '#1a1a2e', border: '1px solid #333', borderRadius: 10, padding: 20,
                    display: 'flex', flexDirection: 'column', gap: 10,
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ fontWeight: 700, marginBottom: 4, fontSize: 15 }}>{opp.title}</div>
                        <div style={{ fontSize: 12, color: '#888' }}>{opp.category_name} • {opp.type?.replace(/_/g, ' ')}</div>
                      </div>
                      <div style={{ fontSize: 20, fontWeight: 700, color: '#7c3aed' }}>
                        {Math.round((opp.trend_score || 0) * 100)}%
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      <span style={{ padding: '2px 8px', borderRadius: 10, fontSize: 11, ...revColor }}>
                        {opp.revenue_potential} potential
                      </span>
                      <span style={{ padding: '2px 8px', borderRadius: 10, fontSize: 11, background: `${compColor}20`, color: compColor }}>
                        {opp.competition_level} competition
                      </span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: 12 }}>
                      <div style={{ color: '#888' }}>⏱ {opp.estimated_time_to_market}</div>
                      <div style={{ color: '#28a745' }}>💰 {opp.estimated_monthly_revenue}/mo</div>
                    </div>
                    {opp.action_items?.length > 0 && (
                      <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12, color: '#aaa' }}>
                        {opp.action_items.slice(0, 3).map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    )}
                    <button
                      className={`btn ${hasTeam ? 'btn-outline' : 'btn-primary'}`}
                      style={{ width: '100%', fontSize: 12, marginTop: 4 }}
                      disabled={hasTeam || creatingTeam === opp.id}
                      onClick={() => createTeam(opp.id)}
                    >
                      {hasTeam ? '✅ Team Assigned' : creatingTeam === opp.id ? 'Creating Team...' : '🚀 Deploy Agent Team'}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        <div className="content-section">
          <h2>👥 Agent Teams ({teams.length})</h2>
          {teams.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '48px 0', color: '#555' }}>
              <Users size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
              <p>No teams yet. Deploy a team from an opportunity above.</p>
            </div>
          ) : teams.map((team) => (
            <div key={team.id} style={{
              background: '#1a1a2e', border: '1px solid #333', borderRadius: 10,
              padding: 20, marginBottom: 16,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 16 }}>{team.opportunity_title || team.id}</div>
                  <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                    Category: {team.category} • Team ID: {team.id}
                  </div>
                </div>
                <span style={{
                  padding: '3px 10px', borderRadius: 10, fontSize: 12,
                  background: team.status === 'active' ? '#28a74520' : '#ffc10720',
                  color: team.status === 'active' ? '#28a745' : '#ffc107',
                }}>{team.status}</span>
              </div>

              {/* Team agents */}
              {team.agents?.length > 0 && (
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
                  {team.agents.map((agent, i) => (
                    <span key={i} style={{
                      padding: '3px 10px', borderRadius: 10, fontSize: 11,
                      background: '#7c3aed20', color: '#7c3aed', border: '1px solid #7c3aed40',
                    }}>
                      {agent.name}
                    </span>
                  ))}
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 12 }}>
                <div style={{ background: '#0d0d1a', borderRadius: 8, padding: '10px 14px', textAlign: 'center' }}>
                  <div style={{ fontSize: 20, fontWeight: 700 }}>{team.tasks_completed || 0}</div>
                  <div style={{ fontSize: 11, color: '#888' }}>Tasks Done</div>
                </div>
                <div style={{ background: '#0d0d1a', borderRadius: 8, padding: '10px 14px', textAlign: 'center' }}>
                  <div style={{ fontSize: 20, fontWeight: 700 }}>{team.products_created || 0}</div>
                  <div style={{ fontSize: 11, color: '#888' }}>Products</div>
                </div>
                <div style={{ background: '#0d0d1a', borderRadius: 8, padding: '10px 14px', textAlign: 'center' }}>
                  <div style={{ fontSize: 20, fontWeight: 700, color: '#28a745' }}>${team.revenue_generated || 0}</div>
                  <div style={{ fontSize: 11, color: '#888' }}>Revenue</div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  className="btn btn-primary"
                  style={{ fontSize: 12, flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4 }}
                  onClick={() => advanceTeam(team.id)}
                  disabled={advancingTeam === team.id}
                >
                  <FastForward size={13} />
                  {advancingTeam === team.id ? 'Advancing...' : 'Advance Phase'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Inline icon helper referenced in HunterPage above
function Target({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  );
}

export default HunterPage;
