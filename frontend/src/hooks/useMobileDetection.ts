import { useState, useEffect } from 'react';
import { useMediaQuery, useTheme } from '@mui/material';

interface MobileDetectionState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  orientation: 'portrait' | 'landscape';
  screenWidth: number;
  screenHeight: number;
  pixelRatio: number;
  touchDevice: boolean;
}

/**
 * Custom hook for detecting mobile devices, screen orientation, and device characteristics
 * Provides comprehensive device detection for optimal UX
 */
export const useMobileDetection = (): MobileDetectionState => {
  const theme = useTheme();
  
  // Material-UI breakpoint detection
  const isMobileBreakpoint = useMediaQuery(theme.breakpoints.down('md'));
  const isTabletBreakpoint = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  const isDesktopBreakpoint = useMediaQuery(theme.breakpoints.up('md'));

  const [detectionState, setDetectionState] = useState<MobileDetectionState>({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    orientation: 'landscape',
    screenWidth: 1920,
    screenHeight: 1080,
    pixelRatio: 1,
    touchDevice: false,
  });

  useEffect(() => {
    const updateDetectionState = () => {
      const screenWidth = window.innerWidth;
      const screenHeight = window.innerHeight;
      const pixelRatio = window.devicePixelRatio || 1;
      
      // Detect orientation
      const orientation = screenHeight > screenWidth ? 'portrait' : 'landscape';
      
      // Touch device detection
      const touchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      
      // Enhanced mobile detection
      const isMobile = screenWidth <= 768 || isMobileBreakpoint || touchDevice;
      const isTablet = screenWidth > 768 && screenWidth <= 1024 && touchDevice;
      const isDesktop = screenWidth > 1024 && !touchDevice;

      setDetectionState({
        isMobile,
        isTablet,
        isDesktop,
        orientation,
        screenWidth,
        screenHeight,
        pixelRatio,
        touchDevice,
      });
    };

    // Initial detection
    updateDetectionState();

    // Listen for resize and orientation changes
    window.addEventListener('resize', updateDetectionState);
    window.addEventListener('orientationchange', updateDetectionState);

    // Cleanup
    return () => {
      window.removeEventListener('resize', updateDetectionState);
      window.removeEventListener('orientationchange', updateDetectionState);
    };
  }, [isMobileBreakpoint]);

  return detectionState;
};

/**
 * Utility hook for responsive values based on device type
 */
export const useResponsiveValue = <T>(
  mobileValue: T,
  tabletValue: T,
  desktopValue: T
): T => {
  const { isMobile, isTablet } = useMobileDetection();
  
  if (isMobile) return mobileValue;
  if (isTablet) return tabletValue;
  return desktopValue;
};

export default useMobileDetection;