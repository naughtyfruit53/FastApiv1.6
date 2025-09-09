/**
 * OAuth Hook for handling OAuth2 authentication flows
 */

import { useState, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

interface OAuthProvider {
  name: string;
  display_name: string;
  icon: string;
  scopes: string[];
}

interface OAuthLoginResponse {
  authorization_url: string;
  state: string;
  provider: string;
}

interface UserEmailToken {
  id: number;
  user_id: number;
  organization_id: number;
  provider: string;
  email_address: string;
  display_name: string | null;
  token_type: string;
  expires_at: string | null;
  status: string;
  sync_enabled: boolean;
  sync_folders: string[] | null;
  last_sync_at: string | null;
  last_sync_status: string | null;
  last_sync_error: string | null;
  created_at: string;
  updated_at: string;
  last_used_at: string | null;
  refresh_count: number;
  has_access_token: boolean;
  has_refresh_token: boolean;
  is_expired: boolean;
  is_active: boolean;
}

interface EmailSyncResponse {
  success: boolean;
  message: string;
  synced_emails: number;
  errors: string[];
  last_sync_at: string;
}

export const useOAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { getAuthHeaders } = useAuth();

  const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  });

  // Add auth headers to all requests
  apiClient.interceptors.request.use((config) => {
    const headers = getAuthHeaders();
    if (headers.Authorization) {
      config.headers.Authorization = headers.Authorization;
    }
    return config;
  });

  const getProviders = useCallback(async (): Promise<{ providers: OAuthProvider[] }> => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/api/v1/oauth/providers');
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || 'Failed to fetch OAuth providers. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).';
      if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth providers endpoint not found. Ensure the backend server is running on port 8000 and that the route is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const initiateOAuthFlow = useCallback(async (
    provider: string,
    redirectUri?: string
  ): Promise<OAuthLoginResponse> => {
    try {
      setLoading(true);
      setError(null);
      // Fetch the authorization URL from the backend with auth headers
      const response = await apiClient.post(`/api/v1/oauth/login/${provider}`);
      const { authorization_url, state } = response.data;
      console.log(`Storing provider for state: ${state} - ${provider}`);
      localStorage.setItem(`oauth_provider_${state}`, provider);
      console.log(`Redirecting to OAuth provider: ${authorization_url}`);
      window.location.href = authorization_url;
      // Return the response for completeness, though redirect happens immediately
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || `Failed to initiate ${provider} OAuth flow. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).`;
      if (err.response?.status === 401) {
        errorMsg = 'Unauthorized: Please ensure you are logged in and your session is active. If the issue persists, re-login and try again.';
      } else if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth initiation endpoint not found. Ensure the backend server is running on port 8000 and that the route /api/v1/oauth/login/{provider} is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const handleOAuthCallback = useCallback(async (
    provider: string,
    code: string,
    state: string,
    error?: string,
    errorDescription?: string
  ): Promise<any> => {
    try {
      setLoading(true);
      setError(null);

      if (error) {
        throw new Error(errorDescription || error);
      }

      const response = await apiClient.get(`/api/v1/oauth/callback/${provider}`, {
        params: { code, state, error, error_description: errorDescription }
      });
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || `OAuth callback failed for ${provider}. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).`;
      if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth callback endpoint not found. Ensure the backend server is running on port 8000 and that the route /api/v1/oauth/callback/{provider} is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getUserTokens = useCallback(async (): Promise<UserEmailToken[]> => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/api/v1/oauth/tokens');
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || 'Failed to fetch user tokens. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).';
      if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth tokens endpoint not found. Ensure the backend server is running on port 8000 and that the route /api/v1/oauth/tokens is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getTokenDetails = useCallback(async (tokenId: number): Promise<UserEmailToken> => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get(`/api/v1/oauth/tokens/${tokenId}`);
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || 'Failed to fetch token details. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).';
      if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth token details endpoint not found. Ensure the backend server is running on port 8000 and that the route /api/v1/oauth/tokens/{tokenId} is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateToken = useCallback(async (
    tokenId: number,
    updates: {
      display_name?: string;
      sync_enabled?: boolean;
      sync_folders?: string[];
      status?: string;
    }
  ): Promise<UserEmailToken> => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.put(`/api/v1/oauth/tokens/${tokenId}`, updates);
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || 'Failed to update token. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).';
      if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth update token endpoint not found. Ensure the backend server is running on port 8000 and that the route /api/v1/oauth/tokens/{tokenId} is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshToken = useCallback(async (tokenId: number): Promise<{ success: boolean; message: string }> => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.post(`/api/v1/oauth/tokens/${tokenId}/refresh`);
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || 'Failed to refresh token. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).';
      if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth refresh token endpoint not found. Ensure the backend server is running on port 8000 and that the route /api/v1/oauth/tokens/{tokenId}/refresh is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const revokeToken = useCallback(async (tokenId: number): Promise<{ success: boolean; message: string }> => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.delete(`/api/v1/oauth/tokens/${tokenId}`);
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || 'Failed to revoke token. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).';
      if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth revoke token endpoint not found. Ensure the backend server is running on port 8000 and that the route /api/v1/oauth/tokens/{tokenId} is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const syncEmails = useCallback(async (
    tokenId: number,
    folders?: string[],
    forceSync: boolean = false
  ): Promise<EmailSyncResponse> => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.post(`/api/v1/oauth/tokens/${tokenId}/sync`, {
        token_id: tokenId,
        folders,
        force_sync: forceSync
      });
      return response.data;
    } catch (err: any) {
      let errorMsg = err.response?.data?.detail || 'Failed to sync emails. Please verify that the backend is running and NEXT_PUBLIC_API_URL is correctly set to the backend host (e.g., http://127.0.0.1:8000).';
      if (err.response?.status === 404) {
        errorMsg = 'Backend OAuth sync emails endpoint not found. Ensure the backend server is running on port 8000 and that the route /api/v1/oauth/tokens/{tokenId}/sync is defined.';
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getProviders,
    initiateOAuthFlow,
    handleOAuthCallback,
    getUserTokens,
    getTokenDetails,
    updateToken,
    refreshToken,
    revokeToken,
    syncEmails,
    clearError: () => setError(null)
  };
};