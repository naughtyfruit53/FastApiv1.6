// frontend/src/services/api/client.ts
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
import { getApiUrl } from '../../utils/config';

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
    // Use centralized config to get the full API URL including /api/v1
    // getApiUrl() returns the complete URL (e.g., http://localhost:8000/api/v1)
    let baseURL = getApiUrl();
    
    // Force HTTPS in production
    if (process.env.NODE_ENV === 'production' && baseURL.startsWith('http://')) {
      console.warn('[API Client] Forcing HTTPS in production baseURL');
      baseURL = baseURL.replace('http://', 'https://');
    }

    const isDev = process.env.NODE_ENV === 'development';

    this.client = axios.create({
      baseURL,
      timeout: 120000, // 2 minutes for long-running operations
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: false, // Changed to false to avoid credential issues with CORS
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
        // Validate JWT structure: should have two dots (header.payload.signature)
        if (token && token.trim() && token !== 'null' && token !== 'undefined') {
          const parts = token.split('.');
          if (parts.length === 3) {
            config.headers.Authorization = `Bearer ${token}`;
          } else {
            console.warn('[API Client] Invalid JWT format detected, skipping auth header');
          }
        }

        // Force HTTPS for all requests in production
        if (process.env.NODE_ENV === 'production' && config.url && !config.url.startsWith('https://')) {
          if (config.url.startsWith('http://')) {
            config.url = config.url.replace('http://', 'https://');
          } else if (!config.url.startsWith('http')) {
            // If relative, prepend baseURL which is already HTTPS
            config.url = `${baseURL}${config.url.startsWith('/') ? '' : '/'}${config.url}`;
          }
          console.log('[API Client] Forced HTTPS for request:', config.url);
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
            }).then((token) => {
              // Update the authorization header with new token
              if (originalRequest.headers && token) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              return this.client(originalRequest);
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          const refreshToken = typeof window !== 'undefined' ? localStorage.getItem(REFRESH_TOKEN_KEY) : null;

          if (refreshToken) {
            try {
              // Attempt to refresh the access token
              // Construct refresh endpoint URL - handle both absolute and relative baseURL
              let refreshUrl: string;
              try {
                // Try to construct as absolute URL
                refreshUrl = new URL('/auth/refresh-token', baseURL).toString();
              } catch {
                // If baseURL is relative, construct manually
                refreshUrl = `${baseURL.replace(/\/+$/, '')}/auth/refresh-token`;
              }
              
              // Force HTTPS for refresh URL
              if (process.env.NODE_ENV === 'production' && refreshUrl.startsWith('http://')) {
                refreshUrl = refreshUrl.replace('http://', 'https://');
              }

              const response = await axios.post(
                refreshUrl,
                { refresh_token: refreshToken }
              );

              const { access_token } = response.data;

              if (access_token) {
                localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
                
                // Retry all queued requests with new token
                this.failedQueue.forEach(({ resolve }) => resolve(access_token));
                this.failedQueue = [];
                
                this.isRefreshing = false;

                // Update original request with new token
                if (originalRequest.headers && access_token) {
                  originalRequest.headers.Authorization = `Bearer ${access_token}`;
                }
                
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
          
          // Enhance error with user-friendly message
          const enhancedError = new Error(
            errorData?.detail || 
            `You don't have permission to access this resource. ${permission ? `Required permission: ${permission}` : ''}`
          ) as AxiosError;
          enhancedError.response = error.response;
          enhancedError.config = error.config;
          return Promise.reject(enhancedError);
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
              
              // Enhance error with user-friendly message
              const enhancedError = new Error(
                errorData?.detail || 'Resource not found or you do not have access to it'
              ) as AxiosError;
              enhancedError.response = error.response;
              enhancedError.config = error.config;
              return Promise.reject(enhancedError);
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

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.get(url, config);
    return response;
  }

  async post<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    const response = await this.client.post(url, data, config);
    return response;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.put(url, data, config);
    return response;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.patch(url, data, config);
    return response;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.delete(url, config);
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

export default new ApiClient();
