import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import LandingPage from './pages/LandingPage';
import LegalPage from './pages/LegalPage';
import Dashboard from './pages/Dashboard';
import OpportunitiesPage from './pages/OpportunitiesPage';
import ProductsPage from './pages/ProductsPage';
import BrandingPage from './pages/BrandingPage';
import ContentPage from './pages/ContentPage';
import SalesPage from './pages/SalesPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AutomationPage from './pages/AutomationPage';
import GrowthPage from './pages/GrowthPage';
import SocialMediaPage from './pages/SocialMediaPage';
import SettingsPage from './pages/SettingsPage';
import VaultPage from './pages/VaultPage';
import AssistantPage from './pages/AssistantPage';
import HunterPage from './pages/HunterPage';
import ProjectsPage from './pages/ProjectsPage';
import './App.css';

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '20px' }}>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/:page" element={<LegalPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/opportunities" element={<OpportunitiesPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/branding" element={<BrandingPage />} />
        <Route path="/content" element={<ContentPage />} />
        <Route path="/sales" element={<SalesPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/automation" element={<AutomationPage />} />
        <Route path="/growth" element={<GrowthPage />} />
        <Route path="/social-media" element={<SocialMediaPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/vault" element={<VaultPage />} />
        <Route path="/assistant" element={<AssistantPage />} />
        <Route path="/hunter" element={<HunterPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
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
