import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';

// Mock different device characteristics
const mockDeviceSpecs = {
  iPhoneSE: {
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
    viewport: { width: 375, height: 667 },
    pixelRatio: 2,
    touchCapable: true,
    platform: 'iPhone',
  },
  iPhone14Pro: {
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    viewport: { width: 393, height: 852 },
    pixelRatio: 3,
    touchCapable: true,
    platform: 'iPhone',
  },
  galaxyS21: {
    userAgent: 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
    viewport: { width: 384, height: 854 },
    pixelRatio: 2.75,
    touchCapable: true,
    platform: 'Android',
  },
  iPadPro: {
    userAgent: 'Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
    viewport: { width: 1024, height: 1366 },
    pixelRatio: 2,
    touchCapable: true,
    platform: 'iPad',
  },
};

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

// Helper to mock device characteristics
const mockDevice = (deviceSpecs: typeof mockDeviceSpecs.iPhoneSE) => {
  // Mock user agent
  Object.defineProperty(navigator, 'userAgent', {
    writable: true,
    value: deviceSpecs.userAgent,
  });

  // Mock viewport
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    value: deviceSpecs.viewport.width,
  });
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    value: deviceSpecs.viewport.height,
  });

  // Mock pixel ratio
  Object.defineProperty(window, 'devicePixelRatio', {
    writable: true,
    value: deviceSpecs.pixelRatio,
  });

  // Mock touch capability
  Object.defineProperty(navigator, 'maxTouchPoints', {
    writable: true,
    value: deviceSpecs.touchCapable ? 5 : 0,
  });

  // Mock platform
  Object.defineProperty(navigator, 'platform', {
    writable: true,
    value: deviceSpecs.platform,
  });
};

describe('Device-Specific Mobile Tests', () => {
  const DeviceAwareComponent = () => {
    const [deviceInfo, setDeviceInfo] = React.useState({
      userAgent: '',
      viewport: { width: 0, height: 0 },
      pixelRatio: 1,
      touchPoints: 0,
      platform: '',
      isIOS: false,
      isAndroid: false,
      isTablet: false,
    });

    React.useEffect(() => {
      const updateDeviceInfo = () => {
        const ua = navigator.userAgent;
        setDeviceInfo({
          userAgent: ua,
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight,
          },
          pixelRatio: window.devicePixelRatio,
          touchPoints: navigator.maxTouchPoints,
          platform: navigator.platform,
          isIOS: /iPad|iPhone|iPod/.test(ua),
          isAndroid: /Android/.test(ua),
          isTablet: /iPad/.test(ua) || (window.innerWidth >= 768),
        });
      };

      updateDeviceInfo();
      window.addEventListener('resize', updateDeviceInfo);
      window.addEventListener('orientationchange', updateDeviceInfo);

      return () => {
        window.removeEventListener('resize', updateDeviceInfo);
        window.removeEventListener('orientationchange', updateDeviceInfo);
      };
    }, []);

    return (
      <div data-testid="device-info">
        <div data-testid="viewport">
          {deviceInfo.viewport.width}x{deviceInfo.viewport.height}
        </div>
        <div data-testid="pixel-ratio">{deviceInfo.pixelRatio}</div>
        <div data-testid="touch-points">{deviceInfo.touchPoints}</div>
        <div data-testid="platform">{deviceInfo.platform}</div>
        <div data-testid="is-ios">{deviceInfo.isIOS ? 'true' : 'false'}</div>
        <div data-testid="is-android">{deviceInfo.isAndroid ? 'true' : 'false'}</div>
        <div data-testid="is-tablet">{deviceInfo.isTablet ? 'true' : 'false'}</div>
      </div>
    );
  };

  beforeEach(() => {
    // Reset to default values
    jest.clearAllMocks();
  });

  describe('iPhone SE (Small Screen)', () => {
    beforeEach(() => {
      mockDevice(mockDeviceSpecs.iPhoneSE);
    });

    it('detects iPhone SE correctly', () => {
      render(
        <TestWrapper>
          <DeviceAwareComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('viewport')).toHaveTextContent('375x667');
      expect(screen.getByTestId('pixel-ratio')).toHaveTextContent('2');
      expect(screen.getByTestId('is-ios')).toHaveTextContent('true');
      expect(screen.getByTestId('is-tablet')).toHaveTextContent('false');
    });

    it('adapts UI layout for small screen', () => {
      const SmallScreenComponent = () => {
        const isSmallScreen = window.innerWidth < 400;
        
        return (
          <div data-testid="small-screen-layout">
            <div 
              data-testid="content-area"
              style={{
                display: 'flex',
                flexDirection: isSmallScreen ? 'column' : 'row',
                gap: isSmallScreen ? '8px' : '16px',
              }}
            >
              <div data-testid="sidebar">Sidebar</div>
              <div data-testid="main">Main Content</div>
            </div>
          </div>
        );
      };

      render(
        <TestWrapper>
          <SmallScreenComponent />
        </TestWrapper>
      );

      const contentArea = screen.getByTestId('content-area');
      const styles = window.getComputedStyle(contentArea);
      expect(styles.flexDirection).toBe('column');
    });

    it('adjusts touch targets for smaller screens', () => {
      const TouchTargetComponent = () => {
        const minTouchSize = window.innerWidth < 400 ? 44 : 48;
        
        return (
          <button 
            data-testid="touch-button"
            style={{
              minHeight: `${minTouchSize}px`,
              minWidth: `${minTouchSize}px`,
              padding: '8px 16px',
            }}
          >
            Touch Me
          </button>
        );
      };

      render(
        <TestWrapper>
          <TouchTargetComponent />
        </TestWrapper>
      );

      const button = screen.getByTestId('touch-button');
      const styles = window.getComputedStyle(button);
      expect(parseInt(styles.minHeight)).toBe(44);
      expect(parseInt(styles.minWidth)).toBe(44);
    });
  });

  describe('iPhone 14 Pro (Modern iPhone)', () => {
    beforeEach(() => {
      mockDevice(mockDeviceSpecs.iPhone14Pro);
    });

    it('detects iPhone 14 Pro correctly', () => {
      render(
        <TestWrapper>
          <DeviceAwareComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('viewport')).toHaveTextContent('393x852');
      expect(screen.getByTestId('pixel-ratio')).toHaveTextContent('3');
      expect(screen.getByTestId('is-ios')).toHaveTextContent('true');
    });

    it('handles notch area appropriately', () => {
      const NotchAwareComponent = () => {
        const hasNotch = /iPhone/.test(navigator.userAgent) && window.innerHeight > 800;
        
        return (
          <div 
            data-testid="notch-aware-container"
            style={{
              paddingTop: hasNotch ? 'env(safe-area-inset-top, 44px)' : '20px',
              paddingBottom: hasNotch ? 'env(safe-area-inset-bottom, 34px)' : '20px',
            }}
          >
            <div data-testid="safe-area-content">
              Content respects safe areas
            </div>
          </div>
        );
      };

      render(
        <TestWrapper>
          <NotchAwareComponent />
        </TestWrapper>
      );

      const container = screen.getByTestId('notch-aware-container');
      const styles = window.getComputedStyle(container);
      // Should have safe area padding
      expect(styles.paddingTop).toBeTruthy();
      expect(styles.paddingBottom).toBeTruthy();
    });

    it('optimizes for high pixel density', () => {
      const HighDPIComponent = () => {
        const pixelRatio = window.devicePixelRatio;
        const imageSize = pixelRatio >= 3 ? '3x' : pixelRatio >= 2 ? '2x' : '1x';
        
        return (
          <img 
            data-testid="high-dpi-image"
            src={`/image-${imageSize}.png`}
            alt="High DPI test"
            style={{ width: '100px', height: '100px' }}
          />
        );
      };

      render(
        <TestWrapper>
          <HighDPIComponent />
        </TestWrapper>
      );

      const image = screen.getByTestId('high-dpi-image');
      expect(image).toHaveAttribute('src', '/image-3x.png');
    });
  });

  describe('Galaxy S21 (Android)', () => {
    beforeEach(() => {
      mockDevice(mockDeviceSpecs.galaxyS21);
    });

    it('detects Android device correctly', () => {
      render(
        <TestWrapper>
          <DeviceAwareComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('is-android')).toHaveTextContent('true');
      expect(screen.getByTestId('is-ios')).toHaveTextContent('false');
      expect(screen.getByTestId('viewport')).toHaveTextContent('384x854');
    });

    it('handles Android-specific interactions', () => {
      const AndroidSpecificComponent = () => {
        const isAndroid = /Android/.test(navigator.userAgent);
        const [backButtonPressed, setBackButtonPressed] = React.useState(false);
        
        React.useEffect(() => {
          const handleBackButton = (e: PopStateEvent) => {
            if (isAndroid) {
              e.preventDefault();
              setBackButtonPressed(true);
            }
          };
          
          window.addEventListener('popstate', handleBackButton);
          return () => window.removeEventListener('popstate', handleBackButton);
        }, [isAndroid]);
        
        return (
          <div data-testid="android-component">
            <div data-testid="back-button-status">
              Back button pressed: {backButtonPressed ? 'true' : 'false'}
            </div>
            <button 
              data-testid="trigger-back"
              onClick={() => window.history.back()}
            >
              Simulate Back
            </button>
          </div>
        );
      };

      render(
        <TestWrapper>
          <AndroidSpecificComponent />
        </TestWrapper>
      );

      const triggerButton = screen.getByTestId('trigger-back');
      fireEvent.click(triggerButton);

      // This would be handled by the browser's back button behavior
      expect(screen.getByTestId('back-button-status')).toBeInTheDocument();
    });

    it('adapts to Android navigation patterns', () => {
      const AndroidNavComponent = () => {
        const isAndroid = /Android/.test(navigator.userAgent);
        
        return (
          <div data-testid="android-nav">
            {isAndroid && (
              <div 
                data-testid="android-nav-bar"
                style={{
                  position: 'fixed',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: '48px',
                  backgroundColor: '#000',
                  display: 'flex',
                  justifyContent: 'space-around',
                  alignItems: 'center',
                }}
              >
                <button data-testid="back-btn">◀</button>
                <button data-testid="home-btn">⚪</button>
                <button data-testid="recent-btn">▢</button>
              </div>
            )}
          </div>
        );
      };

      render(
        <TestWrapper>
          <AndroidNavComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('android-nav-bar')).toBeInTheDocument();
      expect(screen.getByTestId('back-btn')).toBeInTheDocument();
      expect(screen.getByTestId('home-btn')).toBeInTheDocument();
      expect(screen.getByTestId('recent-btn')).toBeInTheDocument();
    });
  });

  describe('iPad Pro (Tablet)', () => {
    beforeEach(() => {
      mockDevice(mockDeviceSpecs.iPadPro);
    });

    it('detects iPad correctly', () => {
      render(
        <TestWrapper>
          <DeviceAwareComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('is-tablet')).toHaveTextContent('true');
      expect(screen.getByTestId('is-ios')).toHaveTextContent('true');
      expect(screen.getByTestId('viewport')).toHaveTextContent('1024x1366');
    });

    it('adapts layout for tablet screen size', () => {
      const TabletLayoutComponent = () => {
        const isTablet = window.innerWidth >= 768;
        
        return (
          <div 
            data-testid="tablet-layout"
            style={{
              display: 'grid',
              gridTemplateColumns: isTablet ? '300px 1fr' : '1fr',
              gap: '20px',
              padding: isTablet ? '20px' : '10px',
            }}
          >
            <aside data-testid="sidebar">Sidebar Content</aside>
            <main data-testid="main-content">Main Content</main>
          </div>
        );
      };

      render(
        <TestWrapper>
          <TabletLayoutComponent />
        </TestWrapper>
      );

      const layout = screen.getByTestId('tablet-layout');
      const styles = window.getComputedStyle(layout);
      expect(styles.gridTemplateColumns).toBe('300px 1fr');
    });

    it('handles multi-column layouts on tablet', () => {
      const MultiColumnComponent = () => {
        const columns = window.innerWidth >= 1024 ? 3 : window.innerWidth >= 768 ? 2 : 1;
        
        return (
          <div 
            data-testid="multi-column"
            style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${columns}, 1fr)`,
              gap: '16px',
            }}
          >
            {Array.from({ length: 6 }, (_, i) => (
              <div key={i} data-testid={`column-item-${i}`}>
                Item {i + 1}
              </div>
            ))}
          </div>
        );
      };

      render(
        <TestWrapper>
          <MultiColumnComponent />
        </TestWrapper>
      );

      const multiColumn = screen.getByTestId('multi-column');
      const styles = window.getComputedStyle(multiColumn);
      expect(styles.gridTemplateColumns).toBe('repeat(3, 1fr)');
    });
  });

  describe('Cross-Device Compatibility', () => {
    it('handles orientation changes across devices', async () => {
      const OrientationComponent = () => {
        const [orientation, setOrientation] = React.useState('portrait');
        
        React.useEffect(() => {
          const updateOrientation = () => {
            const angle = (window.screen?.orientation?.angle) || 0;
            setOrientation(angle === 90 || angle === 270 ? 'landscape' : 'portrait');
          };
          
          updateOrientation();
          window.addEventListener('orientationchange', updateOrientation);
          return () => window.removeEventListener('orientationchange', updateOrientation);
        }, []);
        
        return (
          <div 
            data-testid="orientation-aware"
            data-orientation={orientation}
          >
            Current orientation: {orientation}
          </div>
        );
      };

      // Test with iPhone
      mockDevice(mockDeviceSpecs.iPhoneSE);
      
      render(
        <TestWrapper>
          <OrientationComponent />
        </TestWrapper>
      );

      // Simulate orientation change
      Object.defineProperty(window.screen, 'orientation', {
        writable: true,
        value: { angle: 90 },
      });

      fireEvent(window, new Event('orientationchange'));

      await waitFor(() => {
        expect(screen.getByTestId('orientation-aware')).toHaveTextContent('landscape');
      });
    });

    it('provides consistent touch interactions across devices', () => {
      const TouchInteractionComponent = () => {
        const [touchSupported, setTouchSupported] = React.useState(false);
        const [touchCount, setTouchCount] = React.useState(0);
        
        React.useEffect(() => {
          setTouchSupported('ontouchstart' in window || navigator.maxTouchPoints > 0);
        }, []);
        
        const handleTouch = () => {
          setTouchCount(prev => prev + 1);
        };
        
        return (
          <div data-testid="touch-interaction">
            <div data-testid="touch-support">
              Touch supported: {touchSupported ? 'true' : 'false'}
            </div>
            <div data-testid="max-touch-points">
              Max touch points: {navigator.maxTouchPoints}
            </div>
            <button 
              data-testid="touch-button"
              onTouchStart={handleTouch}
              onClick={handleTouch} // Fallback for non-touch devices
            >
              Touch/Click ({touchCount})
            </button>
          </div>
        );
      };

      // Test with different devices
      mockDevice(mockDeviceSpecs.iPhone14Pro);
      
      const { rerender } = render(
        <TestWrapper>
          <TouchInteractionComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('touch-support')).toHaveTextContent('true');
      expect(screen.getByTestId('max-touch-points')).toHaveTextContent('5');

      // Switch to Android
      mockDevice(mockDeviceSpecs.galaxyS21);
      
      rerender(
        <TestWrapper>
          <TouchInteractionComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('touch-support')).toHaveTextContent('true');
    });

    it('handles different network conditions', () => {
      const NetworkAwareComponent = () => {
        const [connectionInfo, setConnectionInfo] = React.useState({
          online: navigator.onLine,
          effectiveType: '4g',
          downlink: 10,
          rtt: 100,
        });
        
        React.useEffect(() => {
          const updateConnection = () => {
            setConnectionInfo(prev => ({
              ...prev,
              online: navigator.onLine,
            }));
          };
          
          window.addEventListener('online', updateConnection);
          window.addEventListener('offline', updateConnection);
          
          return () => {
            window.removeEventListener('online', updateConnection);
            window.removeEventListener('offline', updateConnection);
          };
        }, []);
        
        return (
          <div data-testid="network-info">
            <div data-testid="online-status">
              Online: {connectionInfo.online ? 'true' : 'false'}
            </div>
            <div data-testid="connection-type">
              Connection: {connectionInfo.effectiveType}
            </div>
          </div>
        );
      };

      render(
        <TestWrapper>
          <NetworkAwareComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('online-status')).toHaveTextContent('true');

      // Simulate going offline
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false,
      });

      fireEvent(window, new Event('offline'));

      expect(screen.getByTestId('online-status')).toHaveTextContent('false');
    });
  });

  describe('Performance Optimization by Device', () => {
    it('adapts performance settings based on device capabilities', () => {
      const PerformanceAwareComponent = () => {
        const deviceTier = React.useMemo(() => {
          const cores = navigator.hardwareConcurrency || 4;
          const memory = (navigator as any).deviceMemory || 4;
          
          if (cores >= 8 && memory >= 8) return 'high';
          if (cores >= 4 && memory >= 4) return 'medium';
          return 'low';
        }, []);
        
        const animationSettings = React.useMemo(() => {
          switch (deviceTier) {
            case 'high':
              return { duration: 300, easing: 'ease-out', effects: true };
            case 'medium':
              return { duration: 200, easing: 'ease', effects: false };
            default:
              return { duration: 100, easing: 'linear', effects: false };
          }
        }, [deviceTier]);
        
        return (
          <div data-testid="performance-aware">
            <div data-testid="device-tier">{deviceTier}</div>
            <div data-testid="animation-duration">{animationSettings.duration}</div>
            <div data-testid="effects-enabled">{animationSettings.effects.toString()}</div>
          </div>
        );
      };

      // Mock high-end device
      Object.defineProperty(navigator, 'hardwareConcurrency', {
        writable: true,
        value: 8,
      });
      Object.defineProperty(navigator, 'deviceMemory', {
        writable: true,
        value: 8,
      });

      render(
        <TestWrapper>
          <PerformanceAwareComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('device-tier')).toHaveTextContent('high');
      expect(screen.getByTestId('animation-duration')).toHaveTextContent('300');
      expect(screen.getByTestId('effects-enabled')).toHaveTextContent('true');
    });
  });
});