import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Key, Shield, CheckCircle, XCircle, AlertCircle, 
  Plus, Trash2, RefreshCw, Eye, EyeOff, Save,
  Lock, Unlock, Search, Filter
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const CATEGORIES = {
  marketplace: { name: "Marketplaces", icon: "🛒", color: "from-green-500 to-emerald-500" },
  social: { name: "Social Media", icon: "📱", color: "from-blue-500 to-cyan-500" },
  video: { name: "Video & Streaming", icon: "🎬", color: "from-red-500 to-pink-500" },
  audio: { name: "Podcasting & Audio", icon: "🎧", color: "from-purple-500 to-violet-500" },
  email: { name: "Email & Newsletter", icon: "📧", color: "from-yellow-500 to-orange-500" },
  community: { name: "Community", icon: "💬", color: "from-indigo-500 to-blue-500" },
  ai: { name: "AI & Automation", icon: "🤖", color: "from-pink-500 to-rose-500" },
  automation: { name: "Automation", icon: "⚡", color: "from-amber-500 to-yellow-500" },
  advertising: { name: "Advertising", icon: "📣", color: "from-red-500 to-orange-500" },
  affiliate: { name: "Affiliate Networks", icon: "🤝", color: "from-green-500 to-teal-500" },
  analytics: { name: "Analytics", icon: "📊", color: "from-blue-500 to-indigo-500" },
  payments: { name: "Payments", icon: "💳", color: "from-emerald-500 to-green-500" },
  crm: { name: "CRM & Sales", icon: "🎯", color: "from-orange-500 to-red-500" },
  backend: { name: "Backend & Database", icon: "🗄️", color: "from-gray-500 to-slate-500" },
  messaging: { name: "SMS & Phone", icon: "📞", color: "from-cyan-500 to-blue-500" },
  events: { name: "Events & Webinars", icon: "🎟️", color: "from-purple-500 to-pink-500" },
  website: { name: "Website Builders", icon: "🌐", color: "from-teal-500 to-cyan-500" },
  productivity: { name: "Productivity", icon: "📝", color: "from-violet-500 to-purple-500" },
  seo: { name: "SEO Tools", icon: "🔍", color: "from-lime-500 to-green-500" },
  stores: { name: "App Stores", icon: "🏪", color: "from-blue-500 to-violet-500" }
};

const KeyVault = ({ onClose }) => {
  const [credentials, setCredentials] = useState({ stored: [], available: [] });
  const [selectedType, setSelectedType] = useState(null);
  const [formData, setFormData] = useState({});
  const [showPasswords, setShowPasswords] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [testing, setTesting] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    fetchCredentials();
  }, []);

  const fetchCredentials = async () => {
    try {
      const response = await axios.get(`${API}/vault/credentials`);
      setCredentials(response.data);
    } catch (error) {
      console.error('Error fetching credentials:', error);
    }
  };

  const handleSelectType = async (type) => {
    setSelectedType(type);
    try {
      const response = await axios.get(`${API}/vault/credentials/${type}`);
      const fields = response.data.fields || [];
      const initialData = {};
      fields.forEach(field => initialData[field] = '');
      setFormData(initialData);
    } catch (error) {
      console.error('Error getting schema:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await axios.post(`${API}/vault/credentials`, {
        credential_type: selectedType,
        credentials: formData
      });
      
      if (response.data.success) {
        setMessage({ type: 'success', text: `${response.data.name} credentials saved securely!` });
        fetchCredentials();
        setSelectedType(null);
        setFormData({});
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to save credentials' });
    }
    setLoading(false);
  };

  const handleTest = async (type) => {
    setTesting(type);
    try {
      const response = await axios.post(`${API}/vault/credentials/${type}/test`);
      setMessage({
        type: response.data.success ? 'success' : 'error',
        text: response.data.message
      });
      fetchCredentials();
    } catch (error) {
      setMessage({ type: 'error', text: 'Test failed' });
    }
    setTesting(null);
  };

  const handleDelete = async (type) => {
    if (!window.confirm('Are you sure you want to delete these credentials?')) return;
    
    try {
      await axios.delete(`${API}/vault/credentials/${type}`);
      setMessage({ type: 'success', text: 'Credentials deleted' });
      fetchCredentials();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete' });
    }
  };

  const togglePassword = (field) => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field] }));
  };

  // Filter available credentials
  const filteredAvailable = credentials.available?.filter(cred => {
    const matchesSearch = cred.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cred.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || cred.category === selectedCategory;
    return matchesSearch && matchesCategory;
  }) || [];

  // Group by category
  const groupedByCategory = filteredAvailable.reduce((acc, cred) => {
    const cat = cred.category || 'other';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(cred);
    return acc;
  }, {});

  const totalPlatforms = credentials.available?.length || 0;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden border border-white/20">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield size={32} className="text-white" />
              <div>
                <h2 className="text-2xl font-bold text-white">Secure Key Vault</h2>
                <p className="text-white/70 text-sm">{totalPlatforms}+ platforms • Encrypted storage for maximum reach</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white/70 hover:text-white text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Message */}
          {message && (
            <div className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${
              message.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}>
              {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
              {message.text}
            </div>
          )}

          {/* Stored Credentials */}
          {credentials.stored?.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Lock size={20} className="text-green-400" />
                Connected Services ({credentials.stored?.length || 0})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {credentials.stored?.map(cred => (
                  <div
                    key={cred.type}
                    className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{cred.icon}</span>
                      <div>
                        <p className="font-semibold">{cred.name}</p>
                        <p className={`text-xs ${
                          cred.status === 'verified' ? 'text-green-400' : 
                          cred.status === 'invalid' ? 'text-red-400' : 'text-yellow-400'
                        }`}>
                          {cred.status === 'verified' ? '✓ Connected' : 
                           cred.status === 'invalid' ? '✗ Invalid' : '? Not tested'}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleTest(cred.type)}
                        disabled={testing === cred.type}
                        className="p-2 bg-blue-500/20 hover:bg-blue-500/40 rounded-lg transition-all"
                        title="Test connection"
                      >
                        <RefreshCw size={16} className={testing === cred.type ? 'animate-spin' : ''} />
                      </button>
                      <button
                        onClick={() => handleDelete(cred.type)}
                        className="p-2 bg-red-500/20 hover:bg-red-500/40 rounded-lg transition-all"
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Add New Credentials */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Unlock size={20} className="text-blue-400" />
              Add Platform ({totalPlatforms} available)
            </h3>
            
            {!selectedType ? (
              <>
                {/* Search & Filter */}
                <div className="flex gap-4 mb-6">
                  <div className="flex-1 relative">
                    <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search platforms..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full bg-black/30 border border-white/20 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500"
                    />
                  </div>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="bg-black/30 border border-white/20 rounded-lg px-4 py-2 text-white"
                  >
                    <option value="all">All Categories</option>
                    {Object.entries(CATEGORIES).map(([key, cat]) => (
                      <option key={key} value={key}>{cat.icon} {cat.name}</option>
                    ))}
                  </select>
                </div>

                {/* Category Groups */}
                <div className="space-y-6">
                  {Object.entries(groupedByCategory).map(([category, creds]) => (
                    <div key={category}>
                      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r ${CATEGORIES[category]?.color || 'from-gray-500 to-gray-600'} text-white text-sm font-semibold mb-3`}>
                        {CATEGORIES[category]?.icon} {CATEGORIES[category]?.name || category}
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
                        {creds.map(cred => (
                          <button
                            key={cred.type}
                            onClick={() => handleSelectType(cred.type)}
                            className="bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/30 rounded-xl p-3 text-left transition-all group"
                          >
                            <span className="text-2xl block mb-1">{cred.icon}</span>
                            <p className="font-semibold text-sm group-hover:text-white">{cred.name}</p>
                            <p className="text-xs text-gray-500 truncate">{cred.description}</p>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="bg-white/5 border border-white/10 rounded-xl p-6 max-w-2xl mx-auto">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold">
                    Configure {credentials.available?.find(c => c.type === selectedType)?.name}
                  </h4>
                  <button
                    onClick={() => { setSelectedType(null); setFormData({}); }}
                    className="text-gray-400 hover:text-white"
                  >
                    ← Back
                  </button>
                </div>
                
                <div className="space-y-4">
                  {Object.keys(formData).map(field => (
                    <div key={field}>
                      <label className="block text-sm text-gray-400 mb-1 capitalize">
                        {field.replace(/_/g, ' ')}
                      </label>
                      <div className="relative">
                        <input
                          type={showPasswords[field] ? 'text' : 'password'}
                          value={formData[field]}
                          onChange={(e) => setFormData(prev => ({ ...prev, [field]: e.target.value }))}
                          className="w-full bg-black/30 border border-white/20 rounded-lg px-4 py-2 pr-10 text-white"
                          placeholder={`Enter ${field.replace(/_/g, ' ')}`}
                        />
                        <button
                          type="button"
                          onClick={() => togglePassword(field)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                        >
                          {showPasswords[field] ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                    </div>
                  ))}
                  
                  <button
                    onClick={handleSave}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 disabled:from-gray-600 disabled:to-gray-700 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all"
                  >
                    {loading ? (
                      <RefreshCw size={20} className="animate-spin" />
                    ) : (
                      <>
                        <Save size={20} />
                        Save Securely
                      </>
                    )}
                  </button>
                </div>
                
                <p className="text-xs text-gray-500 mt-4 flex items-center gap-1">
                  <Lock size={12} />
                  All credentials are encrypted with AES-256 before storage
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default KeyVault;
