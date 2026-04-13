import { useCallback } from 'react';
import API_URL from '../config/api';

/**
 * Hook that returns an authenticated fetch function.
 * Automatically attaches the Bearer token and API base URL.
 *
 * Usage:
 *   const fetchApi = useApiClient();
 *   const res = await fetchApi('/api/products');
 */
export default function useApiClient() {
  return useCallback((path, options = {}) => {
    const token = localStorage.getItem('authToken');
    const url = path.startsWith('http') ? path : `${API_URL}${path}`;

    const headers = { ...(options.headers || {}) };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    return fetch(url, { ...options, headers });
  }, []);
}
