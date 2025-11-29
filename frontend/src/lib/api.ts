// frontend/src/lib/api.ts
import axios from "axios";
import { toast } from "react-toastify";
import axiosRetry from 'axios-retry';
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, USER_ROLE_KEY, IS_SUPER_ADMIN_KEY, LEGACY_TOKEN_KEY } from '../constants/auth';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
/**
 * Helper function to get access token with backward compatibility
 * Checks for new key first, then falls back to legacy key
 */
const getAccessToken = (): string | null => {
  let token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (!token) {
    // Check legacy key for backward compatibility
    token = localStorage.getItem(LEGACY_TOKEN_KEY);
    if (token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      localStorage.removeItem(LEGACY_TOKEN_KEY);
    }
  }
  return token;
};
/**
 * Helper function to get refresh token
 */
const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};
// Configure axios-retry with exponential backoff
axiosRetry(axios, {
  retries: 3,
  retryDelay: (retryCount) => {
    return axiosRetry.exponentialDelay(retryCount);
  },
  retryCondition: (error) => {
    return axiosRetry.isNetworkOrIdempotentRequestError(error) || error.response?.status >= 500;
  },
});
const handleTokenExpiry = () => {
  const currentPath = window.location.pathname;
  const currentSearch = window.location.search;
  const currentHash = window.location.hash;
  const returnUrl = `${currentPath}${currentSearch}${currentHash}`;
  const forms = document.querySelectorAll("form");
  const formData: { [key: string]: any } = {};
  forms.forEach((form, index) => {
    const formDataObj = new FormData(form);
    const formEntries: { [key: string]: any } = {};
    for (const [key, value] of formDataObj.entries()) {
      if (typeof value === "string" && value.trim()) {
        formEntries[key] = value;
      }
    }
    if (Object.keys(formEntries).length > 0) {
      formData[`form_${index}`] = formEntries;
    }
  });
  if (Object.keys(formData).length > 0) {
    sessionStorage.setItem("formDataBeforeExpiry", JSON.stringify(formData));
  }
  if (returnUrl !== "/" && !returnUrl.includes("/login")) {
    sessionStorage.setItem("returnUrlAfterLogin", returnUrl);
  }
  // Clear all token-related storage using standardized keys
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(LEGACY_TOKEN_KEY); // Also clear legacy key
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_ROLE_KEY);
  localStorage.removeItem(IS_SUPER_ADMIN_KEY);
  resetAuthReady();
  setTimeout(() => {
    window.location.href = "/login";
  }, 100);
};
let isAuthReady = false;
let authReadyPromise: Promise<void> | null = null;
let authReadyResolve: (() => void) | null = null;
const initializeAuthPromise = () => {
  if (!authReadyPromise) {
    authReadyPromise = new Promise((resolve) => {
      authReadyResolve = resolve;
    });
  }
};
initializeAuthPromise();
export const markAuthReady = (): any => {
  isAuthReady = true;
  if (authReadyResolve) {
    authReadyResolve();
    authReadyResolve = null;
  }
};
export const resetAuthReady = (): any => {
  isAuthReady = false;
  initializeAuthPromise();
};
const waitForAuthIfNeeded = async (config: any) => {
  const publicEndpoints = [
    "/auth/login",
    "/auth/otp/",
    "/auth/admin/setup",
    "/users/me",
    "/organizations/current",
    "/rbac/users/users/permissions",
    "/companies/current",
    "/organizations/org-statistics",
    "/organizations/recent-activities",
  ];
  const isPublicEndpoint = publicEndpoints.some((endpoint) =>
    config.url?.includes(endpoint),
  );
  if (isPublicEndpoint) {
    return;
  }
  if (!isAuthReady && authReadyPromise) {
    const timeoutPromise = new Promise<void>((_, reject) => {
      setTimeout(() => reject(new Error("Auth wait timeout")), 10000);
    });
    try {
      await Promise.race([authReadyPromise, timeoutPromise]);
    } catch (error: any) {
    }
  }
};
const refreshAxios = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 90000,
  withCredentials: true, // Enable sending cookies with cross-origin requests
});
axiosRetry(refreshAxios, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error) => {
    return axiosRetry.isNetworkOrIdempotentRequestError(error) || error.response?.status >= 500;
  },
});
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 90000,
  withCredentials: true, // Enable sending cookies with cross-origin requests
});
api.interceptors.request.use(
  async (config) => {
    await waitForAuthIfNeeded(config);
    const token = getAccessToken();
    if (token && token !== 'undefined' && token.split('.').length === 3) {
      config.headers.Authorization = `Bearer ${token}`;
    } else if (token) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const method = error.config?.method?.toUpperCase();
    const url = error.config?.url;
    const status = error.response?.status;
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      toast.error("Request timed out. Please try again.", {
        position: "top-right",
        autoClose: 3000,
      });
    }
   
    // Handle 403 Forbidden - Permission Denied
    if (status === 403) {
      const data = error.response?.data;
      const requiredPermission = data?.required_permission || 'unknown';
      const module = data?.module || 'this resource';
      const action = data?.action || 'perform this action';
     
      // Show user-friendly error message
      toast.error(
        `Access Denied: You don't have permission to ${action} on ${module}. ` +
        `Required permission: ${requiredPermission}. ` +
        `Please contact your administrator to request access.`,
        {
          position: "top-right",
          autoClose: 5000,
        }
      );
     
      // Return the error with enhanced information for component handling
      return Promise.reject({
        ...error,
        isPermissionDenied: true,
        requiredPermission,
        module,
        action,
        userMessage: `You don't have permission to ${action} on ${module}`,
      });
    }
   
    if (status === 401 && !originalRequest._retry) {
      if (originalRequest.headers?.Authorization) {
        originalRequest._retry = true;
        try {
          const refreshToken = getRefreshToken();
          if (!refreshToken) {
            throw new Error("No refresh token available");
          }
          const response = await refreshAxios.post('/api/v1/auth/refresh-token', {
            refresh_token: refreshToken
          });
          const refreshData = response.data;
          localStorage.setItem(ACCESS_TOKEN_KEY, refreshData.access_token);
          if (refreshData.refresh_token) {
            localStorage.setItem(REFRESH_TOKEN_KEY, refreshData.refresh_token);
          }
          originalRequest.headers.Authorization = `Bearer ${refreshData.access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          const errorDetail = error.response?.data?.detail;
          if (errorDetail && typeof errorDetail === "string") {
            toast.error(`Session expired: ${errorDetail}`, {
              position: "top-right",
              autoClose: 3000,
            });
          } else {
            toast.error("Session expired. Please login again.", {
              position: "top-right",
              autoClose: 3000,
            });
          }
          handleTokenExpiry();
        }
      } else {
        return Promise.reject(error);
      }
    } else if (status === 404 && url?.includes("/companies/current")) {
      const enhancedError = {
        ...error,
        isCompanySetupRequired: true,
        userMessage: "Company setup required",
      };
      return Promise.reject(enhancedError);
    }
    let errorMessage = "An unexpected error occurred";
    const detail = error.response?.data?.detail;
    const message = error.response?.data?.message;
    if (typeof detail === "string" && detail) {
      errorMessage = detail;
    } else if (typeof message === "string" && message) {
      errorMessage = message;
    } else if (Array.isArray(detail) && detail.length > 0) {
      const messages = detail
        .map((err) => err.msg || `${err.loc?.join(" -> ")}: ${err.type}`)
        .filter(Boolean);
      errorMessage =
        messages.length > 0 ? messages.join(", ") : "Validation error";
    } else if (detail && typeof detail === "object") {
      errorMessage = detail.error || detail.message || JSON.stringify(detail);
    } else if (error.message) {
      errorMessage = error.message;
    }
    return Promise.reject({
      ...error,
      userMessage: errorMessage,
      status,
    });
  },
);
export default api;
