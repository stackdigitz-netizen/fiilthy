import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
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

function App() {
  return (
    <Router>
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
    </Router>
  );
}

export default App;
