import React, { useState, useEffect, useCallback } from 'react';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw, Play, Clock, TrendingUp, Award } from 'lucide-react';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };
};

const GRADE_COLORS = {
  'A+': '#10b981',
  A: '#10b981',
  'B+': '#22c55e',
  B: '#84cc16',
  C: '#eab308',
  D: '#f97316',
  F: '#ef4444',
};

const STATUS_ICON = {
  pass: <CheckCircle size={16} style={{ color: '#10b981' }} />,
  warning: <AlertTriangle size={16} style={{ color: '#eab308' }} />,
  fail: <XCircle size={16} style={{ color: '#ef4444' }} />,
};

export default function QualityControlPage() {
  const [products, setProducts] = useState([]);
  const [cycles, setCycles] = useState([]);
  const [cycleStatus, setCycleStatus] = useState(null);
  const [standards, setStandards] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('products');
  const [expanded, setExpanded] = useState(null);
  const [triggering, setTriggering] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [reviewingAll, setReviewingAll] = useState(false);
  const [reviewSummary, setReviewSummary] = useState(null);

  const load = useCallback(async () => {
    try {
      const [prodRes, cycleRes, statusRes, stdRes] = await Promise.all([
        fetch(`${API}/api/quality/products`, { headers: getAuthHeaders() }),
        fetch(`${API}/api/quality/cycle/history?limit=10`, { headers: getAuthHeaders() }),
        fetch(`${API}/api/quality/cycle/status`, { headers: getAuthHeaders() }),
        fetch(`${API}/api/quality/standards`, { headers: getAuthHeaders() }),
      ]);

      if (prodRes.ok) setProducts(await prodRes.json());
      if (cycleRes.ok) setCycles(await cycleRes.json());
      if (statusRes.ok) setCycleStatus(await statusRes.json());
      if (stdRes.ok) setStandards(await stdRes.json());
    } catch (e) {
      console.error('QC load error:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, [load]);

  const triggerCycle = async () => {
    setTriggering(true);
    try {
      await fetch(`${API}/api/quality/cycle/trigger`, { method: 'POST', headers: getAuthHeaders() });
      setTimeout(load, 2000);
    } catch (e) {
      console.error(e);
    } finally {
      setTriggering(false);
    }
  };

  const runQC = async (productId) => {
    try {
      const res = await fetch(`${API}/api/quality/check`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ product_id: productId }),
      });
      if (res.ok) {
        setProducts(prev => prev.map(p =>
          p.id === productId ? { ...p, qc_report: { ...(p.qc_report || {}), ...(res.json() || {}) } } : p
        ));
        await load();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const reviewAllProducts = async () => {
    setReviewingAll(true);
    try {
      const res = await fetch(`${API}/api/quality/review-all`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({}),
      });
      if (res.ok) {
        setReviewSummary(await res.json());
        await load();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setReviewingAll(false);
    }
  };

  const filteredProducts = products.filter(p => {
    if (filterStatus === 'all') return true;
    return p.status === filterStatus;
  });

  const stats = {
    total: products.length,
    approved: products.filter(p => p.status === 'approved').length,
    rejected: products.filter(p => p.status === 'rejected').length,
    avgScore: products.length
      ? Math.round(products.filter(p => p.qc_score).reduce((s, p) => s + p.qc_score, 0) / products.filter(p => p.qc_score).length || 0)
      : 0,
  };

  if (loading) {
    return (
      <div className="page">
        <div className="page-header"><h1>Quality Control</h1></div>
        <div className="empty-state"><p>Loading...</p></div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Quality Control</h1>
        <p>Every product must score 80+ before it can be sold. Cycles run every 2 hours.</p>
      </div>

      {/* Stats row */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Products</div>
          <div className="stat-value">{stats.total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Approved for Sale</div>
          <div className="stat-value" style={{ color: '#10b981' }}>{stats.approved}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Rejected / In Review</div>
          <div className="stat-value" style={{ color: '#ef4444' }}>{stats.rejected}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg QC Score</div>
          <div className="stat-value">{stats.avgScore || '—'}{stats.avgScore ? '/100' : ''}</div>
        </div>
      </div>

      {/* Cycle control */}
      <div className="content-section">
        <div className="section-header">
          <h3>Automated Production Cycle</h3>
          <div className="button-group">
            <button className="btn btn-secondary btn-small" onClick={reviewAllProducts} disabled={reviewingAll}>
              <Award size={14} /> {reviewingAll ? 'Reviewing...' : 'Review Entire Catalog'}
            </button>
            <button className="btn btn-primary btn-small" onClick={triggerCycle} disabled={triggering}>
              <Play size={14} /> {triggering ? 'Starting...' : 'Run Cycle Now'}
            </button>
          </div>
        </div>
        <div className="info-grid">
          <div>
            <strong>Schedule</strong>
            Every 2 hours — 10+ products per cycle
          </div>
          <div>
            <strong>Status</strong>
            {cycleStatus?.running ? '🟢 Scheduler Running' : '🔴 Stopped'}
          </div>
          <div>
            <strong>Next Cycle</strong>
            {cycleStatus?.next_cycle_at
              ? new Date(cycleStatus.next_cycle_at).toLocaleTimeString()
              : '—'}
          </div>
          <div>
            <strong>Min Score to Sell</strong>
            80 / 100
          </div>
        </div>
        {reviewSummary && (
          <div className="info-grid" style={{ marginTop: 16 }}>
            <div><strong>Reviewed</strong> {reviewSummary.processed}</div>
            <div><strong>Approved</strong> {reviewSummary.approved + reviewSummary.published}</div>
            <div><strong>Hidden</strong> {(reviewSummary.rejected || 0) + (reviewSummary.duplicate || 0) + (reviewSummary.retired || 0)}</div>
            <div><strong>Avg Score</strong> {reviewSummary.average_score || '—'}</div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="button-group" style={{ marginBottom: 0, borderBottom: '1px solid var(--color-border)', paddingBottom: 0 }}>
        {['products', 'standards', 'cycles'].map(tab => (
          <button
            key={tab}
            className={`btn btn-small ${activeTab === tab ? 'btn-primary' : 'btn-secondary'}`}
            style={{ borderRadius: '6px 6px 0 0' }}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'products' && 'Products'}
            {tab === 'standards' && 'Quality Standards'}
            {tab === 'cycles' && 'Cycle History'}
          </button>
        ))}
      </div>

      {/* Products tab */}
      {activeTab === 'products' && (
        <div className="content-section" style={{ borderTop: 'none', borderRadius: '0 0 12px 12px' }}>
          <div className="section-header">
            <div className="button-group">
              {['all', 'approved', 'rejected', 'pending'].map(s => (
                <button
                  key={s}
                  className={`btn btn-small ${filterStatus === s ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setFilterStatus(s)}
                >
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </button>
              ))}
            </div>
            <button className="btn btn-secondary btn-small" onClick={load}>
              <RefreshCw size={14} /> Refresh
            </button>
          </div>

          {filteredProducts.length === 0 ? (
            <div className="empty-state">
              <p>No products yet. Run a generation cycle to start creating products.</p>
              <button className="btn btn-primary" onClick={triggerCycle} style={{ marginTop: 12 }}>
                <Play size={14} /> Generate First Batch
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {filteredProducts.map(product => (
                <ProductQCRow
                  key={product.id}
                  product={product}
                  expanded={expanded === product.id}
                  onToggle={() => setExpanded(expanded === product.id ? null : product.id)}
                  onRunQC={() => runQC(product.id)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Standards tab */}
      {activeTab === 'standards' && standards && (
        <div className="content-section" style={{ borderTop: 'none', borderRadius: '0 0 12px 12px' }}>
          <h3>Quality Checklist — Every product must pass all of these</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 16 }}>
            {standards.required_checks.map((check, i) => (
              <div key={i} className="detail-row">
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CheckCircle size={14} style={{ color: '#10b981', flexShrink: 0 }} />
                  {check}
                </span>
              </div>
            ))}
          </div>

          <h3 style={{ marginTop: 24 }}>Grade Scale</h3>
          <div className="info-grid" style={{ marginTop: 12 }}>
            {Object.entries(standards.scoring.grades).map(([grade, range]) => (
              <div key={grade}>
                <strong style={{ color: GRADE_COLORS[grade] || '#ccc' }}>{grade}</strong>
                &nbsp;{range}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cycles tab */}
      {activeTab === 'cycles' && (
        <div className="content-section" style={{ borderTop: 'none', borderRadius: '0 0 12px 12px' }}>
          {cycles.length === 0 ? (
            <div className="empty-state"><p>No cycles run yet.</p></div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {cycles.map(cycle => (
                <div key={cycle.id} className="launch-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8 }}>
                    <div>
                      <p style={{ margin: 0, fontWeight: 600 }}>
                        Cycle — {cycle.started_at ? new Date(cycle.started_at).toLocaleString() : '—'}
                      </p>
                      <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--color-text-secondary)' }}>
                        {cycle.status}
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: 16, fontSize: 13 }}>
                      <span>
                        <span style={{ color: '#10b981', fontWeight: 700 }}>{cycle.products_passed ?? 0}</span> passed
                      </span>
                      <span>
                        <span style={{ color: '#ef4444', fontWeight: 700 }}>{cycle.products_failed_permanently ?? 0}</span> rejected
                      </span>
                      <span>
                        <span style={{ fontWeight: 700 }}>{cycle.products_attempted ?? 0}</span> attempted
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ProductQCRow({ product, expanded, onToggle, onRunQC }) {
  const grade = product.qc_grade;
  const score = product.qc_score;
  const report = product.qc_report;

  return (
    <div className="launch-card" style={{ gap: 0 }}>
      <div
        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, cursor: 'pointer' }}
        onClick={onToggle}
      >
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ margin: 0, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {product.title || 'Untitled'}
          </p>
          <p style={{ margin: '2px 0 0', fontSize: 12, color: 'var(--color-text-secondary)' }}>
            {product.product_type?.replace(/_/g, ' ')} · Generated {product.generated_at ? new Date(product.generated_at).toLocaleDateString() : '—'}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
          {score != null && (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: GRADE_COLORS[grade] || '#ccc' }}>
                {grade || '?'}
              </div>
              <div style={{ fontSize: 11, color: 'var(--color-text-secondary)' }}>{Math.round(score)}/100</div>
            </div>
          )}

          <span
            className="badge"
            style={{
              padding: '4px 10px',
              borderRadius: 20,
              fontSize: 11,
              fontWeight: 700,
              backgroundColor: product.status === 'approved' ? 'rgba(16,185,129,0.2)' : product.status === 'rejected' ? 'rgba(239,68,68,0.2)' : 'rgba(234,179,8,0.2)',
              color: product.status === 'approved' ? '#10b981' : product.status === 'rejected' ? '#ef4444' : '#eab308',
            }}
          >
            {product.status || 'pending'}
          </span>

          <button
            className="btn btn-small btn-secondary"
            onClick={(e) => { e.stopPropagation(); onRunQC(); }}
            style={{ fontSize: 11 }}
          >
            Re-check
          </button>
        </div>
      </div>

      {/* Expanded QC details */}
      {expanded && report && (
        <div style={{ marginTop: 16, padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: 8 }}>
          <p style={{ margin: '0 0 12px', fontWeight: 600, fontSize: 13 }}>QC Breakdown</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {(report.checks || []).map((check, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                <span style={{ marginTop: 1 }}>{STATUS_ICON[check.status]}</span>
                <div style={{ flex: 1 }}>
                  <span style={{ fontWeight: 600, fontSize: 13 }}>{check.name}</span>
                  <span style={{ fontSize: 12, color: 'var(--color-text-secondary)', marginLeft: 6 }}>
                    {Math.round(check.score)}/100
                  </span>
                  <p style={{ margin: '2px 0 0', fontSize: 12, color: 'var(--color-text-secondary)' }}>
                    {check.message}
                  </p>
                  {check.fix && check.status !== 'pass' && (
                    <p style={{ margin: '4px 0 0', fontSize: 12, color: '#f59e0b' }}>
                      → Fix: {check.fix}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {(report.improvements || []).length > 0 && (
            <div style={{ marginTop: 12, padding: 12, background: 'rgba(245,158,11,0.1)', borderRadius: 6, border: '1px solid rgba(245,158,11,0.3)' }}>
              <p style={{ margin: '0 0 8px', fontWeight: 600, fontSize: 12, color: '#f59e0b' }}>
                Required Improvements
              </p>
              {report.improvements.map((imp, i) => (
                <p key={i} style={{ margin: '4px 0', fontSize: 12, color: 'var(--color-text-secondary)' }}>• {imp}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
