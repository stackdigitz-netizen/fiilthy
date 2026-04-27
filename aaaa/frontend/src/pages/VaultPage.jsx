import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import './Pages.css';
import API_URL from '../config/api';

const API = API_URL;

const VAULT_KEYS = [
  { key: 'tiktok_api_key', label: 'TikTok API Key' },
  { key: 'instagram_graph_api_key', label: 'Instagram Graph API Key' },
  { key: 'facebook_api_key', label: 'Facebook API Key' },
  { key: 'youtube_api_key', label: 'YouTube API Key' },
  { key: 'twitter_api_key', label: 'Twitter API Key' },
  { key: 'linkedin_api_key', label: 'LinkedIn API Key' },
  { key: 'openai_key', label: 'OpenAI API Key' },
  { key: 'anthropic_key', label: 'Anthropic API Key' },
  { key: 'stripe_key', label: 'Stripe API Key' },
  { key: 'gumroad_key', label: 'Gumroad API Key' },
  { key: 'sendgrid_key', label: 'SendGrid API Key' },
  { key: 'elevenlabs_key', label: 'ElevenLabs API Key' },
  { key: 'mongodb_url', label: 'MongoDB URL' },
];

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}


const VaultPage = () => {
  const [vaultKeys, setVaultKeys] = useState({});
  const [keyStatus, setKeyStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showKey, setShowKey] = useState({});

  // Fetch all keys
  const loadVault = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/keys/vault`, { headers: getAuthHeaders() });
      if (!res.ok) throw new Error(`Failed to load vault keys (${res.status})`);
      const data = await res.json();
      setVaultKeys(data);
      // Fetch status
      const statusRes = await fetch(`${API}/api/keys/status`, { headers: getAuthHeaders() });
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setKeyStatus(statusData);
      }
    } catch (e) {
      setError(e.message);
      setVaultKeys({});
      setKeyStatus({});
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVault();
    // eslint-disable-next-line
  }, []);


  const toggleShow = (key) => setShowKey((prev) => ({ ...prev, [key]: !prev[key] }));

  return (
    <div className="page">
      <div className="page-header">
        <h1>🔐 Vault</h1>
        <p>All social and service API keys are shown below. Keep them secure!</p>
        <button className="btn btn-outline" onClick={loadVault} style={{ marginLeft: 16 }}>
          <RefreshCw size={14} style={{ marginRight: 4 }} />Refresh
        </button>
      </div>
      {error && <div className="error-banner">⚠️ {error}</div>}
      {loading ? (
        <div className="loading-state">Loading vault...</div>
      ) : (
        <div className="content-section">
          <h2>API Keys</h2>
          <div className="keys-table">
            {VAULT_KEYS.map(({ key, label }) => (
              <div key={key} className="key-row">
                <div className="key-info">
                  <div className="key-name">
                    <h4>{label}</h4>
                    {keyStatus[key] === true && <CheckCircle size={16} color="#28a745" title="Active/Connected" />}
                    {keyStatus[key] === false && <XCircle size={16} color="#dc3545" title="Not Connected" />}
                  </div>
                  <div className="key-display">
                    <input
                      type={showKey[key] ? 'text' : 'password'}
                      value={vaultKeys[key] || ''}
                      readOnly
                      style={{width: '100%', fontFamily: 'monospace', background: '#181818', color: '#fff', border: '1px solid #333', borderRadius: 4, padding: 4, fontSize: 14}}
                    />
                  </div>
                </div>
                <div className="key-actions">
                  <button
                    className="btn btn-secondary btn-small"
                    onClick={() => toggleShow(key)}
                  >
                    {showKey[key] ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VaultPage;
