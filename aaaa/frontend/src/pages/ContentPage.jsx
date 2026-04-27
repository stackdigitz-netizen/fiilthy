import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Calendar, RefreshCw } from 'lucide-react';
import './Pages.css';
import API_URL from '../config/api';

const API = API_URL;

const compactNumberFormatter = new Intl.NumberFormat('en-US', {
  notation: 'compact',
  maximumFractionDigits: 1
});

const formatDateTime = (value) => {
  if (!value) {
    return 'Unscheduled';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return 'Unscheduled';
  }

  return date.toLocaleString();
};

const formatDateLabel = (value) => {
  if (!value) {
    return 'Unscheduled';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return 'Unscheduled';
  }

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric'
  });
};

const truncate = (value, limit = 90) => {
  const text = String(value || 'No content available');
  return text.length > limit ? `${text.slice(0, limit)}...` : text;
};

const ContentPage = () => {
  const [posts, setPosts] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [realtime, setRealtime] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadContentData();
  }, []);

  const loadContentData = async () => {
    setLoading(true);
    setError(null);

    const results = await Promise.allSettled([
      fetch(`${API}/api/marketing/social-posts?limit=50`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load social posts (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/social/campaigns`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load social campaigns (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/analytics/realtime`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load realtime analytics (${response.status})`);
        }
        return response.json();
      })
    ]);

    const [postsResult, campaignsResult, realtimeResult] = results;

    setPosts(postsResult.status === 'fulfilled' && Array.isArray(postsResult.value) ? postsResult.value : []);
    setCampaigns(
      campaignsResult.status === 'fulfilled' && Array.isArray(campaignsResult.value?.campaigns)
        ? campaignsResult.value.campaigns
        : []
    );
    setRealtime(realtimeResult.status === 'fulfilled' ? realtimeResult.value : null);

    const firstRejected = results.find((result) => result.status === 'rejected');
    if (firstRejected?.reason?.message) {
      setError(firstRejected.reason.message);
    }

    setLoading(false);
  };

  const platformSummary = useMemo(() => {
    const summary = new Map();

    posts.forEach((post) => {
      const platform = post.platform || 'unassigned';
      const existing = summary.get(platform) || { count: 0, latest: null };
      const currentDate = post.scheduled_time ? new Date(post.scheduled_time) : null;
      const latestDate = existing.latest ? new Date(existing.latest) : null;

      summary.set(platform, {
        count: existing.count + 1,
        latest:
          currentDate && (!latestDate || currentDate > latestDate)
            ? post.scheduled_time
            : existing.latest
      });
    });

    return Array.from(summary.entries())
      .map(([platform, details]) => ({ platform, ...details }))
      .sort((left, right) => right.count - left.count);
  }, [posts]);

  const scheduledPosts = useMemo(() => {
    return posts
      .filter((post) => post.scheduled_time)
      .sort((left, right) => new Date(left.scheduled_time) - new Date(right.scheduled_time));
  }, [posts]);

  const calendarRows = useMemo(() => {
    const grouped = new Map();

    scheduledPosts.forEach((post) => {
      const label = formatDateLabel(post.scheduled_time);
      const existing = grouped.get(label) || { date: label, posts: 0, platforms: new Set() };

      existing.posts += 1;
      existing.platforms.add(post.platform || 'unassigned');
      grouped.set(label, existing);
    });

    return Array.from(grouped.values())
      .slice(0, 4)
      .map((entry) => ({
        ...entry,
        platforms: Array.from(entry.platforms)
      }));
  }, [scheduledPosts]);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Viral Content Engine</h1>
        <p>Track the real post queue, campaigns, and platform coverage from the backend</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="section-header mb-4">
        <h2>Content Operations</h2>
        <button className="btn btn-secondary" onClick={loadContentData} disabled={loading}>
          <RefreshCw size={16} /> {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Posts</h3>
          <p className="stat-value">{loading ? '...' : posts.length}</p>
          <p className="stat-change">Stored social posts</p>
        </div>
        <div className="stat-card">
          <h3>Scheduled</h3>
          <p className="stat-value">{loading ? '...' : scheduledPosts.length}</p>
          <p className="stat-change">Posts with a scheduled time</p>
        </div>
        <div className="stat-card">
          <h3>Active Platforms</h3>
          <p className="stat-value">{loading ? '...' : platformSummary.length}</p>
          <p className="stat-change">Platforms with stored posts</p>
        </div>
        <div className="stat-card">
          <h3>Campaigns</h3>
          <p className="stat-value">{loading ? '...' : campaigns.length}</p>
          <p className="stat-change">
            {compactNumberFormatter.format(realtime?.traffic?.clicks || 0)} traffic clicks tracked
          </p>
        </div>
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h2>Content by Platform</h2>
          {platformSummary.length === 0 ? (
            <div className="empty-state">
              <p>No stored social posts yet.</p>
            </div>
          ) : (
            <div className="stack-list">
              {platformSummary.map((platform) => (
                <div key={platform.platform} className="detail-row">
                  <span>{platform.platform}</span>
                  <span className="metric-value">
                    {platform.count} posts {platform.latest ? `• latest ${formatDateLabel(platform.latest)}` : ''}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="content-section">
          <h2>Schedule Pipeline</h2>
          {calendarRows.length === 0 ? (
            <div className="empty-state">
              <p>No scheduled posts found.</p>
            </div>
          ) : (
            <div className="stack-list">
              {calendarRows.map((day) => (
                <div key={day.date} className="content-section" style={{ marginBottom: 0, padding: '16px' }}>
                  <div className="section-header" style={{ marginBottom: '12px' }}>
                    <h3 style={{ marginBottom: 0 }}>{day.date}</h3>
                    <span className="badge badge-secondary">{day.posts} posts</span>
                  </div>
                  <div className="inline-tags">
                    {day.platforms.map((platform) => (
                      <span key={`${day.date}-${platform}`} className="badge badge-secondary">
                        {platform}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="content-section">
        <h2>Campaign Queue</h2>
        {campaigns.length === 0 ? (
          <div className="empty-state">
            <p>No social campaigns are stored yet.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Campaign</th>
                  <th>Status</th>
                  <th>Total Posts</th>
                  <th>Platforms</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map((campaign) => {
                  const platformCount = Array.isArray(campaign.platforms)
                    ? campaign.platforms.length
                    : Object.keys(campaign.platforms || {}).length;

                  return (
                    <tr key={campaign.id}>
                      <td className="font-semibold">{campaign.product_title || campaign.product_id || 'Untitled campaign'}</td>
                      <td>
                        <span className="badge badge-secondary">{campaign.status || 'stored'}</span>
                      </td>
                      <td>{campaign.total_posts || 0}</td>
                      <td>{platformCount}</td>
                      <td>{formatDateLabel(campaign.created_at)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="content-section">
        <h2>Recent Posts</h2>
        {posts.length === 0 ? (
          <div className="empty-state">
            <p>No post content has been stored yet.</p>
          </div>
        ) : (
          <div className="activity-list">
            {posts.slice(0, 6).map((post) => (
              <div key={post.id} className="activity-item">
                <div className="activity-time">{post.platform || 'unassigned'}</div>
                <div className="activity-content">
                  <p>{truncate(post.content)}</p>
                  <span className="activity-badge info">{formatDateTime(post.scheduled_time)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentPage;
