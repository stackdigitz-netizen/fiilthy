/**
 * Centralized API configuration.
 * All pages should import API_URL from here.
 */
const PRODUCTION_API_URL = 'https://adequate-respect-production-7ef0.up.railway.app';

const API_URL = process.env.REACT_APP_BACKEND_URL
  || (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : PRODUCTION_API_URL);

export default API_URL;
