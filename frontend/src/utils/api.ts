// fastapi_migration/frontend/src/utils/api.ts

import axios from "axios";
import { ACCESS_TOKEN_KEY, LEGACY_TOKEN_KEY } from "../constants/auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Helper function to get access token with backward compatibility
 */
const getAccessToken = (): string | null => {
  let token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (!token) {
    // Check legacy key for backward compatibility
    token = localStorage.getItem(LEGACY_TOKEN_KEY);
    if (token) {
      console.log('[utils/api] Migrating token from legacy key to new key');
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      localStorage.removeItem(LEGACY_TOKEN_KEY);
    }
  }
  return token;
};

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests - organization context derived from backend session
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    console.log(`[utils/api] Request interceptor: ${config.method?.toUpperCase()} ${config.url}`, {
      hasToken: !!token,
      timestamp: new Date().toISOString(),
    });
    // Skip adding token for auth-related endpoints
    const publicEndpoints = [
      "/auth/login",
      "/auth/login/email",
      "/auth/otp/request",
      "/auth/otp/verify",
      "/auth/refresh-token",
      "/password/forgot",
      "/password/reset",
    ];

    const isPublic = publicEndpoints.some((endpoint) =>
      config.url?.includes(endpoint),
    );

    if (token && !isPublic) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Organization context is derived from backend session, not headers
    return config;
  },
  (error) => {
    console.error("[utils/api] Request interceptor error:", error);
    return Promise.reject(error);
  },
);

// Handle token expiration
api.interceptors.response.use(
  (response) => {
    console.log(`[utils/api] Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      timestamp: new Date().toISOString(),
    });
    return response;
  },
  (error) => {
    console.error(`[utils/api] Response error: ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
      status: error.response?.status,
      detail: error.response?.data?.detail,
      timestamp: new Date().toISOString(),
    });
    // Skip automatic logout/redirect for public auth endpoints
    const publicEndpoints = [
      "/auth/login",
      "/auth/login/email",
      "/auth/otp/request",
      "/auth/otp/verify",
      "/auth/refresh-token",
      "/password/forgot",
      "/password/reset",
    ];

    const isPublic = publicEndpoints.some((endpoint) =>
      error.config?.url?.includes(endpoint),
    );

    if (error.response?.status === 401 && !isPublic) {
      console.log("[utils/api] 401 Unauthorized - clearing token and redirecting to login");
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(LEGACY_TOKEN_KEY);
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export default api;