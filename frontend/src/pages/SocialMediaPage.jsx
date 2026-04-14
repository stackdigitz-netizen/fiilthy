import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Loader, AlertCircle, Check, Plus, Trash2, Share2, Calendar, TrendingUp, Copy, ExternalLink } from 'lucide-react';
import WorkflowGuide from '../components/WorkflowGuide';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export default function SocialMediaPage() {
  const [searchParams] = useSearchParams();
  const [selectedProduct, setSelectedProduct] = useState('');
  const [products, setProducts] = useState([]);
  const [postsGenerated, setPostsGenerated] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState(['tiktok', 'instagram', 'twitter', 'linkedin']);
  const [campaignStatus, setCampaignStatus] = useState('idle');
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    loadProducts();
    loadAnalytics();
  }, []);

  // Auto-select product from URL param (e.g. /social-media?product=abc123)
  useEffect(() => {
    const pid = searchParams.get('product');
    if (pid) setSelectedProduct(pid);
  }, [searchParams]);

  // Returns the correct URL to open each platform's post creation screen.
  // For Twitter + LinkedIn we pre-fill the post text.
  const getPlatformPostUrl = (platform, post) => {
    const text = [post.caption, post.script, post.content, post.hook ? `Hook: ${post.hook}` : null]
      .filter(Boolean)
      .join('\n\n');
    const encoded = encodeURIComponent(text.slice(0, 2000));
    switch (platform) {
      case 'twitter':  return `https://twitter.com/intent/tweet?text=${encoded}`;
      case 'linkedin': return `https://www.linkedin.com/feed/?shareActive=true&text=${encoded}`;
      case 'tiktok':   return 'https://www.tiktok.com/upload';
      case 'instagram':return 'https://www.instagram.com/create/style/';
      case 'youtube':  return 'https://studio.youtube.com/';
      default:         return '#';
    }
  };

  const platformLabel = (p) => ({ tiktok: 'TikTok', instagram: 'Instagram', twitter: 'X (Twitter)', linkedin: 'LinkedIn', youtube: 'YouTube Studio' }[p] || p);

  const loadProducts = async () => {
    try {
      const response = await fetch(`${API}/api/products?limit=100`);
      const data = await response.json();
      setProducts(data || []);
    } catch (err) {
      console.error('Error loading products:', err);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`${API}/api/analytics/realtime`);
      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      console.error('Error loading analytics:', err);
    }
  };

  const handleGenerateMultiPlatformPosts = async (e) => {
    e.preventDefault();
    if (!selectedProduct) {
      setError('Please select a product');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Generate posts for all selected platforms
      const response = await fetch(`${API}/api/social/campaign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: selectedProduct,
          platforms: selectedPlatforms,
          posts_per_platform: 3
        })
      });

      if (!response.ok) throw new Error('Failed to generate campaign');

      const result = await response.json();
      if (result.success) {
        setPostsGenerated(result.campaign.platforms);
        setSuccess(`✅ Generated ${result.campaign.total_posts} social media posts!`);
        setCampaignStatus('generated');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateYouTubeShorts = async (e) => {
    e.preventDefault();
    if (!selectedProduct) {
      setError('Please select a product');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API}/api/social/youtube-shorts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: selectedProduct,
          num_scripts: 5
        })
      });

      if (!response.ok) throw new Error('Failed to generate YouTube Shorts');

      const result = await response.json();
      if (result.success) {
        setPostsGenerated({ youtube: result.shorts });
        setSuccess(`✅ Generated ${result.shorts_generated} YouTube Shorts scripts!`);
        setCampaignStatus('youtube_shorts');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleAllPosts = async () => {
    if (Object.keys(postsGenerated).length === 0) {
      setError('No posts generated yet');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const now = new Date();
      const response = await fetch(`${API}/api/social/schedule-multi-platform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          posts_by_platform: postsGenerated,
          start_date: now.toISOString(),
          interval_hours: 24
        })
      });

      if (!response.ok) {
        throw new Error('Failed to schedule posts');
      }

      setSuccess('✅ All posts scheduled successfully!');
      setCampaignStatus('scheduled');
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const togglePlatform = (platform) => {
    setSelectedPlatforms(prev =>
      prev.includes(platform)
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  const normalizePosts = (posts) => (Array.isArray(posts) ? posts : posts ? [posts] : []);

  const getPlatformConnectionState = (platformId) => {
    const posts = normalizePosts(postsGenerated?.[platformId]);
    return {
      enabled: selectedPlatforms.includes(platformId),
      count: posts.length
    };
  };

  const copyPostToClipboard = async (platform, post) => {
    const parts = [post.caption, post.script, post.content, post.hook && `Hook: ${post.hook}`]
      .filter(Boolean)
      .join('\n\n');

    if (!parts) {
      setError(`No copyable content found for ${platform}.`);
      return;
    }

    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(parts);
      } else {
        const textarea = document.createElement('textarea');
        textarea.value = parts;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'absolute';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
      }

      setSuccess(`${platform} post copied to clipboard.`);
      setError('');
    } catch (err) {
      setError(`Failed to copy ${platform} post: ${err.message}`);
    }
  };

  const deleteGeneratedPost = (platform, indexToDelete) => {
    setPostsGenerated((prev) => {
      const next = { ...prev };
      const currentPosts = normalizePosts(next[platform]);
      const updatedPosts = currentPosts.filter((_, index) => index !== indexToDelete);

      if (updatedPosts.length === 0) {
        delete next[platform];
      } else {
        next[platform] = updatedPosts;
      }

      return next;
    });

    setSuccess(`${platform} post removed from the preview.`);
    setError('');
  };

  const PlatformCard = ({ name, icon, enabled, count }) => (
    <div className={`platform-card ${enabled ? 'active' : ''}`}>
      <div className="platform-header">
        <span className="platform-icon">{icon}</span>
        <span className="platform-name">{name}</span>
      </div>
      <div className="platform-stats">
        <span>Posts: {count}</span>
        {enabled && <Check size={16} style={{ color: '#22c55e' }} />}
      </div>
    </div>
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📱 Multi-Platform Social Media</h1>
        <p>Generate and schedule posts across all major platforms</p>
      </div>

      <WorkflowGuide page="social-media" hasGeneratedPosts={Object.keys(postsGenerated).length > 0} />

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <Check size={18} />
          {success}
        </div>
      )}

      {/* Analytics Overview */}
      {analytics && (
        <div className="analytics-section">
          <h3>📊 Social Media Analytics</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Total Reach</div>
              <div className="stat-value">{analytics.traffic?.clicks?.toLocaleString() || 0}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Engagement Rate</div>
              <div className="stat-value">{analytics.traffic?.conversion_rate || 0}%</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Conversions</div>
              <div className="stat-value">{analytics.traffic?.conversions || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* Campaign Generator */}
      <div className="card">
        <h2>🎯 Create Social Media Campaign</h2>

        <div className="form-group">
          <label>Select Product</label>
          <select
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
            disabled={loading}
          >
            <option value="">-- Choose a product --</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.title || product.product_type}
              </option>
            ))}
          </select>
        </div>

        {/* Platform Selection */}
        <div className="form-group">
          <label>Select Platforms</label>
          <div className="platform-grid">
            {[
              { id: 'tiktok', name: 'TikTok', icon: '🎵' },
              { id: 'instagram', name: 'Instagram', icon: '📸' },
              { id: 'twitter', name: 'Twitter/X', icon: '𝕏' },
              { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
              { id: 'youtube', name: 'YouTube', icon: '▶️' }
            ].map(platform => (
              <button
                key={platform.id}
                type="button"
                onClick={() => togglePlatform(platform.id)}
                className={`platform-toggle ${selectedPlatforms.includes(platform.id) ? 'selected' : ''}`}
              >
                <span>{platform.icon}</span>
                <span>{platform.name}</span>
                {selectedPlatforms.includes(platform.id) && <Check size={14} />}
              </button>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="button-group">
          <button
            onClick={handleGenerateMultiPlatformPosts}
            disabled={loading || !selectedProduct}
            className="btn btn-primary"
            type="button"
          >
            {loading ? (
              <>
                <Loader size={16} />
                Generating...
              </>
            ) : (
              <>
                <Plus size={16} />
                Generate Multi-Platform Posts
              </>
            )}
          </button>

          <button
            onClick={handleGenerateYouTubeShorts}
            disabled={loading || !selectedProduct}
            className="btn btn-secondary"
            type="button"
          >
            {loading ? (
              <>
                <Loader size={16} />
                Generating...
              </>
            ) : (
              <>
                <Plus size={16} />
                Generate YouTube Shorts
              </>
            )}
          </button>

          {Object.keys(postsGenerated).length > 0 && (
            <button
              onClick={handleScheduleAllPosts}
              disabled={loading}
              className="btn btn-success"
              type="button"
            >
              <Calendar size={16} />
              Schedule All Posts
            </button>
          )}
        </div>
      </div>

      {/* Generated Posts Display */}
      {Object.keys(postsGenerated).length > 0 && (
        <div className="card">
          <h2>📋 Generated Posts Preview</h2>

          {Object.entries(postsGenerated).map(([platform, posts]) => (
            <div key={platform} className="posts-section">
              <div className="section-header">
                <h3>
                  {platform === 'tiktok' && '🎵 TikTok'}
                  {platform === 'instagram' && '📸 Instagram'}
                  {platform === 'twitter' && '𝕏 Twitter'}
                  {platform === 'linkedin' && '💼 LinkedIn'}
                  {platform === 'youtube' && '▶️ YouTube'}
                </h3>
                <span className="post-count">{posts.length} posts</span>
              </div>

              <div className="posts-list">
                {normalizePosts(posts).map((post, idx) => (
                  <div key={idx} className="post-preview">
                    <div className="post-meta">
                      <span className="post-type">
                        {post.type || 'Post'} #{idx + 1}
                      </span>
                      {post.scheduled_time && (
                        <span className="post-time">
                          <Calendar size={12} />
                          {new Date(post.scheduled_time).toLocaleString()}
                        </span>
                      )}
                    </div>

                    <div className="post-content">
                      {post.caption && <p>{post.caption}</p>}
                      {post.script && <p>{post.script}</p>}
                      {post.content && <p>{post.content}</p>}
                      {post.hook && <p><strong>Hook:</strong> {post.hook}</p>}
                    </div>

                    <div className="post-footer">
                      {post.hashtags && (
                        <div className="hashtags">
                          {(Array.isArray(post.hashtags) ? post.hashtags : [post.hashtags]).map((tag, i) => (
                            <span key={i} className="hashtag">{tag}</span>
                          ))}
                        </div>
                      )}
                      {post.estimated_reach && (
                        <span className="reach">
                          <TrendingUp size={12} />
                          ~{post.estimated_reach?.toLocaleString()} reach
                        </span>
                      )}
                    </div>

                    <div className="post-actions" style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
                      <button
                        className="icon-btn"
                        title="Copy text"
                        type="button"
                        onClick={() => copyPostToClipboard(platform, post)}
                        style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 10px', fontSize: '12px' }}
                      >
                        <Copy size={13} /> Copy
                      </button>
                      <a
                        href={getPlatformPostUrl(platform, post)}
                        target="_blank"
                        rel="noopener noreferrer"
                        title={`Open ${platformLabel(platform)} to post`}
                        style={{
                          display: 'flex', alignItems: 'center', gap: '4px',
                          padding: '6px 10px', fontSize: '12px', fontWeight: 600,
                          backgroundColor: platform === 'tiktok' ? '#010101' :
                            platform === 'instagram' ? '#c13584' :
                            platform === 'twitter' ? '#1da1f2' :
                            platform === 'linkedin' ? '#0a66c2' : '#ff0000',
                          color: '#fff', borderRadius: '6px', textDecoration: 'none', whiteSpace: 'nowrap'
                        }}
                        onClick={() => copyPostToClipboard(platform, post)}
                      >
                        <ExternalLink size={12} /> Open {platformLabel(platform)} →
                      </a>
                      <button
                        className="icon-btn"
                        title="Delete"
                        type="button"
                        onClick={() => deleteGeneratedPost(platform, idx)}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Platform Status */}
      <div className="card">
        <h2>🔗 Platform Connections</h2>
        <div className="platforms-overview">
          <PlatformCard name="TikTok" icon="🎵" {...getPlatformConnectionState('tiktok')} />
          <PlatformCard name="Instagram" icon="📸" {...getPlatformConnectionState('instagram')} />
          <PlatformCard name="Twitter/X" icon="𝕏" {...getPlatformConnectionState('twitter')} />
          <PlatformCard name="LinkedIn" icon="💼" {...getPlatformConnectionState('linkedin')} />
          <PlatformCard name="YouTube" icon="▶️" {...getPlatformConnectionState('youtube')} />
        </div>
        <p className="info-text">
          💡 <strong>Tip:</strong> Connect your platform accounts in Settings to enable automatic posting. Generated posts can be previewed and modified before publishing.
        </p>
      </div>

      {/* Scheduling Guide */}
      <div className="card">
        <h2>📅 Scheduling Guide</h2>
        <div className="guide-content">
          <h4>Best Posting Times by Platform:</h4>
          <ul>
            <li><strong>TikTok:</strong> 6 PM - 10 PM (Peak engagement)</li>
            <li><strong>Instagram:</strong> 11 AM - 1 PM & 7 PM - 9 PM</li>
            <li><strong>Twitter/X:</strong> 8 AM - 10 AM & 5 PM - 7 PM</li>
            <li><strong>LinkedIn:</strong> 8 AM - 10 AM & 12 PM - 2 PM (Weekdays)</li>
            <li><strong>YouTube:</strong> 2 PM - 4 PM (Consistent posting important)</li>
          </ul>

          <h4>Content Recommendations:</h4>
          <ul>
            <li>🎬 <strong>Video Content:</strong> 15-60 seconds for shorts, up to 10 minutes for full videos</li>
            <li>📝 <strong>Text Posts:</strong> 280 chars for Twitter, 2200 for LinkedIn</li>
            <li>🏷️ <strong>Hashtags:</strong> 3-5 per post for maximum reach</li>
            <li>💬 <strong>Engagement:</strong> Ask questions to boost interaction</li>
            <li>🔗 <strong>Links:</strong> Use link shorteners and include CTAs</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
