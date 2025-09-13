import { defineConfig, devices } from '@playwright/test';

/**
 * Mobile-specific Playwright configuration
 * Optimized for mobile testing across different devices and scenarios
 */
export default defineConfig({
  testDir: './tests/mobile',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'test-results/mobile-html-report' }],
    ['json', { outputFile: 'test-results/mobile-results.json' }],
    ['junit', { outputFile: 'test-results/mobile-junit.xml' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    // Mobile Chrome (Android)
    {
      name: 'Mobile Chrome - Pixel 5',
      use: { 
        ...devices['Pixel 5'],
        contextOptions: {
          permissions: ['notifications'],
          geolocation: { latitude: 37.7749, longitude: -122.4194 }, // San Francisco
        },
      },
      testMatch: /.*\.(test|spec)\.(ts|tsx)$/,
    },
    
    // Mobile Chrome (Larger Android)
    {
      name: 'Mobile Chrome - Galaxy S21',
      use: { 
        ...devices['Galaxy S21'],
        contextOptions: {
          permissions: ['notifications'],
        },
      },
      testMatch: /.*\.(test|spec)\.(ts|tsx)$/,
    },

    // Mobile Safari (iPhone)
    {
      name: 'Mobile Safari - iPhone 12',
      use: { 
        ...devices['iPhone 12'],
        contextOptions: {
          permissions: ['notifications'],
        },
      },
      testMatch: /.*\.(test|spec)\.(ts|tsx)$/,
    },

    // Mobile Safari (Larger iPhone)
    {
      name: 'Mobile Safari - iPhone 14 Pro Max',
      use: { 
        ...devices['iPhone 14 Pro Max'],
        contextOptions: {
          permissions: ['notifications'],
        },
      },
      testMatch: /.*\.(test|spec)\.(ts|tsx)$/,
    },

    // Tablet Testing
    {
      name: 'Tablet - iPad Pro',
      use: { 
        ...devices['iPad Pro'],
        contextOptions: {
          permissions: ['notifications'],
        },
      },
      testMatch: /.*\.(test|spec)\.(ts|tsx)$/,
    },

    // Desktop for comparison (mobile layout should not appear)
    {
      name: 'Desktop - Chrome',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
      testMatch: /.*\.(test|spec)\.(ts|tsx)$/,
    },

    // Accessibility Testing (using Chrome with accessibility tools)
    {
      name: 'Accessibility - Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        launchOptions: {
          args: [
            '--force-prefers-reduced-motion',
            '--force-prefers-color-scheme=light',
          ],
        },
      },
      testMatch: /.*accessibility.*\.(test|spec)\.(ts|tsx)$/,
    },

    // Performance Testing
    {
      name: 'Performance - Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        launchOptions: {
          args: [
            '--no-sandbox',
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
          ],
        },
      },
      testMatch: /.*performance.*\.(test|spec)\.(ts|tsx)$/,
    },

    // Slow Network Testing
    {
      name: 'Mobile Chrome - Slow 3G',
      use: { 
        ...devices['Pixel 5'],
        contextOptions: {
          offline: false,
        },
        launchOptions: {
          args: ['--force-effective-connection-type=slow-2g'],
        },
      },
      testMatch: /.*network.*\.(test|spec)\.(ts|tsx)$/,
    },

    // Device Emulation Testing
    {
      name: 'Device Emulation Tests',
      testMatch: /.*device-emulation.*\.(test|spec)\.(ts|tsx)$/,
      use: {
        // This will be overridden by individual tests
        ...devices['Pixel 5'],
      },
    },
  ],

  // Global test setup
  globalSetup: require.resolve('./tests/mobile/global-setup.ts'),
  globalTeardown: require.resolve('./tests/mobile/global-teardown.ts'),

  // Test timeouts
  timeout: 30000,
  expect: {
    timeout: 10000,
  },

  // Web server configuration (for running tests against local dev server)
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },

  // Output directories
  outputDir: 'test-results/mobile-output',
});