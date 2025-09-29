import { useMobileDetection } from '../../hooks/useMobileDetection';
import { useRouter } from 'next/router';
import { useMemo } from 'react';

/**
 * Hook for mobile-specific routing and navigation
 */
export const useMobileRouting = () => {
  const { isMobile, isTablet } = useMobileDetection();
  const router = useRouter();

  const getMobileRoute = (desktopRoute: string): string => {
    // Convert desktop routes to mobile-optimized routes
    const mobileRoutes: Record<string, string> = {
      '/dashboard': '/mobile/dashboard',
      '/sales/dashboard': '/mobile/sales',
      '/finance-dashboard': '/mobile/finance',
      '/hr/dashboard': '/mobile/hr',
      '/inventory': '/mobile/inventory',
      '/crm': '/mobile/crm',
      '/service/dashboard': '/mobile/service',
      '/reports': '/mobile/reports',
      '/settings': '/mobile/settings',
      '/marketing': '/mobile/marketing',
      // Add more desktop to mobile route mappings
      '/sales': '/mobile/sales',
      '/finance': '/mobile/finance',
      '/hr': '/mobile/hr',
      '/service': '/mobile/service',
      '/admin': '/settings', // Admin routes go to settings on mobile
      '/projects': '/mobile/dashboard', // Projects to dashboard for now
      '/calendar': '/mobile/dashboard', // Calendar to dashboard for now
      '/vouchers': '/mobile/finance', // Vouchers to finance
      '/accounts': '/mobile/finance', // Accounts to finance
    };

    return isMobile ? (mobileRoutes[desktopRoute] || desktopRoute) : desktopRoute;
  };

  const isModalPreferred = (screenType: 'modal' | 'page' = 'modal'): boolean => {
    return isMobile && screenType === 'modal';
  };

  const getLayoutMode = (): 'mobile' | 'tablet' | 'desktop' => {
    if (isMobile) return 'mobile';
    if (isTablet) return 'tablet';
    return 'desktop';
  };

  const getBreadcrumbs = () => {
    const path = router.pathname;
    const segments = path.split('/').filter(Boolean);
    
    const breadcrumbs = [
      { label: 'Home', path: '/mobile/dashboard' }
    ];

    // Build breadcrumbs based on current path
    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      
      // Skip 'mobile' segment
      if (segment === 'mobile') return;
      
      const label = segment.charAt(0).toUpperCase() + segment.slice(1).replace('-', ' ');
      
      breadcrumbs.push({
        label,
        path: currentPath,
        current: index === segments.length - 1
      });
    });

    return breadcrumbs;
  };

  const getPageInfo = () => {
    const path = router.pathname;
    
    // Define page information for mobile pages
    const pageInfoMap: Record<string, { title: string; subtitle?: string; category: string }> = {
      '/mobile/dashboard': { title: 'Dashboard', subtitle: 'Overview and metrics', category: 'Core' },
      '/mobile/sales': { title: 'Sales', subtitle: 'Leads and opportunities', category: 'Core' },
      '/mobile/crm': { title: 'CRM', subtitle: 'Customer management', category: 'Core' },
      '/mobile/finance': { title: 'Finance', subtitle: 'Financial management', category: 'Core' },
      '/mobile/inventory': { title: 'Inventory', subtitle: 'Stock management', category: 'Core' },
      '/mobile/hr': { title: 'HR', subtitle: 'Employee management', category: 'Core' },
      '/mobile/service': { title: 'Service', subtitle: 'Service management', category: 'Core' },
      '/mobile/reports': { title: 'Reports', subtitle: 'Analytics and reports', category: 'Core' },
      '/mobile/settings': { title: 'Settings', subtitle: 'Preferences and config', category: 'Core' },
      '/mobile/marketing': { title: 'Marketing', subtitle: 'Campaigns and analytics', category: 'Core' },
    };

    return pageInfoMap[path] || { title: 'Page', category: 'Other' };
  };

  const navigateToMobile = (desktopRoute: string) => {
    const mobileRoute = getMobileRoute(desktopRoute);
    router.push(mobileRoute);
  };

  const canGoBack = () => {
    return router.asPath !== '/mobile/dashboard';
  };

  const goBack = () => {
    if (canGoBack()) {
      router.back();
    } else {
      router.push('/mobile/dashboard');
    }
  };

  const goHome = () => {
    router.push('/mobile/dashboard');
  };

  // Available mobile routes for navigation
  const availableMobileRoutes = useMemo(() => [
    { name: 'Dashboard', path: '/mobile/dashboard', icon: 'dashboard' },
    { name: 'Sales', path: '/mobile/sales', icon: 'sales' },
    { name: 'CRM', path: '/mobile/crm', icon: 'people' },
    { name: 'Finance', path: '/mobile/finance', icon: 'finance' },
    { name: 'Inventory', path: '/mobile/inventory', icon: 'inventory' },
    { name: 'HR', path: '/mobile/hr', icon: 'hr' },
    { name: 'Service', path: '/mobile/service', icon: 'service' },
    { name: 'Reports', path: '/mobile/reports', icon: 'reports' },
    { name: 'Marketing', path: '/mobile/marketing', icon: 'marketing' },
    { name: 'Settings', path: '/mobile/settings', icon: 'settings' },
  ], []);

  return {
    getMobileRoute,
    isModalPreferred,
    getLayoutMode,
    getBreadcrumbs,
    getPageInfo,
    navigateToMobile,
    canGoBack,
    goBack,
    goHome,
    availableMobileRoutes,
    isMobile,
    isTablet,
    currentPath: router.pathname,
    currentQuery: router.query,
  };
};

export default useMobileRouting;