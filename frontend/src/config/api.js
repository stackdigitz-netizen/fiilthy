/**
 * Centralized API configuration.
 * All pages should import API_URL from here.
 */
const PRODUCTION_API_URL = 'https://ceo-backend-production.up.railway.app';
const LOCAL_API_URL = 'http://localhost:8000';

const API_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
  ? LOCAL_API_URL
  : PRODUCTION_API_URL;

export default API_URL;
