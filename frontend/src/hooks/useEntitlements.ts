// frontend/src/hooks/useEntitlements.ts

/**
 * React hooks for accessing and managing entitlements
 */

import { useCallback, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

export function useEntitlements(orgId: number | undefined, token: string | undefined) {
  const shouldFetch = token !== undefined && orgId !== undefined;

  const { data, error, isLoading } = useQuery({
    queryKey: ['entitlements', orgId],
    queryFn: async () => {
      const res = await axios.get('/api/v1/orgs/entitlements', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.data;
    },
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

  // Check if module is entitled (enabled or trial)
  const isModuleEnabled = useCallback(
    (moduleKey: string): boolean => {
      const ent = data?.entitlements ?? {};
      const module = ent[moduleKey.toLowerCase()];
      if (!module) return false;
      if (module.status === 'enabled') return true;
      if (module.status === 'trial') {
        const expires = module.trial_expires_at ? new Date(module.trial_expires_at) : null;
        return !expires || expires > new Date();
      }
      return false;
    },
    [data]
  );

  // Check if submodule is entitled
  const isSubmoduleEnabled = useCallback(
    (moduleKey: string, submoduleKey: string): boolean => {
      const ent = data?.entitlements ?? {};
      const module = ent[moduleKey.toLowerCase()];
      if (!module) return false;
      if (!isModuleEnabled(moduleKey)) return false;
      return module.submodules?.[submoduleKey] ?? true;
    },
    [data, isModuleEnabled]
  );

  // Get module status
  const getModuleStatus = useCallback(
    (moduleKey: string): 'enabled' | 'disabled' | 'trial' | 'unknown' => {
      const ent = data?.entitlements ?? {};
      const module = ent[moduleKey.toLowerCase()];
      return module?.status || 'unknown';
    },
    [data]
  );

  // Check if module is in trial
  const isModuleTrial = useCallback(
    (moduleKey: string): boolean => {
      const ent = data?.entitlements ?? {};
      const module = ent[moduleKey.toLowerCase()];
      return module?.status === 'trial';
    },
    [data]
  );

  // Get trial expiry date
  const getTrialExpiry = useCallback(
    (moduleKey: string): Date | null => {
      const ent = data?.entitlements ?? {};
      const module = ent[moduleKey.toLowerCase()];
      return module?.trial_expires_at ? new Date(module.trial_expires_at) : null;
    },
    [data]
  );

  return {
    entitlements: data,
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