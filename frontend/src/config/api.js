/**
 * Centralized API configuration.
 * All pages should import API_URL from here.
 */
const API_URL = process.env.REACT_APP_BACKEND_URL
  || (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://ceo-1-34jx.onrender.com');

export default API_URL;
