// frontend/src/hooks/useSharedPermissions.ts
import { useMemo, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

export interface Permission {
  module: string;
  action: string;
  resource?: string;
}

export interface UserPermissions {
  isSuperAdmin: boolean;
  isOrgSuperAdmin: boolean;
  role: string;
  permissions: string[];
  modules: string[];
}

export interface PermissionConfig {
  // Core modules
  dashboard: {
    view: boolean;
    viewAppStats: boolean;
    viewOrgStats: boolean;
  };
  finance: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    viewReports: boolean;
    manageBanks: boolean;
  };
  sales: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    manageCustomers: boolean;
    viewAnalytics: boolean;
  };
  crm: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    manageContacts: boolean;
    viewAnalytics: boolean;
  };
  inventory: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    manageStock: boolean;
    viewReports: boolean;
  };
  hr: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    manageEmployees: boolean;
    viewPayroll: boolean;
  };
  service: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    manageTickets: boolean;
    viewAnalytics: boolean;
  };
  reports: {
    view: boolean;
    export: boolean;
    schedule: boolean;
    viewFinancial: boolean;
    viewOperational: boolean;
  };
  settings: {
    view: boolean;
    manageUsers: boolean;
    manageRoles: boolean;
    manageOrganization: boolean;
    systemSettings: boolean;
  };
  admin: {
    superAdminOnly: boolean;
    manageOrganizations: boolean;
    manageLicenses: boolean;
    viewSystemStats: boolean;
    auditLogs: boolean;
  };
}

/**
 * Shared permissions hook for both desktop and mobile interfaces
 * Provides unified business logic for permission checking and role-based access control
 */
export const useSharedPermissions = () => {
  const { user } = useAuth();

  const userPermissions: UserPermissions = useMemo(() => {
    if (!user) {
      return {
        isSuperAdmin: false,
        isOrgSuperAdmin: false,
        role: 'guest',
        permissions: [],
        modules: [],
      };
    }

    const isSuperAdmin = user.is_super_admin || false;
    const isOrgSuperAdmin = user.role === 'super_admin' || user.role === 'admin';

    // TODO: Integrate with real RBAC service to get user permissions
    // For now, using role-based permissions
    let permissions: string[] = [];
    let modules: string[] = [];

    if (isSuperAdmin) {
      // Super admin has all permissions
      permissions = [
        'dashboard.*',
        'finance.*',
        'sales.*',
        'crm.*',
        'inventory.*',
        'hr.*',
        'service.*',
        'reports.*',
        'settings.*',
        'admin.*',
      ];
      modules = ['dashboard', 'finance', 'sales', 'crm', 'inventory', 'hr', 'service', 'reports', 'settings', 'admin'];
    } else if (isOrgSuperAdmin) {
      // Organization admin has most permissions except super admin functions
      permissions = [
        'dashboard.*',
        'finance.*',
        'sales.*',
        'crm.*',
        'inventory.*',
        'hr.*',
        'service.*',
        'reports.*',
        'settings.view',
        'settings.manageUsers',
        'settings.manageRoles',
        'settings.manageOrganization',
      ];
      modules = ['dashboard', 'finance', 'sales', 'crm', 'inventory', 'hr', 'service', 'reports', 'settings'];
    } else {
      // Regular user - permissions based on role
      switch (user.role) {
        case 'finance_manager':
          permissions = ['dashboard.view', 'finance.*', 'reports.viewFinancial'];
          modules = ['dashboard', 'finance', 'reports'];
          break;
        case 'sales_manager':
          permissions = ['dashboard.view', 'sales.*', 'crm.*', 'reports.viewOperational'];
          modules = ['dashboard', 'sales', 'crm', 'reports'];
          break;
        case 'inventory_manager':
          permissions = ['dashboard.view', 'inventory.*', 'reports.viewOperational'];
          modules = ['dashboard', 'inventory', 'reports'];
          break;
        case 'hr_manager':
          permissions = ['dashboard.view', 'hr.*', 'reports.viewOperational'];
          modules = ['dashboard', 'hr', 'reports'];
          break;
        case 'service_manager':
          permissions = ['dashboard.view', 'service.*', 'reports.viewOperational'];
          modules = ['dashboard', 'service', 'reports'];
          break;
        case 'user':
        case 'employee':
        default:
          permissions = ['dashboard.view'];
          modules = ['dashboard'];
          break;
      }
    }

    return {
      isSuperAdmin,
      isOrgSuperAdmin,
      role: user.role || 'user',
      permissions,
      modules,
    };
  }, [user]);

  const hasPermission = useCallback((permission: string): boolean => {
    if (!user || !userPermissions.permissions.length) return false;
    
    // Super admin has all permissions
    if (userPermissions.isSuperAdmin) return true;

    // Check exact permission match
    if (userPermissions.permissions.includes(permission)) return true;

    // Check wildcard permissions (e.g., 'finance.*' matches 'finance.view')
    const wildcardPermissions = userPermissions.permissions.filter(p => p.endsWith('.*'));
    for (const wildcardPerm of wildcardPermissions) {
      const module = wildcardPerm.replace('.*', '');
      if (permission.startsWith(`${module}.`)) return true;
    }

    return false;
  }, [user, userPermissions]);

  const hasModuleAccess = useCallback((module: string): boolean => {
    if (!user) return false;
    if (userPermissions.isSuperAdmin) return true;
    return userPermissions.modules.includes(module);
  }, [user, userPermissions]);

  const canAccessRoute = useCallback((route: string): boolean => {
    if (!user) return false;

    // Parse route to determine required permissions
    const routeSegments = route.split('/').filter(Boolean);
    if (routeSegments.length === 0) return true;

    const module = routeSegments[0];
    
    // Special handling for mobile routes
    if (module === 'mobile' && routeSegments.length > 1) {
      return hasModuleAccess(routeSegments[1]);
    }

    // Special handling for admin routes
    if (module === 'admin') {
      return userPermissions.isSuperAdmin;
    }

    return hasModuleAccess(module);
  }, [user, userPermissions, hasModuleAccess]);

  const getPermissionConfig = useCallback((): PermissionConfig => {
    return {
      dashboard: {
        view: hasPermission('dashboard.view'),
        viewAppStats: hasPermission('dashboard.viewAppStats') || userPermissions.isSuperAdmin,
        viewOrgStats: hasPermission('dashboard.viewOrgStats') || !userPermissions.isSuperAdmin,
      },
      finance: {
        view: hasPermission('finance.view'),
        create: hasPermission('finance.create'),
        edit: hasPermission('finance.edit'),
        delete: hasPermission('finance.delete'),
        viewReports: hasPermission('finance.viewReports'),
        manageBanks: hasPermission('finance.manageBanks'),
      },
      sales: {
        view: hasPermission('sales.view'),
        create: hasPermission('sales.create'),
        edit: hasPermission('sales.edit'),
        delete: hasPermission('sales.delete'),
        manageCustomers: hasPermission('sales.manageCustomers'),
        viewAnalytics: hasPermission('sales.viewAnalytics'),
      },
      crm: {
        view: hasPermission('crm.view'),
        create: hasPermission('crm.create'),
        edit: hasPermission('crm.edit'),
        delete: hasPermission('crm.delete'),
        manageContacts: hasPermission('crm.manageContacts'),
        viewAnalytics: hasPermission('crm.viewAnalytics'),
      },
      inventory: {
        view: hasPermission('inventory.view'),
        create: hasPermission('inventory.create'),
        edit: hasPermission('inventory.edit'),
        delete: hasPermission('inventory.delete'),
        manageStock: hasPermission('inventory.manageStock'),
        viewReports: hasPermission('inventory.viewReports'),
      },
      hr: {
        view: hasPermission('hr.view'),
        create: hasPermission('hr.create'),
        edit: hasPermission('hr.edit'),
        delete: hasPermission('hr.delete'),
        manageEmployees: hasPermission('hr.manageEmployees'),
        viewPayroll: hasPermission('hr.viewPayroll'),
      },
      service: {
        view: hasPermission('service.view'),
        create: hasPermission('service.create'),
        edit: hasPermission('service.edit'),
        delete: hasPermission('service.delete'),
        manageTickets: hasPermission('service.manageTickets'),
        viewAnalytics: hasPermission('service.viewAnalytics'),
      },
      reports: {
        view: hasPermission('reports.view'),
        export: hasPermission('reports.export'),
        schedule: hasPermission('reports.schedule'),
        viewFinancial: hasPermission('reports.viewFinancial'),
        viewOperational: hasPermission('reports.viewOperational'),
      },
      settings: {
        view: hasPermission('settings.view'),
        manageUsers: hasPermission('settings.manageUsers'),
        manageRoles: hasPermission('settings.manageRoles'),
        manageOrganization: hasPermission('settings.manageOrganization'),
        systemSettings: hasPermission('settings.systemSettings'),
      },
      admin: {
        superAdminOnly: userPermissions.isSuperAdmin,
        manageOrganizations: hasPermission('admin.manageOrganizations'),
        manageLicenses: hasPermission('admin.manageLicenses'),
        viewSystemStats: hasPermission('admin.viewSystemStats'),
        auditLogs: hasPermission('admin.auditLogs'),
      },
    };
  }, [hasPermission, userPermissions]);

  const validateAction = useCallback((
    module: string, 
    action: string, 
    options?: { 
      requireOrgAdmin?: boolean;
      requireSuperAdmin?: boolean;
    }
  ): { allowed: boolean; reason?: string } => {
    if (!user) {
      return { allowed: false, reason: 'Authentication required' };
    }

    if (options?.requireSuperAdmin && !userPermissions.isSuperAdmin) {
      return { allowed: false, reason: 'Super administrator privileges required' };
    }

    if (options?.requireOrgAdmin && !userPermissions.isOrgSuperAdmin && !userPermissions.isSuperAdmin) {
      return { allowed: false, reason: 'Administrator privileges required' };
    }

    const permission = `${module}.${action}`;
    if (!hasPermission(permission)) {
      return { allowed: false, reason: `Permission '${permission}' required` };
    }

    return { allowed: true };
  }, [user, userPermissions, hasPermission]);

  // Get navigation items based on permissions
  const getNavigationItems = useCallback(() => {
    if (!user) return [];

    const items = [];

    if (hasModuleAccess('dashboard')) {
      items.push({
        name: 'Dashboard',
        path: '/dashboard',
        mobilePath: '/mobile/dashboard',
        icon: 'dashboard',
      });
    }

    if (hasModuleAccess('finance')) {
      items.push({
        name: 'Finance',
        path: '/finance-dashboard',
        mobilePath: '/mobile/finance',
        icon: 'account_balance',
      });
    }

    if (hasModuleAccess('sales')) {
      items.push({
        name: 'Sales',
        path: '/sales/dashboard',
        mobilePath: '/mobile/sales',
        icon: 'trending_up',
      });
    }

    if (hasModuleAccess('crm')) {
      items.push({
        name: 'CRM',
        path: '/crm',
        mobilePath: '/mobile/crm',
        icon: 'people',
      });
    }

    if (hasModuleAccess('inventory')) {
      items.push({
        name: 'Inventory',
        path: '/inventory',
        mobilePath: '/mobile/inventory',
        icon: 'inventory',
      });
    }

    if (hasModuleAccess('hr')) {
      items.push({
        name: 'HR',
        path: '/hr/dashboard',
        mobilePath: '/mobile/hr',
        icon: 'group',
      });
    }

    if (hasModuleAccess('service')) {
      items.push({
        name: 'Service',
        path: '/service/dashboard',
        mobilePath: '/mobile/service',
        icon: 'support',
      });
    }

    if (hasModuleAccess('reports')) {
      items.push({
        name: 'Reports',
        path: '/reports',
        mobilePath: '/mobile/reports',
        icon: 'assessment',
      });
    }

    if (hasModuleAccess('settings')) {
      items.push({
        name: 'Settings',
        path: '/settings',
        mobilePath: '/mobile/settings',
        icon: 'settings',
      });
    }

    if (userPermissions.isSuperAdmin) {
      items.push({
        name: 'Admin',
        path: '/admin',
        mobilePath: '/admin', // Admin stays desktop-only for now
        icon: 'admin_panel_settings',
      });
    }

    return items;
  }, [user, hasModuleAccess, userPermissions]);

  return {
    user,
    userPermissions,
    hasPermission,
    hasModuleAccess,
    canAccessRoute,
    validateAction,
    getPermissionConfig,
    getNavigationItems,
  };
};

export default useSharedPermissions;