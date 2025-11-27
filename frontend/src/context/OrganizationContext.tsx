// frontend/src/context/OrganizationContext.tsx

/**
 * Organization Context - Manages current organization context
 * 
 * This context provides:
 * - Current organization ID and name
 * - Organization switching functionality
 * - Data cleanup on organization switch
 * 
 * Usage:
 * ```tsx
 * import { useOrganization } from '@/context/OrganizationContext';
 * 
 * const MyComponent = () => {
 *   const { organizationId, organizationName, switchOrganization } = useOrganization();
 *   
 *   return (
 *     <div>
 *       <p>Current Org: {organizationName} (ID: {organizationId})</p>
 *       <button onClick={() => switchOrganization(123)}>
 *         Switch Organization
 *       </button>
 *     </div>
 *   );
 * };
 * ```
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiClient from '../services/api/client';

interface OrganizationContextType {
  /** Current organization ID */
  organizationId: number | null;
  
  /** Current organization name */
  organizationName: string | null;
  
  /** Loading state */
  loading: boolean;
  
  /** Error state */
  error: string | null;
  
  /** Switch to a different organization */
  switchOrganization: (orgId: number) => Promise<void>;
  
  /** Refresh organization data */
  refreshOrganization: () => Promise<void>;
}

export const OrganizationContext = createContext<OrganizationContextType>({  // NEW: Changed to named export 'export const OrganizationContext' to match import in hooks
  organizationId: null,
  organizationName: null,
  loading: true,
  error: null,
  switchOrganization: async () => {},
  refreshOrganization: async () => {},
});

interface OrganizationProviderProps {
  children: React.ReactNode;
}

export const OrganizationProvider: React.FC<OrganizationProviderProps> = ({ children }) => {
  const [organizationId, setOrganizationId] = useState<number | null>(null);
  const [organizationName, setOrganizationName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Clear organization-specific cached data
   */
  const clearOrganizationCache = useCallback(() => {
    if (typeof window !== 'undefined') {
      // Clear organization-specific data from localStorage
      const keysToRemove: string[] = [];
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (
          key.includes('cached_') ||
          key.includes('_cache') ||
          key.includes('voucher') ||
          key.includes('inventory') ||
          key.includes('stock')
        )) {
          keysToRemove.push(key);
        }
      }
      
      keysToRemove.forEach(key => {
        console.log('[OrganizationContext] Clearing cache:', key);
        localStorage.removeItem(key);
      });
    }
  }, []);

  /**
   * Load current organization from backend
   */
  const loadOrganization = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get current user info which includes organization
      const response = await apiClient.get<{
        organization_id: number;
        organization_name: string;
      }>('/users/me');
      
      const orgId = response.data.organization_id;
      const orgName = response.data.organization_name;
      
      setOrganizationId(orgId);
      setOrganizationName(orgName);
      
      console.log('[OrganizationContext] Loaded organization:', orgName, `(ID: ${orgId})`);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load organization';
      setError(errorMessage);
      console.error('[OrganizationContext] Error loading organization:', err);
      
      // On error, clear organization data
      setOrganizationId(null);
      setOrganizationName(null);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Load organization on mount
   */
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        loadOrganization();
      } else {
        setLoading(false);
      }
    }
  }, [loadOrganization]);

  /**
   * Switch to a different organization
   * This will clear cached data and reload the page to ensure clean state
   */
  const switchOrganization = useCallback(async (orgId: number) => {
    try {
      console.log('[OrganizationContext] Switching to organization:', orgId);
      
      // Clear organization-specific cached data
      clearOrganizationCache();
      
      // Update organization in backend if needed
      // This depends on your backend implementation
      // await apiClient.post('/users/switch-organization', { organization_id: orgId });
      
      // Reload the page to ensure clean state
      if (typeof window !== 'undefined') {
        window.location.reload();
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to switch organization';
      setError(errorMessage);
      console.error('[OrganizationContext] Error switching organization:', err);
      throw err;
    }
  }, [clearOrganizationCache]);

  /**
   * Refresh organization data
   */
  const refreshOrganization = useCallback(async () => {
    await loadOrganization();
  }, [loadOrganization]);

  const value: OrganizationContextType = {
    organizationId,
    organizationName,
    loading,
    error,
    switchOrganization,
    refreshOrganization,
  };

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  );
};

/**
 * Hook to access organization context
 * @throws Error if used outside of OrganizationProvider
 */
export const useOrganization = (): OrganizationContextType => {
  const context = useContext(OrganizationContext);
  
  if (!context) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  
  return context;
};

// Removed 'export default OrganizationContext;' as it's now named export