import { ReactNode } from 'react';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface DeviceConditionalProps {
  children: ReactNode;
  mobile?: ReactNode;
  tablet?: ReactNode;
  desktop?: ReactNode;
}

/**
 * Component that conditionally renders content based on device type
 * Allows for seamless mobile/desktop UI switching
 */
export const DeviceConditional: React.FC<DeviceConditionalProps> = ({
  children,
  mobile,
  tablet,
  desktop,
}) => {
  const { isMobile, isTablet, isDesktop } = useMobileDetection();

  if (isMobile && mobile) return <>{mobile}</>;
  if (isTablet && tablet) return <>{tablet}</>;
  if (isDesktop && desktop) return <>{desktop}</>;
  
  return <>{children}</>;
};

/**
 * HOC for creating mobile-aware components
 */
export const withMobileDetection = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return (props: P) => {
    const deviceInfo = useMobileDetection();
    return <Component {...props} deviceInfo={deviceInfo} />;
  };
};

/**
 * Utility function to get responsive values
 */
export const getResponsiveValue = <T>(
  mobileValue: T,
  tabletValue: T,
  desktopValue: T,
  isMobile: boolean,
  isTablet: boolean
): T => {
  if (isMobile) return mobileValue;
  if (isTablet) return tabletValue;
  return desktopValue;
};

export default DeviceConditional;