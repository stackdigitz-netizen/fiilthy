import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import LandingPage from './pages/LandingPage';
import LegalPage from './pages/LegalPage';
import CommandCenterPage from './pages/CommandCenterPage';
import ApprovalQueuePage from './pages/ApprovalQueuePage';
import AnalyticsPage from './pages/AnalyticsPage';
import VaultPage from './pages/VaultPage';
import SettingsPage from './pages/SettingsPage';
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
        <Route path="/" element={<CommandCenterPage />} />
        <Route path="/approvals" element={<ApprovalQueuePage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/vault" element={<VaultPage />} />
        <Route path="/settings" element={<SettingsPage />} />
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
