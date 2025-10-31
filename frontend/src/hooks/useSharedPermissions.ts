// frontend/src/hooks/useSharedPermissions.ts
import { useMemo, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { hasNormalizedPermission as checkNormalizedPermission } from '../utils/permissionNormalizer';

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
  submodules: Record<string, string[]>;
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
 * Now integrates with AuthContext for real-time RBAC data
 */
export const useSharedPermissions = () => {
  const { user, userPermissions: contextPermissions } = useAuth();

  const userPermissions: UserPermissions = useMemo(() => {
    if (!user) {
      return {
        isSuperAdmin: false,
        isOrgSuperAdmin: false,
        role: 'guest',
        permissions: [],
        modules: [],
        submodules: {},
      };
    }

    const isSuperAdmin = user.is_super_admin || false;
    const isOrgSuperAdmin = ['super_admin', 'admin', 'org_admin', 'management'].includes(user.role || '');

    // Use permissions from AuthContext if available
    if (contextPermissions) {
      let modules = contextPermissions.modules || [];
      let submodules = contextPermissions.submodules || {};
      if (modules.length === 0) {
        modules = [...new Set(contextPermissions.permissions.map(p => p.split('_')[0]))];
      }
      return {
        isSuperAdmin,
        isOrgSuperAdmin,
        role: contextPermissions.role || user.role || 'user',
        permissions: contextPermissions.permissions,
        modules,
        submodules,
      };
    }

    // Fallback to role-based permissions for backward compatibility
    let permissions: string[] = [];
    let modules: string[] = [];
    let submodules: Record<string, string[]> = {};

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
        'master_data.*',
        'manufacturing.*',
        'vouchers.*',
        'accounting.*',
        'reportsAnalytics.*',
        'aiAnalytics.*',
        'marketing.*',
        'projects.*',
        'tasks_calendar.*',
        'email.*',
      ];
      modules = [
        'dashboard', 'finance', 'sales', 'crm', 'inventory', 'hr', 'service', 'reports', 'settings', 'admin',
        'master_data', 'manufacturing', 'vouchers', 'accounting', 'reportsAnalytics', 'aiAnalytics',
        'marketing', 'projects', 'tasks_calendar', 'email'
      ];
      submodules = modules.reduce((acc, mod) => {
        acc[mod] = ['all'];
        return acc;
      }, {} as Record<string, string[]>);
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
        'master_data.*',
        'manufacturing.*',
        'vouchers.*',
        'accounting.*',
        'reportsAnalytics.*',
        'aiAnalytics.*',
        'marketing.*',
        'projects.*',
        'tasks_calendar.*',
        'email.*',
      ];
      modules = [
        'dashboard', 'finance', 'sales', 'crm', 'inventory', 'hr', 'service', 'reports', 'settings',
        'master_data', 'manufacturing', 'vouchers', 'accounting', 'reportsAnalytics', 'aiAnalytics',
        'marketing', 'projects', 'tasks_calendar', 'email'
      ];
      submodules = modules.reduce((acc, mod) => {
        acc[mod] = ['all'];
        return acc;
      }, {} as Record<string, string[]>);
    } else {
      // Regular user - permissions based on role
      switch (user.role) {
        case 'finance_manager':
          permissions = ['dashboard.view', 'finance.*', 'reports.viewFinancial'];
          modules = ['dashboard', 'finance', 'reports'];
          submodules = {
            dashboard: ['view'],
            finance: ['view', 'create', 'edit', 'delete', 'viewReports', 'manageBanks'],
            reports: ['viewFinancial'],
          };
          break;
        case 'sales_manager':
          permissions = ['dashboard.view', 'sales.*', 'crm.*', 'reports.viewOperational'];
          modules = ['dashboard', 'sales', 'crm', 'reports'];
          submodules = {
            dashboard: ['view'],
            sales: ['view', 'create', 'edit', 'delete', 'manageCustomers', 'viewAnalytics'],
            crm: ['view', 'create', 'edit', 'delete', 'manageContacts', 'viewAnalytics'],
            reports: ['viewOperational'],
          };
          break;
        case 'inventory_manager':
          permissions = ['dashboard.view', 'inventory.*', 'reports.viewOperational'];
          modules = ['dashboard', 'inventory', 'reports'];
          submodules = {
            dashboard: ['view'],
            inventory: ['view', 'create', 'edit', 'delete', 'manageStock', 'viewReports'],
            reports: ['viewOperational'],
          };
          break;
        case 'hr_manager':
          permissions = ['dashboard.view', 'hr.*', 'reports.viewOperational'];
          modules = ['dashboard', 'hr', 'reports'];
          submodules = {
            dashboard: ['view'],
            hr: ['view', 'create', 'edit', 'delete', 'manageEmployees', 'viewPayroll'],
            reports: ['viewOperational'],
          };
          break;
        case 'service_manager':
          permissions = ['dashboard.view', 'service.*', 'reports.viewOperational'];
          modules = ['dashboard', 'service', 'reports'];
          submodules = {
            dashboard: ['view'],
            service: ['view', 'create', 'edit', 'delete', 'manageTickets', 'viewAnalytics'],
            reports: ['viewOperational'],
          };
          break;
        case 'user':
        case 'employee':
        default:
          permissions = [
            'dashboard.view',
            'master_data.view',
            'inventory.view',
            'manufacturing.view',
            'vouchers.view',
            'finance.view',
            'accounting.view',
            'reportsAnalytics.view',
            'aiAnalytics.view',
            'sales.view',
            'marketing.view',
            'service.view',
            'projects.view',
            'hrManagement.view',
            'tasksCalendar.view',
            'email.view',
          ];
          modules = [
            'dashboard', 'master_data', 'inventory', 'manufacturing', 'vouchers',
            'finance', 'accounting', 'reportsAnalytics', 'aiAnalytics', 'sales',
            'marketing', 'service', 'projects', 'hrManagement', 'tasksCalendar', 'email'
          ];
          submodules = modules.reduce((acc, mod) => {
            acc[mod] = ['view'];
            return acc;
          }, {} as Record<string, string[]>);
          break;
      }
    }

    return {
      isSuperAdmin,
      isOrgSuperAdmin,
      role: user.role || 'user',
      permissions,
      modules,
      submodules,
    };
  }, [user, contextPermissions]);

  const hasPermission = useCallback((moduleOrPermission: string, action?: string): boolean => {
    if (!user || !userPermissions.permissions.length) return false;
    
    // Super admin has all permissions
    if (userPermissions.isSuperAdmin) return true;

    // Support both signatures:
    // 1. hasPermission('finance.view') - single string
    // 2. hasPermission('finance', 'view') - separate parameters
    const permission = action ? `${moduleOrPermission}.${action}` : moduleOrPermission;

    // Use normalized permission checking which handles backend → frontend mapping
    return checkNormalizedPermission(userPermissions.permissions, permission);
  }, [user, userPermissions]);

  const hasModuleAccess = useCallback((module: string): boolean => {
    if (!user) return false;
    if (userPermissions.isSuperAdmin) return true;
    return userPermissions.modules.includes(module);
  }, [user, userPermissions]);

  const hasSubmoduleAccess = useCallback((module: string, submodule: string): boolean => {
    if (!user) return false;
    if (userPermissions.isSuperAdmin) return true;
    
    // Check if we have contextPermissions with submodule data
    if (contextPermissions?.submodules && contextPermissions.submodules[module]) {
      const subs = contextPermissions.submodules[module];
      if (subs.includes('all')) return true;
      return subs.includes(submodule);
    }
    
    // Return false if no submodule data and no module access
    return hasModuleAccess(module);
  }, [user, userPermissions, contextPermissions, hasModuleAccess]);

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
    hasSubmoduleAccess,
    canAccessRoute,
    validateAction,
    getPermissionConfig,
    getNavigationItems,
  };
};

export default useSharedPermissions;