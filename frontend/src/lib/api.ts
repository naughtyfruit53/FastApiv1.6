// Revised: frontend/src/lib/api.ts
import axios from "axios";
import { toast } from "react-toastify";
// API base URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
// Token expiry handling with state preservation
const handleTokenExpiry = () => {
  console.log("[API] Handling token expiry - preserving application state");
  // Store current location for redirect after login
  const currentPath = window.location.pathname;
  const currentSearch = window.location.search;
  const currentHash = window.location.hash;
  const returnUrl = `${currentPath}${currentSearch}${currentHash}`;
  // Store form data if available (attempt to preserve form state)
  try {
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
      console.log("[API] Preserved form data before logout");
    }
  } catch (error) {
    console.warn("[API] Could not preserve form data:", error);
  }
  // Store return URL for redirect after successful login
  if (returnUrl !== "/" && !returnUrl.includes("/login")) {
    sessionStorage.setItem("returnUrlAfterLogin", returnUrl);
    console.log("[API] Stored return URL:", returnUrl);
  }
  // Clear auth data
  localStorage.removeItem("token");
  localStorage.removeItem("user_role");
  localStorage.removeItem("is_super_admin");
  // Reset auth ready state
  resetAuthReady();
  // Add a small delay to allow logging and toast to complete, then redirect to login
  setTimeout(() => {
    window.location.href = "/login";
  }, 100);
};
// Auth state management for request queuing
let isAuthReady = false;
let authReadyPromise: Promise<void> | null = null;
let authReadyResolve: (() => void) | null = null;
// Initialize auth ready promise
const initializeAuthPromise = () => {
  if (!authReadyPromise) {
    authReadyPromise = new Promise((resolve) => {
      authReadyResolve = resolve;
    });
  }
};
initializeAuthPromise();
// Mark auth as ready (called from AuthContext)
export const markAuthReady = (): any => {
  console.log("[API] Auth context marked as ready");
  isAuthReady = true;
  if (authReadyResolve) {
    authReadyResolve();
    authReadyResolve = null;
  }
};
// Reset auth ready state (called on logout)
export const resetAuthReady = (): any => {
  console.log("[API] Auth context reset");
  isAuthReady = false;
  initializeAuthPromise();
};
// Wait for auth to be ready for protected endpoints
const waitForAuthIfNeeded = async (config: any) => {
  // Skip auth waiting for public endpoints
  const publicEndpoints = ["/auth/login", "/auth/otp/", "/auth/admin/setup"];
  const isPublicEndpoint = publicEndpoints.some((endpoint) =>
    config.url?.includes(endpoint),
  );
  if (isPublicEndpoint) {
    console.log("[API] Public endpoint, skipping auth wait:", config.url);
    return;
  }
  // Wait for auth context if not ready, with timeout to prevent deadlocks
  if (!isAuthReady && authReadyPromise) {
    console.log("[API] Waiting for auth context to be ready for:", config.url);
    // Add timeout to prevent infinite waiting
    const authTimeout = new Promise<void>((_, reject) => {
      setTimeout(() => {
        console.warn(
          "[API] Auth wait timeout - proceeding without auth ready state",
        );
        reject(new Error("Auth wait timeout"));
      }, 10000); // 10 second timeout
    });
    try {
      await Promise.race([authReadyPromise, authTimeout]);
      console.log(
        "[API] Auth context ready, proceeding with request:",
        config.url,
      );
    } catch (error: any) {
      console.warn(
        "[API] Auth wait failed or timed out, proceeding anyway:",
        error?.message || error,
      );
      // Continue with request even if auth wait fails
    }
  }
};
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});
// Add token to requests - organization context derived from backend session
api.interceptors.request.use(
  async (config) => {
    // Wait for auth context if needed before proceeding
    await waitForAuthIfNeeded(config);
    const token = localStorage.getItem("token");
    // Debug logging for all requests
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
      hasToken: !!token,
      authReady: isAuthReady,
      timestamp: new Date().toISOString(),
      note: "Organization context derived from backend session",
    });
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Log the full request URL for debugging 404 issues
    const fullUrl = `${config.baseURL}${config.url}`;
    console.log(`[API] Request URL: ${fullUrl}`, {
      method: config.method?.toUpperCase(),
      hasAuth: !!token,
    });
    return config;
  },
  (error) => {
    console.error("[API] Request interceptor error:", error);
    return Promise.reject(error);
  },
);
// Handle token expiration and network errors with enhanced debugging and refresh
api.interceptors.response.use(
  (response) => {
    // Log successful responses for protected endpoints
    if (response.config.headers?.Authorization) {
      console.log(
        `[API] Success ${response.config.method?.toUpperCase()} ${response.config.url}`,
        {
          status: response.status,
          hasData: !!response.data,
          timestamp: new Date().toISOString(),
        },
      );
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const method = error.config?.method?.toUpperCase();
    const url = error.config?.url;
    const status = error.response?.status;
    console.error(`[API] Error ${method} ${url}`, {
      status,
      error: error.response?.data,
      timestamp: new Date().toISOString(),
    });
    if ((status === 401 || status === 403) && !originalRequest._retry) {
      if (originalRequest.headers?.Authorization) {
        // Only handle as expired token if it had one
        console.log(`[API] ${status} Auth error - attempting token refresh`);
        originalRequest._retry = true;
        try {
          // Import authService here to avoid circular dependency
          const { authService } = await import("../services/authService");
          // Check if we have a refresh token
          const refreshToken = localStorage.getItem("refresh_token");
          if (!refreshToken) {
            throw new Error("No refresh token available");
          }
          // Use authService's refresh method
          const refreshData = await authService.refreshToken();
          console.log("[API] Token refreshed successfully");
          // Update original request with new token and retry
          originalRequest.headers.Authorization = `Bearer ${refreshData.access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          console.error("[API] Token refresh failed:", refreshError);
          // Show specific error message if available before redirect
          const errorDetail = error.response?.data?.detail;
          if (errorDetail && typeof errorDetail === "string") {
            console.log(`[API] ${status} Error reason:`, errorDetail);
            // Show toast notification with error reason before redirect
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
          // Store current location and form state before logout
          handleTokenExpiry();
        }
      } else {
        // No token: Just log and reject (don't refresh or reset auth)
        console.log(`[API] ${status} Error - No token present, not refreshing`);
        return Promise.reject(error);
      }
    } else if (status === 404 && url?.includes("/companies/current")) {
      // Special handling for company missing scenario - DO NOT logout
      console.log(
        "[API] 404 on /companies/current - company setup required, not an auth error",
      );
      // Add a flag to indicate this is a company setup scenario
      const enhancedError = {
        ...error,
        isCompanySetupRequired: true,
        userMessage: "Company setup required",
      };
      // Don't clear auth data or redirect - let the component handle company onboarding
      return Promise.reject(enhancedError);
    }
    // Extract error message with proper handling for arrays and objects
    let errorMessage = "An unexpected error occurred";
    const detail = error.response?.data?.detail;
    const message = error.response?.data?.message;
    if (typeof detail === "string" && detail) {
      errorMessage = detail;
    } else if (typeof message === "string" && message) {
      errorMessage = message;
    } else if (Array.isArray(detail) && detail.length > 0) {
      // Handle Pydantic validation errors (array of objects)
      const messages = detail
        .map((err) => err.msg || `${err.loc?.join(" -> ")}: ${err.type}`)
        .filter(Boolean);
      errorMessage =
        messages.length > 0 ? messages.join(", ") : "Validation error";
    } else if (detail && typeof detail === "object") {
      // Handle object error details
      errorMessage = detail.error || detail.message || JSON.stringify(detail);
    } else if (error.message) {
      errorMessage = error.message;
    }
    console.error("[API] Processed error message:", errorMessage);
    return Promise.reject({
      ...error,
      userMessage: errorMessage,
      status: status,
    });
  },
);
export default api;
