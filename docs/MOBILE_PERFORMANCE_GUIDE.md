# Mobile Performance Optimization Guide

## Overview

This guide provides comprehensive performance optimization strategies, monitoring techniques, and best practices for the mobile implementation of FastAPI v1.6. It covers Core Web Vitals optimization, battery efficiency, network resilience, and user experience metrics.

## Table of Contents

1. [Performance Metrics & Targets](#performance-metrics--targets)
2. [Core Web Vitals Optimization](#core-web-vitals-optimization)
3. [Mobile-Specific Optimizations](#mobile-specific-optimizations)
4. [Battery Efficiency](#battery-efficiency)
5. [Network Optimization](#network-optimization)
6. [Caching Strategies](#caching-strategies)
7. [Bundle Optimization](#bundle-optimization)
8. [Image & Asset Optimization](#image--asset-optimization)
9. [Performance Monitoring](#performance-monitoring)
10. [Performance Testing](#performance-testing)

## Performance Metrics & Targets

### Core Web Vitals Targets (Mobile)

| Metric | Target | Good | Needs Improvement | Poor |
|--------|--------|------|-------------------|------|
| **LCP (Largest Contentful Paint)** | < 2.5s | < 2.5s | 2.5s - 4.0s | > 4.0s |
| **FID (First Input Delay)** | < 100ms | < 100ms | 100ms - 300ms | > 300ms |
| **CLS (Cumulative Layout Shift)** | < 0.1 | < 0.1 | 0.1 - 0.25 | > 0.25 |
| **INP (Interaction to Next Paint)** | < 200ms | < 200ms | 200ms - 500ms | > 500ms |

### Mobile-Specific Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| **Time to Interactive** | < 3.0s | Lighthouse audit |
| **Speed Index** | < 2.0s | Lighthouse audit |
| **Bundle Size (Initial)** | < 200KB | Webpack Bundle Analyzer |
| **Battery Drain** | < 5%/hour | Browser DevTools |
| **Memory Usage** | < 50MB | Performance API |
| **PageSpeed Score (Mobile)** | > 90 | Google PageSpeed Insights |

## Core Web Vitals Optimization

### Largest Contentful Paint (LCP) Optimization

#### 1. Critical Resource Optimization
```typescript
// Preload critical resources
export const CriticalResourceLoader = () => {
  useEffect(() => {
    // Preload critical fonts
    const fontLink = document.createElement('link');
    fontLink.rel = 'preload';
    fontLink.as = 'font';
    fontLink.href = '/fonts/critical-font.woff2';
    fontLink.type = 'font/woff2';
    fontLink.crossOrigin = 'anonymous';
    document.head.appendChild(fontLink);

    // Preload hero image
    const imageLink = document.createElement('link');
    imageLink.rel = 'preload';
    imageLink.as = 'image';
    imageLink.href = '/images/mobile-hero.webp';
    document.head.appendChild(imageLink);
  }, []);
};
```

#### 2. Server-Side Rendering (SSR) Optimization
```typescript
// Next.js SSR with critical data prefetching
export async function getServerSideProps(context) {
  const { isMobile } = detectDevice(context.req.headers);
  
  if (isMobile) {
    // Prefetch critical mobile data only
    const criticalData = await fetchCriticalMobileData();
    return {
      props: {
        criticalData,
        isMobile: true
      }
    };
  }
  
  return {
    props: {
      isMobile: false
    }
  };
}
```

### First Input Delay (FID) Optimization

#### 1. Main Thread Optimization
```typescript
// Break up long tasks using time slicing
export const useLongTaskOptimization = () => {
  const processLargeDataset = useCallback(async (data: any[]) => {
    const batchSize = 50;
    const results = [];
    
    for (let i = 0; i < data.length; i += batchSize) {
      const batch = data.slice(i, i + batchSize);
      
      // Process batch
      const batchResults = batch.map(item => processItem(item));
      results.push(...batchResults);
      
      // Yield to main thread
      if (i + batchSize < data.length) {
        await new Promise(resolve => setTimeout(resolve, 0));
      }
    }
    
    return results;
  }, []);
  
  return { processLargeDataset };
};
```

#### 2. Input Handler Optimization
```typescript
// Debounced and optimized input handlers
export const MobileOptimizedInput = ({ onSearch }: Props) => {
  const [query, setQuery] = useState('');
  const searchTimeoutRef = useRef<NodeJS.Timeout>();

  const handleInputChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setQuery(value);

    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Debounce search to avoid blocking main thread
    searchTimeoutRef.current = setTimeout(() => {
      onSearch(value);
    }, 300);
  }, [onSearch]);

  return (
    <input
      type="text"
      value={query}
      onChange={handleInputChange}
      placeholder="Search..."
    />
  );
};
```

### Cumulative Layout Shift (CLS) Optimization

#### 1. Skeleton Loading Strategy
```typescript
// Consistent skeleton loading to prevent layout shifts
export const MobileSkeletonLoader = ({ type, count = 3 }: Props) => {
  const skeletonItems = Array.from({ length: count }, (_, index) => (
    <div key={index} className="skeleton-item">
      <div className="skeleton-avatar" />
      <div className="skeleton-content">
        <div className="skeleton-title" />
        <div className="skeleton-subtitle" />
      </div>
    </div>
  ));

  return (
    <div className="skeleton-container" aria-label="Loading content">
      {skeletonItems}
    </div>
  );
};

// CSS for consistent skeleton dimensions
.skeleton-item {
  height: 80px; /* Fixed height prevents layout shift */
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
}
```

#### 2. Image Optimization for CLS
```typescript
// Aspect ratio containers for images
export const MobileOptimizedImage = ({ 
  src, 
  alt, 
  aspectRatio = '16/9',
  priority = false 
}: Props) => {
  return (
    <div 
      className="image-container"
      style={{ aspectRatio }}
    >
      <Image
        src={src}
        alt={alt}
        fill
        sizes="(max-width: 768px) 100vw, 50vw"
        priority={priority}
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,..."
      />
    </div>
  );
};
```

## Mobile-Specific Optimizations

### Touch Interaction Optimization

#### 1. Touch Event Handling
```typescript
// Optimized touch event handling
export const useMobileTouch = () => {
  const [touchState, setTouchState] = useState({
    startX: 0,
    startY: 0,
    deltaX: 0,
    deltaY: 0
  });

  const handleTouchStart = useCallback((event: TouchEvent) => {
    const touch = event.touches[0];
    setTouchState(prev => ({
      ...prev,
      startX: touch.clientX,
      startY: touch.clientY
    }));
  }, []);

  const handleTouchMove = useCallback((event: TouchEvent) => {
    const touch = event.touches[0];
    setTouchState(prev => ({
      ...prev,
      deltaX: touch.clientX - prev.startX,
      deltaY: touch.clientY - prev.startY
    }));
  }, []);

  // Use passive listeners for better scroll performance
  useEffect(() => {
    const options = { passive: true };
    document.addEventListener('touchstart', handleTouchStart, options);
    document.addEventListener('touchmove', handleTouchMove, options);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
    };
  }, [handleTouchStart, handleTouchMove]);

  return touchState;
};
```

#### 2. Scroll Performance Optimization
```typescript
// Virtual scrolling for large lists on mobile
export const MobileVirtualList = ({ 
  items, 
  itemHeight = 60,
  containerHeight = 400 
}: Props) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  );
  
  const visibleItems = items.slice(visibleStart, visibleEnd);
  const totalHeight = items.length * itemHeight;
  const offsetY = visibleStart * itemHeight;

  const handleScroll = useCallback((event: UIEvent) => {
    const target = event.target as HTMLElement;
    setScrollTop(target.scrollTop);
  }, []);

  return (
    <div 
      className="virtual-list-container"
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div 
          style={{ 
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            width: '100%'
          }}
        >
          {visibleItems.map((item, index) => (
            <div 
              key={visibleStart + index}
              style={{ height: itemHeight }}
            >
              {/* Item content */}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

### Memory Management

#### 1. Component Cleanup
```typescript
// Proper cleanup to prevent memory leaks
export const MobileComponent = () => {
  const [data, setData] = useState([]);
  const intervalRef = useRef<NodeJS.Timeout>();
  const observerRef = useRef<IntersectionObserver>();

  useEffect(() => {
    // Setup intersection observer for lazy loading
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // Load data when component is visible
            loadData();
          }
        });
      },
      { threshold: 0.1 }
    );

    // Setup periodic data refresh
    intervalRef.current = setInterval(refreshData, 30000);

    return () => {
      // Cleanup observers and intervals
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const loadData = useCallback(() => {
    // Load data implementation
  }, []);

  const refreshData = useCallback(() => {
    // Refresh data implementation
  }, []);

  return (
    <div ref={el => el && observerRef.current?.observe(el)}>
      {/* Component content */}
    </div>
  );
};
```

## Battery Efficiency

### CPU Usage Optimization

#### 1. Animation Optimization
```typescript
// Use CSS animations for better battery efficiency
export const MobileAnimation = ({ isVisible }: Props) => {
  return (
    <div 
      className={`mobile-animation ${isVisible ? 'visible' : ''}`}
      style={{
        // Use transform and opacity for GPU acceleration
        transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
        opacity: isVisible ? 1 : 0,
        // Enable hardware acceleration
        willChange: 'transform, opacity',
        // Use CSS transitions instead of JavaScript animations
        transition: 'transform 0.3s ease-out, opacity 0.3s ease-out'
      }}
    >
      {/* Content */}
    </div>
  );
};

// Reduce animations based on battery status
export const useBatteryOptimization = () => {
  const [lowBattery, setLowBattery] = useState(false);

  useEffect(() => {
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        const updateBatteryStatus = () => {
          setLowBattery(battery.level < 0.2 || !battery.charging);
        };

        battery.addEventListener('levelchange', updateBatteryStatus);
        battery.addEventListener('chargingchange', updateBatteryStatus);
        updateBatteryStatus();
      });
    }
  }, []);

  return { 
    lowBattery,
    shouldReduceAnimations: lowBattery
  };
};
```

### Network Request Optimization

#### 1. Request Batching and Caching
```typescript
// Batch API requests to reduce network overhead
export const useAPIBatching = () => {
  const batchQueue = useRef<APIRequest[]>([]);
  const batchTimeoutRef = useRef<NodeJS.Timeout>();

  const addToBatch = useCallback((request: APIRequest) => {
    batchQueue.current.push(request);

    if (batchTimeoutRef.current) {
      clearTimeout(batchTimeoutRef.current);
    }

    batchTimeoutRef.current = setTimeout(() => {
      if (batchQueue.current.length > 0) {
        executeBatch(batchQueue.current);
        batchQueue.current = [];
      }
    }, 50); // Batch requests within 50ms
  }, []);

  const executeBatch = async (requests: APIRequest[]) => {
    const batchResponse = await fetch('/api/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ requests })
    });

    const results = await batchResponse.json();
    
    // Resolve individual request promises
    requests.forEach((request, index) => {
      request.resolve(results[index]);
    });
  };

  return { addToBatch };
};
```

## Performance Monitoring

### Real User Monitoring (RUM)

#### 1. Performance Observer Integration
```typescript
// Comprehensive performance monitoring
export class MobilePerformanceMonitor {
  private static instance: MobilePerformanceMonitor;
  private observers: PerformanceObserver[] = [];

  static getInstance() {
    if (!MobilePerformanceMonitor.instance) {
      MobilePerformanceMonitor.instance = new MobilePerformanceMonitor();
    }
    return MobilePerformanceMonitor.instance;
  }

  init() {
    this.observeLCP();
    this.observeFID();
    this.observeCLS();
    this.observeLongTasks();
  }

  private observeLCP() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'largest-contentful-paint') {
          this.reportMetric('LCP', entry.startTime);
        }
      }
    });
    
    observer.observe({ entryTypes: ['largest-contentful-paint'] });
    this.observers.push(observer);
  }

  private observeFID() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'first-input') {
          const fid = entry.processingStart - entry.startTime;
          this.reportMetric('FID', fid);
        }
      }
    });
    
    observer.observe({ entryTypes: ['first-input'] });
    this.observers.push(observer);
  }

  private observeCLS() {
    let clsValue = 0;
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'layout-shift' && !(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
        }
      }
      this.reportMetric('CLS', clsValue);
    });
    
    observer.observe({ entryTypes: ['layout-shift'] });
    this.observers.push(observer);
  }

  private observeLongTasks() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) {
          this.reportMetric('LongTask', entry.duration);
        }
      }
    });
    
    observer.observe({ entryTypes: ['longtask'] });
    this.observers.push(observer);
  }

  private reportMetric(name: string, value: number) {
    // Send to analytics service
    analytics.track('performance_metric', {
      metric: name,
      value,
      device: 'mobile',
      timestamp: Date.now()
    });
  }

  cleanup() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}
```

### Performance Testing Framework

#### 1. Automated Performance Tests
```typescript
// Playwright performance testing setup
export const performanceTest = async (page: Page, url: string) => {
  // Start performance tracing
  await page.tracing.start({
    path: 'trace.json',
    screenshots: true
  });

  // Navigate to page
  const startTime = Date.now();
  await page.goto(url, { waitUntil: 'networkidle' });
  const loadTime = Date.now() - startTime;

  // Measure Core Web Vitals
  const metrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      const metrics = { LCP: 0, FID: 0, CLS: 0 };
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'largest-contentful-paint') {
            metrics.LCP = entry.startTime;
          }
          if (entry.entryType === 'first-input') {
            metrics.FID = entry.processingStart - entry.startTime;
          }
          if (entry.entryType === 'layout-shift') {
            metrics.CLS += (entry as any).value;
          }
        });
      });
      
      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
      
      setTimeout(() => {
        observer.disconnect();
        resolve(metrics);
      }, 5000);
    });
  });

  await page.tracing.stop();

  return {
    loadTime,
    ...metrics
  };
};

// Performance test suite
describe('Mobile Performance Tests', () => {
  test('Dashboard loads within performance budget', async ({ page }) => {
    const results = await performanceTest(page, '/dashboard');
    
    expect(results.loadTime).toBeLessThan(3000);
    expect(results.LCP).toBeLessThan(2500);
    expect(results.FID).toBeLessThan(100);
    expect(results.CLS).toBeLessThan(0.1);
  });
});
```

## Performance Best Practices Summary

### Development Guidelines

1. **Bundle Size Management**
   - Keep initial bundle < 200KB
   - Implement code splitting at route level
   - Use dynamic imports for heavy components

2. **Image Optimization**
   - Use WebP format with fallbacks
   - Implement responsive images with srcset
   - Use lazy loading for below-the-fold images

3. **Caching Strategy**
   - Implement service worker for offline functionality
   - Use browser caching for static assets
   - Cache API responses appropriately

4. **Network Optimization**
   - Batch API requests where possible
   - Implement request deduplication
   - Use compression for text resources

5. **Memory Management**
   - Clean up event listeners and observers
   - Avoid memory leaks in useEffect hooks
   - Use React.memo for expensive components

### Monitoring and Alerting

1. **Set up performance budgets** in CI/CD pipeline
2. **Monitor Core Web Vitals** in production
3. **Track battery usage** on target devices
4. **Alert on performance regressions** > 10%
5. **Regular performance audits** using Lighthouse

This comprehensive mobile performance guide ensures optimal user experience across all mobile devices while maintaining efficient resource usage and battery life.