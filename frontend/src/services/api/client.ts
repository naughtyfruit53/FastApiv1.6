/**
 * API Client - Centralized HTTP client for API communication
 * 
 * Features:
 * - Automatic Bearer token attachment
 * - Request/response logging in dev mode
 * - Retry logic for transient failures
 * - Refresh token support
 * - Comprehensive error handling
 * - RBAC permission denial handling
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import axiosRetry from 'axios-retry';
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from '../../constants/auth';

interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

class ApiClient {
  private client: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value?: any) => void;
    reject: (reason?: any) => void;
  }> = [];

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    const isDev = process.env.NODE_ENV === 'development';

    this.client = axios.create({
      baseURL,
      timeout: 120000, // 2 minutes for long-running operations
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Enable sending cookies with cross-origin requests
    });

    // Configure retry logic for transient failures
    axiosRetry(this.client, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => {
        // Retry on network errors or 5xx server errors
        return axiosRetry.isNetworkOrIdempotentRequestError(error) || 
               (error.response?.status ? error.response.status >= 500 : false);
      },
      onRetry: (retryCount, error, requestConfig) => {
        console.log(`[API Client] Retry attempt ${retryCount} for ${requestConfig.url}`, {
          status: error.response?.status,
          message: error.message
        });
      }
    });

    // Request interceptor to add auth token and logging
    this.client.interceptors.request.use(
      (config) => {
        // Get token from localStorage
        const token = typeof window !== 'undefined' ? localStorage.getItem(ACCESS_TOKEN_KEY) : null;
        
        // Attach Bearer token if available
        if (token && token !== 'null' && token !== 'undefined') {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Development mode logging
        if (isDev) {
          console.log('[API Client] Request:', {
            method: config.method?.toUpperCase(),
            url: config.url,
            hasAuth: !!config.headers.Authorization,
            timestamp: new Date().toISOString()
          });
        }

        return config;
      },
      (error) => {
        if (isDev) {
          console.error('[API Client] Request error:', error);
        }
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling and token refresh
    this.client.interceptors.response.use(
      (response) => {
        // Development mode logging
        if (isDev) {
          console.log('[API Client] Response:', {
            method: response.config.method?.toUpperCase(),
            url: response.config.url,
            status: response.status,
            timestamp: new Date().toISOString()
          });
        }
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Development mode logging
        if (isDev) {
          console.error('[API Client] Response error:', {
            method: error.config?.method?.toUpperCase(),
            url: error.config?.url,
            status: error.response?.status,
            detail: (error.response?.data as any)?.detail,
            timestamp: new Date().toISOString()
          });
        }

        // Handle 401 Unauthorized - attempt token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Queue the request while refresh is in progress
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            }).then(() => {
              return this.client(originalRequest);
            }).catch((err) => {
              return Promise.reject(err);
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          const refreshToken = typeof window !== 'undefined' ? localStorage.getItem(REFRESH_TOKEN_KEY) : null;

          if (refreshToken) {
            try {
              // Attempt to refresh the access token
              const response = await axios.post(
                `${baseURL.replace('/api/v1', '')}/api/v1/auth/refresh-token`,
                { refresh_token: refreshToken }
              );

              const { access_token } = response.data;

              if (access_token) {
                localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
                
                // Retry all queued requests
                this.failedQueue.forEach(({ resolve }) => resolve());
                this.failedQueue = [];
                
                this.isRefreshing = false;

                // Retry the original request
                return this.client(originalRequest);
              }
            } catch (refreshError) {
              console.error('[API Client] Token refresh failed:', refreshError);
              this.failedQueue.forEach(({ reject }) => reject(refreshError));
              this.failedQueue = [];
              this.isRefreshing = false;
              
              // Clear tokens and redirect to login
              if (typeof window !== 'undefined') {
                localStorage.removeItem(ACCESS_TOKEN_KEY);
                localStorage.removeItem(REFRESH_TOKEN_KEY);
                window.location.href = '/login';
              }
              return Promise.reject(refreshError);
            }
          } else {
            // No refresh token available - redirect to login
            this.isRefreshing = false;
            if (typeof window !== 'undefined') {
              localStorage.removeItem(ACCESS_TOKEN_KEY);
              window.location.href = '/login';
            }
          }
        }

        // Handle 403 Forbidden - RBAC permission denial
        if (error.response?.status === 403) {
          const errorData = error.response.data as any;
          const permission = errorData?.required_permission || errorData?.detail || 'unknown permission';
          const module = errorData?.module || '';
          
          console.warn('[RBAC] Permission denied:', {
            endpoint: error.config?.url,
            method: error.config?.method?.toUpperCase(),
            requiredPermission: permission,
            module: module,
            timestamp: new Date().toISOString(),
          });
        }

        // Handle 404 Not Found - could be access denial for cross-org resources
        if (error.response?.status === 404) {
          const errorData = error.response.data as any;
          
          if (errorData?.detail && typeof errorData.detail === 'string') {
            const isAccessDenial = errorData.detail.toLowerCase().includes('not found') ||
                                   errorData.detail.toLowerCase().includes('access');
            
            if (isAccessDenial) {
              console.warn('[RBAC] Resource not found or access denied:', {
                endpoint: error.config?.url,
                method: error.config?.method?.toUpperCase(),
                detail: errorData.detail,
                timestamp: new Date().toISOString(),
              });
            }
          }
        }

        // Handle connection errors
        if (!error.response && error.message) {
          console.error('[API Client] Connection error:', {
            message: error.message,
            code: error.code,
            url: error.config?.url
          });
          
          // Provide user-friendly error message
          const enhancedError = new Error(
            'Failed to establish a secure connection to the server. Please check your internet connection and try again.'
          );
          return Promise.reject(enhancedError);
        }

        return Promise.reject(error);
      }
    );
  }

  async get<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    const response = await this.client.get(url, { params });
    return response;
  }

  async post<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    const response = await this.client.post(url, data, config);
    return response;
  }

  async put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.client.put(url, data);
    return response;
  }

  async patch<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.client.patch(url, data);
    return response;
  }

  async delete<T = any>(url: string): Promise<ApiResponse<T>> {
    const response = await this.client.delete(url);
    return response;
  }

  // File upload method
  async uploadFile<T = any>(url: string, file: File, onProgress?: (progress: number) => void): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response;
  }

  // Download file method
  async downloadFile(url: string, filename?: string): Promise<void> {
    const response = await this.client.get(url, {
      responseType: 'blob',
    });

    // Create blob link to download
    const blob = new Blob([response.data]);
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = filename || 'download';
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up
    window.URL.revokeObjectURL(link.href);
  }
}

export const apiClient = new ApiClient();