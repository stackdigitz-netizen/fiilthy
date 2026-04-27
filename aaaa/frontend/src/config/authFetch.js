import API_URL from './api';

/**
 * Authenticated fetch wrapper.
 * Automatically attaches the Bearer token from localStorage and
 * prepends the API_URL to relative paths.
 * 
 * SAAS: Also handles LIMIT_REACHED responses by dispatching a global event.
 */
export default async function authFetch(path, options = {}) {
  const token = localStorage.getItem('authToken');
  const url = path.startsWith('http') ? path : `${API_URL}${path}`;

  const headers = {
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Default to JSON content type for requests with a body
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, { ...options, headers });

  // SAAS: Handle usage limit exceeded
  if (response.status === 403) {
    try {
      const data = await response.clone().json();
      if (data.detail === 'LIMIT_REACHED') {
        // Dispatch global event so UI can show upgrade modal
        window.dispatchEvent(new CustomEvent('LIMIT_REACHED', {
          detail: { message: data.message || 'You have reached your plan limit. Upgrade to continue.' }
        }));
        throw new Error('LIMIT_REACHED');
      }
    } catch (e) {
      if (e.message === 'LIMIT_REACHED') throw e;
      // If JSON parsing fails, ignore and return original response
    }
  }

  return response;
}

export { API_URL };
