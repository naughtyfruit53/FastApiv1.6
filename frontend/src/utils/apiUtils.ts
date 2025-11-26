// Revised: v1/frontend/src/utils/apiUtils.ts
import axios from "axios";
import { getApiUrl } from "./config";

const api = axios.create({
  baseURL: getApiUrl(), // Use centralized config to prevent URL duplication
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to force HTTPS in production
api.interceptors.request.use(
  (config) => {
    // Force HTTPS in production
    if (process.env.NODE_ENV === 'production' && config.url && config.url.startsWith('http://')) {
      config.url = config.url.replace('http://', 'https://');
      console.log('[apiUtils] Forced HTTPS for request:', config.url);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
// Add error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);
export const handleApiError = (error: unknown): string => {
  if (typeof error === "object" && error !== null && "response" in error) {
    const apiError = error as {
      response?: { data?: { message?: string; detail?: string } };
    };
    return (
      apiError.response?.data?.message ||
      apiError.response?.data?.detail ||
      "An error occurred"
    );
  } else if (
    typeof error === "object" &&
    error !== null &&
    "request" in error
  ) {
    return "No response received from server";
  } else if (error instanceof Error) {
    return error.message || "Unknown error";
  } else {
    return "Unknown error";
  }
};
export const getApiParams = (
  params: Record<string, unknown>,
): URLSearchParams => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });
  return searchParams;
};
export const uploadStockBulk = async (file: File): Promise<any> => {
  try {
    const formData = new FormData();
    formData.append("file", file); // Ensure field name matches backend expectation ('file')
    const response = await api.post("/stock/bulk", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
export default api;