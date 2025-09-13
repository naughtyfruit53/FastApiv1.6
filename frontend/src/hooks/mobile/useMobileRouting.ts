import { useMobileDetection } from '../../hooks/useMobileDetection';

/**
 * Hook for mobile-specific routing and navigation
 */
export const useMobileRouting = () => {
  const { isMobile, isTablet } = useMobileDetection();

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

  return {
    getMobileRoute,
    isModalPreferred,
    getLayoutMode,
    isMobile,
    isTablet,
  };
};

export default useMobileRouting;