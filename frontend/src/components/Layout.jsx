import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';
import {
  Menu,
  X,
  BarChart3,
  Search,
  Package,
  Palette,
  TrendingUp,
  Zap,
  Settings,
  Lightbulb,
  LineChart,
  Share2,
  Shield,
  Bot,
  Radar,
  FolderOpen
} from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') {
      return true;
    }

    return window.innerWidth > 768;
  });
  const { user, logout } = useAuth();

  useEffect(() => {
    const handleResize = () => {
      setSidebarOpen(window.innerWidth > 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined' && window.innerWidth <= 768) {
      setSidebarOpen(false);
    }
  }, [location.pathname]);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Opportunities', href: '/opportunities', icon: Search },
    { name: 'Products', href: '/products', icon: Package },
    { name: 'Branding', href: '/branding', icon: Palette },
    { name: 'Content', href: '/content', icon: TrendingUp },
    { name: 'Sales', href: '/sales', icon: Zap },
    { name: 'Social Media', href: '/social-media', icon: Share2 },
    { name: 'Analytics', href: '/analytics', icon: LineChart },
    { name: 'Automation', href: '/automation', icon: Settings },
    { name: 'Growth Lab', href: '/growth', icon: Lightbulb },
    { name: 'Factory', href: '/factory', icon: Package },
    { name: 'Hunter', href: '/hunter', icon: Radar },
    { name: 'Projects', href: '/projects', icon: FolderOpen },
    { name: 'Atlas AI', href: '/assistant', icon: Bot },
    { name: 'Vault', href: '/vault', icon: Shield },
    { name: 'Settings', href: '/settings', icon: Settings }
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="logo-icon">F</div>
            {sidebarOpen && <div className="logo-text">FiiLTHY<span style={{color: '#e040fb'}}>.ai</span></div>}
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
                <Icon size={20} />
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
