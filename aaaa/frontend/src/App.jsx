import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import AuthCallbackPage from './pages/AuthCallbackPage';
import SignupPage from './pages/SignupPage';
import LandingPage from './pages/LandingPage';
import LegalPage from './pages/LegalPage';
import CommandCenterPage from './pages/CommandCenterPage';
import ApprovalQueuePage from './pages/ApprovalQueuePage';
import AnalyticsPage from './pages/AnalyticsPage';
import VaultPage from './pages/VaultPage';
import SettingsPage from './pages/SettingsPage';
import StorePage from './pages/StorePage';
import ProductsPage from './pages/ProductsPage';
import ProjectsPage from './pages/ProjectsPage';
import ProductLaunchPage from './pages/ProductLaunchPage';
import SocialMediaPage from './pages/SocialMediaPage';
import GrowthPage from './pages/GrowthPage';
import SuccessPage from './pages/SuccessPage';
import './App.css';

const AUTHENTICATED_PATHS = [
  '/products',
  '/projects',
  '/launch',
  '/social-media',
  '/growth',
  '/approvals',
  '/analytics',
  '/vault',
  '/settings'
];

const buildLoginRedirect = (path) => `/login?next=${encodeURIComponent(path)}`;

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '20px' }}>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/store" element={<StorePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/success" element={<SuccessPage />} />
        {AUTHENTICATED_PATHS.map((path) => (
          <Route key={path} path={path} element={<Navigate to={buildLoginRedirect(path)} replace />} />
        ))}
        <Route path="/:page" element={<LegalPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<CommandCenterPage />} />
        <Route path="/store" element={<StorePage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/launch" element={<ProductLaunchPage />} />
        <Route path="/social-media" element={<SocialMediaPage />} />
        <Route path="/growth" element={<GrowthPage />} />
        <Route path="/approvals" element={<ApprovalQueuePage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/vault" element={<VaultPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/success" element={<SuccessPage />} />
        <Route path="/billing/success" element={<CommandCenterPage />} />
        <Route path="/billing/cancel" element={<CommandCenterPage />} />

        <Route path="/:page" element={<LegalPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
