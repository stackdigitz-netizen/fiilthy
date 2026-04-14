import React, { useState, useEffect, useCallback } from 'react';
import {
  CheckCircle2, XCircle, Clock, Users, TrendingUp,
  Package, Link2, Megaphone, RefreshCw,
} from 'lucide-react';
import './ApprovalQueue.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const TYPE_ICON = {
  product:   <Package size={14} />,
  affiliate: <Link2 size={14} />,
};

function ago(iso) {
  if (!iso) return '';
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export default function ApprovalQueuePage() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState({});
  const [dismissed, setDismissed] = useState(new Set());

  const authHeader = () => {
    const t = localStorage.getItem('authToken');
    return t ? { Authorization: `Bearer ${t}` } : {};
  };

  const fetchApprovals = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/agents/approvals`, { headers: authHeader() });
      if (res.ok) {
        const data = await res.json();
        setApprovals(data.approvals || []);
      }
    } catch (err) { /* offline */ }
    finally { setLoading(false); }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 8000);
    return () => clearInterval(interval);
  }, [fetchApprovals]);

  const act = async (id, action, reason = '') => {
    setActing(a => ({ ...a, [id]: action }));
    try {
      await fetch(`${API}/api/agents/approvals/${id}/${action}${reason ? `?reason=${encodeURIComponent(reason)}` : ''}`, {
        method: 'POST',
        headers: authHeader(),
      });
      // animate out
      setDismissed(d => new Set([...d, id]));
      setTimeout(() => {
        setApprovals(prev => prev.filter(a => a.id !== id));
        setDismissed(d => { const s = new Set(d); s.delete(id); return s; });
      }, 400);
    } catch (err) { /* ignore */ }
    setActing(a => { const n = {...a}; delete n[id]; return n; });
  };

  const visible = approvals.filter(a => !dismissed.has(a.id));

  if (loading) {
    return (
      <div className="aq-root">
        <div className="aq-loading">Loading approval queue…</div>
      </div>
    );
  }

  return (
    <div className="aq-root">
      <div className="aq-header">
        <div className="aq-header-left">
          <Megaphone size={18} className="aq-header-icon" />
          <h1 className="aq-title">APPROVAL QUEUE</h1>
          {visible.length > 0 && (
            <span className="aq-count">{visible.length}</span>
          )}
        </div>
        <button className="aq-refresh" onClick={fetchApprovals} title="Refresh">
          <RefreshCw size={14} />
        </button>
      </div>
      <p className="aq-subtitle">
        Campaigns built by your agents — review and approve before they go live.
      </p>

      {visible.length === 0 ? (
        <div className="aq-empty">
          <CheckCircle2 size={32} className="aq-empty-icon" />
          <p>Queue is clear — agents are working…</p>
        </div>
      ) : (
        <div className="aq-list">
          {visible.map(item => (
            <div
              key={item.id}
              className={`aq-card ${dismissed.has(item.id) ? 'dismissing' : ''}`}
            >
              <div className="aq-card-top">
                <div className="aq-card-meta">
                  <span className={`aq-type-badge ${item.type || 'product'}`}>
                    {TYPE_ICON[item.type] || TYPE_ICON.product}
                    {item.type === 'affiliate' ? 'Affiliate Promo' : 'Product Campaign'}
                  </span>
                  <span className="aq-card-time">
                    <Clock size={10} />
                    {ago(item.created_at)}
                  </span>
                </div>
                <h2 className="aq-card-title">{item.product_title || 'Campaign'}</h2>
                {item.product_niche && item.product_niche !== 'affiliate' && (
                  <span className="aq-niche">Niche: {item.product_niche}</span>
                )}
              </div>

              {/* Platform chips */}
              <div className="aq-platforms">
                {(item.platforms || []).map(p => (
                  <span key={p} className="aq-platform-chip">{p}</span>
                ))}
              </div>

              {/* Campaign details */}
              <div className="aq-details">
                {item.estimated_reach && (
                  <div className="aq-detail">
                    <TrendingUp size={11} />
                    Est. reach: <strong>{item.estimated_reach}</strong>
                  </div>
                )}
                {item.targeting && (
                  <div className="aq-detail">
                    <Users size={11} />
                    {item.targeting}
                  </div>
                )}
                {item.budget && (
                  <div className="aq-detail">
                    <span className="aq-budget">${item.budget} budget · {item.duration_days}d</span>
                  </div>
                )}
                {item.commission_value && (
                  <div className="aq-detail">
                    <Link2 size={11} />
                    {item.commission_value}/sale commission
                  </div>
                )}
              </div>

              {/* Content preview */}
              {item.content && item.content.length > 0 && (
                <div className="aq-content-preview">
                  <div className="aq-preview-label">CONTENT PREVIEW</div>
                  <div className="aq-preview-list">
                    {item.content.slice(0, 3).map((c, i) => (
                      <div key={i} className="aq-preview-item">
                        <span className="aq-preview-platform">{c.platform}</span>
                        <span className="aq-preview-caption">{c.caption}</span>
                      </div>
                    ))}
                    {item.content.length > 3 && (
                      <div className="aq-preview-more">
                        +{item.content.length - 3} more platforms
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="aq-actions">
                <button
                  className="aq-btn-approve"
                  onClick={() => act(item.id, 'approve')}
                  disabled={!!acting[item.id]}
                >
                  <CheckCircle2 size={14} />
                  {acting[item.id] === 'approve' ? 'Launching…' : 'Approve & Launch'}
                </button>
                <button
                  className="aq-btn-reject"
                  onClick={() => act(item.id, 'reject', 'Not a fit')}
                  disabled={!!acting[item.id]}
                >
                  <XCircle size={14} />
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
