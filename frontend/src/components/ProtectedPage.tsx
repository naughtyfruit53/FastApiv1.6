// frontend/src/components/ProtectedPage.tsx
import React, { ReactNode } from 'react';
import { Box, CircularProgress, Alert, Button, Container, Paper, Typography } from '@mui/material';
import { Lock as LockIcon, ErrorOutline as ErrorIcon } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { usePermissionCheck } from '../hooks/usePermissionCheck';
import { useAuth } from '../context/AuthContext';

/**
 * Props for the ProtectedPage wrapper component
 */
interface ProtectedPageProps {
  /** The content to render when access is granted */
  children: ReactNode;
 
  /** Module key to check (e.g., 'crm', 'inventory') */
  moduleKey?: string;
 
  /** Submodule key to check (optional, requires moduleKey) */
  submoduleKey?: string;
 
  /** Action to check (default: 'read') */
  action?: string;
 
  /** Custom permission check function (overrides module/submodule checks) */
  customCheck?: (permissionCheck: ReturnType<typeof usePermissionCheck>) => boolean;
 
  /** Custom access denied message */
  accessDeniedMessage?: string;
 
  /** Whether to show upgrade prompt for disabled/trial modules */
  showUpgradePrompt?: boolean;
 
  /** Callback when access is denied */
  onAccessDenied?: (reason: string) => void;
 
  /** Whether to redirect to dashboard on access denied (default: false) */
  redirectOnDenied?: boolean;
 
  /** Custom loading component */
  loadingComponent?: ReactNode;
 
  /** Custom access denied component */
  accessDeniedComponent?: ReactNode;
}

/**
 * ProtectedPage Component
 *
 * Wraps page content with 3-layer security checks:
 * - Layer 1: Tenant context validation
 * - Layer 2: Module/submodule entitlement check
 * - Layer 3: RBAC permission check
 *
 * Shows loading state while checking, and access denied UI if any check fails.
 *
 * @example
 * // Protect entire page with module access check
 * <ProtectedPage moduleKey="crm" action="read">
 * <CRMDashboard />
 * </ProtectedPage>
 *
 * @example
 * // Protect with submodule access check
 * <ProtectedPage moduleKey="crm" submoduleKey="leads" action="write">
 * <LeadForm />
 * </ProtectedPage>
 *
 * @example
 * // Protect with custom permission check
 * <ProtectedPage customCheck={(pc) => pc.checkIsSuperAdmin()}>
 * <AdminPanel />
 * </ProtectedPage>
 */
export const ProtectedPage: React.FC<ProtectedPageProps> = ({
  children,
  moduleKey,
  submoduleKey,
  action = 'read',
  customCheck,
  accessDeniedMessage,
  showUpgradePrompt = true,
  onAccessDenied,
  redirectOnDenied = false,
  loadingComponent,
  accessDeniedComponent,
}) => {
  const router = useRouter();
  const permissionCheck = usePermissionCheck();
  const { permissionsLoading } = useAuth(); // NEW: Get permissionsLoading from AuthContext
  const {
    isReady,
    isLoading,
    checkModuleAccess,
    checkSubmoduleAccess,
  } = permissionCheck;
  // Show loading state
  if (isLoading || !isReady || permissionsLoading) { // NEW: Added permissionsLoading
    if (loadingComponent) {
      return <>{loadingComponent}</>;
    }
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          gap: 2,
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="body2" color="text.secondary">
          Verifying access...
        </Typography>
      </Box>
    );
  }
  // Perform access check
  let hasAccess = true;
  let denialReason = '';
  let enforcementLevel = '';
  if (customCheck) {
    // Custom check function
    hasAccess = customCheck(permissionCheck);
    denialReason = accessDeniedMessage || 'You do not have permission to access this page';
  } else if (moduleKey) {
    // Module/submodule check
    const result = submoduleKey
      ? checkSubmoduleAccess(moduleKey, submoduleKey, action)
      : checkModuleAccess(moduleKey, action);
    hasAccess = result.hasPermission;
    denialReason = result.reason || 'Access denied';
    enforcementLevel = result.enforcementLevel || '';
  }
  // Handle access denied
  if (!hasAccess) {
    // Trigger callback if provided
    if (onAccessDenied) {
      onAccessDenied(denialReason);
    }
    // Redirect if requested
    if (redirectOnDenied) {
      router.push('/dashboard');
      return null;
    }
    // Show custom access denied component
    if (accessDeniedComponent) {
      return <>{accessDeniedComponent}</>;
    }
    // Default access denied UI
    const isEntitlementIssue = enforcementLevel === 'ENTITLEMENT';
    return (
      <Container maxWidth="md" sx={{ mt: 8 }}>
        <Paper
          elevation={3}
          sx={{
            p: 4,
            textAlign: 'center',
            borderTop: 3,
            borderColor: 'error.main',
          }}
        >
          <Box sx={{ mb: 3 }}>
            {isEntitlementIssue ? (
              <LockIcon sx={{ fontSize: 64, color: 'warning.main' }} />
            ) : (
              <ErrorIcon sx={{ fontSize: 64, color: 'error.main' }} />
            )}
          </Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {denialReason}
          </Typography>
          {isEntitlementIssue && showUpgradePrompt && (
            <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
              <Typography variant="body2" fontWeight="medium" gutterBottom>
                Module Not Enabled
              </Typography>
              <Typography variant="body2">
                This feature requires the <strong>{moduleKey}</strong> module to be enabled for your organization.
                Contact your administrator or upgrade your plan to access this feature.
              </Typography>
            </Alert>
          )}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 4 }}>
            <Button
              variant="outlined"
              onClick={() => router.back()}
            >
              Go Back
            </Button>
            <Button
              variant="contained"
              onClick={() => router.push('/dashboard')}
            >
              Go to Dashboard
            </Button>
            {isEntitlementIssue && showUpgradePrompt && (
              <Button
                variant="contained"
                color="primary"
                onClick={() => router.push('/settings')}
              >
                View Settings
              </Button>
            )}
          </Box>
        </Paper>
      </Container>
    );
  }
  // Access granted - render children
  return <>{children}</>;
};
/**
 * Higher-Order Component version of ProtectedPage
 *
 * @example
 * const ProtectedCRMPage = withProtection(CRMDashboard, {
 * moduleKey: 'crm',
 * action: 'read',
 * });
 */
export function withProtection<P extends object>(
  Component: React.ComponentType<P>,
  options: Omit<ProtectedPageProps, 'children'>
): React.FC<P> {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedPage {...options}>
        <Component {...props} />
      </ProtectedPage>
    );
  };
}
export default ProtectedPage;