// frontend/src/lib/api.ts
import axios from "axios";
import { toast } from "react-toastify";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const handleTokenExpiry = () => {
  console.log("[API] Handling token expiry - preserving application state");
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
    console.log("[API] Preserved form data before logout");
  }
  if (returnUrl !== "/" && !returnUrl.includes("/login")) {
    sessionStorage.setItem("returnUrlAfterLogin", returnUrl);
    console.log("[API] Stored return URL:", returnUrl);
  }
  localStorage.removeItem("token");
  localStorage.removeItem("user_role");
  localStorage.removeItem("is_super_admin");
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
  console.log("[API] Auth context marked as ready");
  isAuthReady = true;
  if (authReadyResolve) {
    authReadyResolve();
    authReadyResolve = null;
  }
};

export const resetAuthReady = (): any => {
  console.log("[API] Auth context reset");
  isAuthReady = false;
  initializeAuthPromise();
};

const waitForAuthIfNeeded = async (config: any) => {
  const publicEndpoints = ["/auth/login", "/auth/otp/", "/auth/admin/setup"];
  const isPublicEndpoint = publicEndpoints.some((endpoint) =>
    config.url?.includes(endpoint),
  );
  if (isPublicEndpoint) {
    console.log("[API] Public endpoint, skipping auth wait:", config.url);
    return;
  }
  if (!isAuthReady && authReadyPromise) {
    console.log("[API] Waiting for auth context to be ready for:", config.url);
    const authTimeout = new Promise<void>((_, reject) => {
      setTimeout(() => {
        console.warn(
          "[API] Auth wait timeout - proceeding without auth ready state",
        );
        reject(new Error("Auth wait timeout"));
      }, 10000);
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
    }
  }
};

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  async (config) => {
    await waitForAuthIfNeeded(config);
    const token = localStorage.getItem("token");
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
      hasToken: !!token,
      hasRefreshToken: !!localStorage.getItem("refresh_token"),
      authReady: isAuthReady,
      timestamp: new Date().toISOString(),
    });
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
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

api.interceptors.response.use(
  (response) => {
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
    if (status === 401 && !originalRequest._retry) {
      if (originalRequest.headers?.Authorization) {
        console.log(`[API] ${status} Auth error - attempting token refresh`);
        originalRequest._retry = true;
        try {
          const { authService } = await import("../services/authService");
          const refreshData = await authService.refreshToken();
          if (!refreshData) {
            console.error("[API] Refresh token attempt returned null");
            handleTokenExpiry();
            return Promise.reject(error);
          }
          console.log("[API] Token refreshed successfully");
          originalRequest.headers.Authorization = `Bearer ${refreshData.access_token}`;
          if (refreshData.refresh_token) {
            localStorage.setItem("refresh_token", refreshData.refresh_token);
            console.log("[API] Updated refresh token in localStorage");
          }
          return api(originalRequest);
        } catch (refreshError) {
          console.error("[API] Token refresh failed:", refreshError);
          const errorDetail = error.response?.data?.detail;
          if (errorDetail && typeof errorDetail === "string") {
            console.log(`[API] ${status} Error reason:`, errorDetail);
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
        console.log(`[API] ${status} Error - No token present, not refreshing`);
        return Promise.reject(error);
      }
    } else if (status === 404 && url?.includes("/companies/current")) {
      console.log(
        "[API] 404 on /companies/current - company setup required, not an auth error",
      );
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
    console.error("[API] Processed error message:", errorMessage);
    return Promise.reject({
      ...error,
      userMessage: errorMessage,
      status: status,
    });
  },
);

export default api;