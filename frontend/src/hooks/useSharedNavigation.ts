// frontend/src/hooks/useSharedNavigation.ts
import { useCallback, useMemo } from 'react';
import { useRouter } from 'next/router';
import { useMobileDetection } from './useMobileDetection';
import useSharedPermissions from './useSharedPermissions';

export interface NavigationItem {
  id: string;
  name: string;
  path: string;
  mobilePath: string;
  icon: string;
  badge?: number;
  color?: string;
  description?: string;
  children?: NavigationItem[];
  permission?: string;
  superAdminOnly?: boolean;
  requiresOrgAdmin?: boolean;
}

export interface QuickAction {
  id: string;
  name: string;
  icon: string;
  color?: string;
  path?: string;
  action?: () => void;
  permission?: string;
}

/**
 * Shared navigation hook for both desktop and mobile interfaces
 * Provides unified business logic for navigation, routing, and quick actions
 */
export const useSharedNavigation = () => {
  const router = useRouter();
  const { isMobile, isTablet } = useMobileDetection();
  const { 
    userPermissions, 
    hasPermission, 
    hasModuleAccess, 
    canAccessRoute,
    getNavigationItems: getPermissionBasedNavigation 
  } = useSharedPermissions();

  // Get current active route
  const currentRoute = router.pathname;
  const currentMobileRoute = currentRoute.startsWith('/mobile/') 
    ? currentRoute 
    : `/mobile${currentRoute}`;

  // Core navigation items with permission checking
  const coreNavigationItems = useMemo<NavigationItem[]>(() => {
    const items: NavigationItem[] = [
      {
        id: 'dashboard',
        name: 'Dashboard',
        path: '/dashboard',
        mobilePath: '/mobile/dashboard',
        icon: 'dashboard',
        description: 'Overview and key metrics',
        permission: 'dashboard.view',
      },
      {
        id: 'finance',
        name: 'Finance',
        path: '/finance-dashboard',
        mobilePath: '/mobile/finance',
        icon: 'account_balance',
        description: 'Financial management and reporting',
        permission: 'finance.view',
        children: [
          {
            id: 'finance-dashboard',
            name: 'Finance Dashboard',
            path: '/finance-dashboard',
            mobilePath: '/mobile/finance',
            icon: 'dashboard',
            permission: 'finance.view',
          },
          {
            id: 'accounts-payable',
            name: 'Accounts Payable',
            path: '/accounts-payable',
            mobilePath: '/mobile/finance?tab=payable',
            icon: 'payment',
            permission: 'finance.view',
          },
          {
            id: 'accounts-receivable',
            name: 'Accounts Receivable',
            path: '/accounts-receivable',
            mobilePath: '/mobile/finance?tab=receivable',
            icon: 'account_balance_wallet',
            permission: 'finance.view',
          },
        ],
      },
      {
        id: 'sales',
        name: 'Sales',
        path: '/sales/dashboard',
        mobilePath: '/mobile/sales',
        icon: 'trending_up',
        description: 'Sales management and pipeline',
        permission: 'sales.view',
        children: [
          {
            id: 'sales-dashboard',
            name: 'Sales Dashboard',
            path: '/sales/dashboard',
            mobilePath: '/mobile/sales',
            icon: 'dashboard',
            permission: 'sales.view',
          },
          {
            id: 'sales-leads',
            name: 'Leads',
            path: '/sales/leads',
            mobilePath: '/mobile/sales?tab=leads',
            icon: 'person_add',
            permission: 'sales.view',
          },
          {
            id: 'sales-opportunities',
            name: 'Opportunities',
            path: '/sales/opportunities',
            mobilePath: '/mobile/sales?tab=opportunities',
            icon: 'star',
            permission: 'sales.view',
          },
        ],
      },
      {
        id: 'crm',
        name: 'CRM',
        path: '/crm',
        mobilePath: '/mobile/crm',
        icon: 'people',
        description: 'Customer relationship management',
        permission: 'crm.view',
      },
      {
        id: 'inventory',
        name: 'Inventory',
        path: '/inventory',
        mobilePath: '/mobile/inventory',
        icon: 'inventory',
        description: 'Stock and inventory management',
        permission: 'inventory.view',
      },
      {
        id: 'hr',
        name: 'HR',
        path: '/hr/dashboard',
        mobilePath: '/mobile/hr',
        icon: 'group',
        description: 'Human resources management',
        permission: 'hr.view',
      },
      {
        id: 'service',
        name: 'Service',
        path: '/service/dashboard',
        mobilePath: '/mobile/service',
        icon: 'support',
        description: 'Service desk and support',
        permission: 'service.view',
      },
      {
        id: 'reports',
        name: 'Reports',
        path: '/reports',
        mobilePath: '/mobile/reports',
        icon: 'assessment',
        description: 'Analytics and reporting',
        permission: 'reports.view',
      },
      {
        id: 'settings',
        name: 'Settings',
        path: '/settings',
        mobilePath: '/mobile/settings',
        icon: 'settings',
        description: 'System configuration',
        permission: 'settings.view',
      },
    ];

    // Add admin section for super admins
    if (userPermissions.isSuperAdmin) {
      items.push({
        id: 'admin',
        name: 'Admin',
        path: '/admin',
        mobilePath: '/admin', // Admin stays desktop-only for now
        icon: 'admin_panel_settings',
        description: 'System administration',
        superAdminOnly: true,
        permission: 'admin.view',
      });
    }

    return items;
  }, [userPermissions.isSuperAdmin]);

  // Filter navigation items based on permissions
  const filteredNavigationItems = useMemo(() => {
    return coreNavigationItems.filter(item => {
      // Check super admin requirement
      if (item.superAdminOnly && !userPermissions.isSuperAdmin) {
        return false;
      }

      // Check org admin requirement
      if (item.requiresOrgAdmin && !userPermissions.isOrgSuperAdmin && !userPermissions.isSuperAdmin) {
        return false;
      }

      // Check permission
      if (item.permission && !hasPermission(item.permission)) {
        return false;
      }

      // Filter children as well
      if (item.children) {
        item.children = item.children.filter(child => {
          if (child.permission && !hasPermission(child.permission)) {
            return false;
          }
          return true;
        });
      }

      return true;
    });
  }, [coreNavigationItems, userPermissions, hasPermission]);

  // Get quick actions based on current page and permissions
  const getQuickActions = useCallback((): QuickAction[] => {
    const actions: QuickAction[] = [];

    // Dashboard quick actions
    if (currentRoute.includes('dashboard')) {
      if (hasPermission('finance.create')) {
        actions.push({
          id: 'new-transaction',
          name: 'New Transaction',
          icon: 'add_circle',
          color: 'primary',
          path: isMobile ? '/mobile/finance?action=create' : '/finance/transactions/create',
        });
      }
      if (hasPermission('sales.create')) {
        actions.push({
          id: 'new-lead',
          name: 'New Lead',
          icon: 'person_add',
          color: 'success',
          path: isMobile ? '/mobile/sales?action=create' : '/sales/leads/create',
        });
      }
    }

    // Finance quick actions
    if (currentRoute.includes('finance')) {
      if (hasPermission('finance.create')) {
        actions.push(
          {
            id: 'receipt-entry',
            name: 'Receipt Entry',
            icon: 'trending_up',
            color: 'success',
            path: '/finance/receipts/create',
          },
          {
            id: 'payment-entry',
            name: 'Payment Entry',
            icon: 'trending_down',
            color: 'error',
            path: '/finance/payments/create',
          }
        );
      }
    }

    // Sales quick actions
    if (currentRoute.includes('sales')) {
      if (hasPermission('sales.create')) {
        actions.push(
          {
            id: 'add-lead',
            name: 'Add Lead',
            icon: 'person_add',
            color: 'primary',
            path: '/sales/leads/create',
          },
          {
            id: 'create-opportunity',
            name: 'New Opportunity',
            icon: 'star',
            color: 'warning',
            path: '/sales/opportunities/create',
          }
        );
      }
    }

    // CRM quick actions
    if (currentRoute.includes('crm')) {
      if (hasPermission('crm.create')) {
        actions.push(
          {
            id: 'add-contact',
            name: 'Add Contact',
            icon: 'person_add',
            color: 'primary',
            path: '/crm/contacts/create',
          },
          {
            id: 'log-activity',
            name: 'Log Activity',
            icon: 'event_note',
            color: 'info',
            path: '/crm/activities/create',
          }
        );
      }
    }

    return actions;
  }, [currentRoute, hasPermission, isMobile]);

  // Navigate to appropriate path based on device
  const navigateTo = useCallback((item: NavigationItem) => {
    const targetPath = isMobile ? item.mobilePath : item.path;
    
    // Check if user can access the route
    if (!canAccessRoute(targetPath)) {
      console.warn(`Access denied to route: ${targetPath}`);
      return;
    }

    router.push(targetPath);
  }, [router, isMobile, canAccessRoute]);

  // Get breadcrumb navigation
  const getBreadcrumbs = useCallback(() => {
    const pathSegments = currentRoute.split('/').filter(Boolean);
    const breadcrumbs = [];

    // Handle mobile routes
    if (pathSegments[0] === 'mobile') {
      breadcrumbs.push({ name: 'Mobile', path: '/mobile/dashboard' });
      pathSegments.shift(); // Remove 'mobile' from segments
    }

    // Build breadcrumbs from remaining segments
    let currentPath = '';
    for (const segment of pathSegments) {
      currentPath += `/${segment}`;
      
      // Find matching navigation item
      const navItem = filteredNavigationItems.find(item => 
        item.path.includes(segment) || item.mobilePath.includes(segment)
      );
      
      if (navItem) {
        breadcrumbs.push({
          name: navItem.name,
          path: isMobile ? navItem.mobilePath : navItem.path,
        });
      } else {
        // Fallback to formatted segment name
        breadcrumbs.push({
          name: segment.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()),
          path: currentPath,
        });
      }
    }

    return breadcrumbs;
  }, [currentRoute, filteredNavigationItems, isMobile]);

  // Check if current route is active
  const isActiveRoute = useCallback((path: string) => {
    if (isMobile) {
      return currentRoute === path || currentMobileRoute === path;
    }
    return currentRoute === path;
  }, [currentRoute, currentMobileRoute, isMobile]);

  // Get mobile bottom navigation items
  const getMobileBottomNavItems = useCallback(() => {
    return filteredNavigationItems
      .filter(item => ['dashboard', 'finance', 'sales', 'crm', 'inventory'].includes(item.id))
      .slice(0, 5) // Limit to 5 items for mobile bottom nav
      .map(item => ({
        ...item,
        isActive: isActiveRoute(item.mobilePath),
      }));
  }, [filteredNavigationItems, isActiveRoute]);

  return {
    navigationItems: filteredNavigationItems,
    quickActions: getQuickActions(),
    currentRoute,
    currentMobileRoute,
    navigateTo,
    getBreadcrumbs,
    isActiveRoute,
    getMobileBottomNavItems,
    userPermissions,
    isMobile,
    isTablet,
  };
};

export default useSharedNavigation;