import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for mobile testing
 * Prepares the test environment and performs initial validations
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting Mobile Test Environment Setup...');

  // Launch a browser for setup tasks
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 1. Check if the application is running
    console.log('📡 Checking application availability...');
    const baseURL = config.use?.baseURL || 'http://localhost:3000';
    
    await page.goto(baseURL, { waitUntil: 'networkidle', timeout: 30000 });
    console.log('✅ Application is accessible');

    // 2. Verify mobile routes are available
    console.log('📱 Verifying mobile routes...');
    const mobileRoutes = [
      '/mobile/dashboard',
      '/mobile/login',
    ];

    for (const route of mobileRoutes) {
      try {
        await page.goto(`${baseURL}${route}`, { waitUntil: 'networkidle', timeout: 10000 });
        console.log(`✅ Route accessible: ${route}`);
      } catch (error) {
        console.log(`⚠️ Route may not be fully ready: ${route}`);
      }
    }

    // 3. Check for mobile detection
    console.log('🔍 Testing mobile detection...');
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE size
    await page.goto(`${baseURL}/mobile/dashboard`);
    
    const isMobileDetected = await page.evaluate(() => {
      return window.innerWidth <= 768;
    });

    if (isMobileDetected) {
      console.log('✅ Mobile viewport detection working');
    } else {
      console.log('⚠️ Mobile viewport detection may need verification');
    }

    // 4. Test basic touch capabilities
    console.log('👆 Testing touch event support...');
    const hasTouchSupport = await page.evaluate(() => {
      return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    });

    console.log(`${hasTouchSupport ? '✅' : '⚠️'} Touch support: ${hasTouchSupport ? 'Available' : 'Limited'}`);

    // 5. Verify accessibility tools are available
    console.log('♿ Checking accessibility tools...');
    try {
      await page.addScriptTag({
        url: 'https://unpkg.com/axe-core@4.7.0/axe.min.js'
      });
      console.log('✅ Accessibility testing tools loaded');
    } catch (error) {
      console.log('⚠️ Accessibility tools may be loaded differently in tests');
    }

    // 6. Performance baseline check
    console.log('⚡ Establishing performance baseline...');
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
      };
    });

    console.log(`📊 Performance baseline:
      - DOM Content Loaded: ${Math.round(performanceMetrics.domContentLoaded)}ms
      - Load Complete: ${Math.round(performanceMetrics.loadComplete)}ms
      - First Paint: ${Math.round(performanceMetrics.firstPaint)}ms
      - First Contentful Paint: ${Math.round(performanceMetrics.firstContentfulPaint)}ms`);

    // 7. Environment information
    console.log('🔧 Test environment information:');
    const userAgent = await page.evaluate(() => navigator.userAgent);
    console.log(`   User Agent: ${userAgent}`);
    
    const viewport = page.viewportSize();
    console.log(`   Viewport: ${viewport?.width}x${viewport?.height}`);

    console.log('✅ Mobile test environment setup complete!');

  } catch (error) {
    console.error('❌ Error during mobile test setup:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;