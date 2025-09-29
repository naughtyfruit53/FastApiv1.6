# Contributing to FastApiV1.5 Audit System

This guide provides comprehensive instructions for maintaining and extending the automated UI audit system in FastApiV1.5.

## 🎯 Overview

The FastApiV1.5 UI Audit System is a critical component that ensures continuous quality and accessibility of our ERP platform. Contributors should understand both the technical implementation and the business impact of audit maintenance.

## 🔧 Audit System Architecture

### Core Components

```
scripts/
├── audit_ui_features.py      # Main audit script
└── audit_helpers/            # Helper modules (future)

.github/
└── workflows/
    └── audit.yml            # CI/CD automation

audit_results/
├── screenshots/             # Visual debugging artifacts
├── audit_report_*.md       # Human-readable reports
└── audit_report_*.json     # Machine-readable data
```

### Key Classes

- **`UIAuditSystem`**: Main orchestrator class
- **`AuditResult`**: Data structure for individual feature results
- **`MenuSection`**: Navigation structure definition

## 📋 Adding New Features to Audit

### Step 1: Update Menu Structure

When adding new features to the application, you **must** update the audit system to maintain comprehensive coverage.

```python
# In scripts/audit_ui_features.py
self.menu_structure = {
    "your_new_module": {
        "title": "Your New Module",
        "path": "/your-module",
        "items": [
            {"name": "Feature A", "path": "/your-module/feature-a"},
            {"name": "Feature B", "path": "/your-module/feature-b"},
            # Add all accessible features
        ]
    }
    # ... existing modules
}
```

### Step 2: Define Feature Validation Rules

For complex features, add custom validation logic:

```python
async def audit_feature(self, feature_name: str, path: str) -> AuditResult:
    # ... existing audit logic ...
    
    # Custom validation for specific feature types
    if self._is_report_feature(path):
        await self._validate_report_functionality(feature_name, path)
    
    if self._is_voucher_feature(path):
        await self._validate_voucher_workflow(feature_name, path)
    
    if self._is_crud_feature(path):
        await self._validate_crud_operations(feature_name, path)
```

### Step 3: Update Test Data

Ensure the audit has appropriate test data for new features:

```python
# Add test data generation for new features
async def generate_test_data_for_feature(self, feature_type: str):
    if feature_type == "inventory":
        await self.create_test_products()
    elif feature_type == "vouchers":
        await self.create_test_vouchers()
    # Add cases for new feature types
```

## 🚀 CI/CD Workflow Maintenance

### Workflow Triggers

The audit workflow runs on:
- **Pull Requests** targeting `main` or `develop`
- **Pushes** to `main` branch
- **Daily schedule** at 2 AM UTC
- **Manual dispatch** with configurable scope

### Modifying Workflow Triggers

```yaml
# In .github/workflows/audit.yml
on:
  pull_request:
    branches: [ main, develop, staging ]  # Add new branches
    paths:
      - 'frontend/**'
      - 'app/**'
      - 'your-new-module/**'              # Add new paths
      - 'scripts/audit_ui_features.py'
      - '.github/workflows/audit.yml'
```

### Environment Configuration

Update environment URLs for new deployment targets:

```yaml
- name: 🔧 Set environment URLs
  id: urls
  run: |
    if [ "${{ github.event.inputs.environment }}" = "staging" ]; then
      echo "frontend-url=https://staging.your-domain.com" >> $GITHUB_OUTPUT
      echo "api-url=https://api-staging.your-domain.com" >> $GITHUB_OUTPUT
    fi
```

## 🔍 Debugging Failed Audits

### Local Debugging

```bash
# Run audit with visual browser for debugging
python scripts/audit_ui_features.py \
  --url http://localhost:3000 \
  --headless=false \
  --screenshots

# Debug specific feature
python -c "
import asyncio
from scripts.audit_ui_features import UIAuditSystem

async def debug_feature():
    audit = UIAuditSystem(headless=False)
    await audit.start_browser()
    await audit.login()
    result = await audit.audit_feature('Feature Name', '/feature/path')
    print(f'Result: {result.status} - {result.error_message}')
    await audit.cleanup()

asyncio.run(debug_feature())
"
```

### Analyzing Screenshots

Screenshots are automatically captured for:
- **Broken features** with runtime errors
- **Slow pages** (>5s load time)
- **Failed audits** due to exceptions

```bash
# View screenshots from failed audit
ls audit_results/screenshots/
open audit_results/screenshots/audit_feature_name_broken_20241219_103045.png
```

### Common Issues and Solutions

#### Authentication Failures
```python
# Update login credentials in audit script
async def login(self, username: str = "admin@test.com", password: str = "admin123"):
    # Verify credentials match your test environment
    # Check for changed selectors
    await self.page.fill('input[name="email"]', username)  # Update selector if needed
```

#### Selector Changes
```python
# Update feature validation selectors
error_selectors = [
    '[data-testid="error"]',    # Primary selector
    '.error',                   # Fallback selectors
    '.error-message',
    '.MuiAlert-standardError',  # Add new component selectors
    '[role="alert"]'
]
```

#### Timeout Issues
```python
# Adjust timeouts for slow environments
await self.page.goto(full_url, timeout=60000)  # Increase from 30000
await self.page.wait_for_load_state('networkidle', timeout=20000)  # Increase from 10000
```

## 📊 Performance Optimization

### Audit Performance Guidelines

- **Target audit runtime**: <10 minutes for full audit
- **Individual feature timeout**: <30 seconds
- **Screenshot capture**: Only for failures to reduce overhead
- **Parallel execution**: Future enhancement for cross-browser testing

### Optimizing Audit Speed

```python
# Skip unnecessary screenshots for passing features
if result.status == "accessible" and result.load_time < 3:
    result.screenshot_path = None
else:
    result.screenshot_path = await self.take_screenshot(...)

# Reduce wait times for fast features
if "dashboard" in path or "simple" in feature_name:
    timeout = 10000
else:
    timeout = 30000
```

### Caching Strategies

```python
# Cache authentication to avoid repeated logins
if not hasattr(self, '_authenticated'):
    await self.login()
    self._authenticated = True

# Cache navigation state
if not self.page.url.startswith(self.base_url):
    await self.page.goto(f"{self.base_url}/dashboard")
```

## 🎯 Quality Standards

### Accessibility Thresholds

- **Production**: ≥95% accessibility rate required
- **Staging**: ≥90% accessibility rate required  
- **Development**: ≥85% accessibility rate required

### Performance Budgets

- **Fast pages**: <2s load time (target 60%+ of features)
- **Medium pages**: 2-3s load time (acceptable)
- **Slow pages**: >3s load time (requires optimization)

### Code Quality Standards

```python
# Follow existing code patterns
@dataclass
class NewAuditResult:
    """Well-documented data class"""
    feature_name: str
    status: str  # Use enum in future versions
    timestamp: datetime
    
async def new_audit_method(self) -> AuditResult:
    """
    Async method with proper error handling
    
    Returns:
        AuditResult: Structured result data
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"Audit method failed: {str(e)}")
        raise
```

## 🔄 Release Process

### Pre-Release Checklist

1. **Test audit locally** with all new features
2. **Verify CI/CD workflow** on feature branch
3. **Update documentation** for new features
4. **Review performance impact** of changes
5. **Validate report formats** (Markdown + JSON)

### Release Steps

```bash
# 1. Create feature branch
git checkout -b feature/audit-enhancement

# 2. Make changes and test
python scripts/audit_ui_features.py --url http://localhost:3000

# 3. Commit with descriptive message
git commit -m "feat(audit): Add support for new inventory features"

# 4. Push and create PR
git push origin feature/audit-enhancement

# 5. Verify CI passes before merging
```

### Post-Release Validation

```bash
# Verify audit works on main branch
git checkout main
git pull origin main

# Run full audit to validate
python scripts/audit_ui_features.py --headless

# Check GitHub Actions are working
# Visit: https://github.com/your-org/FastApiV1.5/actions
```

## 📚 Advanced Customization

### Custom Validation Rules

```python
class CustomAuditRules:
    """Define business-specific validation rules"""
    
    @staticmethod
    async def validate_erp_workflow(page, feature_name: str):
        """Validate ERP-specific workflows"""
        if "voucher" in feature_name.lower():
            # Check for required voucher fields
            required_fields = ['voucher_number', 'date', 'reference']
            for field in required_fields:
                element = await page.query_selector(f'[name="{field}"]')
                assert element, f"Missing required field: {field}"
    
    @staticmethod
    async def validate_crm_workflow(page, feature_name: str):
        """Validate CRM-specific workflows"""
        if "service" in feature_name.lower():
            # Check for service-specific components
            pass
```

### Browser Configuration

```python
# Custom browser settings for specific environments
async def start_browser(self, browser_type: str = "chromium"):
    """Enhanced browser initialization"""
    playwright = await async_playwright().start()
    
    if browser_type == "chromium":
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',  # For CI environments
                '--no-sandbox'              # For Docker environments
            ]
        )
    elif browser_type == "firefox":
        self.browser = await playwright.firefox.launch(headless=self.headless)
```

### Reporting Customization

```python
def generate_custom_report(self, report_type: str = "executive"):
    """Generate custom report formats"""
    if report_type == "executive":
        return self._generate_executive_summary()
    elif report_type == "technical":
        return self._generate_technical_details()
    elif report_type == "performance":
        return self._generate_performance_analysis()
```

## 🤝 Getting Help

### Resources
- **Playwright Documentation**: https://playwright.dev/python/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **GitHub Actions**: https://docs.github.com/en/actions

### Contact
- **Technical Issues**: Create GitHub issue with `audit-system` label
- **Enhancement Requests**: Discuss in team meetings
- **Urgent Problems**: Contact DevOps team directly

### Contributing Guidelines
1. **Follow existing patterns** and code style
2. **Add comprehensive tests** for new functionality
3. **Update documentation** for all changes
4. **Test across environments** before submitting PRs
5. **Consider performance impact** of modifications

## 📱 Mobile Development Guidelines

### Mobile-First Development Workflow

#### 1. Setting Up Mobile Development Environment

```bash
# Install mobile testing dependencies
npm install --save-dev @playwright/test
playwright install

# Install mobile development tools
npm install --save-dev @types/react-native
npm install react-native-web

# Setup mobile emulation for testing
npm run test:mobile:setup
```

#### 2. Mobile Component Development Standards

##### Component Architecture
```typescript
// Follow the additive mobile pattern
// ✅ Correct: Additive mobile components
export const AdaptiveDataGrid = () => {
  const { isMobile } = useDeviceDetection();
  
  return isMobile ? (
    <MobileDataGrid {...props} />
  ) : (
    <DesktopDataGrid {...props} />
  );
};

// ❌ Incorrect: Modifying existing desktop components
export const DataGrid = ({ isMobile, ...props }) => {
  // Don't modify existing components
};
```

##### Mobile Component Checklist
- [ ] **Touch Targets**: Minimum 44px click targets
- [ ] **Accessibility**: ARIA labels and semantic markup
- [ ] **Performance**: Lazy loading and virtualization
- [ ] **Gestures**: Touch, swipe, and pinch support
- [ ] **Responsive**: Works across device sizes
- [ ] **Offline**: Functions with limited connectivity

#### 3. Mobile Testing Requirements

##### Required Test Coverage
```typescript
// Every mobile component must include these tests
describe('MobileComponent', () => {
  // Device compatibility
  it('renders correctly on mobile devices', () => {});
  it('handles touch interactions', () => {});
  it('supports accessibility features', () => {});
  it('performs well under slow network conditions', () => {});
  
  // Gesture tests
  it('handles swipe gestures', () => {});
  it('supports pinch-to-zoom', () => {});
  it('responds to long press', () => {});
});
```

##### Mobile Test Command Standards
```bash
# Run mobile-specific tests
npm run test:mobile

# Test across multiple device profiles
npm run test:devices

# Performance testing on mobile
npm run test:mobile:performance

# Accessibility compliance testing
npm run test:mobile:accessibility
```

#### 4. Mobile Code Review Criteria

##### Pre-Submission Checklist
- [ ] **Device Testing**: Tested on iOS and Android browsers
- [ ] **Performance**: Mobile PageSpeed score > 90
- [ ] **Accessibility**: WCAG 2.1 AA compliance verified
- [ ] **Offline Support**: Works with limited connectivity
- [ ] **Touch Interface**: All interactions work with touch
- [ ] **Battery Efficiency**: No excessive battery drain

##### Code Quality Standards
```typescript
// ✅ Follow mobile-specific patterns
const MobileOptimizedComponent = memo(() => {
  const { isMobile } = useDeviceDetection();
  
  // Lazy load heavy components
  const HeavyChart = lazy(() => import('./HeavyChart'));
  
  // Use mobile-optimized state management
  const [data] = useMobileOptimizedQuery('getData');
  
  return (
    <Suspense fallback={<MobileSkeletonLoader />}>
      <MobileContainer>
        {isMobile ? <MobileView /> : <DesktopView />}
      </MobileContainer>
    </Suspense>
  );
});
```

#### 5. Mobile Performance Guidelines

##### Core Web Vitals Requirements
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **Mobile PageSpeed Score**: > 90

##### Optimization Patterns
```typescript
// Image optimization for mobile
<MobileOptimizedImage
  src="/api/images/product.jpg"
  alt="Product image"
  loading="lazy"
  sizes="(max-width: 768px) 100vw, 50vw"
  srcSet="/api/images/product-400.jpg 400w, /api/images/product-800.jpg 800w"
/>

// Data pagination for mobile
const { data, loadMore, hasNextPage } = useMobilePagination({
  endpoint: '/api/data',
  pageSize: 20, // Smaller page size for mobile
  prefetch: 1 // Prefetch next page
});
```

#### 6. Mobile Accessibility Standards

##### WCAG 2.1 AA Compliance Requirements
```typescript
// Semantic HTML structure
<MobileCard
  role="article"
  aria-labelledby="card-title"
  aria-describedby="card-description"
  tabIndex={0}
>
  <h3 id="card-title">Card Title</h3>
  <p id="card-description">Card description</p>
</MobileCard>

// Focus management
const handleMobileNavigation = () => {
  // Ensure focus moves to main content after navigation
  const mainContent = document.getElementById('main-content');
  mainContent?.focus();
};
```

##### Screen Reader Testing
```bash
# Test with VoiceOver (macOS)
# Use iOS Simulator with VoiceOver enabled

# Test with TalkBack (Android)
# Use Android Emulator with TalkBack enabled

# Automated accessibility testing
npm run test:accessibility:mobile
```

#### 7. Mobile-Specific Git Workflow

##### Branch Naming Convention
```bash
# Mobile feature branches
git checkout -b mobile/feature-name
git checkout -b mobile/fix-touch-interaction
git checkout -b mobile/performance-optimization

# Mobile testing branches  
git checkout -b mobile-tests/component-name
```

##### Commit Message Standards
```bash
# Mobile-specific commit formats
git commit -m "mobile: add swipe gesture support to DataGrid"
git commit -m "mobile: optimize image loading for touch devices"
git commit -m "mobile: fix accessibility focus management"
git commit -m "mobile-test: add device emulation tests"
```

#### 8. Mobile Documentation Requirements

##### Required Documentation Updates
For every mobile feature, update:
- [ ] Component documentation with mobile-specific props
- [ ] Usage examples for mobile contexts
- [ ] Performance considerations
- [ ] Accessibility implementation notes
- [ ] Testing instructions
- [ ] Browser support matrix

##### Documentation Format
```markdown
## MobileComponent

### Mobile-Specific Features
- Touch gesture support
- Responsive breakpoints
- Accessibility features
- Performance optimizations

### Usage Examples
\`\`\`typescript
// Basic mobile usage
<MobileComponent
  data={data}
  onSwipe={handleSwipe}
  touchTargetSize="large"
  accessibilityLabel="Interactive data component"
/>
\`\`\`

### Performance Notes
- Uses virtual scrolling for large datasets
- Lazy loads images below the fold
- Implements pull-to-refresh pattern

### Browser Support
- iOS Safari 14+
- Chrome Mobile 90+
- Samsung Internet 14+
```

#### 9. Mobile Integration Testing

##### End-to-End Mobile Tests
```typescript
// Playwright mobile integration tests
test.describe('Mobile Workflow', () => {
  test.use({ 
    ...devices['iPhone 12'],
    contextOptions: {
      permissions: ['notifications', 'geolocation']
    }
  });

  test('complete mobile user journey', async ({ page }) => {
    // Test full mobile workflow
    await page.goto('/mobile');
    await expect(page.locator('[data-testid=mobile-nav]')).toBeVisible();
    
    // Test touch interactions
    await page.locator('[data-testid=swipeable-card]').swipe('left');
    await expect(page.locator('[data-testid=action-menu]')).toBeVisible();
  });
});
```

### Mobile Development Resources

- **[Mobile Implementation Guide](./MOBILE_IMPLEMENTATION_GUIDE.md)**: Comprehensive technical guide
- **[Mobile Testing Guide](./docs/MOBILE_QA_GUIDE.md)**: Testing strategies and best practices
- **[Mobile Accessibility Guide](./docs/MODULE_ACCESSIBILITY_SUMMARY.md)**: WCAG compliance details
- **[Mobile Performance Guide](./docs/MOBILE_PERFORMANCE_GUIDE.md)**: Optimization strategies

---

Thank you for contributing to the FastApiV1.5 audit system! Your contributions help maintain the quality and reliability of our ERP platform. 🚀