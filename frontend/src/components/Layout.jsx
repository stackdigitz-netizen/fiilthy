import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import BrandLogo from './BrandLogo';
import './Layout.css';
import {
  Menu, X, Cpu, Bell, LineChart, Shield, Settings, ShoppingBag, Package, FolderOpen, Rocket, Share2, TrendingUp,
} from 'lucide-react';
import API_URL from '../config/api';

const API = API_URL;

const Layout = ({ children }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') return true;
    return window.innerWidth > 768;
  });
  const [pendingApprovals, setPendingApprovals] = useState(0);
  const { user, logout } = useAuth();

  useEffect(() => {
    const handleResize = () => setSidebarOpen(window.innerWidth > 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined' && window.innerWidth <= 768) setSidebarOpen(false);
  }, [location.pathname]);

  // Poll pending approvals for badge
  useEffect(() => {
    const fetchBadge = async () => {
      try {
        const t = localStorage.getItem('authToken');
        const res = await fetch(`${API}/api/agents/metrics`, {
          headers: t ? { Authorization: `Bearer ${t}` } : {},
        });
        if (res.ok) {
          const data = await res.json();
          setPendingApprovals(data.pending_approvals || 0);
        }
      } catch (_) { /* offline */ }
    };
    fetchBadge();
    const interval = setInterval(fetchBadge, 10000);
    return () => clearInterval(interval);
  }, []);

  const navigation = [
    { name: 'Command Center', href: '/',          icon: Cpu },
    { name: 'Approvals',      href: '/approvals', icon: Bell,      badge: pendingApprovals },
    { name: 'Products',       href: '/products',  icon: Package },
    { name: 'Projects',       href: '/projects',  icon: FolderOpen },
    { name: 'Launch',         href: '/launch',    icon: Rocket },
    { name: 'Social',         href: '/social-media', icon: Share2 },
    { name: 'Growth',         href: '/growth',    icon: TrendingUp },
    { name: 'Store',          href: '/store',     icon: ShoppingBag },
    { name: 'Analytics',      href: '/analytics', icon: LineChart },
    { name: 'Vault',          href: '/vault',      icon: Shield },
    { name: 'Settings',       href: '/settings',  icon: Settings },
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <BrandLogo variant={sidebarOpen ? 'full' : 'icon'} theme="light" size="sm" />
          </div>
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="sidebar-nav">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`nav-link ${active ? 'active' : ''}`}
                title={!sidebarOpen ? item.name : ''}
              >
                <span style={{ position: 'relative', display: 'flex' }}>
                  <Icon size={20} />
                  {item.badge > 0 && (
                    <span style={{
                      position: 'absolute', top: -5, right: -6,
                      background: '#ff6d00', color: '#000',
                      fontSize: 9, fontWeight: 700, borderRadius: 8,
                      padding: '1px 4px', lineHeight: '14px',
                    }}>
                      {item.badge}
                    </span>
                  )}
                </span>
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          {sidebarOpen && <p className="text-xs text-gray-500">FiiLTHY.ai Digital Empire</p>}
        </div>
      </aside>

      {sidebarOpen && <button className="sidebar-overlay" type="button" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}

      {/* Main Content */}
      <main className="main-content">
        <header className="top-bar">
          <div className="top-bar-left">
            <button
              className="menu-button"
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
          <div className="top-bar-right">
            <div className="user-badge">{user?.email || 'Signed in'}</div>
            <div className="status-badge">
              <span className="status-dot"></span>
              LIVE
            </div>
            <button className="logout-button" type="button" onClick={logout}>Logout</button>
          </div>
        </header>

        <div className="page-container">{children}</div>
      </main>
    </div>
  );
};

export default Layout;
