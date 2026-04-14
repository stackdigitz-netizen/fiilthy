import React, { useState, useEffect } from 'react';
import { Palette, Save, RotateCcw, ChevronUp, ChevronDown } from 'lucide-react';
import '../pages/Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
};

const BrandingEditor = ({ productId, initialBranding, onClose }) => {
  const [branding, setBranding] = useState(initialBranding || {
    primary_color: '#0ea5e9',
    secondary_color: '#10b981',
    accent_color: '#f59e0b',
    logo_url: '',
    font_primary: 'Segoe UI, sans-serif',
    font_secondary: 'Inter, sans-serif',
    tagline: '',
    brand_voice: 'professional',
    tone: 'friendly'
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [expandedSection, setExpandedSection] = useState('colors');

  const saveBranding = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API}/api/products/${productId}/branding`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(branding)
      });

      if (response.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      }
    } catch (error) {
      console.error('Failed to save branding:', error);
    } finally {
      setSaving(false);
    }
  };

  const resetBranding = () => {
    setBranding(initialBranding || {});
  };

  const Section = ({ title, id, children }) => (
    <div className="branding-section">
      <button
        className="branding-section-header"
        onClick={() => setExpandedSection(expandedSection === id ? null : id)}
      >
        <span>{title}</span>
        {expandedSection === id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      {expandedSection === id && (
        <div className="branding-section-content">
          {children}
        </div>
      )}
    </div>
  );

  return (
    <div className="branding-editor">
      <div className="branding-editor-header">
        <h2>🎨 Brand Control Center</h2>
        <p>Customize the look, feel, and voice of your product</p>
      </div>

      <div className="branding-editor-body">
        {/* Color Branding */}
        <Section title="🎨 Colors" id="colors">
          <div className="color-controls">
            <div className="color-input-group">
              <label>Primary Color</label>
              <div className="color-picker-row">
                <input
                  type="color"
                  value={branding.primary_color || '#0ea5e9'}
                  onChange={(e) => setBranding({ ...branding, primary_color: e.target.value })}
                  className="color-picker"
                />
                <input
                  type="text"
                  value={branding.primary_color || '#0ea5e9'}
                  onChange={(e) => setBranding({ ...branding, primary_color: e.target.value })}
                  className="color-text"
                />
              </div>
            </div>

            <div className="color-input-group">
              <label>Secondary Color</label>
              <div className="color-picker-row">
                <input
                  type="color"
                  value={branding.secondary_color || '#10b981'}
                  onChange={(e) => setBranding({ ...branding, secondary_color: e.target.value })}
                  className="color-picker"
                />
                <input
                  type="text"
                  value={branding.secondary_color || '#10b981'}
                  onChange={(e) => setBranding({ ...branding, secondary_color: e.target.value })}
                  className="color-text"
                />
              </div>
            </div>

            <div className="color-input-group">
              <label>Accent Color</label>
              <div className="color-picker-row">
                <input
                  type="color"
                  value={branding.accent_color || '#f59e0b'}
                  onChange={(e) => setBranding({ ...branding, accent_color: e.target.value })}
                  className="color-picker"
                />
                <input
                  type="text"
                  value={branding.accent_color || '#f59e0b'}
                  onChange={(e) => setBranding({ ...branding, accent_color: e.target.value })}
                  className="color-text"
                />
              </div>
            </div>
          </div>

          {/* Live Preview */}
          <div className="color-preview">
            <div
              className="preview-swatch"
              style={{ backgroundColor: branding.primary_color }}
              title="Primary"
            />
            <div
              className="preview-swatch"
              style={{ backgroundColor: branding.secondary_color }}
              title="Secondary"
            />
            <div
              className="preview-swatch"
              style={{ backgroundColor: branding.accent_color }}
              title="Accent"
            />
          </div>
        </Section>

        {/* Typography */}
        <Section title="✍️ Typography" id="typography">
          <div className="branding-form-group">
            <label>Primary Font</label>
            <input
              type="text"
              value={branding.font_primary || ''}
              onChange={(e) => setBranding({ ...branding, font_primary: e.target.value })}
              placeholder="e.g., Segoe UI, sans-serif"
              className="branding-input"
            />
          </div>

          <div className="branding-form-group">
            <label>Secondary Font</label>
            <input
              type="text"
              value={branding.font_secondary || ''}
              onChange={(e) => setBranding({ ...branding, font_secondary: e.target.value })}
              placeholder="e.g., Inter, sans-serif"
              className="branding-input"
            />
          </div>
        </Section>

        {/* Voice & Tone */}
        <Section title="💬 Voice & Tone" id="voice">
          <div className="branding-form-group">
            <label>Brand Voice</label>
            <select
              value={branding.brand_voice || 'professional'}
              onChange={(e) => setBranding({ ...branding, brand_voice: e.target.value })}
              className="branding-input"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="playful">Playful</option>
              <option value="inspirational">Inspirational</option>
              <option value="educational">Educational</option>
            </select>
          </div>

          <div className="branding-form-group">
            <label>Tone</label>
            <select
              value={branding.tone || 'friendly'}
              onChange={(e) => setBranding({ ...branding, tone: e.target.value })}
              className="branding-input"
            >
              <option value="friendly">Friendly</option>
              <option value="formal">Formal</option>
              <option value="humorous">Humorous</option>
              <option value="serious">Serious</option>
              <option value="motivational">Motivational</option>
            </select>
          </div>

          <div className="branding-form-group">
            <label>Tagline / Slogan</label>
            <input
              type="text"
              value={branding.tagline || ''}
              onChange={(e) => setBranding({ ...branding, tagline: e.target.value })}
              placeholder="Your product's memorable tagline"
              className="branding-input"
            />
          </div>
        </Section>

        {/* Assets */}
        <Section title="🖼️ Assets" id="assets">
          <div className="branding-form-group">
            <label>Logo URL</label>
            <input
              type="url"
              value={branding.logo_url || ''}
              onChange={(e) => setBranding({ ...branding, logo_url: e.target.value })}
              placeholder="https://example.com/logo.png"
              className="branding-input"
            />
          </div>

          {branding.logo_url && (
            <div className="logo-preview">
              <img
                src={branding.logo_url}
                alt="Brand Logo"
                className="logo-image"
                onError={() => {}}
              />
            </div>
          )}
        </Section>
      </div>

      {/* Actions */}
      <div className="branding-editor-footer">
        {saved && (
          <div className="save-message">✓ Branding saved successfully</div>
        )}
        <div className="branding-actions">
          <button className="btn btn-secondary" onClick={resetBranding}>
            <RotateCcw size={16} /> Reset
          </button>
          <button
            className="btn btn-primary"
            onClick={saveBranding}
            disabled={saving}
          >
            <Save size={16} /> {saving ? 'Saving...' : 'Save Branding'}
          </button>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default BrandingEditor;
