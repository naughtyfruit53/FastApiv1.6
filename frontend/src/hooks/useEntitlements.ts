// frontend/src/hooks/useEntitlements.ts

/**
 * React hooks for accessing and managing entitlements
 */

import { useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  fetchEntitlements,
  AppEntitlementsResponse,
} from '../services/entitlementsApi';

export function useEntitlements(orgId: number | undefined, token: string | undefined) {
  const shouldFetch = token !== undefined;

  const { data, error, isLoading } = useQuery({
    queryKey: ['entitlements'],
    queryFn: () => fetchEntitlements(token!),
    enabled: shouldFetch,
    staleTime: 60000, // 1 minute
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
    onError: (err) => {
      console.error('[useEntitlements] Error fetching entitlements:', err);
    },
    onSuccess: (data) => {
      console.log('[useEntitlements] Fetched entitlements:', data);
    },
  });

  // Check if module is entitled
  const isModuleEnabled = useCallback(
    (moduleKey: string): boolean => {
      if (!data) return false;
      const module = data.entitlements[moduleKey.toLowerCase()];
      if (!module) return false;
      return module.status === 'enabled' || module.status === 'trial';
    },
    [data]
  );

  // Check if submodule is entitled
  const isSubmoduleEnabled = useCallback(
    (moduleKey: string, submoduleKey: string): boolean => {
      if (!data) return false;
      const module = data.entitlements[moduleKey.toLowerCase()];
      if (!module) return false;
      if (module.status !== 'enabled' && module.status !== 'trial') return false;
      
      // If no submodule entry, default to enabled
      if (!module.submodules || !(submoduleKey in module.submodules)) {
        return true;
      }
      
      return module.submodules[submoduleKey] === true;
    },
    [data]
  );

  // Get module status
  const getModuleStatus = useCallback(
    (moduleKey: string): 'enabled' | 'disabled' | 'trial' | 'unknown' => {
      if (!data) return 'unknown';
      const module = data.entitlements[moduleKey.toLowerCase()];
      return module?.status || 'unknown';
    },
    [data]
  );

  // Check if module is in trial
  const isModuleTrial = useCallback(
    (moduleKey: string): boolean => {
      if (!data) return false;
      const module = data.entitlements[moduleKey.toLowerCase()];
      return module?.status === 'trial';
    },
    [data]
  );

  // Get trial expiry date
  const getTrialExpiry = useCallback(
    (moduleKey: string): Date | null => {
      if (!data) return null;
      const module = data.entitlements[moduleKey.toLowerCase()];
      if (module?.status === 'trial' && module.trial_expires_at) {
        return new Date(module.trial_expires_at);
      }
      return null;
    },
    [data]
  );

  return {
    entitlements: data?.entitlements,
    isLoading,
    error,
    isModuleEnabled,
    isSubmoduleEnabled,
    getModuleStatus,
    isModuleTrial,
    getTrialExpiry,
  };
}

/**
 * Hook to invalidate entitlements cache (useful after updates)
 */
export function useInvalidateEntitlements() {
  const queryClient = useQueryClient();
  
  const invalidate = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['entitlements'] });
  }, [queryClient]);

  return { invalidateEntitlements: invalidate };
}

/**
 * Hook to check if user has access to a specific feature
 */
export function useFeatureAccess(
  orgId: number | undefined,
  token: string | undefined,
  moduleKey: string,
  submoduleKey?: string
) {
  const { isModuleEnabled, isSubmoduleEnabled, isLoading } = useEntitlements(orgId, token);

  const hasAccess = !isLoading && (
    submoduleKey
      ? isSubmoduleEnabled(moduleKey, submoduleKey)
      : isModuleEnabled(moduleKey)
  );

  return {
    hasAccess,
    isLoading,
  };
}