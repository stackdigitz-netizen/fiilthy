/**
 * Centralized API configuration.
 * All pages should import API_URL from here.
 */
const PRODUCTION_API_URL = process.env.REACT_APP_BACKEND_URL || 'https://adequate-respect-production-7ef0.up.railway.app';
const LOCAL_API_URL = 'http://localhost:8000';

const API_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
  ? (process.env.REACT_APP_BACKEND_URL || LOCAL_API_URL)
  : PRODUCTION_API_URL;

export default API_URL;
