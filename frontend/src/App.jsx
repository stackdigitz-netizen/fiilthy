import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
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
import './App.css';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '20px' }}>Loading...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '20px' }}>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
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
