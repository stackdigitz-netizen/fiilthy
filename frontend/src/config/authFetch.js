import API_URL from './api';

/**
 * Authenticated fetch wrapper.
 * Automatically attaches the Bearer token from localStorage and
 * prepends the API_URL to relative paths.
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

  return fetch(url, { ...options, headers });
}

export { API_URL };
