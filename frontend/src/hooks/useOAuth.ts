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
      const errorMsg = err.response?.data?.detail || 'Failed to fetch OAuth providers';
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
      const response = await apiClient.post(`/api/v1/oauth/login/${provider}`, {
        redirect_uri: redirectUri
      });
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || `Failed to initiate ${provider} OAuth flow`;
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

      const response = await apiClient.post(`/api/v1/oauth/callback/${provider}`, null, {
        params: { code, state, error, error_description: errorDescription }
      });
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || `OAuth callback failed for ${provider}`;
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
      const errorMsg = err.response?.data?.detail || 'Failed to fetch user tokens';
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
      const errorMsg = err.response?.data?.detail || 'Failed to fetch token details';
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
      const errorMsg = err.response?.data?.detail || 'Failed to update token';
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
      const errorMsg = err.response?.data?.detail || 'Failed to refresh token';
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
      const errorMsg = err.response?.data?.detail || 'Failed to revoke token';
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
      const errorMsg = err.response?.data?.detail || 'Failed to sync emails';
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