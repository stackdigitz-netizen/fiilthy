import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Check, Plus, RefreshCw, X } from 'lucide-react';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const BACKEND_KEY_TEMPLATES = [
  { name: 'openai_key', label: 'OpenAI API Key', category: 'AI', description: 'Used for product ideation, copy, and AI generation.' },
  { name: 'anthropic_key', label: 'Anthropic Claude Key', category: 'AI', description: 'Used for long-form analysis and strategy tasks.' },
  { name: 'dalle_key', label: 'DALL-E API Key', category: 'AI', description: 'Used for image generation and visual assets.' },
  { name: 'sendgrid_key', label: 'SendGrid API Key', category: 'Email', description: 'Used for transactional email and sequences.' },
  { name: 'sendgrid_from_email', label: 'SendGrid Sender Email', category: 'Email', description: 'Verified sender address used in outgoing emails.' },
  { name: 'stripe_key', label: 'Stripe Live Key', category: 'Platform', description: 'Used for payments and checkout sessions.' },
  { name: 'stripe_webhook_secret', label: 'Stripe Webhook Secret', category: 'Platform', description: 'Used to verify Stripe webhook events and finalize completed payments.' },
  { name: 'gumroad_key', label: 'Gumroad Access Token', category: 'Platform', description: 'Used to publish to Gumroad and sync sales data.' },
  { name: 'gumroad_secret', label: 'Gumroad Secret', category: 'Platform', description: 'Legacy optional secret for older Gumroad auth flows.' },
  { name: 'mongodb_url', label: 'MongoDB Connection String', category: 'Database', description: 'Used for persistent storage and backend reconnects.' }
];

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
};

const SettingsPage = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);
  const [keyStatus, setKeyStatus] = useState({});
  const [formData, setFormData] = useState({
    templateName: 'openai_key',
    key: ''
  });

  const categories = ['AI', 'Platform', 'Email', 'Social', 'Analytics', 'Database'];

  const loadKeyStatus = async () => {
    setLoading(true);

    try {
      const response = await fetch(`${API}/api/keys/status`);
      if (!response.ok) {
        throw new Error(`Failed to load key status (${response.status})`);
      }

      const data = await response.json();
      setKeyStatus(data.api_keys_status || {});
    } catch (loadError) {
      console.error('Failed to load backend key status:', loadError);
      setSyncStatus({
        type: 'error',
        message: loadError.message
      });
      setKeyStatus({});
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKeyStatus();
  }, []);

  const apiKeys = useMemo(() => {
    return BACKEND_KEY_TEMPLATES.map((template) => {
      const rawStatus = keyStatus[template.name] || 'Missing';
      const configured = String(rawStatus).includes('Configured') || String(rawStatus).includes('Connected');

      return {
        ...template,
        configured,
        statusText: rawStatus
      };
    });
  }, [keyStatus]);

  const handleSaveKey = async (e) => {
    e.preventDefault();
    if (!formData.templateName || !formData.key) {
      setSyncStatus({
        type: 'error',
        message: 'Select a key template and provide the secret value.'
      });
      return;
    }

    setSaving(true);
    setSyncStatus(null);

    try {
      const response = await fetch(`${API}/api/keys/store`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          [formData.templateName]: formData.key
        })
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const result = await response.json();
      setSyncStatus({
        type: 'success',
        message: `Stored ${result.keys_stored} key securely in the backend.`
      });
      setFormData({ templateName: 'openai_key', key: '' });
      setShowAddForm(false);
      await loadKeyStatus();
    } catch (error) {
      setSyncStatus({
        type: 'error',
        message: `Failed to store key: ${error.message}`
      });
      console.error('Key storage error:', error);
    } finally {
      setSaving(false);
    }
  };

  const getCategoryCount = (category) => {
    return apiKeys.filter((key) => key.category === category && key.configured).length;
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Settings & API Keys</h1>
        <p>Manage all API credentials and integrations for the Factory system</p>
      </div>

      <div className="content-section">
        <div className="section-header">
          <h2>API Keys Overview</h2>
          <div className="button-group">
            <button className="btn btn-secondary" onClick={loadKeyStatus} disabled={loading}>
              <RefreshCw size={16} /> {loading ? 'Refreshing...' : 'Refresh Status'}
            </button>
            <button className="btn btn-primary" onClick={() => setShowAddForm(true)}>
              <Plus size={16} /> Configure Key
            </button>
          </div>
        </div>

        <div className="keys-summary">
          <div className="summary-item">
            <span className="summary-label">Supported Keys</span>
            <span className="summary-value">{apiKeys.length}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Configured</span>
            <span className="summary-value text-success">{apiKeys.filter((key) => key.configured).length}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Missing</span>
            <span className="summary-value text-warning">{apiKeys.filter((key) => !key.configured).length}</span>
          </div>
        </div>

        {syncStatus && (
          <div className={`alert ${syncStatus.type === 'success' ? 'alert-success' : 'alert-error'}`}>
            {syncStatus.message}
          </div>
        )}
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h3>Key Categories</h3>
          <div className="category-list">
            {categories.map((cat, idx) => (
              <div key={idx} className="category-item">
                <span>{cat}</span>
                <span className="category-count">{getCategoryCount(cat)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="content-section">
          <h3>Key Management Tips</h3>
          <ul className="tips-list">
            <li><strong>Keep Secure:</strong> Never share API keys or commit to Git</li>
            <li><strong>Rotate Regularly:</strong> Update keys every 90 days</li>
            <li><strong>Use Permissions:</strong> Give each key only necessary permissions</li>
            <li><strong>Monitor Usage:</strong> Check logs for unusual activity</li>
            <li><strong>Environment Variables:</strong> Store keys in .env files</li>
            <li><strong>Backup Keys:</strong> Keep secure backup of critical keys</li>
          </ul>
        </div>
      </div>

      <div className="content-section">
        <h2>Backend Key Status</h2>
        {loading ? (
          <div className="empty-state">
            <p>Loading backend key status...</p>
          </div>
        ) : (
          <div className="keys-table">
            {apiKeys.map((key) => (
              <div key={key.name} className="key-row">
                <div className="key-info">
                  <div className="key-name">
                    <h4>{key.label}</h4>
                    <span className={`badge badge-${key.category.toLowerCase()}`}>{key.category}</span>
                  </div>
                  <p className="text-secondary">{key.description}</p>
                  <div className="key-display">
                    <code>{key.statusText}</code>
                  </div>
                </div>

                <div className="key-actions">
                  <button
                    className="btn btn-secondary btn-small"
                    onClick={() => {
                      setFormData({ templateName: key.name, key: '' });
                      setShowAddForm(true);
                    }}
                  >
                    {key.configured ? 'Update' : 'Configure'}
                  </button>
                  <span className={`status-dot ${key.configured ? 'status-connected' : 'status-pending'}`}></span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal for adding new key */}
      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Configure Backend Key</h2>
              <button
                className="modal-close"
                onClick={() => setShowAddForm(false)}
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSaveKey} className="add-key-form">
              <div className="form-group">
                <label>Backend Key</label>
                <select
                  value={formData.templateName}
                  onChange={(event) => setFormData({ ...formData, templateName: event.target.value })}
                >
                  {BACKEND_KEY_TEMPLATES.map((template) => (
                    <option key={template.name} value={template.name}>
                      {template.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>Category</label>
                  <input
                    type="text"
                    value={BACKEND_KEY_TEMPLATES.find((template) => template.name === formData.templateName)?.category || ''}
                    disabled
                  />
                </div>
              </div>

              <div className="form-group">
                <label>API Key / Token *</label>
                <input
                  type="password"
                  placeholder="Paste the secret value to store securely in the backend"
                  value={formData.key}
                  onChange={(event) => setFormData({ ...formData, key: event.target.value })}
                />
              </div>

              <p className="text-secondary" style={{ margin: 0 }}>
                Keys are written directly to the backend and are no longer displayed or cached in the browser UI.
              </p>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Key'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowAddForm(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="content-section">
        <h2>System Configuration</h2>
        <div className="settings-grid">
          <div className="setting">
            <label>Auto-encrypt keys</label>
            <input type="checkbox" defaultChecked />
          </div>
          <div className="setting">
            <label>2FA Enabled</label>
            <input type="checkbox" defaultChecked />
          </div>
          <div className="setting">
            <label>Key rotation frequency</label>
            <select>
              <option>Every 30 days</option>
              <option>Every 60 days</option>
              <option>Every 90 days</option>
              <option>Manual only</option>
            </select>
          </div>
          <div className="setting">
            <label>Log all key access</label>
            <input type="checkbox" defaultChecked />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
