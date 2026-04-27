import React, { useEffect, useMemo, useState } from 'react';
import { TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';
import './Pages.css';
import API_URL from '../config/api';

const API = API_URL;

const normalizeTrendScore = (value) => {
  const numericValue = Number(value || 0);
  return numericValue <= 1 ? numericValue * 100 : numericValue;
};

const OpportunitiesPage = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [minTrendScore, setMinTrendScore] = useState(60);

  useEffect(() => {
    loadOpportunities();
  }, []);

  const loadOpportunities = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API}/api/opportunities?limit=50`);
      if (!response.ok) {
        throw new Error(`Failed to load opportunities (${response.status})`);
      }

      const data = await response.json();
      setOpportunities(Array.isArray(data) ? data : []);
    } catch (loadError) {
      console.error('Failed to load opportunities:', loadError);
      setError(loadError.message);
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredOpportunities = useMemo(() => {
    return opportunities.filter((opportunity) => {
      const trendScore = normalizeTrendScore(opportunity.trend_score);
      const matchesTrend = trendScore >= minTrendScore;
      const matchesSearch = opportunity.niche
        ?.toLowerCase()
        .includes(searchTerm.trim().toLowerCase());

      return matchesTrend && (searchTerm ? matchesSearch : true);
    });
  }, [minTrendScore, opportunities, searchTerm]);

  const averageTrendScore = filteredOpportunities.length
    ? Math.round(
        filteredOpportunities.reduce(
          (sum, opportunity) => sum + normalizeTrendScore(opportunity.trend_score),
          0
        ) / filteredOpportunities.length
      )
    : 0;

  const lowCompetitionCount = filteredOpportunities.filter(
    (opportunity) => (opportunity.competition_level || '').toLowerCase() === 'low'
  ).length;

  const highPotentialCount = filteredOpportunities.filter(
    (opportunity) => normalizeTrendScore(opportunity.trend_score) >= 80
  ).length;

  const topOpportunity = filteredOpportunities[0] || null;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Opportunity Scanner</h1>
        <p>Review live market opportunities captured by the backend scanner</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Tracked Opportunities</h3>
          <p className="stat-value">{loading ? '...' : filteredOpportunities.length}</p>
          <p className="stat-change">Filtered from {opportunities.length} total records</p>
        </div>
        <div className="stat-card">
          <h3>Average Trend Score</h3>
          <p className="stat-value">{loading ? '...' : averageTrendScore}</p>
          <p className="stat-change">Current minimum threshold: {minTrendScore}</p>
        </div>
        <div className="stat-card">
          <h3>High-Potential Niches</h3>
          <p className="stat-value">{loading ? '...' : highPotentialCount}</p>
          <p className="stat-change">Trend score 80 and above</p>
        </div>
        <div className="stat-card">
          <h3>Low Competition</h3>
          <p className="stat-value">{loading ? '...' : lowCompetitionCount}</p>
          <p className="stat-change">Best candidates for fast execution</p>
        </div>
      </div>

      <div className="content-section">
        <div className="section-header">
          <h2>Active Opportunities</h2>
          <button className="btn btn-secondary" onClick={loadOpportunities} disabled={loading}>
            <RefreshCw size={16} /> {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        <div className="filter-controls mb-4">
          <input
            className="search-input"
            type="text"
            placeholder="Search niches"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
          <label style={{ marginBottom: 0, minWidth: '180px' }}>
            Min Trend Score: {minTrendScore}
          </label>
          <input
            className="slider"
            type="range"
            min="0"
            max="100"
            value={minTrendScore}
            onChange={(event) => setMinTrendScore(Number(event.target.value))}
          />
        </div>

        {loading ? (
          <div className="empty-state">
            <p>Loading live opportunity data...</p>
          </div>
        ) : filteredOpportunities.length === 0 ? (
          <div className="empty-state">
            <p>No opportunities match the current filters yet.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Niche</th>
                  <th>Trend Score</th>
                  <th>Competition</th>
                  <th>Market Size</th>
                  <th>Keywords</th>
                  <th>Suggested Products</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredOpportunities.map((opportunity) => {
                  const competition = (opportunity.competition_level || 'unknown').toLowerCase();
                  const competitionBadge =
                    competition === 'low'
                      ? 'low'
                      : competition === 'medium'
                        ? 'medium'
                        : 'high';

                  return (
                    <tr key={opportunity.id}>
                      <td className="font-semibold">{opportunity.niche}</td>
                      <td>
                        <div className="score-badge">{normalizeTrendScore(opportunity.trend_score).toFixed(1)}</div>
                      </td>
                      <td>
                        <span className={`badge badge-${competitionBadge}`}>
                          {opportunity.competition_level || 'Unknown'}
                        </span>
                      </td>
                      <td>{opportunity.market_size || 'Unknown'}</td>
                      <td>{(opportunity.keywords || []).length}</td>
                      <td>{(opportunity.suggested_products || []).length}</td>
                      <td>
                        <span className="badge badge-secondary">{(opportunity.status || 'identified').replace('_', ' ')}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h3>Top Signal</h3>
          <div className="insight-box">
            <TrendingUp size={20} />
            <div>
              <p className="font-semibold">{topOpportunity ? topOpportunity.niche : 'No opportunity ranked yet'}</p>
              <p className="text-secondary">
                {topOpportunity
                  ? `Trend score ${normalizeTrendScore(topOpportunity.trend_score).toFixed(1)} with ${topOpportunity.market_size || 'unknown market size'}`
                  : 'Run the backend opportunity flow to populate this queue.'}
              </p>
            </div>
          </div>
        </div>

        <div className="content-section">
          <h3>Scanner Notes</h3>
          <div className="insight-box">
            <AlertCircle size={20} />
            <div>
              <p className="font-semibold">Filter Coverage</p>
              <p className="text-secondary">
                {filteredOpportunities.length} opportunities currently meet the active threshold and search filters.
              </p>
            </div>
          </div>
          <div className="insight-box">
            <TrendingUp size={20} />
            <div>
              <p className="font-semibold">Low-Competition Window</p>
              <p className="text-secondary">
                {lowCompetitionCount} niches are currently tagged as low competition.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpportunitiesPage;
