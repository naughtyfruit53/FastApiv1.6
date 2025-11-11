"use client";

import React, { ReactNode } from "react";
import { useAuth } from "../context/AuthContext";
import { useRouter } from "next/navigation";
import { Box, Alert, Typography, Button, CircularProgress } from "@mui/material";
import { LockOutlined } from "@mui/icons-material";

interface RoleGateProps {
  allowedRoles?: string[];
  requiredPermissions?: string[];
  requireModule?: string;
  requireSubmodule?: { module: string; submodule: string };
  fallbackUI?: ReactNode;
  redirectTo?: string;
  children: ReactNode;
}

const RoleGate: React.FC<RoleGateProps> = ({ 
  allowedRoles = [], 
  requiredPermissions = [],
  requireModule,
  requireSubmodule,
  fallbackUI,
  redirectTo,
  children 
}) => {
  const { user, userPermissions, permissionsLoading } = useAuth();
  const router = useRouter();

  if (permissionsLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          p: 3,
        }}
      >
        <CircularProgress sx={{ mb: 2 }} />
        <Typography variant="body1" color="text.secondary">
          Loading permissions...
        </Typography>
      </Box>
    );
  }

  if (!user) {
    if (redirectTo) {
      router.push(redirectTo);
      return null;
    }
    router.push("/login");
    return null;
  }

  // STRICT ENFORCEMENT: No super admin bypass
  
  // Check role-based access
  const hasRoleAccess = allowedRoles.length === 0 || 
    allowedRoles.includes(user.role);

  // Check permission-based access
  let hasPermissionAccess = requiredPermissions.length === 0;
  if (!hasPermissionAccess && userPermissions) {
    // User has access if they have ANY of the required permissions
    hasPermissionAccess = requiredPermissions.some(permission => 
      userPermissions.permissions.includes(permission)
    );
  }

  // Check module access - no bypass for any role
  let hasModuleAccess = !requireModule;
  if (requireModule && userPermissions) {
    hasModuleAccess = userPermissions.modules.includes(requireModule);
  }

  // Check submodule access - no bypass for any role
  let hasSubmoduleAccess = !requireSubmodule;
  if (requireSubmodule && userPermissions) {
    const { module, submodule } = requireSubmodule;
    hasSubmoduleAccess = userPermissions.submodules[module]?.includes(submodule) ?? false;
  }

  const hasAccess = hasRoleAccess && hasPermissionAccess && hasModuleAccess && hasSubmoduleAccess;

  if (!hasAccess) {
    if (redirectTo) {
      router.push(redirectTo);
      return null;
    }

    // Show custom fallback UI if provided
    if (fallbackUI) {
      return <>{fallbackUI}</>;
    }

    // Default unauthorized UI
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          p: 3,
        }}
      >
        <LockOutlined sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom color="error">
          Access Denied
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3, textAlign: 'center', maxWidth: 500 }}>
          You don't have the required permissions to access this resource. 
          Please contact your administrator if you believe this is an error.
        </Typography>
        <Alert severity="warning" sx={{ mb: 2, maxWidth: 500 }}>
          {requiredPermissions.length > 0 && (
            <Typography variant="body2">
              Required permissions: {requiredPermissions.join(', ')}
            </Typography>
          )}
          {requireModule && (
            <Typography variant="body2">
              Required module: {requireModule}
            </Typography>
          )}
          {requireSubmodule && (
            <Typography variant="body2">
              Required submodule: {requireSubmodule.module}/{requireSubmodule.submodule}
            </Typography>
          )}
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => router.push('/dashboard')}
        >
          Go to Dashboard
        </Button>
      </Box>
    );
  }

  return <>{children}</>;
};

export default RoleGate;