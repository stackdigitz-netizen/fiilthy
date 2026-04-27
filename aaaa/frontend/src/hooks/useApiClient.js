import { useCallback } from 'react';
import API_URL from '../config/api';

/**
 * Hook that returns an authenticated fetch function.
 * Automatically attaches the Bearer token and API base URL.
 * 
 * SAAS: Handles LIMIT_REACHED responses by dispatching a global event.
 *
 * Usage:
 *   const fetchApi = useApiClient();
 *   const res = await fetchApi('/api/products');
 */
export default function useApiClient() {
  return useCallback(async (path, options = {}) => {
    const token = localStorage.getItem('authToken');
    const url = path.startsWith('http') ? path : `${API_URL}${path}`;

    const headers = { ...(options.headers || {}) };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, { ...options, headers });

    // SAAS: Handle usage limit exceeded
    if (response.status === 403) {
      try {
        const data = await response.clone().json();
        if (data.detail === 'LIMIT_REACHED') {
          window.dispatchEvent(new CustomEvent('LIMIT_REACHED', {
            detail: { message: data.message || 'You have reached your plan limit. Upgrade to continue.' }
          }));
          throw new Error('LIMIT_REACHED');
        }
      } catch (e) {
        if (e.message === 'LIMIT_REACHED') throw e;
      }
    }

    return response;
  }, []);
}
