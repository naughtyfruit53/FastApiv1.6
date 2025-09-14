# Mobile Contributor Guide

## Overview

This guide provides comprehensive information for developers contributing to the mobile frontend implementation. The mobile interface is built as an additive layer on top of the existing desktop React application, ensuring zero impact on desktop functionality.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Mobile Component Development](#mobile-component-development)
4. [Design Patterns](#design-patterns)
5. [Testing Guidelines](#testing-guidelines)
6. [Performance Considerations](#performance-considerations)
7. [Accessibility Standards](#accessibility-standards)
8. [Code Style Guidelines](#code-style-guidelines)
9. [Common Patterns](#common-patterns)
10. [Troubleshooting](#troubleshooting)

## Architecture Overview

### Design Principles

- **Additive Architecture**: Mobile components exist alongside desktop components without modification
- **Progressive Enhancement**: Core functionality works on all devices, enhanced features for mobile
- **Component Reusability**: Shared business logic, separate presentation layers
- **Touch-First Design**: Optimized for touch interactions with fallbacks

### Directory Structure

```
frontend/src/
├── components/
│   ├── mobile/                    # Mobile-specific components
│   │   ├── MobileLayout.tsx       # Layout components
│   │   ├── SwipeableCard.tsx      # Advanced interactions
│   │   ├── MobileBottomSheet.tsx  # Mobile-specific patterns
│   │   └── index.ts               # Barrel exports
│   └── shared/                    # Shared components
├── pages/
│   ├── mobile/                    # Mobile page implementations
│   │   ├── dashboard.tsx
│   │   ├── sales.tsx
│   │   └── ...
│   └── desktop/                   # Desktop pages (existing)
├── hooks/
│   ├── mobile/                    # Mobile-specific hooks
│   │   ├── useMobileRouting.ts
│   │   └── useMobileDetection.ts
│   └── shared/                    # Shared business logic
├── utils/
│   ├── mobile/                    # Mobile utilities
│   │   ├── hapticFeedback.ts
│   │   └── deviceDetection.ts
│   └── shared/
└── styles/
    ├── mobile/                    # Mobile-specific styles
    └── shared/
```

### Technology Stack

- **Framework**: Next.js 15+ with React 18+
- **UI Library**: Material-UI (MUI) 7+
- **TypeScript**: Full type safety
- **State Management**: React Query + Context API
- **Styling**: MUI theme system + CSS-in-JS
- **Testing**: Jest + Testing Library + Playwright
- **Build**: Next.js build system with mobile optimizations

## Development Setup

### Prerequisites

```bash
Node.js 18+
npm 8+
Git
```

### Environment Setup

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd FastApiv1.6/frontend
   npm install
   ```

2. **Development Server**
   ```bash
   npm run dev
   # Visit http://localhost:3000/mobile/dashboard
   ```

3. **Mobile Development Tools**
   ```bash
   # Install browser dev tools for mobile testing
   # Chrome DevTools Device Mode
   # Safari Web Inspector (for iOS testing)
   ```

### IDE Configuration

**VSCode Extensions:**
```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "ms-playwright.playwright",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

**ESLint Configuration:**
```json
{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended"
  ],
  "rules": {
    "react-hooks/exhaustive-deps": "warn",
    "unused-imports/no-unused-imports": "error"
  }
}
```

## Mobile Component Development

### Component Creation Guidelines

#### 1. Basic Mobile Component Template

```typescript
import React from 'react';
import { Box, BoxProps } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileComponentProps extends BoxProps {
  children: React.ReactNode;
  // Component-specific props
}

const MobileComponent: React.FC<MobileComponentProps> = ({
  children,
  ...boxProps
}) => {
  const { isMobile } = useMobileDetection();

  if (!isMobile) {
    return null; // or desktop fallback
  }

  return (
    <Box
      {...boxProps}
      sx={{
        // Mobile-optimized styles
        touchAction: 'manipulation',
        WebkitTapHighlightColor: 'transparent',
        userSelect: 'none',
        ...boxProps.sx,
      }}
    >
      {children}
    </Box>
  );
};

export default MobileComponent;
```

#### 2. Touch Interaction Component

```typescript
import React, { useState, useRef } from 'react';
import { useHapticFeedback } from '../../utils/mobile/hapticFeedback';

interface TouchInteractiveProps {
  onTap?: () => void;
  onLongPress?: () => void;
  onSwipe?: (direction: 'left' | 'right' | 'up' | 'down') => void;
  hapticFeedback?: boolean;
  children: React.ReactNode;
}

const TouchInteractive: React.FC<TouchInteractiveProps> = ({
  onTap,
  onLongPress,
  onSwipe,
  hapticFeedback = true,
  children,
}) => {
  const { trigger, HapticFeedbackType } = useHapticFeedback();
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  const longPressTimer = useRef<NodeJS.Timeout>();

  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY });

    if (onLongPress) {
      longPressTimer.current = setTimeout(() => {
        if (hapticFeedback) {
          trigger(HapticFeedbackType.MEDIUM);
        }
        onLongPress();
      }, 500);
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
    }

    if (!touchStart) return;

    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStart.x;
    const deltaY = touch.clientY - touchStart.y;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

    if (distance < 10) {
      // Tap
      if (onTap) {
        if (hapticFeedback) {
          trigger(HapticFeedbackType.LIGHT);
        }
        onTap();
      }
    } else if (onSwipe && distance > 50) {
      // Swipe
      const absX = Math.abs(deltaX);
      const absY = Math.abs(deltaY);
      
      if (absX > absY) {
        onSwipe(deltaX > 0 ? 'right' : 'left');
      } else {
        onSwipe(deltaY > 0 ? 'down' : 'up');
      }
    }

    setTouchStart(null);
  };

  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      style={{ touchAction: 'manipulation' }}
    >
      {children}
    </div>
  );
};
```

### Component Testing

#### Unit Test Template

```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import YourMobileComponent from '../YourMobileComponent';

// Mock mobile detection
jest.mock('../../hooks/useMobileDetection', () => ({
  useMobileDetection: () => ({ isMobile: true }),
}));

const theme = createTheme();
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('YourMobileComponent', () => {
  it('renders correctly on mobile', () => {
    render(
      <TestWrapper>
        <YourMobileComponent>Test Content</YourMobileComponent>
      </TestWrapper>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('handles touch interactions', () => {
    const onTap = jest.fn();
    render(
      <TestWrapper>
        <YourMobileComponent onTap={onTap}>Test</YourMobileComponent>
      </TestWrapper>
    );

    const element = screen.getByText('Test');
    fireEvent.touchStart(element, {
      touches: [{ clientX: 0, clientY: 0 }],
    });
    fireEvent.touchEnd(element, {
      changedTouches: [{ clientX: 0, clientY: 0 }],
    });

    expect(onTap).toHaveBeenCalledTimes(1);
  });
});
```

## Design Patterns

### 1. Responsive Component Pattern

```typescript
const ResponsiveComponent: React.FC = () => {
  const { isMobile } = useMobileDetection();

  return (
    <DeviceConditional
      mobile={<MobileImplementation />}
      desktop={<DesktopImplementation />}
    />
  );
};
```

### 2. Progressive Enhancement Pattern

```typescript
const EnhancedMobileCard: React.FC = ({ children, ...props }) => {
  const { isMobile } = useMobileDetection();
  const [enhanced, setEnhanced] = useState(false);

  useEffect(() => {
    if (isMobile && 'ontouchstart' in window) {
      setEnhanced(true);
    }
  }, [isMobile]);

  if (enhanced) {
    return <SwipeableCard {...props}>{children}</SwipeableCard>;
  }

  return <BasicCard {...props}>{children}</BasicCard>;
};
```

### 3. Touch Gesture Pattern

```typescript
const useSwipeGesture = (onSwipe: (direction: string) => void) => {
  const [startPos, setStartPos] = useState<{ x: number; y: number } | null>(null);

  const handlers = {
    onTouchStart: (e: React.TouchEvent) => {
      const touch = e.touches[0];
      setStartPos({ x: touch.clientX, y: touch.clientY });
    },
    onTouchEnd: (e: React.TouchEvent) => {
      if (!startPos) return;

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - startPos.x;
      const deltaY = touch.clientY - startPos.y;

      // Determine swipe direction
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        onSwipe(deltaX > 0 ? 'right' : 'left');
      } else {
        onSwipe(deltaY > 0 ? 'down' : 'up');
      }

      setStartPos(null);
    },
  };

  return handlers;
};
```

### 4. Accessibility Pattern

```typescript
const AccessibleMobileComponent: React.FC = ({ children, ...props }) => {
  const focusRef = useRef<HTMLElement>(null);

  useEffect(() => {
    // Ensure focusable on keyboard navigation
    const element = focusRef.current;
    if (element && !element.hasAttribute('tabindex')) {
      element.setAttribute('tabindex', '0');
    }
  }, []);

  return (
    <Box
      ref={focusRef}
      role="button"
      aria-label="Interactive mobile component"
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          // Handle keyboard activation
        }
      }}
      {...props}
    >
      {children}
    </Box>
  );
};
```

## Performance Considerations

### 1. Lazy Loading

```typescript
// Lazy load heavy mobile components
const MobileChart = lazy(() => import('./MobileChart'));
const MobileDataGrid = lazy(() => import('./MobileDataGrid'));

const MobileDashboard: React.FC = () => {
  const { isMobile } = useMobileDetection();

  if (!isMobile) return null;

  return (
    <Suspense fallback={<MobileLoadingSkeleton />}>
      <MobileChart />
      <MobileDataGrid />
    </Suspense>
  );
};
```

### 2. Bundle Optimization

```typescript
// Use dynamic imports for mobile-only features
const loadMobileFeatures = async () => {
  if (window.innerWidth <= 768) {
    const { hapticFeedback } = await import('./utils/mobile/hapticFeedback');
    const { gestureHandler } = await import('./utils/mobile/gestures');
    return { hapticFeedback, gestureHandler };
  }
  return null;
};
```

### 3. Memory Management

```typescript
const useMobileOptimizations = () => {
  useEffect(() => {
    // Clean up event listeners
    return () => {
      // Remove touch event listeners
      // Clear timers
      // Cancel pending requests
    };
  }, []);

  const throttledHandler = useCallback(
    throttle((e) => {
      // Handle expensive operations
    }, 100),
    []
  );

  return { throttledHandler };
};
```

## Accessibility Standards

### WCAG 2.1 Compliance

1. **Touch Targets**: Minimum 44x44px
2. **Color Contrast**: 4.5:1 for normal text, 3:1 for large text
3. **Keyboard Navigation**: All interactive elements accessible
4. **Screen Reader Support**: Proper ARIA labels and roles

### Implementation Guidelines

```typescript
// Touch target sizing
const MobileButton: React.FC = ({ children, ...props }) => (
  <Button
    {...props}
    sx={{
      minHeight: 44,
      minWidth: 44,
      ...props.sx,
    }}
  >
    {children}
  </Button>
);

// Screen reader support
const MobileIcon: React.FC = ({ icon, label }) => (
  <Box role="img" aria-label={label}>
    {icon}
  </Box>
);

// High contrast support
const useHighContrast = () => {
  const [highContrast, setHighContrast] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    setHighContrast(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => setHighContrast(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return highContrast;
};
```

## Code Style Guidelines

### File Naming Conventions

- Components: `PascalCase.tsx` (e.g., `MobileBottomSheet.tsx`)
- Hooks: `camelCase.ts` (e.g., `useMobileDetection.ts`)
- Utils: `camelCase.ts` (e.g., `hapticFeedback.ts`)
- Types: `camelCase.types.ts` (e.g., `mobile.types.ts`)

### Import Organization

```typescript
// 1. React imports
import React, { useState, useEffect } from 'react';

// 2. Third-party imports
import { Box, Typography } from '@mui/material';

// 3. Internal imports (absolute paths)
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { MobileCard } from '../mobile';

// 4. Types
import type { MobileComponentProps } from '../../types/mobile.types';
```

### Component Props Interface

```typescript
interface ComponentProps {
  // Required props first
  children: React.ReactNode;
  onAction: () => void;
  
  // Optional props
  title?: string;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
  
  // Extending existing interfaces
  className?: string;
}
```

## Common Patterns

### Error Boundaries for Mobile

```typescript
class MobileErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Mobile component error:', error, errorInfo);
    // Log to mobile analytics
  }

  render() {
    if (this.state.hasError) {
      return <MobileErrorFallback />;
    }

    return this.props.children;
  }
}
```

### Custom Hook Pattern

```typescript
const useMobileFeature = (enabled: boolean = true) => {
  const { isMobile } = useMobileDetection();
  const [feature, setFeature] = useState<any>(null);

  useEffect(() => {
    if (isMobile && enabled) {
      // Initialize mobile-specific feature
      const cleanup = initializeFeature();
      return cleanup;
    }
  }, [isMobile, enabled]);

  const triggerFeature = useCallback((params: any) => {
    if (feature && isMobile) {
      feature.execute(params);
    }
  }, [feature, isMobile]);

  return {
    available: isMobile && enabled && !!feature,
    trigger: triggerFeature,
  };
};
```

## Troubleshooting

### Common Issues

1. **Touch Events Not Working**
   ```typescript
   // Ensure touch-action is set correctly
   style={{ touchAction: 'manipulation' }}
   
   // Prevent default browser behaviors
   onTouchStart={(e) => e.preventDefault()}
   ```

2. **Performance Issues**
   ```typescript
   // Use React.memo for expensive components
   const MobileComponent = React.memo(() => {
     // Component implementation
   });
   
   // Throttle touch handlers
   const throttledHandler = useCallback(
     throttle(handler, 16), // 60fps
     []
   );
   ```

3. **Styling Issues**
   ```typescript
   // Use viewport units carefully
   sx={{
     height: '100vh', // May cause issues with mobile browsers
     height: '100dvh', // Better for mobile (if supported)
   }}
   ```

### Debug Tools

```typescript
// Mobile detection debug
const MobileDebugger: React.FC = () => {
  const { isMobile, device } = useMobileDetection();
  
  if (process.env.NODE_ENV !== 'development') return null;
  
  return (
    <Box sx={{ position: 'fixed', top: 0, right: 0, background: 'red', color: 'white', p: 1, zIndex: 9999 }}>
      Mobile: {isMobile ? 'Yes' : 'No'}
      <br />
      Device: {device.type}
      <br />
      Screen: {window.innerWidth}x{window.innerHeight}
    </Box>
  );
};
```

## Contributing Guidelines

1. **Pull Request Process**
   - Create feature branch from `main`
   - Follow naming convention: `feature/mobile-component-name`
   - Include tests for new components
   - Update documentation

2. **Code Review Checklist**
   - [ ] Mobile-first responsive design
   - [ ] Touch interaction support
   - [ ] Accessibility compliance
   - [ ] Performance optimization
   - [ ] Cross-browser compatibility
   - [ ] Test coverage > 80%

3. **Testing Requirements**
   - Unit tests for component logic
   - Integration tests for workflows
   - Device emulation tests
   - Accessibility tests

For additional help or questions, please reach out to the mobile development team or create an issue in the repository.