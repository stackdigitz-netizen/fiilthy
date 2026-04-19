import React, { useState, useEffect } from 'react';
import { Palette, Video, Target, AlertCircle, CheckCircle, Clock, ExternalLink, RefreshCw } from 'lucide-react';
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

const readErrorMessage = async (response, fallbackMessage) => {
  try {
    const data = await response.json();
    if (typeof data?.detail === 'string' && data.detail.trim()) {
      return data.detail;
    }
    if (typeof data?.message === 'string' && data.message.trim()) {
      return data.message;
    }
  } catch {
    // Fall through to text/default parsing.
  }

  try {
    const text = await response.text();
    if (text.trim()) {
      return text;
    }
  } catch {
    // Ignore parsing failures.
  }

  return fallbackMessage;
};

const STORE_PLATFORMS = {
  gumroad: { name: 'Gumroad', color: '#FF90E8', icon: '🛍️', canPublish: true },
  etsy: { name: 'Etsy', color: '#F1641E', icon: '🧵', canPublish: true },
  stripe: { name: 'Stripe Store', color: '#635BFF', icon: '💳', canPublish: true }
};

const LIVE_SOCIAL_PLATFORMS = {
  tiktok: { name: 'TikTok', color: '#000', icon: '🎵' },
  instagram: { name: 'Instagram', color: '#E4405F', icon: '📸' },
  youtube: { name: 'YouTube', color: '#FF0000', icon: '▶️' },
};

const ProductLaunchPage = () => {
  const [products, setProducts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [launchState, setLaunchState] = useState({});
  const [videoProgress, setVideoProgress] = useState({});
  const [showBrandingEditor, setShowBrandingEditor] = useState(false);
  const [liveReadiness, setLiveReadiness] = useState({});
  const [liveLoading, setLiveLoading] = useState(false);
  const [liveForm, setLiveForm] = useState({
    title: '',
    description: '',
    hashtags: '',
    videoPublicUrl: '',
    videoPath: '',
  });
  const [liveResults, setLiveResults] = useState({});
  const [publishingLive, setPublishingLive] = useState({});
  const [productVideos, setProductVideos] = useState([]);

  const loadLiveReadiness = async () => {
    setLiveLoading(true);
    try {
      const response = await fetch(`${API}/api/distribution/live-readiness`, {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to load live distribution readiness'));
      }

      const data = await response.json();
      setLiveReadiness(data.platforms || {});
    } catch (error) {
      setLiveReadiness({});
      setLaunchState((prev) => ({
        ...prev,
        [selected]: {
          ...(prev[selected] || {}),
          error: error.message,
        },
      }));
    } finally {
      setLiveLoading(false);
    }
  };

  const loadProductVideos = async (productId) => {
    if (!productId) {
      setProductVideos([]);
      return;
    }

    try {
      const response = await fetch(`${API}/api/videos/product/${productId}`, {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to load generated videos'));
      }

      const data = await response.json();
      const videos = Array.isArray(data.videos) ? [...data.videos] : [];
      videos.sort((left, right) => new Date(right.created_at || 0).getTime() - new Date(left.created_at || 0).getTime());
      setProductVideos(videos);

      if (videos[0]?.video_path) {
        setLiveForm((prev) => ({
          ...prev,
          videoPath: videos[0].video_path,
        }));
      }
    } catch {
      setProductVideos([]);
    }
  };

  useEffect(() => {
    loadProducts();
    loadLiveReadiness();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Poll video progress every 5 seconds
  useEffect(() => {
    const interval = setInterval(checkVideoProgress, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  useEffect(() => {
    const product = products.find((item) => item.id === selected);

    if (!product) {
      setProductVideos([]);
      return;
    }

    setLiveForm({
      title: product.title || '',
      description: product.description || '',
      hashtags: Array.isArray(product.tags) ? product.tags.join(', ') : '',
      videoPublicUrl: '',
      videoPath: '',
    });
    loadProductVideos(product.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [products, selected]);

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
              await loadProductVideos(selected);
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

  const publishLive = async (platform) => {
    if (!selected) return;

    const product = products.find((item) => item.id === selected);
    if (!product) return;

    setPublishingLive((prev) => ({ ...prev, [platform]: true }));
    setLaunchState((prev) => ({
      ...prev,
      [selected]: {
        ...(prev[selected] || {}),
        error: '',
      },
    }));

    try {
      const response = await fetch(`${API}/api/distribution/publish-live`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          product_id: selected,
          title: liveForm.title.trim() || product.title,
          description: liveForm.description.trim() || product.description || '',
          hashtags: liveForm.hashtags
            .split(',')
            .map((tag) => tag.trim())
            .filter(Boolean),
          platforms: [platform],
          privacy_status: 'public',
          video_public_url: liveForm.videoPublicUrl.trim() || undefined,
          video_path: liveForm.videoPath.trim() || undefined,
        }),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to publish live');
      }

      const platformResult = data.platforms?.[platform] || {};
      const status = platformResult.status || data.status || 'updated';
      const success = status === 'uploaded' || status === 'submitted';

      setLiveResults((prev) => ({
        ...prev,
        [selected]: {
          ...(prev[selected] || {}),
          [platform]: platformResult,
        },
      }));

      setLaunchState((prev) => ({
        ...prev,
        [selected]: {
          ...(prev[selected] || {}),
          notice: platformResult.message || `Live publish status: ${status}`,
          noticeType: success ? 'success' : 'warning',
          error: '',
        },
      }));
    } catch (error) {
      setLaunchState((prev) => ({
        ...prev,
        [selected]: {
          ...(prev[selected] || {}),
          error: error.message,
        },
      }));
    } finally {
      setPublishingLive((prev) => ({ ...prev, [platform]: false }));
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
  const selectedLiveResults = liveResults[selected] || {};

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

          {/* Live Distribution */}
          <div className="content-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
              <div>
                <h3>📡 Live Distribution</h3>
                <p className="text-secondary">Use the backend's real readiness checks before attempting live uploads.</p>
              </div>
              <button className="btn btn-secondary btn-small" onClick={loadLiveReadiness} disabled={liveLoading}>
                <RefreshCw size={16} /> {liveLoading ? 'Refreshing…' : 'Refresh Readiness'}
              </button>
            </div>

            <div className="grid-2" style={{ marginTop: 16 }}>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Live Title</label>
                <input
                  value={liveForm.title}
                  onChange={(event) => setLiveForm((prev) => ({ ...prev, title: event.target.value }))}
                  placeholder="Video title"
                  style={{ width: '100%', padding: 12, borderRadius: 10, border: '1px solid #d1d5db', marginBottom: 14 }}
                />

                <label style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Hashtags</label>
                <input
                  value={liveForm.hashtags}
                  onChange={(event) => setLiveForm((prev) => ({ ...prev, hashtags: event.target.value }))}
                  placeholder="ai, sidehustle, digitalproducts"
                  style={{ width: '100%', padding: 12, borderRadius: 10, border: '1px solid #d1d5db' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Public Video URL</label>
                <input
                  value={liveForm.videoPublicUrl}
                  onChange={(event) => setLiveForm((prev) => ({ ...prev, videoPublicUrl: event.target.value }))}
                  placeholder="https://cdn.example.com/video.mp4"
                  style={{ width: '100%', padding: 12, borderRadius: 10, border: '1px solid #d1d5db', marginBottom: 14 }}
                />

                <label style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Server Video Path</label>
                <input
                  value={liveForm.videoPath}
                  onChange={(event) => setLiveForm((prev) => ({ ...prev, videoPath: event.target.value }))}
                  placeholder="C:\\path\\to\\video.mp4"
                  style={{ width: '100%', padding: 12, borderRadius: 10, border: '1px solid #d1d5db' }}
                />
              </div>
            </div>

            <div style={{ marginTop: 14 }}>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Caption / Description</label>
              <textarea
                value={liveForm.description}
                onChange={(event) => setLiveForm((prev) => ({ ...prev, description: event.target.value }))}
                rows={4}
                placeholder="Write the caption that should be sent to the live distribution endpoint"
                style={{ width: '100%', padding: 12, borderRadius: 10, border: '1px solid #d1d5db', resize: 'vertical' }}
              />
            </div>

            {productVideos.length > 0 && (
              <p style={{ marginTop: 12, fontSize: 13, color: '#4b5563' }}>
                Latest generated server video detected: {productVideos[0].video_path}
              </p>
            )}

            <div className="store-grid" style={{ marginTop: 20 }}>
              {Object.entries(LIVE_SOCIAL_PLATFORMS).map(([key, platform]) => {
                const readiness = liveReadiness[key] || { status: 'blocked', missing: [], notes: [] };
                const result = selectedLiveResults[key];
                const ready = readiness.status === 'ready';
                const hasRequiredVideo = key === 'youtube' ? Boolean(liveForm.videoPath.trim()) : Boolean(liveForm.videoPublicUrl.trim());
                const canPublish = ready && hasRequiredVideo && Boolean(liveForm.title.trim());

                return (
                  <div key={key} className={`store-card ${ready ? 'published' : ''}`}>
                    <div className="store-badge">{platform.icon}</div>
                    <h4>{platform.name}</h4>
                    <p style={{ fontSize: 12, color: ready ? '#16a34a' : '#b45309', marginBottom: 10 }}>
                      {ready ? 'Ready for live publishing' : 'Blocked'}
                    </p>
                    {readiness.missing?.length > 0 && (
                      <p style={{ fontSize: 12, color: '#6b7280', lineHeight: 1.5, marginBottom: 10 }}>
                        Missing: {readiness.missing.join(', ')}
                      </p>
                    )}
                    {readiness.notes?.length > 0 && (
                      <p style={{ fontSize: 12, color: '#6b7280', lineHeight: 1.5, marginBottom: 10 }}>
                        {readiness.notes.join(' ')}
                      </p>
                    )}
                    {result && (
                      <p style={{ fontSize: 12, color: result.status === 'uploaded' || result.status === 'submitted' ? '#16a34a' : '#b45309', lineHeight: 1.5, marginBottom: 10 }}>
                        Last result: {result.message || result.status}
                      </p>
                    )}
                    {result?.url && (
                      <a href={result.url} target="_blank" rel="noreferrer" className="store-link" style={{ marginBottom: 10, display: 'inline-flex' }}>
                        Open <ExternalLink size={12} />
                      </a>
                    )}
                    <button
                      className="btn btn-small btn-secondary"
                      onClick={() => publishLive(key)}
                      disabled={!canPublish || Boolean(publishingLive[key])}
                    >
                      {publishingLive[key]
                        ? 'Publishing…'
                        : !ready
                          ? 'Blocked'
                          : !hasRequiredVideo
                            ? key === 'youtube'
                              ? 'Add Video Path'
                              : 'Add Video URL'
                            : 'Publish Live'}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Store Publishing */}
          <div className="content-section">
            <h3>📦 Where to Sell</h3>
            <p className="text-secondary">Publish your product to storefronts and marketplaces that are wired through the product publish route.</p>
            
            <div className="store-grid">
              {Object.entries(STORE_PLATFORMS).map(([key, platform]) => {
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
