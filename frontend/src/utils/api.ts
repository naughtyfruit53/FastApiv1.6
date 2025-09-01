// fastapi_migration/frontend/src/utils/api.ts

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests - organization context derived from backend session
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    // Skip adding token for auth-related endpoints
    const publicEndpoints = [
      '/auth/login',
      '/auth/login/email',
      '/auth/otp/request',
      '/auth/otp/verify',
      '/auth/refresh-token',
      '/password/forgot',
      '/password/reset'
    ];
    
    const isPublic = publicEndpoints.some(endpoint => config.url?.includes(endpoint));
    
    if (token && !isPublic) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Organization context is derived from backend session, not headers
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Skip automatic logout/redirect for public auth endpoints
    const publicEndpoints = [
      '/auth/login',
      '/auth/login/email',
      '/auth/otp/request',
      '/auth/otp/verify',
      '/auth/refresh-token',
      '/password/forgot',
      '/password/reset'
    ];
    
    const isPublic = publicEndpoints.some(endpoint => error.config?.url?.includes(endpoint));
    
    if (error.response?.status === 401 && !isPublic) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;