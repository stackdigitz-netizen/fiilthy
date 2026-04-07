import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
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
  Share2
} from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

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
    { name: 'Settings', href: '/settings', icon: Settings }
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="logo-icon">AI</div>
            {sidebarOpen && <div className="logo-text">Factory</div>}
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
          {sidebarOpen && <p className="text-xs text-gray-500">v5.0 Production</p>}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="top-bar">
          <div className="top-bar-left">
            <button
              className="menu-button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
          <div className="top-bar-right">
            <div className="status-badge">
              <span className="status-dot"></span>
              Active
            </div>
          </div>
        </header>

        <div className="page-container">{children}</div>
      </main>
    </div>
  );
};

export default Layout;
