'use client';

import React, { ReactNode, useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/navigation';
import { rbacService } from '../../services/rbacService';
import { SERVICE_PERMISSIONS } from '../../types/rbac.types';

interface ServiceRoleGateProps {
  requiredPermissions?: string[];
  requiredRoles?: string[];
  requireAll?: boolean; // If true, user must have ALL permissions/roles; if false, ANY will suffice
  fallbackComponent?: ReactNode;
  children: ReactNode;
}

/**
 * ServiceRoleGate - Enhanced role gate that supports Service CRM permissions
 * 
 * This component provides fine-grained access control based on:
 * - Traditional system roles (org_admin, admin, etc.)
 * - Service CRM specific permissions (service_create, technician_read, etc.)
 * 
 * Usage examples:
 * 
 * // Require specific service permission
 * <ServiceRoleGate requiredPermissions={[SERVICE_PERMISSIONS.SERVICE_CREATE]}>
 *   <CreateServiceButton />
 * </ServiceRoleGate>
 * 
 * // Require multiple permissions (user must have ALL)
 * <ServiceRoleGate 
 *   requiredPermissions={[SERVICE_PERMISSIONS.SERVICE_READ, SERVICE_PERMISSIONS.SERVICE_UPDATE]}
 *   requireAll={true}
 * >
 *   <ServiceManagementPage />
 * </ServiceRoleGate>
 * 
 * // Require ANY of the specified permissions
 * <ServiceRoleGate 
 *   requiredPermissions={[SERVICE_PERMISSIONS.APPOINTMENT_READ, SERVICE_PERMISSIONS.WORK_ORDER_READ]}
 *   requireAll={false}
 * >
 *   <DashboardWidget />
 * </ServiceRoleGate>
 * 
 * // Combine system roles and service permissions
 * <ServiceRoleGate 
 *   requiredRoles={['admin', 'org_admin']}
 *   requiredPermissions={[SERVICE_PERMISSIONS.CRM_ADMIN]}
 *   requireAll={false} // User needs admin role OR crm_admin permission
 * >
 *   <AdminPanel />
 * </ServiceRoleGate>
 * 
 * // Provide fallback component instead of redirecting
 * <ServiceRoleGate 
 *   requiredPermissions={[SERVICE_PERMISSIONS.SERVICE_REPORTS_EXPORT]}
 *   fallbackComponent={<div>Export feature not available</div>}
 * >
 *   <ExportButton />
 * </ServiceRoleGate>
 */
const ServiceRoleGate: React.FC<ServiceRoleGateProps> = ({ 
  requiredPermissions = [],
  requiredRoles = [],
  requireAll = true,
  fallbackComponent,
  children 
}) => {
  const { user } = useAuth();
  const router = useRouter();
  const [userPermissions, setUserPermissions] = useState<string[]>([]);
  const [permissionsLoaded, setPermissionsLoaded] = useState(false);
  const [hasAccess, setHasAccess] = useState(false);

  // Load user's service permissions
  useEffect(() => {
    const loadUserPermissions = async () => {
      if (!user) {
        setPermissionsLoaded(true);
        return;
      }

      try {
        const permissions = await rbacService.getCurrentUserPermissions();
        setUserPermissions(permissions);
      } catch (error) {
        console.warn('Failed to load user service permissions:', error);
        setUserPermissions([]);
      } finally {
        setPermissionsLoaded(true);
      }
    };

    loadUserPermissions();
  }, [user]);

  // Check access whenever user, permissions, or requirements change
  useEffect(() => {
    if (!permissionsLoaded) return;

    const checkAccess = () => {
      if (!user) {
        setHasAccess(false);
        return;
      }

      // Super admins bypass all checks
      if (user.is_super_admin === true) {
        setHasAccess(true);
        return;
      }

      const checks = [];

      // Check system roles
      if (requiredRoles.length > 0) {
        const hasRequiredRole = requireAll
          ? requiredRoles.every(role => user.role === role)
          : requiredRoles.some(role => user.role === role);
        checks.push(hasRequiredRole);
      }

      // Check service permissions
      if (requiredPermissions.length > 0) {
        const hasRequiredPermission = requireAll
          ? requiredPermissions.every(permission => userPermissions.includes(permission))
          : requiredPermissions.some(permission => userPermissions.includes(permission));
        checks.push(hasRequiredPermission);
      }

      // If no requirements specified, allow access
      if (requiredRoles.length === 0 && requiredPermissions.length === 0) {
        setHasAccess(true);
        return;
      }

      // Determine final access based on requireAll setting
      const finalAccess = requireAll
        ? checks.every(check => check) // All checks must pass
        : checks.some(check => check);  // Any check can pass

      setHasAccess(finalAccess);
    };

    checkAccess();
  }, [user, userPermissions, permissionsLoaded, requiredPermissions, requiredRoles, requireAll]);

  // Handle access denial
  useEffect(() => {
    if (permissionsLoaded && !hasAccess && user && !fallbackComponent) {
      router.push('/login');
    }
  }, [hasAccess, permissionsLoaded, user, fallbackComponent, router]);

  // Show loading state while checking permissions
  if (!permissionsLoaded) {
    return null; // or a loading spinner
  }

  // If no user, don't render anything (will redirect to login)
  if (!user) {
    return fallbackComponent || null;
  }

  // If user doesn't have access, show fallback or redirect
  if (!hasAccess) {
    return fallbackComponent || null;
  }

  // User has access, render children
  return <>{children}</>;
};

export default ServiceRoleGate;

// Convenience components for common permission checks
export const ServiceCreateGate: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({ 
  children, 
  fallback 
}) => (
  <ServiceRoleGate 
    requiredPermissions={[SERVICE_PERMISSIONS.SERVICE_CREATE]}
    fallbackComponent={fallback}
  >
    {children}
  </ServiceRoleGate>
);

export const ServiceReadGate: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({ 
  children, 
  fallback 
}) => (
  <ServiceRoleGate 
    requiredPermissions={[SERVICE_PERMISSIONS.SERVICE_READ]}
    fallbackComponent={fallback}
  >
    {children}
  </ServiceRoleGate>
);

export const ServiceManageGate: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({ 
  children, 
  fallback 
}) => (
  <ServiceRoleGate 
    requiredPermissions={[
      SERVICE_PERMISSIONS.SERVICE_CREATE,
      SERVICE_PERMISSIONS.SERVICE_UPDATE,
      SERVICE_PERMISSIONS.SERVICE_DELETE
    ]}
    requireAll={false} // Any of these permissions grants access
    fallbackComponent={fallback}
  >
    {children}
  </ServiceRoleGate>
);

export const TechnicianManageGate: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({ 
  children, 
  fallback 
}) => (
  <ServiceRoleGate 
    requiredPermissions={[
      SERVICE_PERMISSIONS.TECHNICIAN_CREATE,
      SERVICE_PERMISSIONS.TECHNICIAN_UPDATE,
      SERVICE_PERMISSIONS.TECHNICIAN_DELETE
    ]}
    requireAll={false}
    fallbackComponent={fallback}
  >
    {children}
  </ServiceRoleGate>
);

export const AppointmentManageGate: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({ 
  children, 
  fallback 
}) => (
  <ServiceRoleGate 
    requiredPermissions={[
      SERVICE_PERMISSIONS.APPOINTMENT_CREATE,
      SERVICE_PERMISSIONS.APPOINTMENT_UPDATE,
      SERVICE_PERMISSIONS.APPOINTMENT_DELETE
    ]}
    requireAll={false}
    fallbackComponent={fallback}
  >
    {children}
  </ServiceRoleGate>
);

export const ServiceReportsGate: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({ 
  children, 
  fallback 
}) => (
  <ServiceRoleGate 
    requiredPermissions={[SERVICE_PERMISSIONS.SERVICE_REPORTS_READ]}
    fallbackComponent={fallback}
  >
    {children}
  </ServiceRoleGate>
);

export const CRMAdminGate: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({ 
  children, 
  fallback 
}) => (
  <ServiceRoleGate 
    requiredPermissions={[SERVICE_PERMISSIONS.CRM_ADMIN]}
    fallbackComponent={fallback}
  >
    {children}
  </ServiceRoleGate>
);