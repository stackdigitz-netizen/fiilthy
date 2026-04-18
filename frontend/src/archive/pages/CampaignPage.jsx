import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import API_URL from '../config/api';
import './CampaignPage.css';

export default function CampaignPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    product_id: '',
    product_title: '',
    product_description: '',
    price: 0,
    budget: 100.0,
    schedule_start_days_ahead: 1,
    duration_days: 14,
    target_audience: {}
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'price' || name === 'budget' || name === 'schedule_start_days_ahead' || name === 'duration_days' ? parseFloat(value) : value
    }));
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/campaigns/generate-product-campaign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        setCampaigns(prev => [...prev, data.campaign]);
        setFormData({
          product_id: '',
          product_title: '',
          product_description: '',
          price: 0,
          budget: 100.0,
          schedule_start_days_ahead: 1,
          duration_days: 14,
          target_audience: {}
        });
        setShowForm(false);
        alert(`✅ Campaign created! Generated ${data.campaign.videos.tiktok.count} TikTok and ${data.campaign.videos.instagram.count} Instagram videos.`);
      } else {
        alert(`❌ Error: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Campaign creation error:', error);
      alert('Failed to create campaign');
    } finally {
      setLoading(false);
    }
  };

  const handleActivateCampaign = async (campaignId) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/campaigns/campaigns/${campaignId}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (data.success) {
        setCampaigns(prev => prev.map(c => 
          c.id === campaignId ? { ...c, status: 'active' } : c
        ));
        alert('✅ Campaign activated!');
      }
    } catch (error) {
      console.error('Error activating campaign:', error);
      alert('Failed to activate campaign');
    } finally {
      setLoading(false);
    }
  };

  const handleViewCampaignVideos = (campaignId) => {
    navigate(`/campaign-videos/${campaignId}`);
  };

  return (
    <div className="campaign-page">
      <div className="campaign-header">
        <h1>📱 Video Campaign Manager</h1>
        <p>Create viral campaigns with AI-generated videos for TikTok & Instagram</p>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? '✕ Cancel' : '+ Create New Campaign'}
        </button>
      </div>

      {showForm && (
        <div className="campaign-form-container">
          <form className="campaign-form" onSubmit={handleCreateCampaign}>
            <div className="form-section">
              <h3>Product Information</h3>
              
              <div className="form-group">
                <label>Product ID</label>
                <input
                  type="text"
                  name="product_id"
                  value={formData.product_id}
                  onChange={handleInputChange}
                  placeholder="your-product-id"
                  required
                />
              </div>

              <div className="form-group">
                <label>Product Title</label>
                <input
                  type="text"
                  name="product_title"
                  value={formData.product_title}
                  onChange={handleInputChange}
                  placeholder="My Awesome Product"
                  required
                />
              </div>

              <div className="form-group">
                <label>Product Description</label>
                <textarea
                  name="product_description"
                  value={formData.product_description}
                  onChange={handleInputChange}
                  placeholder="Describe what makes your product special..."
                  rows={3}
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Price ($)</label>
                  <input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleInputChange}
                    placeholder="29.99"
                    step="0.01"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Budget ($)</label>
                  <input
                    type="number"
                    name="budget"
                    value={formData.budget}
                    onChange={handleInputChange}
                    placeholder="100.00"
                    step="10"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Campaign Schedule</h3>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Start in (days)</label>
                  <input
                    type="number"
                    name="schedule_start_days_ahead"
                    value={formData.schedule_start_days_ahead}
                    onChange={handleInputChange}
                    placeholder="1"
                    min="0"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Duration (days)</label>
                  <input
                    type="number"
                    name="duration_days"
                    value={formData.duration_days}
                    onChange={handleInputChange}
                    placeholder="14"
                    min="1"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="form-section info-box">
              <h4>📊 What You'll Get:</h4>
              <ul>
                <li>✅ 10 TikTok videos (optimized for max viral potential)</li>
                <li>✅ 10 Instagram videos (Reels with trending hashtags)</li>
                <li>✅ Automatic scheduling across all platforms</li>
                <li>✅ AI-generated captions and hashtags</li>
                <li>✅ Analytics tracking and ROI measurement</li>
              </ul>
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? '⏳ Creating Campaign...' : '🚀 Generate Campaign (20 Videos)'}
            </button>
          </form>
        </div>
      )}

      <div className="campaigns-grid">
        {campaigns.length === 0 ? (
          <div className="empty-state">
            <p>No campaigns yet. Create your first campaign to get started!</p>
          </div>
        ) : (
          campaigns.map(campaign => (
            <div key={campaign.id} className={`campaign-card status-${campaign.status}`}>
              <div className="card-header">
                <h3>{campaign.product_title}</h3>
                <span className={`status-badge ${campaign.status}`}>{campaign.status.toUpperCase()}</span>
              </div>

              <div className="card-body">
                <div className="campaign-stat">
                  <label>TikTok Videos</label>
                  <p>{campaign.videos.tiktok.count}</p>
                </div>
                <div className="campaign-stat">
                  <label>Instagram Videos</label>
                  <p>{campaign.videos.instagram.count}</p>
                </div>
                <div className="campaign-stat">
                  <label>Budget</label>
                  <p>${campaign.budget.toFixed(2)}</p>
                </div>
                <div className="campaign-stat">
                  <label>Impressions</label>
                  <p>{campaign.analytics?.impressions || 0}</p>
                </div>
              </div>

              <div className="card-footer">
                <button 
                  className="btn-secondary"
                  onClick={() => handleViewCampaignVideos(campaign.id)}
                >
                  📹 View Videos
                </button>
                {campaign.status === 'draft' && (
                  <button 
                    className="btn-primary"
                    onClick={() => handleActivateCampaign(campaign.id)}
                    disabled={loading}
                  >
                    🚀 Activate
                  </button>
                )}
                {campaign.status === 'active' && (
                  <span className="status-active">✅ LIVE</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
