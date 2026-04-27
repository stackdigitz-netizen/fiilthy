import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Bot, Bell, ChevronRight, CheckCircle, AlertCircle,
  TrendingUp, Package, Zap, ExternalLink, X,
  Sparkles, Target, DollarSign, Clock
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const AIAssistant = ({ onClose, onAction }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [publishingGuide, setPublishingGuide] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    fetchStatus();
    fetchNotifications();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API}/assistant/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
    setLoading(false);
  };

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`${API}/assistant/notifications?unread_only=true`);
      setNotifications(response.data.notifications || []);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const fetchPublishingGuide = async (productId) => {
    try {
      const response = await axios.get(`${API}/assistant/publishing-guide/${productId}`);
      setPublishingGuide(response.data);
      setSelectedProduct(productId);
    } catch (error) {
      console.error('Error fetching publishing guide:', error);
    }
  };

  const handleAction = (action) => {
    if (onAction) onAction(action);
    if (action === 'open_vault' || action === 'open_hunter') {
      onClose();
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'border-red-500 bg-red-500/10',
      medium: 'border-yellow-500 bg-yellow-500/10',
      low: 'border-blue-500 bg-blue-500/10'
    };
    return colors[priority] || 'border-gray-500 bg-gray-500/10';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="text-center">
          <Bot size={48} className="mx-auto mb-4 text-purple-400 animate-pulse" />
          <p>Loading assistant...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden border border-white/20">
        {/* Header */}
        <div className="bg-gradient-to-r from-violet-600 to-purple-600 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
                <Bot size={28} className="text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Atlas</h2>
                <p className="text-white/70 text-sm">{status?.greeting}</p>
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
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {/* Quick Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white/5 rounded-xl p-4 text-center">
              <Package className="mx-auto mb-2 text-blue-400" size={24} />
              <p className="text-2xl font-bold">{status?.summary?.total_products || 0}</p>
              <p className="text-xs text-gray-400">Products</p>
            </div>
            <div className="bg-white/5 rounded-xl p-4 text-center">
              <Target className="mx-auto mb-2 text-orange-400" size={24} />
              <p className="text-2xl font-bold">{status?.summary?.active_opportunities || 0}</p>
              <p className="text-xs text-gray-400">Opportunities</p>
            </div>
            <div className="bg-white/5 rounded-xl p-4 text-center">
              <Sparkles className="mx-auto mb-2 text-purple-400" size={24} />
              <p className="text-2xl font-bold">{status?.summary?.agent_teams || 0}</p>
              <p className="text-xs text-gray-400">AI Teams</p>
            </div>
            <div className="bg-white/5 rounded-xl p-4 text-center">
              <Clock className="mx-auto mb-2 text-yellow-400" size={24} />
              <p className="text-2xl font-bold">{status?.summary?.unpublished_products || 0}</p>
              <p className="text-xs text-gray-400">To Publish</p>
            </div>
          </div>

          {/* Alerts */}
          {status?.alerts?.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <Bell size={20} className="text-yellow-400" />
                Alerts
              </h3>
              <div className="space-y-2">
                {status.alerts.map((alert, idx) => (
                  <div
                    key={idx}
                    className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center gap-3"
                  >
                    <span className="text-2xl">{alert.icon}</span>
                    <div className="flex-1">
                      <p className="font-medium">{alert.message}</p>
                      <p className="text-sm text-gray-400">{alert.action}</p>
                    </div>
                    <ChevronRight size={20} className="text-gray-500" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {status?.recommendations?.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <Zap size={20} className="text-blue-400" />
                Recommendations
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {status.recommendations.map((rec, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAction(rec.action)}
                    className={`text-left p-4 rounded-xl border-l-4 transition-all hover:scale-[1.02] ${getPriorityColor(rec.priority)}`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{rec.icon}</span>
                      <div>
                        <p className="font-semibold">{rec.title}</p>
                        <p className="text-sm text-gray-400">{rec.description}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Publishing Guide */}
          {publishingGuide && (
            <div className="mb-6 bg-white/5 border border-white/10 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Publishing Guide</h3>
                <button onClick={() => setPublishingGuide(null)} className="text-gray-400 hover:text-white">
                  <X size={20} />
                </button>
              </div>
              
              <div className="mb-4 p-4 bg-black/20 rounded-lg">
                <p className="font-medium">{publishingGuide.product?.title}</p>
                <p className="text-sm text-gray-400">Type: {publishingGuide.product?.type} • Price: ${publishingGuide.product?.price}</p>
              </div>

              {/* Automated */}
              {publishingGuide.publishing_options?.automated?.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-semibold text-green-400 mb-2 flex items-center gap-2">
                    <CheckCircle size={16} />
                    Automated ({publishingGuide.publishing_options.automated.length})
                  </p>
                  <div className="space-y-2">
                    {publishingGuide.publishing_options.automated.map(platform => (
                      <div key={platform.id} className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <p className="font-medium">{platform.name}</p>
                          <span className="text-xs text-green-400">Auto-publish</span>
                        </div>
                        <p className="text-xs text-gray-400 mt-1">{platform.instructions}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Manual */}
              {publishingGuide.publishing_options?.manual?.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-yellow-400 mb-2 flex items-center gap-2">
                    <AlertCircle size={16} />
                    Manual Required ({publishingGuide.publishing_options.manual.length})
                  </p>
                  <div className="space-y-2">
                    {publishingGuide.publishing_options.manual.map(platform => (
                      <div key={platform.id} className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <p className="font-medium">{platform.name}</p>
                          <span className="text-xs text-yellow-400">{platform.time}</span>
                        </div>
                        <p className="text-xs text-gray-400 mt-1">{platform.instructions}</p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-gray-500">Fees: {platform.fees}</span>
                          {platform.url && (
                            <a
                              href={platform.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-400 hover:underline flex items-center gap-1"
                            >
                              Open <ExternalLink size={12} />
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Recent Activity */}
          {status?.recent_activity?.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <TrendingUp size={20} className="text-green-400" />
                Recent Activity
              </h3>
              <div className="space-y-2">
                {status.recent_activity.map((activity, idx) => (
                  <div
                    key={idx}
                    className="bg-white/5 rounded-lg p-3 flex items-center justify-between cursor-pointer hover:bg-white/10 transition-all"
                    onClick={() => activity.type === 'product' && fetchPublishingGuide(activity.id || activity.title)}
                  >
                    <div className="flex items-center gap-3">
                      <Package size={18} className="text-blue-400" />
                      <div>
                        <p className="font-medium text-sm">{activity.title}</p>
                        <p className="text-xs text-gray-500">{activity.status}</p>
                      </div>
                    </div>
                    <span className="text-xs text-gray-500">
                      {activity.time ? new Date(activity.time).toLocaleDateString() : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-white/10 p-4 bg-black/20">
          <p className="text-center text-sm text-gray-500">
            💡 Click on any product to see where you can publish it
          </p>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
