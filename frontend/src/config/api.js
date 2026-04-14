/**
 * Centralized API configuration.
 * All pages should import API_URL from here.
 */
const PRODUCTION_API_URL = 'https://fiilthy-ai-backend-2ni1ra3dm-stackdigitz-5790s-projects.vercel.app';

const API_URL = process.env.REACT_APP_BACKEND_URL
  || (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : PRODUCTION_API_URL);

export default API_URL;
