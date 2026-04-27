import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import API_URL from '../config/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state from localStorage and verify with backend
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('authToken');
      
      if (storedToken) {
        try {
          // Verify token is still valid by calling /me endpoint
          const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${storedToken}`
            }
          });
          
          if (response.ok) {
            // Token is valid, load fresh user data from backend
            const userData = await response.json();
            setToken(storedToken);
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
          } else {
            // Token is invalid/expired, clear it
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
          }
        } catch (e) {
          console.error('Failed to verify auth token:', e);
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = (token, user) => {
    setToken(token);
    setUser(user);
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  };

  // SAAS: Refresh user data from backend (called after upgrades)
  const refreshUser = useCallback(async () => {
    const storedToken = localStorage.getItem('authToken');
    if (!storedToken) return;
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${storedToken}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
      }
    } catch (e) {
      console.error('Failed to refresh user:', e);
    }
  }, []);

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, login, logout, loading, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
