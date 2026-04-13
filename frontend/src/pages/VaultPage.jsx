import React, { useState, useEffect, useCallback } from 'react';
import { Shield, Plus, Trash2, CheckCircle, XCircle, Eye, EyeOff, RefreshCw } from 'lucide-react';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const CATEGORY_LABELS = {
  payments: '💳 Payments',
  marketplace: '🛒 Marketplaces',
  social: '📱 Social Media',
  video: '🎬 Video',
  audio: '🎧 Audio',
  email: '📧 Email & Marketing',
  ads: '📊 Advertising',
  ai: '🤖 AI Services',
  analytics: '📈 Analytics',
  affiliate: '🔗 Affiliate',
};

const VaultPage = () => {
  const [storedCreds, setStoredCreds] = useState([]);
  const [availableCreds, setAvailableCreds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedType, setSelectedType] = useState(null);
  const [schema, setSchema] = useState(null);
  const [formValues, setFormValues] = useState({});
  const [saving, setSaving] = useState(false);
  const [testResults, setTestResults] = useState({});
  const [showFields, setShowFields] = useState({});
  const [activeCategory, setActiveCategory] = useState('all');

  const loadCredentials = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API}/api/vault/credentials`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      setStoredCreds(data.stored || []);
      setAvailableCreds(data.available || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCredentials();
  }, [loadCredentials]);

  const openAdd = async (credType) => {
    setSelectedType(credType);
    setFormValues({});
    setSchema(null);
    try {
      const r = await fetch(`${API}/api/vault/credentials/${credType}`);
      if (r.ok) {
        const s = await r.json();
        setSchema(s);
      }
    } catch (_) {}
  };

  const saveCredentials = async () => {
    if (!selectedType) return;
    setSaving(true);
    try {
      const r = await fetch(`${API}/api/vault/credentials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential_type: selectedType, credentials: formValues }),
      });
      const data = await r.json();
      if (data.success) {
        setSelectedType(null);
        loadCredentials();
      } else {
        alert(data.message || 'Failed to save credentials');
      }
    } catch (e) {
      alert(e.message);
    } finally {
      setSaving(false);
    }
  };

  const testCredential = async (credType) => {
    setTestResults((prev) => ({ ...prev, [credType]: 'testing' }));
    try {
      const r = await fetch(`${API}/api/vault/credentials/${credType}/test`, { method: 'POST' });
      const data = await r.json();
      setTestResults((prev) => ({ ...prev, [credType]: data.success ? 'ok' : 'fail' }));
    } catch (_) {
      setTestResults((prev) => ({ ...prev, [credType]: 'fail' }));
    }
  };

  const deleteCredential = async (credType) => {
    if (!window.confirm(`Delete credentials for ${credType}?`)) return;
    try {
      await fetch(`${API}/api/vault/credentials/${credType}`, { method: 'DELETE' });
      loadCredentials();
    } catch (e) {
      alert(e.message);
    }
  };

  const allCreds = [...storedCreds, ...availableCreds];
  const categories = ['all', ...new Set(
    allCreds.map((c) => c.category || 'other').filter(Boolean)
  )];

  const stored = activeCategory === 'all'
    ? storedCreds
    : storedCreds.filter((c) => (c.category || 'other') === activeCategory);
  const available = activeCategory === 'all'
    ? availableCreds
    : availableCreds.filter((c) => (c.category || 'other') === activeCategory);

  const toggleShow = (key) => setShowFields((p) => ({ ...p, [key]: !p[key] }));

  return (
    <div className="page">
      <div className="page-header">
        <h1><Shield size={28} style={{ marginRight: 8, verticalAlign: 'middle' }} />Credential Vault</h1>
        <p>Securely store API keys and credentials for all platforms</p>
      </div>

      {error && (
        <div className="error-banner">⚠️ {error}</div>
      )}

      {/* Category filter */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 24 }}>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`btn ${activeCategory === cat ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '6px 14px', fontSize: 13 }}
          >
            {cat === 'all' ? '🔐 All' : (CATEGORY_LABELS[cat] || cat)}
          </button>
        ))}
        <button
          className="btn btn-outline"
          onClick={loadCredentials}
          style={{ marginLeft: 'auto', padding: '6px 14px' }}
        >
          <RefreshCw size={14} style={{ marginRight: 4 }} />Refresh
        </button>
      </div>

      {loading ? (
        <div className="loading-state">Loading vault...</div>
      ) : (
        <>
          {/* Stored credentials */}
          {stored.length > 0 && (
            <div className="content-section">
              <h2>✅ Connected ({stored.length})</h2>
              <div className="stats-grid">
                {stored.map((cred) => (
                  <div key={cred.type || cred.credential_type} className="stat-card" style={{ position: 'relative' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ fontSize: 22 }}>{cred.icon || '🔑'}</div>
                        <h3 style={{ margin: '8px 0 4px' }}>{cred.name}</h3>
                        <p style={{ fontSize: 12, color: '#666', margin: 0 }}>{cred.description}</p>
                      </div>
                      <div style={{ display: 'flex', gap: 4 }}>
                        {testResults[cred.type] === 'ok' && <CheckCircle size={16} color="#28a745" />}
                        {testResults[cred.type] === 'fail' && <XCircle size={16} color="#dc3545" />}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 6, marginTop: 12 }}>
                      <button
                        className="btn btn-outline"
                        style={{ fontSize: 11, padding: '4px 8px', flex: 1 }}
                        onClick={() => testCredential(cred.type || cred.credential_type)}
                        disabled={testResults[cred.type] === 'testing'}
                      >
                        {testResults[cred.type] === 'testing' ? 'Testing…' : 'Test'}
                      </button>
                      <button
                        className="btn btn-outline"
                        style={{ fontSize: 11, padding: '4px 8px', flex: 1 }}
                        onClick={() => openAdd(cred.type || cred.credential_type)}
                      >
                        Update
                      </button>
                      <button
                        className="btn"
                        style={{ fontSize: 11, padding: '4px 8px', background: '#dc354520', color: '#dc3545', border: '1px solid #dc3545' }}
                        onClick={() => deleteCredential(cred.type || cred.credential_type)}
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Available to add */}
          {available.length > 0 && (
            <div className="content-section">
              <h2>➕ Available to Connect ({available.length})</h2>
              <div className="stats-grid">
                {available.map((cred) => (
                  <div key={cred.type || cred.credential_type} className="stat-card" style={{ opacity: 0.75 }}>
                    <div style={{ fontSize: 22 }}>{cred.icon || '🔑'}</div>
                    <h3 style={{ margin: '8px 0 4px' }}>{cred.name}</h3>
                    <p style={{ fontSize: 12, color: '#666', margin: '0 0 12px' }}>{cred.description}</p>
                    <button
                      className="btn btn-primary"
                      style={{ width: '100%', fontSize: 12 }}
                      onClick={() => openAdd(cred.type || cred.credential_type)}
                    >
                      <Plus size={12} style={{ marginRight: 4 }} />Connect
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Add / Edit modal */}
      {selectedType && (
        <div
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
          }}
          onClick={(e) => e.target === e.currentTarget && setSelectedType(null)}
        >
          <div style={{
            background: '#1a1a2e', border: '1px solid #333', borderRadius: 12,
            padding: 32, width: '100%', maxWidth: 480, maxHeight: '80vh', overflowY: 'auto',
          }}>
            <h2 style={{ marginBottom: 8 }}>
              {schema?.icon || '🔑'} {schema?.name || selectedType}
            </h2>
            <p style={{ color: '#888', marginBottom: 24, fontSize: 14 }}>
              {schema?.description || 'Enter your credentials below'}
            </p>
            {(schema?.fields || []).map((field) => (
              <div key={field} style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', marginBottom: 6, fontSize: 13, color: '#ccc', textTransform: 'capitalize' }}>
                  {field.replace(/_/g, ' ')}
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showFields[field] ? 'text' : 'password'}
                    value={formValues[field] || ''}
                    onChange={(e) => setFormValues((p) => ({ ...p, [field]: e.target.value }))}
                    placeholder={`Enter ${field.replace(/_/g, ' ')}`}
                    style={{
                      width: '100%', padding: '10px 40px 10px 12px',
                      background: '#0d0d1a', border: '1px solid #444',
                      borderRadius: 6, color: '#fff', fontSize: 14, boxSizing: 'border-box',
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => toggleShow(field)}
                    style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#888', cursor: 'pointer' }}
                  >
                    {showFields[field] ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
            ))}
            <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={saveCredentials} disabled={saving}>
                {saving ? 'Saving...' : 'Save Credentials'}
              </button>
              <button className="btn btn-outline" onClick={() => setSelectedType(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VaultPage;
