import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Copy, Check, Trash2, Plus, X } from 'lucide-react';
import './Pages.css';

const SettingsPage = () => {
  const [showKeys, setShowKeys] = useState({});
  const [copied, setCopied] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [apiKeys, setApiKeys] = useState([]);
  const [syncing, setSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    key: '',
    category: 'AI',
    description: ''
  });

  // Backend API key templates
  const backendKeyTemplates = [
    { name: 'openai_key', label: 'OpenAI API Key', category: 'AI' },
    { name: 'anthropic_key', label: 'Anthropic Claude Key', category: 'AI' },
    { name: 'dalle_key', label: 'DALL-E API Key', category: 'AI' },
    { name: 'sendgrid_key', label: 'SendGrid API Key', category: 'Email' },
    { name: 'stripe_key', label: 'Stripe Live Key', category: 'Platform' },
    { name: 'gumroad_key', label: 'Gumroad API Key', category: 'Platform' },
    { name: 'gumroad_secret', label: 'Gumroad Secret', category: 'Platform' },
    { name: 'mongodb_url', label: 'MongoDB Connection String', category: 'Database' }
  ];

  // Function to load keys from localStorage
  const loadKeysFromStorage = () => {
    const savedKeys = localStorage.getItem('apiKeys');
    if (savedKeys) {
      try {
        const parsed = JSON.parse(savedKeys);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setApiKeys(parsed);
        }
      } catch (e) {
        console.error('Failed to load saved keys', e);
      }
    }
  };

  // Load keys from localStorage on mount and when storage changes
  useEffect(() => {
    // Load immediately
    loadKeysFromStorage();

    // Also try loading after a small delay in case localStorage is being populated
    const timer = setTimeout(() => {
      loadKeysFromStorage();
    }, 500);

    // Listen for storage changes
    window.addEventListener('storage', loadKeysFromStorage);
    window.addEventListener('apiKeysUpdated', loadKeysFromStorage);
    
    return () => {
      clearTimeout(timer);
      window.removeEventListener('storage', loadKeysFromStorage);
      window.removeEventListener('apiKeysUpdated', loadKeysFromStorage);
    };
  }, []);

  // Save keys to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('apiKeys', JSON.stringify(apiKeys));
  }, [apiKeys]);

  const categories = ['AI', 'Platform', 'Email', 'Social', 'Analytics', 'Database'];

  const copyToClipboard = (key, id) => {
    navigator.clipboard.writeText(key);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const toggleKeyVisibility = (id) => {
    setShowKeys(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleAddKey = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.key) {
      alert('Please fill in key name and value');
      return;
    }
    
    const newKey = {
      id: Date.now(),
      ...formData,
      status: 'connected',
      createdAt: new Date().toISOString()
    };
    
    setApiKeys([...apiKeys, newKey]);
    setFormData({ name: '', key: '', category: 'AI', description: '' });
    setShowAddForm(false);
  };

  const handleDeleteKey = (id) => {
    if (confirm('Are you sure you want to delete this key?')) {
      setApiKeys(apiKeys.filter(k => k.id !== id));
    }
  };

  const maskKey = (key) => {
    if (!key || key.length < 8) return '***';
    return key.substring(0, 4) + '***...' + key.substring(key.length - 4);
  };

  // Sync keys to backend API
  const syncKeysToBackend = async () => {
    setSyncing(true);
    setSyncStatus(null);
    
    try {
      // Transform localStorage keys to backend format
      const keysToSend = {};
      apiKeys.forEach(apiKey => {
        // Map display names to backend key names
        if (apiKey.name.toLowerCase().includes('openai')) keysToSend.openai_key = apiKey.key;
        if (apiKey.name.toLowerCase().includes('anthropic')) keysToSend.anthropic_key = apiKey.key;
        if (apiKey.name.toLowerCase().includes('dall')) keysToSend.dalle_key = apiKey.key;
        if (apiKey.name.toLowerCase().includes('sendgrid')) keysToSend.sendgrid_key = apiKey.key;
        if (apiKey.name.toLowerCase().includes('stripe')) keysToSend.stripe_key = apiKey.key;
        if (apiKey.category === 'Platform' && apiKey.name.toLowerCase().includes('gumroad')) {
          if (apiKey.name.toLowerCase().includes('secret')) {
            keysToSend.gumroad_secret = apiKey.key;
          } else {
            keysToSend.gumroad_key = apiKey.key;
          }
        }
        if (apiKey.name.toLowerCase().includes('mongodb')) keysToSend.mongodb_url = apiKey.key;
      });

      const response = await fetch('http://localhost:8000/api/keys/store', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(keysToSend)
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const result = await response.json();
      setSyncStatus({
        type: 'success',
        message: `✅ Successfully synced ${result.keys_stored} keys to backend!`
      });
      setTimeout(() => setSyncStatus(null), 5000);
    } catch (error) {
      setSyncStatus({
        type: 'error',
        message: `❌ Failed to sync keys: ${error.message}`
      });
      console.error('Sync error:', error);
    } finally {
      setSyncing(false);
    }
  };

  const getCategoryCount = (category) => {
    return apiKeys.filter(k => k.category === category).length;
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
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddForm(true)}
          >
            + Add New Key
          </button>
        </div>

        <div className="keys-summary">
          <div className="summary-item">
            <span className="summary-label">Total Keys</span>
            <span className="summary-value">{apiKeys.length}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Connected</span>
            <span className="summary-value text-success">{apiKeys.filter(k => k.status === 'connected').length}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Pending</span>
            <span className="summary-value text-warning">{apiKeys.filter(k => k.status === 'pending').length}</span>
          </div>
        </div>

        {syncStatus && (
          <div style={{
            padding: '12px 16px',
            marginBottom: '16px',
            borderRadius: '6px',
            backgroundColor: syncStatus.type === 'success' ? '#d4edda' : '#f8d7da',
            color: syncStatus.type === 'success' ? '#155724' : '#721c24',
            border: `1px solid ${syncStatus.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`
          }}>
            {syncStatus.message}
          </div>
        )}

        <button
          onClick={syncKeysToBackend}
          disabled={syncing || apiKeys.length === 0}
          style={{
            padding: '10px 20px',
            backgroundColor: syncing ? '#cccccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: syncing ? 'not-allowed' : 'pointer',
            marginBottom: '16px',
            fontSize: '14px',
            fontWeight: '600'
          }}
        >
          {syncing ? '🔄 Syncing...' : '📤 Sync Keys to Backend'}
        </button>
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
        <h2>All API Keys</h2>
        {apiKeys.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
            <p>No API keys added yet. Click "+ Add New Key" to get started.</p>
          </div>
        ) : (
          <div className="keys-table">
            {apiKeys.map((key, idx) => (
              <div key={key.id} className="key-row">
                <div className="key-info">
                  <div className="key-name">
                    <h4>{key.name}</h4>
                    <span className={`badge badge-${key.category.toLowerCase()}`}>{key.category}</span>
                  </div>
                  <div className="key-display">
                    <code>
                      {showKeys[key.id] ? key.key : maskKey(key.key)}
                    </code>
                  </div>
                  {key.description && (
                    <div style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
                      {key.description}
                    </div>
                  )}
                </div>

                <div className="key-actions">
                  <button
                    className="key-btn"
                    onClick={() => toggleKeyVisibility(key.id)}
                    title={showKeys[key.id] ? 'Hide' : 'Show'}
                  >
                    {showKeys[key.id] ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                  <button
                    className="key-btn"
                    onClick={() => copyToClipboard(key.key, key.id)}
                    title="Copy to clipboard"
                  >
                    {copied === key.id ? <Check size={18} className="text-success" /> : <Copy size={18} />}
                  </button>
                  <button
                    className="key-btn"
                    onClick={() => handleDeleteKey(key.id)}
                    title="Delete key"
                    style={{ color: '#ff6b6b' }}
                  >
                    <Trash2 size={18} />
                  </button>
                  <span className={`status-dot status-${key.status}`}></span>
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
              <h2>Add New API Key</h2>
              <button
                className="modal-close"
                onClick={() => setShowAddForm(false)}
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleAddKey} className="add-key-form">
              <div className="form-grid">
                <div className="form-group">
                  <label>Key Name *</label>
                  <input
                    type="text"
                    placeholder="e.g., Production OpenAI Key"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>API Key / Token *</label>
                <input
                  type="password"
                  placeholder="Paste your API key here"
                  value={formData.key}
                  onChange={(e) => setFormData({...formData, key: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Description (Optional)</label>
                <textarea
                  placeholder="What is this key used for?"
                  rows="3"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                ></textarea>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary">Save Key</button>
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
