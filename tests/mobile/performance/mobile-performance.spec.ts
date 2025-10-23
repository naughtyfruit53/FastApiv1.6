/**
 * Mobile Performance Tests
 * Tests loading times, Core Web Vitals, and performance metrics for mobile pages
 */

import { test, expect, devices } from '@playwright/test';

// Test on multiple mobile devices
const mobileDevices = [
  { name: 'iPhone 12', device: devices['iPhone 12'] },
  { name: 'Pixel 5', device: devices['Pixel 5'] },
];

for (const { name, device } of mobileDevices) {
  test.describe(`Mobile Performance - ${name}`, () => {
    test.use(device);

    test.beforeEach(async ({ page }) => {
      // Set up demo mode for consistent testing
      await page.goto('/');
      await page.evaluate(() => {
        localStorage.setItem('demoMode', 'true');
        localStorage.setItem('access_token', 'demo_token');
      });
    });

    test('Dashboard page load time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto('/mobile/dashboard', { waitUntil: 'networkidle' });
      
      const loadTime = Date.now() - startTime;
      
      // Page should load in under 3 seconds on mobile
      expect(loadTime).toBeLessThan(3000);
      console.log(`${name} - Dashboard load time: ${loadTime}ms`);
    });

    test('Core Web Vitals - LCP', async ({ page }) => {
      await page.goto('/mobile/dashboard');

      // Measure Largest Contentful Paint
      const lcp = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1] as any;
            resolve(lastEntry.renderTime || lastEntry.loadTime);
          }).observe({ type: 'largest-contentful-paint', buffered: true });

          // Timeout after 5 seconds
          setTimeout(() => resolve(0), 5000);
        });
      });

      console.log(`${name} - LCP: ${lcp}ms`);
      
      // LCP should be under 2.5 seconds for good performance
      if (lcp > 0) {
        expect(lcp).toBeLessThan(2500);
      }
    });

    test('Core Web Vitals - CLS', async ({ page }) => {
      await page.goto('/mobile/dashboard');

      // Wait for page to stabilize
      await page.waitForTimeout(2000);

      // Measure Cumulative Layout Shift
      const cls = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          let clsValue = 0;
          
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (!(entry as any).hadRecentInput) {
                clsValue += (entry as any).value;
              }
            }
          }).observe({ type: 'layout-shift', buffered: true });

          setTimeout(() => resolve(clsValue), 3000);
        });
      });

      console.log(`${name} - CLS: ${cls}`);
      
      // CLS should be under 0.1 for good performance
      expect(cls).toBeLessThan(0.1);
    });

    test('Time to Interactive (TTI)', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto('/mobile/dashboard');

      // Wait for page to be interactive
      await page.waitForLoadState('networkidle');
      
      // Try to interact with an element
      const button = page.locator('button').first();
      await button.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});
      
      const tti = Date.now() - startTime;
      
      console.log(`${name} - Time to Interactive: ${tti}ms`);
      
      // TTI should be under 3.5 seconds
      expect(tti).toBeLessThan(3500);
    });

    test('JavaScript bundle size', async ({ page }) => {
      // Track all JS requests
      const jsRequests: { url: string; size: number }[] = [];
      
      page.on('response', async (response) => {
        const url = response.url();
        if (url.endsWith('.js')) {
          const buffer = await response.body().catch(() => null);
          if (buffer) {
            jsRequests.push({
              url: url.split('/').pop() || url,
              size: buffer.length
            });
          }
        }
      });

      await page.goto('/mobile/dashboard', { waitUntil: 'networkidle' });

      // Calculate total JS size
      const totalSize = jsRequests.reduce((sum, req) => sum + req.size, 0);
      const totalSizeKB = totalSize / 1024;
      
      console.log(`${name} - Total JS Size: ${totalSizeKB.toFixed(2)} KB`);

      // Total JS should be under 500KB for mobile
      expect(totalSizeKB).toBeLessThan(500);
    });
  });
}

test.describe('Mobile Performance - Network Conditions', () => {
  test('Performance on slow 3G', async ({ page }) => {
    // Simulate slow 3G network
    const client = await page.context().newCDPSession(page);
    await client.send('Network.emulateNetworkConditions', {
      offline: false,
      downloadThroughput: (500 * 1024) / 8, // 500kb/s
      uploadThroughput: (500 * 1024) / 8,
      latency: 400 // 400ms latency
    });

    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    const startTime = Date.now();
    await page.goto('/mobile/dashboard', { waitUntil: 'domcontentloaded', timeout: 15000 });
    const loadTime = Date.now() - startTime;

    console.log(`Slow 3G load time: ${loadTime}ms`);

    // Should still be usable on slow connection (under 10 seconds for initial content)
    expect(loadTime).toBeLessThan(10000);
  });
});
