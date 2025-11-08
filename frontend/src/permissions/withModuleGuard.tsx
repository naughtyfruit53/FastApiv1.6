// frontend/src/permissions/withModuleGuard.tsx

/**
 * Higher-Order Component (HOC) for protecting routes with module entitlements
 */

import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Box, CircularProgress, Typography, Button, Paper } from '@mui/material';
import { Lock as LockIcon } from '@mui/icons-material';
import { useEntitlements } from '../hooks/useEntitlements';

interface WithModuleGuardOptions {
  moduleKey: string;
  submoduleKey?: string;
  redirectTo?: string; // Where to redirect non-admin users
  showLockedUI?: boolean; // Show locked UI for admins instead of redirecting
}

/**
 * HOC to protect a page with module/submodule entitlement check
 * 
 * Usage:
 * ```tsx
 * export default withModuleGuard(SalesPage, {
 *   moduleKey: 'sales',
 *   submoduleKey: 'lead_management',
 *   showLockedUI: true,
 * });
 * ```
 */
export function withModuleGuard<P extends object>(
  Component: React.ComponentType<P>,
  options: WithModuleGuardOptions
) {
  const { moduleKey, submoduleKey, redirectTo = '/', showLockedUI = true } = options;

  return function ModuleGuardedComponent(props: P) {
    const router = useRouter();
    
    // Get user info from context/auth (adjust based on your auth setup)
    // For now, using placeholder - replace with actual auth context
    const orgId = typeof window !== 'undefined' ? 
      parseInt(localStorage.getItem('organizationId') || '0') : 0;
    const token = typeof window !== 'undefined' ? 
      localStorage.getItem('authToken') || '' : '';
    const userRole = typeof window !== 'undefined' ? 
      localStorage.getItem('userRole') || '' : '';
    
    const isAdminLike = ['org_admin', 'super_admin'].includes(userRole);
    const isSuperAdmin = userRole === 'super_admin';

    const { isModuleEnabled, isSubmoduleEnabled, isLoading, error } = useEntitlements(
      orgId || undefined,
      token || undefined
    );

    useEffect(() => {
      if (isLoading) return;

      // Super admin bypasses checks
      if (isSuperAdmin) return;

      // Check access
      const hasAccess = submoduleKey
        ? isSubmoduleEnabled(moduleKey, submoduleKey)
        : isModuleEnabled(moduleKey);

      if (!hasAccess) {
        if (!isAdminLike || !showLockedUI) {
          // Redirect non-admin users or if showLockedUI is false
          router.replace(redirectTo);
        }
        // Otherwise, show locked UI for admins (handled in render)
      }
    }, [isLoading, isModuleEnabled, isSubmoduleEnabled, isAdminLike, isSuperAdmin, router]);

    // Loading state
    if (isLoading) {
      return (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
          <CircularProgress />
        </Box>
      );
    }

    // Error state
    if (error) {
      return (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
          <Typography color="error">
            Failed to load entitlements. Please refresh the page.
          </Typography>
        </Box>
      );
    }

    // Super admin always has access
    if (isSuperAdmin) {
      return <Component {...props} />;
    }

    // Check access
    const hasAccess = submoduleKey
      ? isSubmoduleEnabled(moduleKey, submoduleKey)
      : isModuleEnabled(moduleKey);

    // If admin-like and showLockedUI, show locked UI
    if (!hasAccess && isAdminLike && showLockedUI) {
      return <LockedModuleUI moduleKey={moduleKey} submoduleKey={submoduleKey} />;
    }

    // If has access, render component
    if (hasAccess) {
      return <Component {...props} />;
    }

    // Should not reach here (redirect happens in useEffect)
    return null;
  };
}

/**
 * Locked Module UI for administrators
 */
function LockedModuleUI({
  moduleKey,
  submoduleKey,
}: {
  moduleKey: string;
  submoduleKey?: string;
}) {
  const router = useRouter();

  const handleManageModules = () => {
    router.push('/admin/module-management');
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="600px"
      p={3}
    >
      <Paper
        elevation={3}
        sx={{
          p: 6,
          maxWidth: 600,
          textAlign: 'center',
        }}
      >
        <LockIcon sx={{ fontSize: 80, color: 'warning.main', mb: 3 }} />
        
        <Typography variant="h4" gutterBottom>
          Module Not Available
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          {submoduleKey ? (
            <>
              The feature <strong>{submoduleKey}</strong> in the{' '}
              <strong>{moduleKey}</strong> module is not enabled for your organization.
            </>
          ) : (
            <>
              The <strong>{moduleKey}</strong> module is not enabled for your
              organization.
            </>
          )}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          As an administrator, you can manage module access for your organization.
        </Typography>
        
        <Box mt={4} display="flex" gap={2} justifyContent="center">
          <Button
            variant="contained"
            color="primary"
            onClick={handleManageModules}
          >
            Manage Modules
          </Button>
          <Button
            variant="outlined"
            onClick={() => router.back()}
          >
            Go Back
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
