
import React, { useEffect, useMemo, useState } from 'react';
// --- Vault Section ---
const VAULT_KEY_LIST = [
  'openai_key', 'anthropic_key', 'dalle_key', 'gemini_key', 'sendgrid_key', 'sendgrid_from_email',
  'mailchimp_key', 'stripe_key', 'stripe_webhook_secret', 'gumroad_key', 'gumroad_secret',
  'tiktok_api_key', 'tiktok_api_secret', 'instagram_graph_api_key', 'twitter_api_key',
  'linkedin_api_key', 'youtube_api_key', 'elevenlabs_key', 'pexels_key', 'pixabay_key', 'mongodb_url'
];
  // Vault state


  // Fetch all decrypted keys for Vault section
  const loadVaultKeys = async () => {
    setVaultLoading(true);
    setVaultError(null);
    try {
      const response = await fetch(`${API}/api/keys/vault`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        throw new Error(`Failed to load vault keys (${response.status})`);
      }
      const data = await response.json();
      setVaultKeys(data);
    } catch (err) {
      setVaultError(err.message);
      setVaultKeys({});
    } finally {
      setVaultLoading(false);
    }
  };

  // Move useEffect inside SettingsPage component
  // Vault key display helper
  const getVaultKeyLabel = (key) => {
    const template = BACKEND_KEY_TEMPLATES.find((t) => t.name === key);
    return template ? template.label : key;
  };
  // Vault Section UI
  const VaultSection = () => (
    <div className="content-section">
      <h2>Vault: All API Keys</h2>
      <p className="text-secondary" style={{marginBottom: 12}}>These are the decrypted keys your app will read and use. <b>Keep these secure!</b></p>
      {vaultLoading ? (
        <div className="empty-state"><p>Loading vault keys...</p></div>
      ) : vaultError ? (
        <div className="alert alert-error">{vaultError}</div>
      ) : Object.keys(vaultKeys).length === 0 ? (
        <div className="empty-state"><p>No keys found in vault.</p></div>
      ) : (
        <div className="keys-table">
          {VAULT_KEY_LIST.map((key) => (
            vaultKeys[key] ? (
              <div key={key} className="key-row">
                <div className="key-info">
                  <div className="key-name">
                    <h4>{getVaultKeyLabel(key)}</h4>
                    <span className={`badge badge-${(BACKEND_KEY_TEMPLATES.find(t=>t.name===key)?.category||'Other').toLowerCase()}`}>{BACKEND_KEY_TEMPLATES.find(t=>t.name===key)?.category||'Other'}</span>
                  </div>
                  <div className="key-display">
                    <input
                      type={showKey[key] ? 'text' : 'password'}
                      value={vaultKeys[key]}
                      readOnly
                      style={{width: '100%', fontFamily: 'monospace', background: '#181818', color: '#fff', border: '1px solid #333', borderRadius: 4, padding: 4, fontSize: 14}}
                    />
                  </div>
                </div>
                <div className="key-actions">
                  <button
                    className="btn btn-secondary btn-small"
                    onClick={() => setShowKey((prev) => ({ ...prev, [key]: !prev[key] }))}
                  >
                    {showKey[key] ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>
            ) : null
          ))}
        </div>
      )}
    </div>
  );
import { AlertCircle, Check, ExternalLink, Plus, RefreshCw, Save, X } from 'lucide-react';
import './Pages.css';
import API_URL from '../config/api';

const API = API_URL;

const BACKEND_KEY_TEMPLATES = [
  { name: 'openai_key', label: 'OpenAI API Key', category: 'AI', required: true, description: 'Used for product ideation, copy, and AI generation.' },
  { name: 'anthropic_key', label: 'Anthropic Claude Key', category: 'AI', required: false, description: 'Used for long-form analysis and strategy tasks.' },
  { name: 'dalle_key', label: 'DALL-E API Key', category: 'AI', required: false, description: 'Used for image generation and visual assets. Falls back to OpenAI key if not set.' },
  { name: 'gemini_key', label: 'Gemini API Key', category: 'AI', required: false, description: 'Used for Gemini AI generation tasks.' },
  { name: 'sendgrid_key', label: 'SendGrid API Key', category: 'Email', required: false, description: 'Used for transactional email and sequences.' },
  { name: 'sendgrid_from_email', label: 'SendGrid Sender Email', category: 'Email', required: false, description: 'Verified sender address used in outgoing emails.' },
  { name: 'mailchimp_key', label: 'Mailchimp API Key', category: 'Email', required: false, description: 'Used for email list management and campaigns.' },
  { name: 'stripe_key', label: 'Stripe Secret Key', category: 'Commerce', required: false, description: 'Used for Stripe payments and checkout sessions.' },
  { name: 'stripe_webhook_secret', label: 'Stripe Webhook Secret', category: 'Commerce', required: false, description: 'Used to verify Stripe webhook events and finalize completed payments.' },
  { name: 'gumroad_key', label: 'Gumroad Access Token', category: 'Commerce', required: true, description: 'Used to publish to Gumroad and sync sales data.' },
  { name: 'gumroad_secret', label: 'Gumroad Secret', category: 'Commerce', required: false, description: 'Optional secret for Gumroad OAuth auth flows.' },
  { name: 'tiktok_api_key', label: 'TikTok Client Key', category: 'Social', required: false, description: 'Used for TikTok content posting API.' },
  { name: 'tiktok_api_secret', label: 'TikTok Client Secret', category: 'Social', required: false, description: 'Used for TikTok OAuth authentication.' },
  { name: 'instagram_graph_api_key', label: 'Instagram / Meta Access Token', category: 'Social', required: false, description: 'Used to post to Instagram via the Meta Graph API.' },
  { name: 'twitter_api_key', label: 'Twitter / X API Key', category: 'Social', required: false, description: 'Used for Twitter/X posting and analytics.' },
  { name: 'linkedin_api_key', label: 'LinkedIn Client ID', category: 'Social', required: false, description: 'Used for LinkedIn content publishing.' },
  { name: 'youtube_api_key', label: 'YouTube API Key', category: 'Social', required: false, description: 'Used for YouTube Shorts upload and channel analytics.' },
  { name: 'elevenlabs_key', label: 'ElevenLabs API Key', category: 'Video', required: false, description: 'Used for AI voiceover generation in faceless videos.' },
  { name: 'pexels_key', label: 'Pexels API Key', category: 'Video', required: false, description: 'Used for background footage in generated videos.' },
  { name: 'pixabay_key', label: 'Pixabay API Key', category: 'Video', required: false, description: 'Used as fallback footage source for video generation.' },
  { name: 'mongodb_url', label: 'MongoDB Connection String', category: 'Database', required: true, description: 'Used for persistent storage and backend reconnects.' }
];

const SOCIAL_LINKS_STORAGE_KEY = 'fiilthy_social_accounts';

const SOCIAL_ACCOUNT_CONFIG = [
  {
    id: 'instagram',
    label: 'Instagram',
    description: 'Use this to keep your main Instagram profile handy and jump straight into account editing.',
    placeholder: 'https://www.instagram.com/yourbrand/',
    manageUrl: 'https://www.instagram.com/accounts/edit/',
    composerUrl: 'https://www.instagram.com/create/style/'
  },
  {
    id: 'tiktok',
    label: 'TikTok',
    description: 'Save your TikTok profile so product posting and profile updates are one click away.',
    placeholder: 'https://www.tiktok.com/@yourbrand',
    manageUrl: 'https://www.tiktok.com/upload',
    composerUrl: 'https://www.tiktok.com/upload'
  },
  {
    id: 'twitter',
    label: 'X / Twitter',
    description: 'Keep your X profile URL here for faster launches into profile edits and posting.',
    placeholder: 'https://twitter.com/yourbrand',
    manageUrl: 'https://twitter.com/settings/profile',
    composerUrl: 'https://twitter.com/compose/post'
  },
  {
    id: 'linkedin',
    label: 'LinkedIn',
    description: 'Store your LinkedIn profile or company page for direct access while publishing products.',
    placeholder: 'https://www.linkedin.com/in/yourbrand/',
    manageUrl: 'https://www.linkedin.com/feed/',
    composerUrl: 'https://www.linkedin.com/feed/'
  },
  {
    id: 'youtube',
    label: 'YouTube',
    description: 'Point this at your channel so Shorts, videos, and profile management stay in one workflow.',
    placeholder: 'https://www.youtube.com/@yourbrand',
    manageUrl: 'https://studio.youtube.com/',
    composerUrl: 'https://studio.youtube.com/'
  }
];

const normalizeUrl = (value) => {
  const trimmedValue = String(value || '').trim();
  if (!trimmedValue) {
    return '';
  }

  if (/^https?:\/\//i.test(trimmedValue)) {
    return trimmedValue;
  }

  return `https://${trimmedValue}`;
};

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
};

const SettingsPage = () => {
      useEffect(() => {
        loadVaultKeys();
      }, []);
    const [vaultKeys, setVaultKeys] = useState({});
    const [vaultLoading, setVaultLoading] = useState(false);
    const [vaultError, setVaultError] = useState(null);
    const [showKey, setShowKey] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);
  const [keyStatus, setKeyStatus] = useState({});
  const [socialLinks, setSocialLinks] = useState({});
  const [socialStatus, setSocialStatus] = useState(null);
  const [formData, setFormData] = useState({
    templateName: 'openai_key',
    key: ''
  });

  const categories = ['AI', 'Commerce', 'Email', 'Social', 'Video', 'Analytics', 'Database'];

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

  useEffect(() => {
    try {
      const savedLinks = JSON.parse(localStorage.getItem(SOCIAL_LINKS_STORAGE_KEY) || '{}');
      setSocialLinks(savedLinks);
    } catch (error) {
      console.error('Failed to read saved social links:', error);
      setSocialLinks({});
    }
  }, []);

  const apiKeys = useMemo(() => {
    return BACKEND_KEY_TEMPLATES.map((template) => {
      const rawStatus = keyStatus[template.name] || '[FAIL] Not configured';
      const configured = String(rawStatus).includes('Configured') || String(rawStatus).includes('Connected');

      return {
        ...template,
        configured,
        statusText: rawStatus
      };
    });
  }, [keyStatus]);

  const socialAccounts = useMemo(() => {
    return SOCIAL_ACCOUNT_CONFIG.map((account) => {
      const currentValue = socialLinks[account.id] || '';
      const normalizedValue = normalizeUrl(currentValue);

      return {
        ...account,
        value: currentValue,
        normalizedValue,
        connected: Boolean(normalizedValue)
      };
    });
  }, [socialLinks]);

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
    if (category === 'Social') {
      return socialAccounts.filter((account) => account.connected).length;
    }

    return apiKeys.filter((key) => key.category === category && key.configured).length;
  };

  const handleSaveSocialLinks = () => {
    const normalizedLinks = SOCIAL_ACCOUNT_CONFIG.reduce((accumulator, account) => {
      const normalizedValue = normalizeUrl(socialLinks[account.id]);

      if (normalizedValue) {
        accumulator[account.id] = normalizedValue;
      }

      return accumulator;
    }, {});

    localStorage.setItem(SOCIAL_LINKS_STORAGE_KEY, JSON.stringify(normalizedLinks));
    setSocialLinks(normalizedLinks);
    setSocialStatus({
      type: 'success',
      message: `Saved ${Object.keys(normalizedLinks).length} social account link${Object.keys(normalizedLinks).length === 1 ? '' : 's'} for quick access.`
    });
  };

  const updateSocialLink = (platformId, value) => {
    setSocialLinks((previousLinks) => ({
      ...previousLinks,
      [platformId]: value
    }));
    setSocialStatus(null);
  };

  return (
    <div className="page">
        {/* Vault Section - All decrypted keys */}
        <VaultSection />
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
            <span className="summary-label">Required Keys</span>
            <span className="summary-value text-success">
              {apiKeys.filter((key) => key.required && key.configured).length}
              <span style={{ color: 'var(--text-secondary)', fontWeight: 400 }}>
                /{apiKeys.filter((key) => key.required).length}
              </span>
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Optional Keys</span>
            <span className="summary-value" style={{ color: 'var(--text-secondary)' }}>
              {apiKeys.filter((key) => !key.required && key.configured).length}
              <span style={{ fontWeight: 400 }}>
                /{apiKeys.filter((key) => !key.required).length}
              </span>
            </span>
          </div>
          {apiKeys.filter((key) => key.required && !key.configured).length > 0 && (
            <div className="summary-item">
              <span className="summary-label">Required Missing</span>
              <span className="summary-value text-warning">
                {apiKeys.filter((key) => key.required && !key.configured).length}
              </span>
            </div>
          )}
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
                    {!key.required && (
                      <span className="badge" style={{ background: 'rgba(255,255,255,0.07)', color: 'var(--text-secondary)', fontSize: '10px' }}>Optional</span>
                    )}
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

      <div className="content-section">
        <div className="section-header">
          <div>
            <h2>Social Accounts & Quick Links</h2>
            <p className="text-secondary" style={{ margin: '6px 0 0' }}>
              Save the profile URLs you actually use so posting and account edits are always one click away.
            </p>
          </div>
          <button className="btn btn-primary" onClick={handleSaveSocialLinks}>
            <Save size={16} /> Save Social Links
          </button>
        </div>

        {socialStatus && (
          <div className={`alert ${socialStatus.type === 'success' ? 'alert-success' : 'alert-error'}`}>
            {socialStatus.message}
          </div>
        )}

        <div className="keys-table">
          {socialAccounts.map((account) => (
            <div key={account.id} className="key-row">
              <div className="key-info">
                <div className="key-name">
                  <h4>{account.label}</h4>
                  <span className="badge badge-social">Social</span>
                </div>
                <p className="text-secondary">{account.description}</p>
                <div className="form-group" style={{ marginBottom: 0, marginTop: 12 }}>
                  <label>{account.label} Profile URL</label>
                  <input
                    type="url"
                    placeholder={account.placeholder}
                    value={account.value}
                    onChange={(event) => updateSocialLink(account.id, event.target.value)}
                  />
                </div>
                {account.connected && (
                  <div className="key-display" style={{ marginTop: 10 }}>
                    <code>{account.normalizedValue}</code>
                  </div>
                )}
              </div>

              <div className="key-actions" style={{ alignItems: 'flex-end', display: 'flex', flexDirection: 'column', gap: 8 }}>
                <button
                  className="btn btn-secondary btn-small"
                  type="button"
                  onClick={() => window.open(account.manageUrl, '_blank', 'noopener,noreferrer')}
                >
                  <ExternalLink size={14} /> Manage
                </button>
                <button
                  className="btn btn-secondary btn-small"
                  type="button"
                  onClick={() => window.open(account.composerUrl, '_blank', 'noopener,noreferrer')}
                >
                  <ExternalLink size={14} /> Create Post
                </button>
                {account.connected && (
                  <button
                    className="btn btn-secondary btn-small"
                    type="button"
                    onClick={() => window.open(account.normalizedValue, '_blank', 'noopener,noreferrer')}
                  >
                    <ExternalLink size={14} /> Open Saved Link
                  </button>
                )}
                <span className={`status-dot ${account.connected ? 'status-connected' : 'status-pending'}`}></span>
              </div>
            </div>
          ))}
        </div>

        <p className="text-secondary" style={{ marginBottom: 0 }}>
          Social links are stored in this browser so the app can launch the right profile and posting screens while you work.
        </p>
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
