import React, { useState, useEffect, useCallback } from 'react';
import {
  FlaskConical, ShieldCheck, Megaphone, Package,
  Telescope, Link2, Play, Pause, Zap, Activity,
  Clock, CheckCircle2, AlertCircle, Bell, TrendingUp,
} from 'lucide-react';
import './CommandCenter.css';
import API_URL from '../config/api';

const API = API_URL;

const DIVISION_META = {
  product_rd:      { icon: FlaskConical,  label: 'Product R&D' },
  quality_control: { icon: ShieldCheck,   label: 'Quality Control' },
  social_ads:      { icon: Megaphone,     label: 'Social & Ads' },
  distribution:    { icon: Package,       label: 'Distribution' },
  discovery:       { icon: Telescope,     label: 'Discovery' },
  affiliate:       { icon: Link2,         label: 'Affiliate' },
};

const LEVEL_CLASS = { info: 'log-info', success: 'log-success', warning: 'log-warn', error: 'log-error' };

function ago(iso) {
  if (!iso) return '';
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

function money(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

export default function CommandCenterPage() {
  const [divisions, setDivisions] = useState({});
  const [metrics, setMetrics] = useState({});
  const [activity, setActivity] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState({});

  const authHeader = () => {
    const t = localStorage.getItem('authToken');
    return t ? { Authorization: `Bearer ${t}` } : {};
  };

  const fetchStatus = useCallback(async () => {
    try {
      const [statusRes, activityRes, pipelineRes] = await Promise.all([
        fetch(`${API}/api/agents/status`, { headers: authHeader() }),
        fetch(`${API}/api/agents/activity?limit=60`, { headers: authHeader() }),
        fetch(`${API}/api/agents/pipeline?limit=6`, { headers: authHeader() }),
      ]);
      if (statusRes.ok) {
        const data = await statusRes.json();
        setDivisions(data.divisions || {});
        setMetrics(data.metrics || {});
      }
      if (activityRes.ok) {
        const data = await activityRes.json();
        setActivity(data.activity || []);
      }
      if (pipelineRes.ok) {
        const data = await pipelineRes.json();
        setTopProducts(data.products || []);
      }
    } catch (err) {
      // backend offline
    } finally {
      setLoading(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 4000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const toggleDivision = async (divId, isRunning) => {
    setToggling(t => ({ ...t, [divId]: true }));
    try {
      const action = isRunning ? 'stop' : 'start';
      await fetch(`${API}/api/agents/${divId}/${action}`, {
        method: 'POST',
        headers: authHeader(),
      });
      await fetchStatus();
    } catch (err) { /* ignore */ }
    setToggling(t => ({ ...t, [divId]: false }));
  };

  const startAll = async () => {
    await fetch(`${API}/api/agents/start-all`, {
      method: 'POST',
      headers: authHeader(),
    });
    await fetchStatus();
  };

  const activeDivisions = Object.values(divisions).filter(d => d.is_running).length;
  const pendingApprovals = metrics.pending_approvals || 0;

  if (loading) {
    return (
      <div className="cc-loading">
        <div className="cc-pulse">Initialising Agent Empire…</div>
      </div>
    );
  }

  return (
    <div className="cc-root">
      {/* ── Top bar ── */}
      <div className="cc-topbar">
        <div className="cc-topbar-left">
          <h1 className="cc-title">AGENT EMPIRE</h1>
          <div className={`cc-live-badge ${activeDivisions > 0 ? 'active' : ''}`}>
            <span className="cc-live-dot" />
            {activeDivisions > 0 ? `${activeDivisions} divisions live` : 'All paused'}
          </div>
        </div>
        <div className="cc-topbar-right">
          {pendingApprovals > 0 && (
            <a href="/approvals" className="cc-approval-alert">
              <Bell size={14} />
              {pendingApprovals} awaiting approval
            </a>
          )}
          <button className="cc-btn-launch" onClick={startAll}>
            <Zap size={14} />
            Launch All
          </button>
        </div>
      </div>

      {/* ── Metrics row ── */}
      <div className="cc-metrics">
        {[
          { label: 'Products Today', value: metrics.products_today ?? 0 },
          { label: 'Approved Today', value: metrics.approved_today ?? 0 },
          { label: 'Store Ready', value: metrics.store_ready ?? 0 },
          { label: 'Published', value: metrics.published_products ?? 0 },
          { label: 'Live Campaigns', value: metrics.live_campaigns ?? 0 },
          { label: 'Pending Approval', value: metrics.pending_approvals ?? 0, highlight: true },
          { label: 'Revenue', value: money(metrics.revenue_total ?? 0) },
          { label: 'Total Products', value: metrics.total_products ?? 0 },
          { label: 'Opportunities', value: metrics.total_opportunities ?? 0 },
          { label: 'Affiliate Links', value: metrics.total_affiliate ?? 0 },
        ].map(m => (
          <div key={m.label} className={`cc-metric ${m.highlight ? 'highlight' : ''}`}>
            <div className="cc-metric-value">{m.value}</div>
            <div className="cc-metric-label">{m.label}</div>
          </div>
        ))}
      </div>

      {/* ── Division grid ── */}
      <div className="cc-divisions">
        {Object.entries(DIVISION_META).map(([divId, meta]) => {
          const div = divisions[divId] || {};
          const Icon = meta.icon;
          const isRunning = div.is_running;
          const color = div.color || '#00e5ff';
          const progress = div.cycle_progress || 0;
          const target = div.cycle_target || div.products_per_cycle || 0;
          const pct = target > 0 ? Math.min(100, Math.round((progress / target) * 100)) : 0;

          return (
            <div
              key={divId}
              className={`cc-card ${isRunning ? 'running' : 'idle'}`}
              style={{ '--div-color': color }}
            >
              <div className="cc-card-accent" />
              <div className="cc-card-header">
                <div className="cc-card-icon">
                  <Icon size={18} />
                </div>
                <div className="cc-card-title">
                  <span className="cc-card-name">{div.name || meta.label}</span>
                  <span className={`cc-status-badge ${isRunning ? 'on' : 'off'}`}>
                    {isRunning ? 'LIVE' : 'IDLE'}
                  </span>
                </div>
                <button
                  className={`cc-toggle ${isRunning ? 'running' : ''}`}
                  onClick={() => toggleDivision(divId, isRunning)}
                  disabled={!!toggling[divId]}
                  title={isRunning ? 'Pause division' : 'Start division'}
                >
                  {isRunning ? <Pause size={14} /> : <Play size={14} />}
                </button>
              </div>

              <p className="cc-card-tagline">{div.tagline || ''}</p>

              <div className="cc-card-task">
                {isRunning && <span className="cc-task-dot" />}
                <span>{div.current_task || 'Ready'}</span>
              </div>

              {target > 0 && (
                <div className="cc-progress-wrap">
                  <div className="cc-progress-bar">
                    <div className="cc-progress-fill" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="cc-progress-label">{progress}/{target}</span>
                </div>
              )}

              <div className="cc-card-agents">
                {(div.agents || []).map(a => (
                  <span key={a} className={`cc-agent-chip ${isRunning ? 'active' : ''}`}>
                    {a}
                  </span>
                ))}
              </div>

              {div.last_cycle_at && (
                <div className="cc-card-meta">
                  <Clock size={10} />
                  Last cycle {ago(div.last_cycle_at)}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="cc-panel">
        <div className="cc-panel-header">
          <TrendingUp size={14} />
          TOP LIVE OFFERS
          <span className="cc-feed-count">{topProducts.length} tracked</span>
        </div>
        {topProducts.length === 0 ? (
          <div className="cc-feed-empty">No store-ready offers yet — launch the divisions above.</div>
        ) : (
          <div className="cc-product-list">
            {topProducts.map((product) => (
              <div key={product.id || product.title} className="cc-product-row">
                <div className="cc-product-main">
                  <div className="cc-product-title-row">
                    <span className="cc-product-title">{product.title || 'Untitled product'}</span>
                    {(product.featured || product.featured_candidate) && (
                      <span className="cc-pill featured">Featured</span>
                    )}
                    <span className="cc-pill status">{product.status || 'draft'}</span>
                  </div>
                  <div className="cc-product-meta-row">
                    <span>Launch {Math.round(product.launch_score || 0)}</span>
                    <span>QC {Math.round(product.qc_score || 0)}</span>
                    <span>{money(product.revenue || 0)}</span>
                    <span>{product.campaign_status || 'campaign pending'}</span>
                  </div>
                </div>
                <a
                  className="cc-product-link"
                  href={product.store_url || '/store'}
                  target="_blank"
                  rel="noreferrer"
                >
                  View Store
                </a>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Activity feed ── */}
      <div className="cc-feed-wrap">
        <div className="cc-feed-header">
          <Activity size={14} />
          LIVE ACTIVITY
          <span className="cc-feed-count">{activity.length} events</span>
        </div>
        <div className="cc-feed">
          {activity.length === 0 && (
            <div className="cc-feed-empty">No activity yet — start the divisions above</div>
          )}
          {activity.map((evt, i) => (
            <div key={evt.id || i} className={`cc-feed-row ${LEVEL_CLASS[evt.level] || 'log-info'}`}>
              <span className="cc-feed-time">{ago(evt.timestamp)}</span>
              <span className="cc-feed-div" style={{ color: divisions[evt.division]?.color || '#888' }}>
                {evt.division_name || evt.division}
              </span>
              <span className="cc-feed-agent">[{evt.agent}]</span>
              <span className="cc-feed-msg">{evt.message}</span>
              {evt.level === 'success' && <CheckCircle2 size={11} className="cc-feed-icon" />}
              {evt.level === 'warning' && <AlertCircle size={11} className="cc-feed-icon warn" />}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
