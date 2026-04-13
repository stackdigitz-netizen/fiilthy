import React, { useState, useEffect, useCallback } from 'react';
import { Bot, Bell, TrendingUp, Package, Target, CheckCircle, RefreshCw, BellOff } from 'lucide-react';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const AssistantPage = () => {
  const [status, setStatus] = useState(null);
  const [quickStats, setQuickStats] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [markingRead, setMarkingRead] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statusRes, statsRes, notifsRes] = await Promise.all([
        fetch(`${API}/api/assistant/status`),
        fetch(`${API}/api/assistant/quick-stats`),
        fetch(`${API}/api/assistant/notifications`),
      ]);

      if (statusRes.ok) setStatus(await statusRes.json());
      if (statsRes.ok) setQuickStats(await statsRes.json());
      if (notifsRes.ok) {
        const nd = await notifsRes.json();
        setNotifications(nd.notifications || []);
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

  const markRead = async (id) => {
    setMarkingRead(id);
    try {
      await fetch(`${API}/api/assistant/notifications/${id}/read`, { method: 'POST' });
      setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n));
    } catch (_) {}
    setMarkingRead(null);
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  const statCards = quickStats ? [
    { label: 'Products', value: quickStats.products || 0, icon: <Package size={20} /> },
    { label: 'Revenue', value: `$${(quickStats.revenue || 0).toFixed(2)}`, icon: <TrendingUp size={20} /> },
    { label: 'Opportunities', value: quickStats.opportunities || 0, icon: <Target size={20} /> },
    { label: 'Pending Tasks', value: quickStats.pending_tasks || 0, icon: <CheckCircle size={20} /> },
  ] : [];

  return (
    <div className="page">
      <div className="page-header">
        <h1><Bot size={28} style={{ marginRight: 8, verticalAlign: 'middle' }} />Atlas — AI Assistant</h1>
        <p>{status?.greeting || 'Your personal AI that keeps the empire running'}</p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <button className="btn btn-outline" onClick={load} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          Refresh
        </button>
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {/* Quick stats row */}
      <div className="stats-grid">
        {loading
          ? [1, 2, 3, 4].map((i) => (
              <div key={i} className="stat-card" style={{ opacity: 0.4 }}>
                <h3>Loading...</h3>
                <p className="stat-value">—</p>
              </div>
            ))
          : statCards.map((s) => (
              <div key={s.label} className="stat-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <h3>{s.label}</h3>
                  <span style={{ color: '#7c3aed' }}>{s.icon}</span>
                </div>
                <p className="stat-value">{s.value}</p>
              </div>
            ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Alerts */}
        <div className="content-section">
          <h2>🚨 Alerts</h2>
          {loading ? <p>Loading...</p> : (status?.alerts?.length ? (
            status.alerts.map((alert, i) => (
              <div key={i} style={{
                padding: '12px 16px', borderRadius: 8, marginBottom: 10,
                background: alert.type === 'opportunity' ? '#1a2a1a' : '#1a1a2e',
                border: `1px solid ${alert.type === 'opportunity' ? '#28a745' : '#7c3aed'}`,
              }}>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{alert.icon} {alert.message}</div>
                <div style={{ fontSize: 12, color: '#888' }}>{alert.action}</div>
              </div>
            ))
          ) : <p style={{ color: '#666' }}>No active alerts — all clear!</p>)}
        </div>

        {/* Recommendations */}
        <div className="content-section">
          <h2>💡 Recommendations</h2>
          {loading ? <p>Loading...</p> : (status?.recommendations?.length ? (
            status.recommendations.map((rec, i) => (
              <div key={i} style={{
                padding: '12px 16px', borderRadius: 8, marginBottom: 10,
                background: '#1a1a2e', border: '1px solid #333',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontWeight: 600, marginBottom: 4 }}>{rec.icon} {rec.title}</div>
                    <div style={{ fontSize: 12, color: '#aaa' }}>{rec.description}</div>
                  </div>
                  <span style={{
                    padding: '2px 8px', borderRadius: 10, fontSize: 10,
                    background: rec.priority === 'high' ? '#dc354520' : '#28a74520',
                    color: rec.priority === 'high' ? '#dc3545' : '#28a745',
                  }}>
                    {rec.priority}
                  </span>
                </div>
              </div>
            ))
          ) : <p style={{ color: '#666' }}>No recommendations right now.</p>)}
        </div>
      </div>

      {/* Recent activity */}
      {status?.recent_activity?.length > 0 && (
        <div className="content-section">
          <h2>⏱ Recent Activity</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #333' }}>
                  {['Title', 'Status', 'Time'].map((h) => (
                    <th key={h} style={{ textAlign: 'left', padding: '8px 12px', color: '#888', fontWeight: 500 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {status.recent_activity.map((item, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #1a1a1a' }}>
                    <td style={{ padding: '10px 12px' }}>{item.title || '—'}</td>
                    <td style={{ padding: '10px 12px' }}>
                      <span style={{
                        padding: '2px 10px', borderRadius: 10, fontSize: 11,
                        background: item.status === 'live' ? '#28a74520' : '#ffc10720',
                        color: item.status === 'live' ? '#28a745' : '#ffc107',
                      }}>{item.status}</span>
                    </td>
                    <td style={{ padding: '10px 12px', color: '#666', fontSize: 12 }}>
                      {item.time ? new Date(item.time).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Notifications */}
      <div className="content-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2>
            <Bell size={18} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Notifications
            {unreadCount > 0 && (
              <span style={{
                marginLeft: 8, background: '#7c3aed', color: '#fff',
                borderRadius: 10, padding: '1px 8px', fontSize: 12,
              }}>{unreadCount}</span>
            )}
          </h2>
        </div>
        {loading ? <p>Loading...</p> : notifications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#555' }}>
            <BellOff size={32} style={{ marginBottom: 8 }} />
            <p>No notifications yet</p>
          </div>
        ) : (
          notifications.map((n) => (
            <div key={n.id} style={{
              padding: '12px 16px', borderRadius: 8, marginBottom: 8,
              background: n.read ? '#111' : '#1a1a2e',
              border: `1px solid ${n.read ? '#222' : '#7c3aed'}`,
              display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
            }}>
              <div>
                <div style={{ fontWeight: n.read ? 400 : 600, marginBottom: 4 }}>
                  {n.icon && `${n.icon} `}{n.message || n.title || 'Notification'}
                </div>
                <div style={{ fontSize: 11, color: '#666' }}>
                  {n.timestamp ? new Date(n.timestamp).toLocaleString() : ''}
                </div>
              </div>
              {!n.read && (
                <button
                  className="btn btn-outline"
                  style={{ fontSize: 11, padding: '3px 8px', marginLeft: 12, whiteSpace: 'nowrap' }}
                  onClick={() => markRead(n.id)}
                  disabled={markingRead === n.id}
                >
                  Mark read
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AssistantPage;
