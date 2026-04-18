import React, { useState, useEffect } from 'react';
import { Package, Rocket, Palette, Play, Video, Target, AlertCircle, CheckCircle, Clock, Download, ExternalLink } from 'lucide-react';
import BrandingEditor from '../components/BrandingEditor';
import './Pages.css';
import API_URL from '../config/api';

const API = API_URL;

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
};

// Platform data with logos and status
const PLATFORMS = {
  tiktok: { name: 'TikTok', color: '#000', icon: '🎵', canPublish: true },
  instagram: { name: 'Instagram', color: '#E4405F', icon: '📸', canPublish: true },
  youtube: { name: 'YouTube', color: '#FF0000', icon: '▶️', canPublish: true },
  gumroad: { name: 'Gumroad', color: '#FF90E8', icon: '🛍️', canPublish: true },
  etsy: { name: 'Etsy', color: '#F1641E', icon: '🧵', canPublish: true },
  stripe: { name: 'Stripe Store', color: '#635BFF', icon: '💳', canPublish: true }
};

const ProductLaunchPage = () => {
  const [products, setProducts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [launchState, setLaunchState] = useState({});
  const [videoProgress, setVideoProgress] = useState({});
  const [showBrandingEditor, setShowBrandingEditor] = useState(false);

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Poll video progress every 5 seconds
  useEffect(() => {
    const interval = setInterval(checkVideoProgress, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  const loadProducts = async () => {
    try {
      const response = await fetch(`${API}/api/products?limit=100`, { headers: getAuthHeaders() });
      if (response.ok) {
        const data = await response.json();
        setProducts(data);
        if (data.length > 0 && !selected) setSelected(data[0].id);
      }
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkVideoProgress = async () => {
    if (!selected) return;
    try {
      const response = await fetch(`${API}/api/products/${selected}/video-status`, {
        headers: getAuthHeaders()
      });
      if (response.ok) {
        const data = await response.json();
        setVideoProgress(prev => ({
          ...prev,
          [selected]: data
        }));
      }
    } catch (error) {
      console.error('Failed to check video progress:', error);
    }
  };

  const generateVideos = async () => {
    if (!selected) return;
    
    setLaunchState(prev => ({
      ...prev,
      [selected]: { generating: true, step: 'Creating TikTok videos...' }
    }));

    try {
      const response = await fetch(`${API}/api/products/${selected}/generate-videos`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          tiktok_count: 10,
          instagram_count: 10
        })
      });

      if (response.ok) {
        const data = await response.json();
        setLaunchState(prev => ({
          ...prev,
          [selected]: { generating: true, step: 'Videos queued for generation', videoJobId: data.job_id }
        }));
        
        // Start polling
        let attempts = 0;
        const pollInterval = setInterval(async () => {
          attempts++;
          if (attempts > 120) { // 10 minutes max
            clearInterval(pollInterval);
            setLaunchState(prev => ({
              ...prev,
              [selected]: { error: 'Video generation timed out' }
            }));
            return;
          }

          const statusResponse = await fetch(`${API}/api/products/${selected}/video-status`, {
            headers: getAuthHeaders()
          });
          if (statusResponse.ok) {
            const status = await statusResponse.json();
            if (status.complete) {
              clearInterval(pollInterval);
              setLaunchState(prev => ({
                ...prev,
                [selected]: { videosReady: true, videoCount: status.totalVideos }
              }));
              await checkVideoProgress();
            }
          }
        }, 5000);
      }
    } catch (error) {
      setLaunchState(prev => ({
        ...prev,
        [selected]: { error: error.message }
      }));
    }
  };

  const launchCampaign = async (platforms) => {
    if (!selected) return;

    setLaunchState(prev => ({
      ...prev,
      [selected]: { campaigning: true, step: 'Setting up advertising...' }
    }));

    try {
      const response = await fetch(`${API}/api/products/${selected}/launch-campaign`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          platforms,
          autoSchedule: true,
          budget: null // Will use default
        })
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok || !data.success) {
        throw new Error(data.detail || data.message || 'Failed to launch campaign');
      }

      setLaunchState(prev => ({
        ...prev,
        [selected]: {
          campaignLive: true,
          campaignId: data.campaign_id,
          publishedOn: data.platforms || platforms,
          notice: data.unsupported_platforms?.length
            ? `Skipped unsupported platforms: ${data.unsupported_platforms.join(', ')}`
            : data.message,
          noticeType: data.unsupported_platforms?.length ? 'warning' : 'success'
        }
      }));
      await loadProducts();
    } catch (error) {
      setLaunchState(prev => ({
        ...prev,
        [selected]: { error: error.message }
      }));
    }
  };

  const publishToStore = async (platform) => {
    if (!selected) return;

    try {
      const response = await fetch(`${API}/api/products/${selected}/publish`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ platform })
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || data.message || `Failed to publish to ${platform}`);
      }

      setLaunchState(prev => ({
        ...prev,
        [selected]: {
          ...(prev[selected] || {}),
          notice: data.message,
          noticeType: data.live ? 'success' : 'warning'
        }
      }));

      if (data.live) {
        setProducts(prev => prev.map(p => 
          p.id === selected 
            ? {
                ...p,
                published_on: [
                  ...(p.published_on || []).filter(entry => entry.platform !== platform),
                  { platform, url: data.url }
                ]
              }
            : p
        ));
      }
    } catch (error) {
      setLaunchState(prev => ({
        ...prev,
        [selected]: { ...(prev[selected] || {}), error: error.message }
      }));
    }
  };

  const currentProduct = products.find(p => p.id === selected);
  const state = launchState[selected] || {};
  const progress = videoProgress[selected] || {};

  return (
    <div className="page">
      <div className="page-header">
        <h1>🚀 Product Launch Control</h1>
        <p>Generate videos, launch campaigns, and publish to stores</p>
      </div>

      {/* Product selector */}
      <div className="content-section">
        <h3>Select Product</h3>
        {loading ? (
          <p>Loading products...</p>
        ) : (
          <div className="button-group">
            {products.map(p => (
              <button
                key={p.id}
                className={`btn ${selected === p.id ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setSelected(p.id)}
              >
                {p.title}
              </button>
            ))}
          </div>
        )}
      </div>

      {currentProduct && (
        <>
          {/* Main Launch Control Panel */}
          <div className="grid-3">
            {/* Video Generation */}
            <div className="launch-card">
              <div className="launch-card-header">
                <Video size={24} />
                <h3>Video Generation</h3>
              </div>
              
              {state.generating ? (
                <div className="status-box">
                  <Clock size={20} className="spinner" />
                  <p>{state.step || 'Generating videos...'}</p>
                  {progress.generated && (
                    <p className="text-small">{progress.generated} / {progress.total || 20} complete</p>
                  )}
                </div>
              ) : state.videosReady ? (
                <div className="status-box success">
                  <CheckCircle size={20} />
                  <p>✓ {state.videoCount || 20} videos ready</p>
                  <button className="btn btn-small btn-secondary" onClick={() => setSelected(selected)}>
                    View Videos
                  </button>
                </div>
              ) : (
                <div className="status-box">
                  <p>Create 10 TikTok + 10 Instagram videos</p>
                  <button className="btn btn-primary" onClick={generateVideos}>
                    <Video size={16} /> Generate Videos
                  </button>
                </div>
              )}
            </div>

            {/* Branding Control */}
            <div className="launch-card">
              <div className="launch-card-header">
                <Palette size={24} />
                <h3>Branding</h3>
              </div>
              <div className="status-box">
                <p>Logo, colors, fonts & messaging</p>
                <button className="btn btn-secondary" onClick={() => setShowBrandingEditor(true)}>
                  <Palette size={16} /> Edit Branding
                </button>
              </div>
            </div>

            {/* Campaign Launch */}
            <div className="launch-card">
              <div className="launch-card-header">
                <Target size={24} />
                <h3>Advertising</h3>
              </div>
              {state.campaignLive ? (
                <div className="status-box success">
                  <CheckCircle size={20} />
                  <p>✓ Campaign live on {state.publishedOn?.length || 0} platforms</p>
                </div>
              ) : (
                <div className="status-box">
                  <p>Auto-scheduled ads on selected platforms</p>
                  <div className="button-group-vertical">
                    <button className="btn btn-primary btn-small" onClick={() => launchCampaign(['tiktok', 'instagram'])}>
                      <Target size={16} /> Launch Campaign
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Store Publishing */}
          <div className="content-section">
            <h3>📦 Where to Sell</h3>
            <p className="text-secondary">Publish your product to these stores</p>
            
            <div className="store-grid">
              {Object.entries(PLATFORMS).map(([key, platform]) => {
                const isPublished = currentProduct.published_on?.some(p => p.platform === key);
                return (
                  <div key={key} className={`store-card ${isPublished ? 'published' : ''}`}>
                    <div className="store-badge">{platform.icon}</div>
                    <h4>{platform.name}</h4>
                    
                    {isPublished ? (
                      <div className="published-status">
                        <CheckCircle size={16} />
                        <span>Published</span>
                        <a href={currentProduct.published_on.find(p => p.platform === key)?.url} target="_blank" rel="noreferrer" className="store-link">
                          View <ExternalLink size={12} />
                        </a>
                      </div>
                    ) : (
                      <button
                        className="btn btn-small btn-secondary"
                        onClick={() => publishToStore(key)}
                      >
                        Publish
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Error Display */}
          {state.error && (
            <div className="alert alert-error">
              <AlertCircle size={18} />
              <span>{state.error}</span>
            </div>
          )}

          {state.notice && (
            <div className={`alert ${state.noticeType === 'warning' ? 'alert-warning' : 'alert-success'}`}>
              <CheckCircle size={18} />
              <span>{state.notice}</span>
            </div>
          )}

          {/* Product Info Summary */}
          <div className="content-section">
            <h3>Product Info</h3>
            <div className="info-grid">
              <div>
                <strong>Title:</strong> {currentProduct.title}
              </div>
              <div>
                <strong>Type:</strong> {currentProduct.product_type?.replace(/_/g, ' ')}
              </div>
              <div>
                <strong>Price:</strong> {currentProduct.price_range || 'Not set'}
              </div>
              <div>
                <strong>Status:</strong> {currentProduct.status}
              </div>
            </div>
            <p style={{ marginTop: '16px', fontSize: '14px', color: '#666' }}>
              {currentProduct.description}
            </p>
          </div>
        </>
      )}

      {/* Branding Editor Modal */}
      {showBrandingEditor && selected && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 2000,
          padding: '20px'
        }}>
          <div style={{ width: '100%', maxWidth: '600px' }}>
            <BrandingEditor
              productId={selected}
              initialBranding={currentProduct.branding}
              onClose={() => setShowBrandingEditor(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductLaunchPage;
