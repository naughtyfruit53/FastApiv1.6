# Advanced Analytics & User Behavior Tracking Guide

## Overview

The TRITIQ BOS includes a comprehensive analytics system for tracking user behavior, optimizing UX, and understanding how users interact with mobile and demo modes.

## Features

### 1. Event Tracking
- **Page Views**: Track all page navigations
- **User Interactions**: Click, scroll, form submissions
- **Navigation Patterns**: User journey through the application
- **Error Tracking**: Capture and analyze errors
- **Custom Events**: Track domain-specific actions

### 2. Session Management
- **Session Identification**: Unique session tracking
- **User Attribution**: Link events to users
- **Device Detection**: Mobile, tablet, desktop
- **Demo Mode Tracking**: Separate demo vs. production analytics

### 3. Metrics & Insights
- **Engagement Metrics**: Time on page, interactions per session
- **Conversion Funnels**: Track user progression through workflows
- **Drop-off Analysis**: Identify where users leave
- **Performance Metrics**: Page load times, response times
- **Feature Usage**: Most/least used features

### 4. Real-Time Analytics
- **Live Dashboard**: Real-time user activity
- **Active Users**: Current active sessions
- **Event Stream**: Live event feed
- **Alerts**: Unusual patterns or errors

## Architecture

### Analytics Tracker Service

Located: `frontend/src/analytics/components/analyticsTracker.ts`

Core service for tracking user behavior.

**Key Features:**
```typescript
class AnalyticsTracker {
  // Initialize with user
  initialize(userId?: string): void;
  
  // Track events
  trackPageView(page, module?, metadata?): void;
  trackClick(element, page, metadata?): void;
  trackFormSubmit(formName, page, success, metadata?): void;
  trackNavigation(from, to, metadata?): void;
  trackError(error, page, metadata?): void;
  trackCustomEvent(action, page, metadata?): void;
  
  // Session management
  getSession(): UserSession;
  getSessionMetrics(): AnalyticsMetrics;
  
  // Data management
  flush(): Promise<void>;
  setEnabled(enabled: boolean): void;
}
```

### Event Types

```typescript
interface AnalyticsEvent {
  id: string;
  type: 'page_view' | 'click' | 'form_submit' | 'navigation' | 'error' | 'custom';
  timestamp: Date;
  userId?: string;
  sessionId: string;
  page: string;
  module?: string;
  action?: string;
  element?: string;
  metadata?: Record<string, any>;
  deviceType: 'mobile' | 'tablet' | 'desktop';
  isDemoMode: boolean;
}
```

### Session Data

```typescript
interface UserSession {
  sessionId: string;
  userId?: string;
  startTime: Date;
  lastActivity: Date;
  events: AnalyticsEvent[];
  deviceType: 'mobile' | 'tablet' | 'desktop';
  isDemoMode: boolean;
}
```

## Integration Guide

### Basic Setup

1. **Initialize analytics:**
```typescript
import { analyticsTracker } from '@/analytics/components/analyticsTracker';

// On app load
useEffect(() => {
  analyticsTracker.initialize(user?.id);
}, [user]);
```

2. **Track page views:**
```typescript
// In your page component
useEffect(() => {
  analyticsTracker.trackPageView('/sales/orders', 'sales', {
    orderCount: orders.length,
  });
}, []);
```

3. **Track interactions:**
```typescript
const handleButtonClick = () => {
  analyticsTracker.trackClick('create-order-button', '/sales/orders', {
    action: 'create_order',
  });
  // Your button logic
};
```

### Automatic Page Tracking

Create a hook for automatic tracking:

```typescript
// hooks/usePageTracking.ts
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { analyticsTracker } from '@/analytics/components/analyticsTracker';

export function usePageTracking(module?: string) {
  const router = useRouter();
  
  useEffect(() => {
    const handleRouteChange = (url: string) => {
      analyticsTracker.trackPageView(url, module);
    };
    
    router.events.on('routeChangeComplete', handleRouteChange);
    
    // Track initial page
    analyticsTracker.trackPageView(router.pathname, module);
    
    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router, module]);
}
```

Usage:
```typescript
function MyPage() {
  usePageTracking('sales');
  // Your component
}
```

### Form Tracking

Track form submissions:

```typescript
const handleSubmit = async (data: FormData) => {
  try {
    await submitForm(data);
    analyticsTracker.trackFormSubmit(
      'sales-order-form',
      '/sales/orders/new',
      true,
      { orderTotal: data.total }
    );
  } catch (error) {
    analyticsTracker.trackFormSubmit(
      'sales-order-form',
      '/sales/orders/new',
      false,
      { error: error.message }
    );
  }
};
```

### Error Tracking

Automatic error tracking:

```typescript
// In error boundary or global error handler
useEffect(() => {
  const handleError = (error: Error) => {
    analyticsTracker.trackError(error, window.location.pathname, {
      userAgent: navigator.userAgent,
      viewport: `${window.innerWidth}x${window.innerHeight}`,
    });
  };
  
  window.addEventListener('error', handleError);
  return () => window.removeEventListener('error', handleError);
}, []);
```

### Custom Events

Track domain-specific events:

```typescript
// Track when user applies a filter
analyticsTracker.trackCustomEvent('filter_applied', '/sales/orders', {
  filterType: 'status',
  filterValue: 'pending',
  resultCount: filteredOrders.length,
});

// Track when user exports data
analyticsTracker.trackCustomEvent('data_export', '/reports/sales', {
  exportFormat: 'pdf',
  dateRange: '30days',
  recordCount: data.length,
});

// Track demo mode activation
analyticsTracker.trackCustomEvent('demo_activated', '/dashboard', {
  userType: 'new_visitor',
  source: 'homepage_banner',
});
```

## Analytics Dashboard

### Session Metrics

Get current session metrics:

```typescript
const metrics = analyticsTracker.getSessionMetrics();

console.log({
  pageViews: metrics.totalPageViews,
  interactions: metrics.totalInteractions,
  duration: metrics.averageSessionDuration,
  topPages: metrics.mostVisitedPages,
});
```

### Real-Time Tracking

Display real-time metrics:

```typescript
function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState(null);
  
  useEffect(() => {
    const interval = setInterval(() => {
      const current = analyticsTracker.getSessionMetrics();
      setMetrics(current);
    }, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <Box>
      <Typography>Page Views: {metrics?.totalPageViews}</Typography>
      <Typography>Interactions: {metrics?.totalInteractions}</Typography>
      <Typography>Session Duration: {metrics?.averageSessionDuration}s</Typography>
    </Box>
  );
}
```

## Mobile & Demo Mode Analytics

### Mobile-Specific Tracking

Track mobile-specific interactions:

```typescript
// Track touch gestures
const handleSwipe = (direction: string) => {
  analyticsTracker.trackCustomEvent('swipe_gesture', '/mobile/orders', {
    direction,
    deviceType: 'mobile',
  });
};

// Track mobile navigation
const handleMobileNav = (tab: string) => {
  analyticsTracker.trackCustomEvent('mobile_nav', '/mobile', {
    tab,
    previousTab: currentTab,
  });
};
```

### Demo Mode Analytics

Track demo mode behavior:

```typescript
// Track demo activation
analyticsTracker.trackCustomEvent('demo_started', '/demo', {
  entryPoint: 'login_page',
  userType: 'anonymous',
});

// Track demo feature exploration
analyticsTracker.trackCustomEvent('demo_feature_explored', '/demo/sales', {
  feature: 'sales_orders',
  timeSpent: 45, // seconds
  actionsPerformed: 5,
});

// Track demo completion
analyticsTracker.trackCustomEvent('demo_completed', '/demo', {
  duration: 600, // 10 minutes
  featuresExplored: ['sales', 'inventory', 'reports'],
  conversionIntent: 'high',
});
```

## Data Export & Reporting

### Export Session Data

```typescript
const session = analyticsTracker.getSession();

// Export as JSON
const exportData = {
  sessionId: session.sessionId,
  userId: session.userId,
  duration: (session.lastActivity - session.startTime) / 1000,
  events: session.events.map(e => ({
    type: e.type,
    page: e.page,
    timestamp: e.timestamp,
    metadata: e.metadata,
  })),
};

// Download or send to backend
console.log(JSON.stringify(exportData, null, 2));
```

### Funnel Analysis

Track conversion funnels:

```typescript
const salesFunnel = [
  'view_products',
  'add_to_cart',
  'checkout',
  'payment',
  'order_complete',
];

// Track funnel step
analyticsTracker.trackCustomEvent('funnel_step', '/sales', {
  funnel: 'sales_order',
  step: 'add_to_cart',
  stepNumber: 2,
  totalSteps: 5,
});
```

## Performance Monitoring

### Track Performance Metrics

```typescript
// Track page load time
window.addEventListener('load', () => {
  const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
  analyticsTracker.trackCustomEvent('page_load', window.location.pathname, {
    loadTime,
    domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
  });
});

// Track API response time
const startTime = Date.now();
await fetchData();
const responseTime = Date.now() - startTime;
analyticsTracker.trackCustomEvent('api_call', '/api/orders', {
  endpoint: '/api/v1/orders',
  responseTime,
  status: 'success',
});
```

## Privacy & Compliance

### Data Privacy

1. **User Consent**: Implement consent management
```typescript
if (userConsent.analytics) {
  analyticsTracker.setEnabled(true);
} else {
  analyticsTracker.setEnabled(false);
}
```

2. **Data Anonymization**: Remove PII from events
```typescript
// Don't track sensitive data
analyticsTracker.trackPageView('/users/profile', 'users', {
  // userId already tracked - don't include email, phone, etc.
  accountType: user.accountType,
});
```

3. **Data Retention**: Implement retention policies
```typescript
// Clear old session data
if (sessionAge > 30days) {
  // Clear or archive
}
```

### GDPR Compliance

- Obtain user consent before tracking
- Provide opt-out mechanism
- Allow data deletion requests
- Anonymize or pseudonymize data
- Document data processing

## Best Practices

### 1. Event Naming
Use consistent, descriptive names:
```typescript
// Good
analyticsTracker.trackCustomEvent('sales_order_created', '/sales/orders');
analyticsTracker.trackCustomEvent('invoice_downloaded', '/invoices');

// Avoid
analyticsTracker.trackCustomEvent('click', '/page');
analyticsTracker.trackCustomEvent('event1', '/page');
```

### 2. Metadata
Include relevant context:
```typescript
analyticsTracker.trackCustomEvent('report_generated', '/reports', {
  reportType: 'sales_summary',
  dateRange: '30days',
  format: 'pdf',
  filters: { status: 'completed' },
  resultCount: 150,
});
```

### 3. Performance
- Batch events before sending
- Use async operations
- Implement retry logic
- Cache common data

### 4. Testing
Test analytics integration:
```typescript
describe('Analytics', () => {
  it('should track page view', () => {
    const spy = jest.spyOn(analyticsTracker, 'trackPageView');
    render(<MyPage />);
    expect(spy).toHaveBeenCalledWith('/my-page', 'module');
  });
});
```

## Troubleshooting

### Common Issues

**Events not tracking:**
- Check if analytics is enabled
- Verify session initialization
- Check browser console for errors

**Data not syncing:**
- Check network connectivity
- Verify backend endpoint
- Review flush interval settings

**Performance impact:**
- Increase flush interval
- Reduce event frequency
- Optimize metadata size

## Version History

- **v1.0.0** (2025-10-23): Initial implementation
  - Event tracking system
  - Session management
  - Mobile and demo mode analytics
  - Real-time metrics
