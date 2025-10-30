/**
 * API Client - Base HTTP client for API communication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { ACCESS_TOKEN_KEY } from '../../constants/auth';  // Import the constant

interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      timeout: 120000, // Increased from 30000 to 60000 (60 seconds)
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Enable sending cookies with cross-origin requests
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        // Get token from localStorage or context
        const token = typeof window !== 'undefined' ? localStorage.getItem(ACCESS_TOKEN_KEY) : null;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          if (typeof window !== 'undefined') {
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            window.location.href = '/login';
          }
        } else if (error.response?.status === 403) {
          // Handle permission denied (RBAC enforcement)
          const errorData = error.response.data as any;
          const permission = errorData?.required_permission || errorData?.detail || 'unknown permission';
          const module = errorData?.module || '';
          
          // Log permission denial for audit and debugging
          console.warn('[RBAC] Permission denied:', {
            endpoint: error.config?.url,
            method: error.config?.method?.toUpperCase(),
            requiredPermission: permission,
            module: module,
            timestamp: new Date().toISOString(),
          });
          
          // Show user-friendly error message
          if (typeof window !== 'undefined' && window.alert) {
            const message = `Access Denied: You don't have permission to perform this action.\n\n` +
              `Required permission: ${permission}\n` +
              (module ? `Module: ${module}\n` : '') +
              `\nPlease contact your administrator to request access.`;
            
            // You can replace window.alert with a toast notification library
            // Example: toast.error(message);
            console.error(message);
          }
        } else if (error.response?.status === 404) {
          // Handle not found - could be access denial for cross-org resources
          // Backend returns 404 instead of 403 to avoid information disclosure
          const errorData = error.response.data as any;
          
          // Check if this is actually an access denial (some endpoints return 404 for security)
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