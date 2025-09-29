# FastAPI v1.6 - Complete Deployment Guide

## Prerequisites
- FastAPI application running
- PostgreSQL database configured
- Redis (optional, for caching)
- SMTP server credentials
- Node.js 18.17+ for frontend build
- SSL certificate for production deployment

## Deployment Steps

### 1. Database Migration
```bash
# Run Alembic migrations
alembic upgrade head

# Verify role tables created
python -c "from app.models.user_models import OrganizationRole; print('✅ Role models available')"
```

### 2. Email Service Configuration
```bash
# Configure email service
python scripts/setup_email_service.py

# Update .env file with SMTP settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Mobile PWA Configuration

#### Service Worker Setup
```bash
# Ensure service worker is properly configured
cd frontend
npm run build:pwa

# Verify PWA manifest
curl -s http://localhost:3000/manifest.json | jq .

# Test service worker installation
npm run test:pwa
```

#### Mobile-Specific Environment Variables
```bash
# Add to .env file
PWA_ENABLED=true
PUSH_NOTIFICATION_VAPID_PUBLIC_KEY=your_vapid_public_key
PUSH_NOTIFICATION_VAPID_PRIVATE_KEY=your_vapid_private_key
MOBILE_API_RATE_LIMIT=2000  # Higher limit for mobile
OFFLINE_CACHE_DURATION=604800  # 7 days in seconds
```

### 4. Frontend Deployment with Mobile Optimization

#### Production Build
```bash
cd frontend
# Install dependencies
npm ci --production

# Build with mobile optimizations
npm run build

# Verify mobile bundle size
npm run analyze:bundle

# Test mobile performance
npm run lighthouse:mobile
```

#### Mobile Performance Validation
```bash
# Run mobile performance tests
npm run test:performance:mobile

# Verify Core Web Vitals
npm run test:vitals

# Check PWA compatibility
npm run test:pwa:compatibility
```

### 5. SSL and Security Configuration

#### SSL Setup for Mobile
```nginx
# nginx configuration for mobile PWA
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.pem;
    ssl_certificate_key /path/to/private-key.pem;
    
    # PWA-specific headers
    location /manifest.json {
        add_header Cache-Control "public, max-age=604800";
        add_header Content-Type "application/json";
    }
    
    location /sw.js {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Service-Worker-Allowed "/";
    }
    
    # Mobile API rate limiting
    location /api/ {
        limit_req zone=mobile_api burst=20 nodelay;
        proxy_pass http://backend;
    }
}
```

#### Security Headers for Mobile
```bash
# Add security headers for mobile browsers
# In your FastAPI app
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff", 
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'"
}
```

### 6. Mobile Push Notifications Setup

#### VAPID Keys Generation
```bash
# Generate VAPID keys for push notifications
npm install -g web-push
web-push generate-vapid-keys

# Add keys to environment
echo "VAPID_PUBLIC_KEY=your_generated_public_key" >> .env
echo "VAPID_PRIVATE_KEY=your_generated_private_key" >> .env
echo "VAPID_EMAIL=mailto:admin@your-domain.com" >> .env
```

#### Firebase Configuration (Optional)
```bash
# If using Firebase for Android push notifications
echo "FIREBASE_PROJECT_ID=your_project_id" >> .env
echo "FIREBASE_PRIVATE_KEY=your_firebase_key" >> .env
echo "FIREBASE_CLIENT_EMAIL=your_firebase_email" >> .env
```

### 7. User Migration
```bash
# Validate and migrate existing users
python scripts/validate_user_migration.py

# Review migration report
cat migration_report.json
```

### 8. Mobile Testing Validation

#### Device Testing
```bash
# Run comprehensive mobile tests
npm run test:mobile:comprehensive

# Test on multiple devices
npm run test:devices

# Accessibility testing
npm run test:accessibility:mobile
```

#### Performance Monitoring Setup
```bash
# Setup mobile performance monitoring
python scripts/setup_mobile_monitoring.py

# Configure Real User Monitoring (RUM)
echo "RUM_API_KEY=your_rum_api_key" >> .env
echo "PERFORMANCE_MONITORING=true" >> .env
```

## Mobile-Specific Post-Deployment

### PWA Installation Testing
1. **iOS Safari**: 
   - Navigate to the site
   - Tap Share → Add to Home Screen
   - Verify app icon and splash screen

2. **Android Chrome**:
   - Navigate to the site  
   - Tap browser menu → Install app
   - Verify installation and functionality

3. **Desktop Chrome**:
   - Look for install prompt in address bar
   - Test desktop PWA functionality

### Mobile Performance Validation

#### Core Web Vitals Monitoring
```bash
# Setup automated Core Web Vitals monitoring
cat > scripts/monitor_mobile_performance.py << 'EOF'
import asyncio
from playwright.async_api import async_playwright

async def measure_core_web_vitals():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to mobile site
        await page.goto("https://your-domain.com")
        
        # Measure Core Web Vitals
        metrics = await page.evaluate("""
            new Promise((resolve) => {
                const vitals = {};
                
                // Measure LCP
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    vitals.LCP = entries[entries.length - 1].startTime;
                }).observe({entryTypes: ['largest-contentful-paint']});
                
                // Measure FID
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    vitals.FID = entries[0].processingStart - entries[0].startTime;
                }).observe({entryTypes: ['first-input']});
                
                // Measure CLS
                let cls = 0;
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach((entry) => {
                        if (!entry.hadRecentInput) {
                            cls += entry.value;
                        }
                    });
                    vitals.CLS = cls;
                }).observe({entryTypes: ['layout-shift']});
                
                setTimeout(() => resolve(vitals), 10000);
            })
        """)
        
        await browser.close()
        return metrics

if __name__ == "__main__":
    metrics = asyncio.run(measure_core_web_vitals())
    print(f"Mobile Performance Metrics: {metrics}")
EOF

# Run performance monitoring
python scripts/monitor_mobile_performance.py
```

### Offline Functionality Testing
```bash
# Test offline capabilities
cat > scripts/test_offline_functionality.py << 'EOF'
from playwright.sync_api import sync_playwright

def test_offline_functionality():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate to site and cache resources
        page.goto("https://your-domain.com")
        page.wait_for_load_state("networkidle")
        
        # Enable offline mode
        context = page.context
        context.set_offline(True)
        
        # Test offline functionality
        page.reload()
        
        # Verify offline banner appears
        offline_banner = page.locator('[data-testid="offline-banner"]')
        assert offline_banner.is_visible()
        
        # Test cached functionality
        dashboard_link = page.locator('a[href="/dashboard"]')
        dashboard_link.click()
        
        # Verify cached content loads
        assert page.locator('[data-testid="cached-dashboard"]').is_visible()
        
        browser.close()

if __name__ == "__main__":
    test_offline_functionality()
    print("✅ Offline functionality working correctly")
EOF

# Run offline tests
python scripts/test_offline_functionality.py
```

### Mobile Analytics Setup
```bash
# Configure mobile-specific analytics
echo "MOBILE_ANALYTICS_ENABLED=true" >> .env
echo "TRACK_MOBILE_GESTURES=true" >> .env
echo "TRACK_PERFORMANCE_METRICS=true" >> .env
echo "MOBILE_ERROR_REPORTING=true" >> .env
```

## Production Deployment Checklist

### Pre-Deployment
- [ ] **Performance Testing**: Core Web Vitals meet targets (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] **Accessibility Testing**: WCAG 2.1 AA compliance verified
- [ ] **Device Testing**: Tested on primary mobile devices and browsers
- [ ] **Offline Testing**: PWA offline functionality working
- [ ] **Push Notifications**: VAPID keys configured and tested
- [ ] **SSL Certificate**: Valid SSL certificate installed
- [ ] **Security Headers**: Mobile security headers configured
- [ ] **Bundle Analysis**: JavaScript bundle size optimized (< 200KB initial)

### Deployment
- [ ] **Database Migrations**: All migrations applied successfully
- [ ] **Environment Variables**: All mobile-specific env vars configured
- [ ] **Service Worker**: SW deployed and functioning
- [ ] **CDN Configuration**: Static assets served via CDN
- [ ] **Load Balancer**: Configured for mobile traffic
- [ ] **Rate Limiting**: Mobile-specific rate limits applied
- [ ] **Monitoring**: Mobile performance monitoring active

### Post-Deployment
- [ ] **PWA Installation**: Install prompts working on all platforms
- [ ] **Core Web Vitals**: Real user metrics meeting targets
- [ ] **Error Monitoring**: Mobile error tracking functional
- [ ] **Performance Alerts**: Alerts configured for performance regressions
- [ ] **User Testing**: Sample users can successfully use mobile interface
- [ ] **Analytics**: Mobile usage analytics collecting data
- [ ] **Push Notifications**: Test notifications delivered successfully

## Troubleshooting Mobile Deployment

### Common Issues

#### PWA Installation Problems
```bash
# Check manifest.json validity
curl -s https://your-domain.com/manifest.json | jq .

# Verify service worker registration
curl -s https://your-domain.com/sw.js | head -5

# Check HTTPS requirement
curl -I https://your-domain.com | grep -i strict-transport-security
```

#### Performance Issues
```bash
# Analyze bundle size
npm run build && npm run analyze

# Check image optimization
find public/images -name "*.jpg" -o -name "*.png" | wc -l
find public/images -name "*.webp" | wc -l

# Monitor real-time performance
npm run lighthouse:mobile -- --view
```

#### Push Notification Issues
```bash
# Test VAPID keys
node -e "
const webpush = require('web-push');
webpush.setVapidDetails(
  'mailto:admin@your-domain.com',
  process.env.VAPID_PUBLIC_KEY,
  process.env.VAPID_PRIVATE_KEY
);
console.log('✅ VAPID keys valid');
"
```

## Mobile Deployment Validation

### Final Validation Script
```bash
# Create comprehensive validation script
cat > scripts/validate_mobile_deployment.py << 'EOF'
#!/usr/bin/env python3
import requests
import json
import subprocess
from playwright.sync_api import sync_playwright

def validate_mobile_deployment():
    results = {
        "pwa_manifest": False,
        "service_worker": False,
        "mobile_performance": False,
        "accessibility": False,
        "push_notifications": False
    }
    
    base_url = "https://your-domain.com"
    
    # Test PWA manifest
    try:
        response = requests.get(f"{base_url}/manifest.json")
        if response.status_code == 200:
            manifest = response.json()
            if "name" in manifest and "icons" in manifest:
                results["pwa_manifest"] = True
    except Exception as e:
        print(f"Manifest test failed: {e}")
    
    # Test service worker
    try:
        response = requests.get(f"{base_url}/sw.js")
        if response.status_code == 200:
            results["service_worker"] = True
    except Exception as e:
        print(f"Service worker test failed: {e}")
    
    # Test mobile performance with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        
        # Navigate and measure
        page.goto(base_url)
        
        # Check if page loads within performance budget
        load_time = page.evaluate("performance.timing.loadEventEnd - performance.timing.navigationStart")
        if load_time < 3000:  # 3 seconds
            results["mobile_performance"] = True
        
        # Basic accessibility check
        accessibility_elements = page.locator('[aria-label], [alt], [role]').count()
        if accessibility_elements > 0:
            results["accessibility"] = True
        
        browser.close()
    
    # Test push notification setup
    try:
        import os
        if os.getenv('VAPID_PUBLIC_KEY') and os.getenv('VAPID_PRIVATE_KEY'):
            results["push_notifications"] = True
    except:
        pass
    
    return results

if __name__ == "__main__":
    results = validate_mobile_deployment()
    
    print("\n🚀 Mobile Deployment Validation Results:")
    print("=" * 50)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")
    
    if all(results.values()):
        print("\n🎉 All mobile deployment tests passed!")
        exit(0)
    else:
        print("\n⚠️ Some mobile deployment tests failed. Please review the issues above.")
        exit(1)
EOF

chmod +x scripts/validate_mobile_deployment.py
python scripts/validate_mobile_deployment.py
```

## Support Resources

### Documentation
- **[Mobile Implementation Guide](./MOBILE_IMPLEMENTATION_GUIDE.md)**: Technical implementation details
- **[Mobile Contributor Guide](./docs/MOBILE_CONTRIBUTOR_GUIDE.md)**: Development guidelines
- **[Mobile Testing Guide](./docs/MOBILE_QA_GUIDE.md)**: Testing strategies
- **[Mobile Performance Guide](./docs/MOBILE_PERFORMANCE_GUIDE.md)**: Optimization techniques
- **[Mobile Accessibility Guide](./docs/MODULE_ACCESSIBILITY_SUMMARY.md)**: Accessibility compliance

### Monitoring and Alerts
- Setup mobile-specific error tracking
- Configure Core Web Vitals monitoring
- Monitor PWA installation rates
- Track mobile user engagement metrics
- Alert on mobile performance regressions

### Maintenance
- Regular mobile performance audits
- PWA cache invalidation strategy
- Mobile browser compatibility updates
- Push notification certificate renewals
- Mobile analytics review and optimization