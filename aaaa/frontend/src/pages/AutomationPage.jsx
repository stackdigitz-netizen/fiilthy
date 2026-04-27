import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, CheckCircle, Clock, RefreshCw } from 'lucide-react';
import './Pages.css';
import API_URL from '../config/api';

const API = API_URL;

const titleCase = (value) =>
  String(value || 'unknown')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());

const parseDate = (value) => {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
};

const formatDateTime = (value) => {
  const date = parseDate(value);
  return date ? date.toLocaleString() : 'Unavailable';
};

const formatRelativeTime = (value) => {
  const date = parseDate(value);
  if (!date) {
    return 'Unknown';
  }

  const differenceMs = Date.now() - date.getTime();
  const absoluteMinutes = Math.round(Math.abs(differenceMs) / 60000);
  const suffix = differenceMs >= 0 ? 'ago' : 'from now';

  if (absoluteMinutes < 1) {
    return 'Just now';
  }

  if (absoluteMinutes < 60) {
    return `${absoluteMinutes} min${absoluteMinutes === 1 ? '' : 's'} ${suffix}`;
  }

  const absoluteHours = Math.round(absoluteMinutes / 60);
  if (absoluteHours < 24) {
    return `${absoluteHours} hour${absoluteHours === 1 ? '' : 's'} ${suffix}`;
  }

  const absoluteDays = Math.round(absoluteHours / 24);
  return `${absoluteDays} day${absoluteDays === 1 ? '' : 's'} ${suffix}`;
};

const AutomationPage = () => {
  const [systemHealth, setSystemHealth] = useState(null);
  const [schedule, setSchedule] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [launchCampaigns, setLaunchCampaigns] = useState([]);
  const [socialPosts, setSocialPosts] = useState([]);
  const [keyStatus, setKeyStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAutomationData();
  }, []);

  const loadAutomationData = async () => {
    setLoading(true);
    setError(null);

    const results = await Promise.allSettled([
      fetch(`${API}/api/system/health`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load system health (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/automation/schedule`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load automation schedule (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/social/campaigns`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load social campaigns (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/marketing/launch-campaigns`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load launch campaigns (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/marketing/social-posts?limit=10`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load social posts (${response.status})`);
        }
        return response.json();
      }),
      fetch(`${API}/api/keys/status`).then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load key status (${response.status})`);
        }
        return response.json();
      })
    ]);

    const [healthResult, scheduleResult, campaignResult, launchResult, postsResult, keysResult] = results;

    setSystemHealth(healthResult.status === 'fulfilled' ? healthResult.value : null);
    setSchedule(
      scheduleResult.status === 'fulfilled' && Array.isArray(scheduleResult.value?.schedule)
        ? scheduleResult.value.schedule
        : []
    );
    setCampaigns(
      campaignResult.status === 'fulfilled' && Array.isArray(campaignResult.value?.campaigns)
        ? campaignResult.value.campaigns
        : []
    );
    setLaunchCampaigns(launchResult.status === 'fulfilled' && Array.isArray(launchResult.value) ? launchResult.value : []);
    setSocialPosts(postsResult.status === 'fulfilled' && Array.isArray(postsResult.value) ? postsResult.value : []);
    setKeyStatus(keysResult.status === 'fulfilled' ? keysResult.value : {});

    const firstRejected = results.find((result) => result.status === 'rejected');
    if (firstRejected?.reason?.message) {
      setError(firstRejected.reason.message);
    }

    setLoading(false);
  };

  const keyEntries = useMemo(() => {
    return Object.entries(keyStatus?.api_keys_status || {}).map(([name, statusText]) => {
      const configured = String(statusText).includes('Configured') || String(statusText).includes('Connected');

      return {
        name,
        label: name === 'mongodb' ? 'MongoDB' : titleCase(name),
        statusText,
        configured
      };
    });
  }, [keyStatus]);

  const serviceEntries = useMemo(() => {
    return Object.entries(systemHealth?.services || {}).map(([name, status]) => ({
      name,
      label: titleCase(name),
      status: titleCase(status)
    }));
  }, [systemHealth]);

  const recentActivity = useMemo(() => {
    return [
      ...campaigns.map((campaign) => ({
        id: `campaign-${campaign.id}`,
        time: campaign.created_at,
        label: `Social campaign prepared for ${campaign.product_title || campaign.product_id || 'an untitled product'}`,
        status: campaign.status || 'ready'
      })),
      ...launchCampaigns.map((campaign) => ({
        id: `launch-${campaign.id}`,
        time: campaign.created_at,
        label: `Launch campaign stored for ${campaign.product_title || campaign.product_id || 'an untitled product'}`,
        status: campaign.status || 'stored'
      })),
      ...socialPosts.map((post) => ({
        id: `post-${post.id}`,
        time: post.scheduled_time || post.created_at,
        label: `Post queued for ${post.platform || 'an unassigned platform'}`,
        status: post.status || (post.scheduled_time ? 'scheduled' : 'stored')
      }))
    ]
      .filter((entry) => parseDate(entry.time))
      .sort((left, right) => parseDate(right.time).getTime() - parseDate(left.time).getTime())
      .slice(0, 6);
  }, [campaigns, launchCampaigns, socialPosts]);

  const notes = useMemo(() => {
    const items = [];

    if (systemHealth?.status === 'healthy') {
      items.push({
        type: 'success',
        title: 'Core systems healthy',
        message: 'Database, automation, and marketplace services are responding.'
      });
    } else if (systemHealth) {
      items.push({
        type: 'warning',
        title: 'Health check reported issues',
        message: 'Review backend services before relying on automation results.'
      });
    }

    const missingCredentials = keyEntries.filter((entry) => !entry.configured).length;
    if (missingCredentials > 0) {
      items.push({
        type: 'warning',
        title: 'Credential gaps',
        message: `${missingCredentials} backend credential slots are still missing.`
      });
    }

    if (campaigns.length === 0) {
      items.push({
        type: 'info',
        title: 'No social campaigns yet',
        message: 'Generate a social campaign to populate the automation queue.'
      });
    }

    if (socialPosts.length === 0) {
      items.push({
        type: 'info',
        title: 'No stored social posts',
        message: 'Social automation activity will appear here once posts are generated or scheduled.'
      });
    }

    return items.slice(0, 4);
  }, [campaigns.length, keyEntries, socialPosts.length, systemHealth]);

  const queueCards = useMemo(() => {
    return [
      {
        title: 'Scheduled cycles',
        value: schedule.length,
        description: 'Automation windows currently planned by the scheduler.'
      },
      {
        title: 'Social campaigns',
        value: campaigns.length,
        description: 'Campaign records created by the social workflow.'
      },
      {
        title: 'Queued posts',
        value: socialPosts.length,
        description: 'Stored social posts available for scheduling or review.'
      },
      {
        title: 'Tracked products',
        value: systemHealth?.stats?.total_products || 0,
        description: 'Products currently visible to backend services.'
      }
    ];
  }, [campaigns.length, schedule.length, socialPosts.length, systemHealth]);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Automation Control</h1>
        <p>Review the real scheduler, backend services, and active campaign queues</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="section-header mb-4">
        <h2>Automation Overview</h2>
        <button className="btn btn-secondary" onClick={loadAutomationData} disabled={loading}>
          <RefreshCw size={16} /> {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Scheduled Cycles</h3>
          <p className="stat-value">{loading ? '...' : schedule.length}</p>
          <p className="stat-change">Backend scheduler entries</p>
        </div>
        <div className="stat-card">
          <h3>Social Campaigns</h3>
          <p className="stat-value">{loading ? '...' : campaigns.length}</p>
          <p className="stat-change">Stored campaign records</p>
        </div>
        <div className="stat-card">
          <h3>Stored Posts</h3>
          <p className="stat-value">{loading ? '...' : socialPosts.length}</p>
          <p className="stat-change">Content available for automation</p>
        </div>
        <div className="stat-card">
          <h3>Configured Keys</h3>
          <p className="stat-value">{loading ? '...' : keyEntries.filter((entry) => entry.configured).length}</p>
          <p className="stat-change">Backend credential slots ready</p>
        </div>
      </div>

      <div className="content-section">
        <h2>Scheduled Automation Cycles</h2>
        {schedule.length === 0 ? (
          <div className="empty-state">
            <p>No automation schedule is available right now.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Cycle</th>
                  <th>Task</th>
                  <th>Next Run</th>
                  <th>Hours Until</th>
                </tr>
              </thead>
              <tbody>
                {schedule.map((entry) => (
                  <tr key={entry.cycle}>
                    <td className="font-semibold">{titleCase(entry.cycle)}</td>
                    <td>{titleCase(entry.task)}</td>
                    <td>{formatDateTime(entry.next_run)}</td>
                    <td>{Number(entry.hours_until || 0).toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h3>Core Services</h3>
          {serviceEntries.length === 0 ? (
            <div className="empty-state">
              <p>System health data is not available yet.</p>
            </div>
          ) : (
            <div className="stack-list">
              {serviceEntries.map((service) => (
                <div key={service.name} className="detail-row">
                  <span>{service.label}</span>
                  <span className="metric-value">{service.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="content-section">
          <h3>Credential Coverage</h3>
          {keyEntries.length === 0 ? (
            <div className="empty-state">
              <p>No backend credential status was returned.</p>
            </div>
          ) : (
            <div className="stack-list">
              {keyEntries.map((entry) => (
                <div key={entry.name} className="detail-row">
                  <span>{entry.label}</span>
                  <span className={`badge ${entry.configured ? 'badge-success' : 'badge-secondary'}`}>
                    {entry.statusText}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid-2">
        <div className="content-section">
          <h3>Operational Notes</h3>
          {notes.length === 0 ? (
            <div className="empty-state">
              <p>No alerts or notable automation events were detected.</p>
            </div>
          ) : (
            notes.map((note) => (
              <div key={note.title} className="insight-box">
                {note.type === 'success' ? <CheckCircle size={18} /> : note.type === 'warning' ? <AlertCircle size={18} /> : <Clock size={18} />}
                <div>
                  <p className="font-semibold">{note.title}</p>
                  <p>{note.message}</p>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="content-section">
          <h3>Recent Queue Activity</h3>
          {recentActivity.length === 0 ? (
            <div className="empty-state">
              <p>No recent automation activity has been stored yet.</p>
            </div>
          ) : (
            <div className="activity-list">
              {recentActivity.map((entry) => (
                <div key={entry.id} className="activity-item">
                  <div className="activity-time">{formatRelativeTime(entry.time)}</div>
                  <div className="activity-content">
                    <p>{entry.label}</p>
                    <span className="activity-badge info">{entry.status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="content-section">
        <h3>Automation Queues</h3>
        <div className="grid-4">
          {queueCards.map((card) => (
            <div key={card.title} className="rule-card">
              <h3>{card.title}</h3>
              <p className="stat-value">{loading ? '...' : card.value}</p>
              <p className="text-secondary">{card.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AutomationPage;
