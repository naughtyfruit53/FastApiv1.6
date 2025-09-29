import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';

// Mock mobile detection hook
jest.mock('../../../frontend/src/hooks/useMobileDetection', () => ({
  useMobileDetection: () => ({ 
    isMobile: true,
    isTablet: false,
    touchCapable: true,
    orientation: 'portrait',
  }),
}));

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

// Helper function to create touch events
const createTouchEvent = (type: string, touches: Array<{ clientX: number; clientY: number; identifier?: number }>) => {
  return new TouchEvent(type, {
    touches: touches.map((touch, index) => ({
      ...touch,
      identifier: touch.identifier ?? index,
      target: document.body,
    } as any)),
    changedTouches: touches.map((touch, index) => ({
      ...touch,
      identifier: touch.identifier ?? index,
      target: document.body,
    } as any)),
  });
};

describe('Mobile Gesture and Touch Interaction Tests', () => {
  describe('Swipe Gestures', () => {
    const SwipeTestComponent = () => {
      const [swipeDirection, setSwipeDirection] = React.useState<string>('');
      const [swipeDistance, setSwipeDistance] = React.useState<number>(0);
      
      const handleTouchStart = (e: React.TouchEvent) => {
        const touch = e.touches[0];
        (e.currentTarget as any).startX = touch.clientX;
        (e.currentTarget as any).startY = touch.clientY;
      };
      
      const handleTouchEnd = (e: React.TouchEvent) => {
        const touch = e.changedTouches[0];
        const element = e.currentTarget as any;
        const deltaX = touch.clientX - element.startX;
        const deltaY = touch.clientY - element.startY;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        
        setSwipeDistance(distance);
        
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          setSwipeDirection(deltaX > 0 ? 'right' : 'left');
        } else {
          setSwipeDirection(deltaY > 0 ? 'down' : 'up');
        }
      };
      
      return (
        <div
          data-testid="swipe-area"
          style={{ 
            width: '300px', 
            height: '200px', 
            backgroundColor: '#f0f0f0',
            touchAction: 'pan-x pan-y',
          }}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
        >
          <div data-testid="swipe-result">
            Direction: {swipeDirection}
          </div>
          <div data-testid="swipe-distance">
            Distance: {Math.round(swipeDistance)}
          </div>
        </div>
      );
    };

    it('detects horizontal swipe gestures', async () => {
      render(
        <TestWrapper>
          <SwipeTestComponent />
        </TestWrapper>
      );

      const swipeArea = screen.getByTestId('swipe-area');

      // Simulate swipe right
      fireEvent.touchStart(swipeArea, {
        touches: [{ clientX: 50, clientY: 100 }],
      });

      fireEvent.touchEnd(swipeArea, {
        changedTouches: [{ clientX: 200, clientY: 100 }],
      });

      await waitFor(() => {
        expect(screen.getByTestId('swipe-result')).toHaveTextContent('Direction: right');
      });

      // Simulate swipe left
      fireEvent.touchStart(swipeArea, {
        touches: [{ clientX: 200, clientY: 100 }],
      });

      fireEvent.touchEnd(swipeArea, {
        changedTouches: [{ clientX: 50, clientY: 100 }],
      });

      await waitFor(() => {
        expect(screen.getByTestId('swipe-result')).toHaveTextContent('Direction: left');
      });
    });

    it('detects vertical swipe gestures', async () => {
      render(
        <TestWrapper>
          <SwipeTestComponent />
        </TestWrapper>
      );

      const swipeArea = screen.getByTestId('swipe-area');

      // Simulate swipe down
      fireEvent.touchStart(swipeArea, {
        touches: [{ clientX: 150, clientY: 50 }],
      });

      fireEvent.touchEnd(swipeArea, {
        changedTouches: [{ clientX: 150, clientY: 180 }],
      });

      await waitFor(() => {
        expect(screen.getByTestId('swipe-result')).toHaveTextContent('Direction: down');
      });

      // Simulate swipe up
      fireEvent.touchStart(swipeArea, {
        touches: [{ clientX: 150, clientY: 180 }],
      });

      fireEvent.touchEnd(swipeArea, {
        changedTouches: [{ clientX: 150, clientY: 50 }],
      });

      await waitFor(() => {
        expect(screen.getByTestId('swipe-result')).toHaveTextContent('Direction: up');
      });
    });

    it('measures swipe velocity and distance', async () => {
      render(
        <TestWrapper>
          <SwipeTestComponent />
        </TestWrapper>
      );

      const swipeArea = screen.getByTestId('swipe-area');

      // Simulate a long swipe
      fireEvent.touchStart(swipeArea, {
        touches: [{ clientX: 10, clientY: 100 }],
      });

      fireEvent.touchEnd(swipeArea, {
        changedTouches: [{ clientX: 290, clientY: 100 }],
      });

      await waitFor(() => {
        const distanceElement = screen.getByTestId('swipe-distance');
        const distance = parseInt(distanceElement.textContent?.match(/\d+/)?.[0] || '0');
        expect(distance).toBeGreaterThan(200); // Should detect long swipe
      });
    });
  });

  describe('Tap and Long Press Gestures', () => {
    const TapTestComponent = () => {
      const [tapCount, setTapCount] = React.useState(0);
      const [longPressTriggered, setLongPressTriggered] = React.useState(false);
      const [doubleTapTriggered, setDoubleTapTriggered] = React.useState(false);
      
      const tapTimeoutRef = React.useRef<NodeJS.Timeout>();
      const longPressTimeoutRef = React.useRef<NodeJS.Timeout>();
      const lastTapTimeRef = React.useRef<number>(0);
      
      const handleTouchStart = () => {
        setLongPressTriggered(false);
        
        // Start long press timer
        longPressTimeoutRef.current = setTimeout(() => {
          setLongPressTriggered(true);
        }, 500);
      };
      
      const handleTouchEnd = () => {
        // Clear long press timer
        if (longPressTimeoutRef.current) {
          clearTimeout(longPressTimeoutRef.current);
        }
        
        if (!longPressTriggered) {
          const now = Date.now();
          const timeSinceLastTap = now - lastTapTimeRef.current;
          
          if (timeSinceLastTap < 300) {
            // Double tap detected
            setDoubleTapTriggered(true);
            if (tapTimeoutRef.current) {
              clearTimeout(tapTimeoutRef.current);
            }
          } else {
            // Single tap (with delay to check for double tap)
            tapTimeoutRef.current = setTimeout(() => {
              setTapCount(prev => prev + 1);
            }, 300);
          }
          
          lastTapTimeRef.current = now;
        }
      };
      
      return (
        <div
          data-testid="tap-area"
          style={{ 
            width: '200px', 
            height: '200px', 
            backgroundColor: '#e0e0e0',
            border: '2px solid #ccc',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            userSelect: 'none',
          }}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
        >
          <div data-testid="tap-count">Taps: {tapCount}</div>
          <div data-testid="long-press">
            Long Press: {longPressTriggered ? 'YES' : 'NO'}
          </div>
          <div data-testid="double-tap">
            Double Tap: {doubleTapTriggered ? 'YES' : 'NO'}
          </div>
        </div>
      );
    };

    it('detects single tap gestures', async () => {
      render(
        <TestWrapper>
          <TapTestComponent />
        </TestWrapper>
      );

      const tapArea = screen.getByTestId('tap-area');

      // Single tap
      fireEvent.touchStart(tapArea);
      fireEvent.touchEnd(tapArea);

      await waitFor(() => {
        expect(screen.getByTestId('tap-count')).toHaveTextContent('Taps: 1');
      }, { timeout: 500 });
    });

    it('detects long press gestures', async () => {
      jest.useFakeTimers();
      
      render(
        <TestWrapper>
          <TapTestComponent />
        </TestWrapper>
      );

      const tapArea = screen.getByTestId('tap-area');

      // Start long press
      fireEvent.touchStart(tapArea);
      
      // Fast-forward time to trigger long press
      jest.advanceTimersByTime(500);
      
      await waitFor(() => {
        expect(screen.getByTestId('long-press')).toHaveTextContent('Long Press: YES');
      });

      fireEvent.touchEnd(tapArea);
      
      jest.useRealTimers();
    });

    it('detects double tap gestures', async () => {
      jest.useFakeTimers();
      
      render(
        <TestWrapper>
          <TapTestComponent />
        </TestWrapper>
      );

      const tapArea = screen.getByTestId('tap-area');

      // First tap
      fireEvent.touchStart(tapArea);
      fireEvent.touchEnd(tapArea);

      // Second tap (within 300ms)
      jest.advanceTimersByTime(100);
      fireEvent.touchStart(tapArea);
      fireEvent.touchEnd(tapArea);

      await waitFor(() => {
        expect(screen.getByTestId('double-tap')).toHaveTextContent('Double Tap: YES');
      });
      
      jest.useRealTimers();
    });
  });

  describe('Pinch and Zoom Gestures', () => {
    const PinchTestComponent = () => {
      const [scale, setScale] = React.useState(1);
      const [isPinching, setIsPinching] = React.useState(false);
      
      let initialDistance = 0;
      let initialScale = 1;
      
      const getDistance = (touch1: Touch, touch2: Touch) => {
        return Math.sqrt(
          Math.pow(touch2.clientX - touch1.clientX, 2) +
          Math.pow(touch2.clientY - touch1.clientY, 2)
        );
      };
      
      const handleTouchStart = (e: React.TouchEvent) => {
        if (e.touches.length === 2) {
          setIsPinching(true);
          initialDistance = getDistance(e.touches[0], e.touches[1]);
          initialScale = scale;
        }
      };
      
      const handleTouchMove = (e: React.TouchEvent) => {
        if (e.touches.length === 2 && isPinching) {
          const currentDistance = getDistance(e.touches[0], e.touches[1]);
          const scaleChange = currentDistance / initialDistance;
          setScale(initialScale * scaleChange);
        }
      };
      
      const handleTouchEnd = (e: React.TouchEvent) => {
        if (e.touches.length < 2) {
          setIsPinching(false);
        }
      };
      
      return (
        <div
          data-testid="pinch-area"
          style={{ 
            width: '300px', 
            height: '300px', 
            backgroundColor: '#f5f5f5',
            border: '2px solid #ddd',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            touchAction: 'none',
          }}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <div
            data-testid="scalable-content"
            style={{
              transform: `scale(${scale})`,
              transformOrigin: 'center',
              transition: isPinching ? 'none' : 'transform 0.2s ease',
              backgroundColor: '#4caf50',
              width: '100px',
              height: '100px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: 'white',
            }}
          >
            {scale.toFixed(2)}x
          </div>
        </div>
      );
    };

    it('detects pinch to zoom gestures', async () => {
      render(
        <TestWrapper>
          <PinchTestComponent />
        </TestWrapper>
      );

      const pinchArea = screen.getByTestId('pinch-area');

      // Simulate pinch out (zoom in)
      fireEvent.touchStart(pinchArea, {
        touches: [
          { clientX: 140, clientY: 140 },
          { clientX: 160, clientY: 160 },
        ],
      });

      fireEvent.touchMove(pinchArea, {
        touches: [
          { clientX: 120, clientY: 120 },
          { clientX: 180, clientY: 180 },
        ],
      });

      const scalableContent = screen.getByTestId('scalable-content');
      await waitFor(() => {
        const scaleText = scalableContent.textContent;
        const scaleValue = parseFloat(scaleText?.replace('x', '') || '1');
        expect(scaleValue).toBeGreaterThan(1);
      });

      fireEvent.touchEnd(pinchArea, {
        touches: [],
      });
    });

    it('detects pinch to shrink gestures', async () => {
      render(
        <TestWrapper>
          <PinchTestComponent />
        </TestWrapper>
      );

      const pinchArea = screen.getByTestId('pinch-area');

      // Simulate pinch in (zoom out)
      fireEvent.touchStart(pinchArea, {
        touches: [
          { clientX: 120, clientY: 120 },
          { clientX: 180, clientY: 180 },
        ],
      });

      fireEvent.touchMove(pinchArea, {
        touches: [
          { clientX: 140, clientY: 140 },
          { clientX: 160, clientY: 160 },
        ],
      });

      const scalableContent = screen.getByTestId('scalable-content');
      await waitFor(() => {
        const scaleText = scalableContent.textContent;
        const scaleValue = parseFloat(scaleText?.replace('x', '') || '1');
        expect(scaleValue).toBeLessThan(1);
      });

      fireEvent.touchEnd(pinchArea, {
        touches: [],
      });
    });
  });

  describe('Drag and Drop Gestures', () => {
    const DragDropTestComponent = () => {
      const [position, setPosition] = React.useState({ x: 0, y: 0 });
      const [isDragging, setIsDragging] = React.useState(false);
      
      let startPos = { x: 0, y: 0 };
      let initialPos = { x: 0, y: 0 };
      
      const handleTouchStart = (e: React.TouchEvent) => {
        setIsDragging(true);
        const touch = e.touches[0];
        startPos = { x: touch.clientX, y: touch.clientY };
        initialPos = { ...position };
      };
      
      const handleTouchMove = (e: React.TouchEvent) => {
        if (isDragging) {
          const touch = e.touches[0];
          const deltaX = touch.clientX - startPos.x;
          const deltaY = touch.clientY - startPos.y;
          
          setPosition({
            x: initialPos.x + deltaX,
            y: initialPos.y + deltaY,
          });
        }
      };
      
      const handleTouchEnd = () => {
        setIsDragging(false);
      };
      
      return (
        <div
          data-testid="drag-container"
          style={{ 
            width: '400px', 
            height: '400px', 
            backgroundColor: '#fafafa',
            border: '2px solid #ccc',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div
            data-testid="draggable-item"
            style={{
              position: 'absolute',
              left: `${position.x}px`,
              top: `${position.y}px`,
              width: '80px',
              height: '80px',
              backgroundColor: isDragging ? '#ff9800' : '#2196f3',
              borderRadius: '8px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: 'white',
              fontWeight: 'bold',
              cursor: 'grab',
              touchAction: 'none',
              transition: isDragging ? 'none' : 'all 0.2s ease',
            }}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
          >
            DRAG
          </div>
          <div data-testid="position-display" style={{ margin: '10px' }}>
            Position: ({Math.round(position.x)}, {Math.round(position.y)})
          </div>
        </div>
      );
    };

    it('handles drag gestures correctly', async () => {
      render(
        <TestWrapper>
          <DragDropTestComponent />
        </TestWrapper>
      );

      const draggableItem = screen.getByTestId('draggable-item');

      // Start drag
      fireEvent.touchStart(draggableItem, {
        touches: [{ clientX: 40, clientY: 40 }],
      });

      // Move item
      fireEvent.touchMove(draggableItem, {
        touches: [{ clientX: 140, clientY: 140 }],
      });

      await waitFor(() => {
        const positionDisplay = screen.getByTestId('position-display');
        expect(positionDisplay).toHaveTextContent('Position: (100, 100)');
      });

      // End drag
      fireEvent.touchEnd(draggableItem);

      // Item should maintain new position
      expect(screen.getByTestId('position-display')).toHaveTextContent('Position: (100, 100)');
    });

    it('provides visual feedback during drag operations', async () => {
      render(
        <TestWrapper>
          <DragDropTestComponent />
        </TestWrapper>
      );

      const draggableItem = screen.getByTestId('draggable-item');

      // Start drag - should change color
      fireEvent.touchStart(draggableItem, {
        touches: [{ clientX: 40, clientY: 40 }],
      });

      const styles = window.getComputedStyle(draggableItem);
      expect(styles.backgroundColor).toContain('rgb(255, 152, 0)'); // Orange color during drag

      // End drag
      fireEvent.touchEnd(draggableItem);
    });
  });

  describe('Multi-touch Gestures', () => {
    const MultiTouchTestComponent = () => {
      const [touches, setTouches] = React.useState<Array<{ id: number; x: number; y: number }>>([]);
      
      const handleTouchStart = (e: React.TouchEvent) => {
        const newTouches = Array.from(e.touches).map((touch, index) => ({
          id: touch.identifier,
          x: touch.clientX,
          y: touch.clientY,
        }));
        setTouches(newTouches);
      };
      
      const handleTouchMove = (e: React.TouchEvent) => {
        const updatedTouches = Array.from(e.touches).map((touch) => ({
          id: touch.identifier,
          x: touch.clientX,
          y: touch.clientY,
        }));
        setTouches(updatedTouches);
      };
      
      const handleTouchEnd = (e: React.TouchEvent) => {
        const remainingTouches = Array.from(e.touches).map((touch) => ({
          id: touch.identifier,
          x: touch.clientX,
          y: touch.clientY,
        }));
        setTouches(remainingTouches);
      };
      
      return (
        <div
          data-testid="multitouch-area"
          style={{ 
            width: '350px', 
            height: '300px', 
            backgroundColor: '#f0f8ff',
            border: '2px solid #87ceeb',
            position: 'relative',
            touchAction: 'none',
          }}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <div data-testid="touch-count" style={{ margin: '10px' }}>
            Active touches: {touches.length}
          </div>
          {touches.map((touch) => (
            <div
              key={touch.id}
              data-testid={`touch-point-${touch.id}`}
              style={{
                position: 'absolute',
                left: `${touch.x - 10}px`,
                top: `${touch.y - 10}px`,
                width: '20px',
                height: '20px',
                backgroundColor: '#ff4444',
                borderRadius: '50%',
                border: '2px solid white',
                pointerEvents: 'none',
              }}
            />
          ))}
        </div>
      );
    };

    it('tracks multiple simultaneous touches', async () => {
      render(
        <TestWrapper>
          <MultiTouchTestComponent />
        </TestWrapper>
      );

      const multitouchArea = screen.getByTestId('multitouch-area');

      // Simulate multiple touches
      fireEvent.touchStart(multitouchArea, {
        touches: [
          { clientX: 100, clientY: 100, identifier: 0 },
          { clientX: 200, clientY: 100, identifier: 1 },
          { clientX: 150, clientY: 200, identifier: 2 },
        ],
      });

      await waitFor(() => {
        expect(screen.getByTestId('touch-count')).toHaveTextContent('Active touches: 3');
      });

      // Remove one touch
      fireEvent.touchEnd(multitouchArea, {
        touches: [
          { clientX: 100, clientY: 100, identifier: 0 },
          { clientX: 200, clientY: 100, identifier: 1 },
        ],
      });

      await waitFor(() => {
        expect(screen.getByTestId('touch-count')).toHaveTextContent('Active touches: 2');
      });
    });

    it('handles complex multi-finger gestures', async () => {
      render(
        <TestWrapper>
          <MultiTouchTestComponent />
        </TestWrapper>
      );

      const multitouchArea = screen.getByTestId('multitouch-area');

      // Start with two touches
      fireEvent.touchStart(multitouchArea, {
        touches: [
          { clientX: 120, clientY: 120, identifier: 0 },
          { clientX: 180, clientY: 180, identifier: 1 },
        ],
      });

      // Move both touches (rotation/scaling gesture)
      fireEvent.touchMove(multitouchArea, {
        touches: [
          { clientX: 130, clientY: 110, identifier: 0 },
          { clientX: 190, clientY: 190, identifier: 1 },
        ],
      });

      await waitFor(() => {
        expect(screen.getByTestId('touch-count')).toHaveTextContent('Active touches: 2');
        expect(screen.getByTestId('touch-point-0')).toBeInTheDocument();
        expect(screen.getByTestId('touch-point-1')).toBeInTheDocument();
      });
    });
  });

  describe('Device Orientation and Motion', () => {
    const OrientationTestComponent = () => {
      const [orientation, setOrientation] = React.useState('portrait');
      const [motion, setMotion] = React.useState({ x: 0, y: 0, z: 0 });
      
      React.useEffect(() => {
        const handleOrientationChange = () => {
          const angle = (window.screen?.orientation?.angle) || 0;
          setOrientation(angle === 90 || angle === 270 ? 'landscape' : 'portrait');
        };
        
        const handleDeviceMotion = (event: DeviceMotionEvent) => {
          setMotion({
            x: event.accelerationIncludingGravity?.x || 0,
            y: event.accelerationIncludingGravity?.y || 0,
            z: event.accelerationIncludingGravity?.z || 0,
          });
        };
        
        window.addEventListener('orientationchange', handleOrientationChange);
        window.addEventListener('devicemotion', handleDeviceMotion);
        
        return () => {
          window.removeEventListener('orientationchange', handleOrientationChange);
          window.removeEventListener('devicemotion', handleDeviceMotion);
        };
      }, []);
      
      return (
        <div data-testid="orientation-component">
          <div data-testid="orientation-display">
            Orientation: {orientation}
          </div>
          <div data-testid="motion-display">
            Motion: X={motion.x.toFixed(2)}, Y={motion.y.toFixed(2)}, Z={motion.z.toFixed(2)}
          </div>
        </div>
      );
    };

    it('responds to device orientation changes', async () => {
      render(
        <TestWrapper>
          <OrientationTestComponent />
        </TestWrapper>
      );

      // Mock orientation change
      Object.defineProperty(window.screen, 'orientation', {
        writable: true,
        value: { angle: 90 },
      });

      fireEvent(window, new Event('orientationchange'));

      await waitFor(() => {
        expect(screen.getByTestId('orientation-display')).toHaveTextContent('Orientation: landscape');
      });

      // Change back to portrait
      Object.defineProperty(window.screen, 'orientation', {
        value: { angle: 0 },
      });

      fireEvent(window, new Event('orientationchange'));

      await waitFor(() => {
        expect(screen.getByTestId('orientation-display')).toHaveTextContent('Orientation: portrait');
      });
    });

    it('handles device motion events', async () => {
      render(
        <TestWrapper>
          <OrientationTestComponent />
        </TestWrapper>
      );

      // Simulate device motion
      const motionEvent = new DeviceMotionEvent('devicemotion', {
        accelerationIncludingGravity: {
          x: 1.5,
          y: -2.3,
          z: 9.8,
        },
      } as any);

      fireEvent(window, motionEvent);

      await waitFor(() => {
        const motionDisplay = screen.getByTestId('motion-display');
        expect(motionDisplay.textContent).toMatch(/X=1\.50.*Y=-2\.30.*Z=9\.80/);
      });
    });
  });

  describe('Performance and Edge Cases', () => {
    it('handles rapid gesture sequences without performance degradation', async () => {
      const RapidGestureTest = () => {
        const [gestureCount, setGestureCount] = React.useState(0);
        
        return (
          <div
            data-testid="rapid-gesture-area"
            style={{ width: '200px', height: '200px', backgroundColor: '#eee' }}
            onTouchStart={() => setGestureCount(prev => prev + 1)}
          >
            Gestures: {gestureCount}
          </div>
        );
      };

      render(
        <TestWrapper>
          <RapidGestureTest />
        </TestWrapper>
      );

      const gestureArea = screen.getByTestId('rapid-gesture-area');
      
      const startTime = performance.now();
      
      // Perform rapid gestures
      for (let i = 0; i < 50; i++) {
        fireEvent.touchStart(gestureArea);
        fireEvent.touchEnd(gestureArea);
      }
      
      const endTime = performance.now();
      
      // Should complete within reasonable time
      expect(endTime - startTime).toBeLessThan(1000);
      
      await waitFor(() => {
        expect(screen.getByText('Gestures: 50')).toBeInTheDocument();
      });
    });

    it('handles edge cases like touch outside boundaries', () => {
      const EdgeCaseTest = () => {
        const [boundaryViolation, setBoundaryViolation] = React.useState(false);
        
        const handleTouchMove = (e: React.TouchEvent) => {
          const touch = e.touches[0];
          const rect = e.currentTarget.getBoundingClientRect();
          
          if (
            touch.clientX < rect.left ||
            touch.clientX > rect.right ||
            touch.clientY < rect.top ||
            touch.clientY > rect.bottom
          ) {
            setBoundaryViolation(true);
          }
        };
        
        return (
          <div
            data-testid="boundary-test"
            style={{ width: '150px', height: '150px', backgroundColor: '#ddd' }}
            onTouchMove={handleTouchMove}
          >
            <div data-testid="boundary-status">
              Boundary violation: {boundaryViolation ? 'YES' : 'NO'}
            </div>
          </div>
        );
      };

      render(
        <TestWrapper>
          <EdgeCaseTest />
        </TestWrapper>
      );

      const boundaryTest = screen.getByTestId('boundary-test');

      // Simulate touch moving outside boundary
      fireEvent.touchStart(boundaryTest, {
        touches: [{ clientX: 75, clientY: 75 }],
      });

      fireEvent.touchMove(boundaryTest, {
        touches: [{ clientX: 200, clientY: 200 }], // Outside boundary
      });

      expect(screen.getByTestId('boundary-status')).toHaveTextContent('Boundary violation: YES');
    });
  });
});