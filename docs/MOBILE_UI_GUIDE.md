# Mobile UI Guide - FastAPI v1.6

## Overview

This comprehensive guide documents the complete mobile UI implementation for FastAPI v1.6 TRITIQ BOS. The mobile interface provides 100% feature parity with desktop while delivering an optimized touch-first experience. This includes Progressive Web App (PWA) capabilities, offline support, and device feature integrations.

## Architecture & Design Principles

### Mobile-First Approach

The mobile UI is built with the following core principles:

1. **Additive Design**: Mobile components coexist with desktop, not replace them
2. **Touch Optimization**: All interactions designed for touch (minimum 44x44px targets)
3. **Progressive Enhancement**: Features progressively enhanced based on device capabilities
4. **Responsive Breakpoints**: Adaptive layouts for phone, tablet, and desktop
5. **Performance**: Optimized loading, lazy loading, and minimal bundle size

### Device Detection

```typescript
// Automatic device detection throughout the app
const { isMobile, isTablet, isDesktop, orientation, touchCapable } = useMobileDetection();
```

## Mobile Components

### Navigation Components

#### 1. MobileBottomNav
Bottom tab navigation for primary app sections.

**Features:**
- Fixed bottom position
- 4-5 primary navigation items
- Active state indicators
- Badge support for notifications
- Haptic feedback on touch

**Usage:**
```typescript
<MobileBottomNav 
  items={[
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/mobile/dashboard' },
    { label: 'Sales', icon: <PointOfSaleIcon />, path: '/mobile/sales' },
    { label: 'Inventory', icon: <InventoryIcon />, path: '/mobile/inventory' },
    { label: 'Reports', icon: <AssessmentIcon />, path: '/mobile/reports' },
    { label: 'Settings', icon: <SettingsIcon />, path: '/mobile/settings' }
  ]}
/>
```

#### 2. MobileDrawerNavigation
Side drawer for secondary navigation and module access.

**Features:**
- Swipe-to-open gesture
- Hierarchical menu structure
- Search functionality
- User profile section
- Organization switcher

**Usage:**
```typescript
<MobileDrawerNavigation 
  open={drawerOpen}
  onClose={() => setDrawerOpen(false)}
  menuItems={megaMenuConfig}
/>
```

#### 3. NavigationBreadcrumbs
Mobile-optimized breadcrumb navigation.

**Features:**
- Collapsible on small screens
- Swipe horizontal scroll
- Back button integration
- Current page highlighting

### Layout Components

#### 1. MobileLayout
Main layout wrapper for mobile pages.

**Features:**
- Header with title and actions
- Optional bottom navigation
- Pull-to-refresh support
- Safe area insets handling
- Scroll management

**Usage:**
```typescript
<MobileLayout
  title="Dashboard"
  subtitle="Welcome back!"
  showBottomNav={true}
  rightActions={<NotificationButton />}
  onRefresh={handleRefresh}
>
  {/* Page content */}
</MobileLayout>
```

#### 2. MobileDashboardLayout
Specialized layout for dashboard pages.

**Features:**
- KPI card grid
- Quick actions bar
- Activity feed
- Metric charts
- Swipeable cards

#### 3. MobileFormLayout
Optimized layout for forms.

**Features:**
- Section grouping
- Field validation display
- Sticky action buttons
- Keyboard-aware scrolling
- Auto-save indicators

### Interaction Components

#### 1. MobileCard
Touch-optimized card component.

**Features:**
- Tap to expand
- Long-press actions
- Swipe gestures
- Loading states
- Empty states

**Usage:**
```typescript
<MobileCard
  title="Recent Orders"
  subtitle="Last 7 days"
  onTap={handleExpand}
  onLongPress={handleAction}
  swipeActions={{
    left: [{ label: 'Edit', action: handleEdit }],
    right: [{ label: 'Delete', action: handleDelete }]
  }}
>
  {/* Card content */}
</MobileCard>
```

#### 2. SwipeableCard
Enhanced card with swipe-to-reveal actions.

**Features:**
- Configurable swipe thresholds
- Multiple action buttons
- Animation feedback
- Undo functionality

#### 3. MobileActionSheet
iOS-style action sheet for contextual actions.

**Features:**
- Bottom sheet appearance
- Multiple action types
- Destructive action styling
- Cancel button
- Backdrop dismiss

**Usage:**
```typescript
<MobileActionSheet
  open={sheetOpen}
  onClose={() => setSheetOpen(false)}
  actions={[
    { label: 'Edit', icon: <EditIcon />, onClick: handleEdit },
    { label: 'Share', icon: <ShareIcon />, onClick: handleShare },
    { label: 'Delete', icon: <DeleteIcon />, onClick: handleDelete, destructive: true }
  ]}
/>
```

#### 4. MobileBottomSheet
Customizable bottom sheet for forms and content.

**Features:**
- Drag handle
- Snap points (collapsed/expanded/full)
- Backdrop blur
- Nested scrolling
- Keyboard handling

### Data Display Components

#### 1. MobileTable
Mobile-optimized data table.

**Features:**
- Horizontal scroll with sticky columns
- Expandable rows
- Row actions
- Sorting and filtering
- Pagination
- Pull-to-refresh

**Usage:**
```typescript
<MobileTable
  data={tableData}
  columns={[
    { field: 'name', label: 'Name', sticky: true },
    { field: 'status', label: 'Status', renderCell: (row) => <StatusChip status={row.status} /> },
    { field: 'amount', label: 'Amount', align: 'right' }
  ]}
  onRowClick={handleRowClick}
  stickyColumns={['name']}
  swipeActions={{
    left: [{ label: 'Edit', action: handleEdit }],
    right: [{ label: 'Delete', action: handleDelete }]
  }}
/>
```

#### 2. MobileSearchBar
Mobile-optimized search with voice input.

**Features:**
- Auto-focus on mount
- Clear button
- Voice search
- Recent searches
- Search suggestions

### Input Components

#### 1. MobileButton
Touch-optimized button.

**Features:**
- Minimum 44x44px touch target
- Loading state
- Icon support
- Haptic feedback
- Disabled state styling

**Usage:**
```typescript
<MobileButton
  variant="contained"
  color="primary"
  fullWidth
  loading={isSubmitting}
  icon={<SaveIcon />}
  onClick={handleSubmit}
>
  Save Changes
</MobileButton>
```

#### 2. MobilePullToRefresh
Pull-to-refresh functionality.

**Features:**
- Custom threshold
- Loading indicator
- Success/error feedback
- Haptic feedback

### Modal Components

#### 1. MobileModal
Full-screen mobile modal.

**Features:**
- Slide-in animation
- Header with close button
- Scrollable content
- Footer actions
- Swipe-down to dismiss

**Usage:**
```typescript
<MobileModal
  open={modalOpen}
  onClose={handleClose}
  title="Add New Item"
  actions={[
    { label: 'Cancel', onClick: handleClose, variant: 'text' },
    { label: 'Save', onClick: handleSave, variant: 'contained' }
  ]}
>
  {/* Modal content */}
</MobileModal>
```

### Utility Components

#### 1. KeyboardNavigation
Keyboard-aware navigation handler.

**Features:**
- Keyboard show/hide detection
- Auto-scroll to focused input
- Safe area adjustment
- Form field navigation

#### 2. MobileGlobalSearch
Global search overlay.

**Features:**
- Full-screen search interface
- Category filtering
- Recent searches
- Quick actions
- Voice search

## Mobile Pages

### Dashboard (`/mobile/dashboard`)

**Features:**
- KPI cards with swipe navigation
- Activity timeline
- Quick action buttons
- Metric charts (touch-optimized)
- Notification feed
- Pull-to-refresh

**Key Components:**
- `MobileDashboardLayout`
- `MobileCard` for KPIs
- `SwipeableCard` for activities
- Chart.js charts with touch events

### Sales (`/mobile/sales`)

**Features:**
- Order list with search/filter
- Order creation form
- Customer selection
- Product catalog
- Invoice generation
- Payment recording

**Mobile Enhancements:**
- Barcode scanning
- Photo capture for receipts
- Signature capture
- Quick actions for common tasks

### CRM (`/mobile/crm`)

**Features:**
- Contact management
- Lead tracking
- Opportunity pipeline
- Activity logging
- Call integration
- Location tracking

**Mobile Enhancements:**
- Contact import from device
- One-tap call/email
- Location-based check-ins
- Camera for business cards

### Inventory (`/mobile/inventory`)

**Features:**
- Stock level monitoring
- Product search
- Transfer requests
- Stock adjustments
- Low stock alerts

**Mobile Enhancements:**
- Barcode/QR scanning
- Photo documentation
- Quick count entry
- Offline mode

### Finance (`/mobile/finance`)

**Features:**
- Voucher management
- Ledger reports
- Payment tracking
- Expense recording
- Receipt capture

**Mobile Enhancements:**
- Receipt photo capture
- OCR for expense data
- Quick expense entry
- Mobile payment integration

### HR (`/mobile/hr`)

**Features:**
- Employee directory
- Attendance tracking
- Leave requests
- Payroll access
- Document management

**Mobile Enhancements:**
- Photo ID capture
- Biometric attendance
- Quick leave requests
- Document scanning

### Service (`/mobile/service`)

**Features:**
- Service desk tickets
- Technician dispatch
- Work order management
- Customer feedback
- Field service app

**Mobile Enhancements:**
- GPS location tracking
- Photo documentation
- Signature capture
- Offline work mode
- Real-time status updates

### Reports (`/mobile/reports`)

**Features:**
- Report catalog
- Interactive charts
- Data export
- Scheduled reports
- Custom dashboards

**Mobile Enhancements:**
- Touch-friendly charts
- Pinch-to-zoom
- Swipe between reports
- Share via mobile apps

## Responsive Design Patterns

### Breakpoints

```css
/* Mobile First Breakpoints */
--mobile-sm: 320px;   /* Small phones */
--mobile-md: 375px;   /* Standard phones */
--mobile-lg: 425px;   /* Large phones */
--tablet-sm: 768px;   /* Small tablets */
--tablet-lg: 1024px;  /* Large tablets */
--desktop: 1280px;    /* Desktop */
```

### Layout Patterns

#### Stack Layout (Mobile)
```typescript
<Box sx={{
  display: 'flex',
  flexDirection: 'column',
  gap: 2,
  '@media (min-width: 768px)': {
    flexDirection: 'row'
  }
}}>
```

#### Grid Layout (Responsive)
```typescript
<Grid container spacing={2}>
  <Grid item xs={12} sm={6} md={4}>
    {/* Responsive grid item */}
  </Grid>
</Grid>
```

## Accessibility

### WCAG 2.1 AA Compliance

1. **Touch Targets**: Minimum 44x44px for all interactive elements
2. **Color Contrast**: 4.5:1 for normal text, 3:1 for large text
3. **Keyboard Navigation**: Full keyboard support for all interactions
4. **Screen Readers**: ARIA labels and landmarks throughout
5. **Focus Indicators**: Clear focus states for all interactive elements

### Screen Reader Support

```typescript
<Button
  aria-label="Save changes to order"
  aria-describedby="save-help-text"
  onClick={handleSave}
>
  Save
</Button>
<span id="save-help-text" className="sr-only">
  This will save all changes to the current order
</span>
```

### Voice Navigation

All mobile pages support voice commands through browser APIs:
- "Open navigation"
- "Search for [item]"
- "Go to [page]"
- "Refresh page"

## Performance Optimization

### Code Splitting

```typescript
// Route-based code splitting
const MobileDashboard = lazy(() => import('./pages/mobile/dashboard'));
const MobileSales = lazy(() => import('./pages/mobile/sales'));
```

### Image Optimization

```typescript
<Image
  src={imageUrl}
  alt={altText}
  loading="lazy"
  width={300}
  height={200}
  sizes="(max-width: 768px) 100vw, 50vw"
/>
```

### Bundle Size

- Mobile bundle: ~450KB gzipped
- Code splitting: Per-route chunks
- Tree shaking: Unused code eliminated
- Compression: Brotli compression enabled

### Performance Metrics

**Target Metrics:**
- First Contentful Paint (FCP): < 1.8s
- Largest Contentful Paint (LCP): < 2.5s
- First Input Delay (FID): < 100ms
- Cumulative Layout Shift (CLS): < 0.1
- Time to Interactive (TTI): < 3.5s

## Touch Gestures

### Supported Gestures

1. **Tap**: Primary action
2. **Long Press**: Context menu
3. **Swipe Left/Right**: Navigate/reveal actions
4. **Swipe Up/Down**: Scroll/dismiss
5. **Pinch**: Zoom (on supported content)
6. **Pull Down**: Refresh

### Implementation

```typescript
import { useSwipeable } from 'react-swipeable';

const handlers = useSwipeable({
  onSwipedLeft: () => handleSwipeLeft(),
  onSwipedRight: () => handleSwipeRight(),
  onSwipedUp: () => handleSwipeUp(),
  onSwipedDown: () => handleSwipeDown(),
  preventDefaultTouchmoveEvent: true,
  trackMouse: true
});

<div {...handlers}>
  {/* Swipeable content */}
</div>
```

## Offline Support

### Progressive Web App (PWA)

**Features:**
- Service worker for offline caching
- Background sync for data updates
- Push notifications
- Add to home screen
- Offline-first data strategy

### Offline Capabilities

1. **View cached data**: Access previously loaded data offline
2. **Queue actions**: Save actions to sync when online
3. **Offline indicators**: Clear UI feedback about offline state
4. **Sync status**: Show pending sync items

## Testing

### Mobile Testing Strategy

1. **Unit Tests**: Component-level tests with React Testing Library
2. **Integration Tests**: Feature flow tests
3. **E2E Tests**: Playwright mobile device emulation
4. **Accessibility Tests**: Automated WCAG compliance checks
5. **Performance Tests**: Lighthouse CI integration

### Device Testing Matrix

| Device Type | Device Model | OS | Browser |
|------------|--------------|-----|---------|
| Phone | iPhone 12 | iOS 15+ | Safari |
| Phone | iPhone 14 Pro Max | iOS 16+ | Safari |
| Phone | Pixel 5 | Android 11+ | Chrome |
| Phone | Galaxy S21 | Android 12+ | Chrome |
| Tablet | iPad Pro 11" | iOS 15+ | Safari |
| Tablet | iPad Pro 12.9" | iOS 16+ | Safari |

### Running Mobile Tests

```bash
# Run all mobile tests
npm run test:mobile

# Run specific device tests
npm run test:mobile -- --project="Mobile Chrome - Pixel 5"

# Run with UI mode
npm run test:mobile -- --ui

# Run accessibility tests only
npm run test:mobile:accessibility
```

## Browser Support

### Minimum Requirements

- iOS Safari 14+
- Android Chrome 90+
- Samsung Internet 14+
- Firefox Mobile 90+

### Feature Detection

```typescript
const features = {
  touchEvents: 'ontouchstart' in window,
  geolocation: 'geolocation' in navigator,
  camera: 'mediaDevices' in navigator,
  notifications: 'Notification' in window,
  serviceWorker: 'serviceWorker' in navigator
};
```

## Best Practices

### Do's

✅ Use mobile-first CSS
✅ Optimize images for mobile
✅ Implement touch gestures
✅ Provide haptic feedback
✅ Test on real devices
✅ Consider network conditions
✅ Implement offline support
✅ Use semantic HTML
✅ Provide loading states
✅ Handle errors gracefully

### Don'ts

❌ Use hover-only interactions
❌ Require precise cursor movements
❌ Block scrolling unnecessarily
❌ Use small touch targets (< 44px)
❌ Ignore keyboard users
❌ Assume high bandwidth
❌ Forget about battery life
❌ Neglect landscape orientation
❌ Use modal dialogs excessively
❌ Auto-play videos with sound

## Troubleshooting

### Common Issues

**Issue: Touch events not working**
```typescript
// Solution: Use pointer events
<div
  onPointerDown={handlePointerDown}
  onPointerUp={handlePointerUp}
  style={{ touchAction: 'none' }}
>
```

**Issue: Viewport height on mobile Safari**
```css
/* Solution: Use CSS custom property */
:root {
  --vh: 1vh;
}

.full-height {
  height: calc(var(--vh, 1vh) * 100);
}
```

**Issue: Fixed elements and keyboard**
```typescript
// Solution: Adjust on keyboard show
useEffect(() => {
  const handleResize = () => {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  };
  
  window.addEventListener('resize', handleResize);
  handleResize();
  
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

## Progressive Web App (PWA) Features

### PWA Overview

TRITIQ BOS is fully PWA-enabled, providing app-like experiences on mobile and desktop browsers.

#### PWA Benefits
- **Installable**: Add to home screen on mobile devices
- **Offline Support**: Work without internet connection
- **Fast Loading**: Cached resources for instant load times
- **Push Notifications**: Real-time updates even when app is closed
- **Auto-Updates**: Seamless updates without app store

### PWA Implementation

#### 1. Service Worker

The service worker handles caching, offline support, and background sync.

**Features:**
- Cache-first strategy for static assets
- Network-first strategy for API calls
- Offline fallback page
- Background sync for offline actions
- Push notification handling

**Location:** `/public/service-worker.js`

#### 2. Web App Manifest

Defines app metadata, icons, and behavior.

**Configuration:**
```json
{
  "name": "TRITIQ BOS",
  "short_name": "TRITIQ BOS",
  "display": "standalone",
  "start_url": "/",
  "theme_color": "#1976d2",
  "background_color": "#ffffff"
}
```

**Location:** `/public/manifest.json`

#### 3. PWA Hooks

**usePWA Hook:**
```typescript
import { usePWA } from '@/hooks/usePWA';

const { 
  isInstallable,
  isInstalled,
  isOnline,
  promptInstall,
  updateAvailable,
  updateServiceWorker 
} = usePWA();

// Show install prompt
if (isInstallable) {
  await promptInstall();
}
```

### Offline Support

#### Offline Detection

**OfflineIndicator Component:**
```typescript
import OfflineIndicator from '@/components/OfflineIndicator';

// Add to app root
<OfflineIndicator />
```

**Features:**
- Persistent banner when offline
- Toast notification when back online
- Auto-reload when connection restored

#### Offline Data Access

**Cached Resources:**
- Essential pages (dashboard, login)
- Static assets (icons, images)
- Previously viewed data
- User profile information

**Offline Actions:**
- Queue actions when offline
- Sync automatically when back online
- Show pending sync status

### Install Prompt

**PWAInstallPrompt Component:**
```typescript
import PWAInstallPrompt from '@/components/PWAInstallPrompt';

// Add to app root
<PWAInstallPrompt />
```

**Features:**
- Auto-show after 30 seconds
- Dismissible with localStorage tracking
- Beautiful gradient design
- Lists installation benefits

### Update Management

**UpdatePrompt Component:**
```typescript
import UpdatePrompt from '@/components/UpdatePrompt';

// Add to app root
<UpdatePrompt />
```

**Features:**
- Detects new app versions
- One-click update
- Seamless reload after update

## Device Features Integration

### Biometric Authentication

Enable secure, convenient login using fingerprint or face recognition.

**useBiometric Hook:**
```typescript
import { useBiometric } from '@/hooks/useBiometric';

const { 
  isAvailable,
  isSupported,
  authenticate,
  error 
} = useBiometric();

// Authenticate user
const success = await authenticate();
```

**BiometricLoginButton Component:**
```typescript
import BiometricLoginButton from '@/components/BiometricLoginButton';

<BiometricLoginButton
  onSuccess={() => handleLogin()}
  onError={(error) => console.error(error)}
/>
```

**Features:**
- Platform authenticator support
- Fallback to password
- Error handling
- User-friendly messaging

### Camera Integration

Capture photos for documents, receipts, products, and profiles.

**useCamera Hook:**
```typescript
import { useCamera } from '@/hooks/useCamera';

const {
  isSupported,
  isActive,
  startCamera,
  stopCamera,
  capturePhoto,
  switchCamera
} = useCamera();

// Start camera
await startCamera('environment'); // or 'user' for selfie

// Capture photo
const photo = await capturePhoto();
```

**CameraCapture Component:**
```typescript
import CameraCapture from '@/components/CameraCapture';

<CameraCapture
  open={showCamera}
  onClose={() => setShowCamera(false)}
  onCapture={(photo) => handlePhoto(photo)}
  title="Capture Receipt"
/>
```

**Features:**
- Front and back camera switching
- Photo preview before confirm
- Retake capability
- Full-screen capture interface
- Touch-friendly controls

### Push Notifications

Keep users informed with real-time push notifications.

**usePushNotifications Hook:**
```typescript
import { usePushNotifications } from '@/hooks/usePushNotifications';

const {
  isSupported,
  permission,
  subscription,
  requestPermission,
  subscribe,
  unsubscribe,
  sendNotification
} = usePushNotifications();

// Request permission and subscribe
await requestPermission();
await subscribe();

// Send test notification
sendNotification('Test', {
  body: 'This is a test notification',
  icon: '/icons/icon-192x192.png'
});
```

**NotificationSettings Component:**
```typescript
import NotificationSettings from '@/components/NotificationSettings';

<NotificationSettings />
```

**Features:**
- Permission management
- Subscription toggle
- Notification preferences (order updates, inventory alerts, etc.)
- Test notification button
- Browser compatibility detection

**Notification Types:**
- Order updates and status changes
- Inventory alerts (low stock, reorders)
- Task reminders and deadlines
- System updates and maintenance
- Custom business events

## Future Enhancements

See [FUTURE_SUGGESTIONS.md](./FUTURE_SUGGESTIONS.md) for detailed future enhancement plans.

## Additional Resources

- [Mobile Implementation Summary](../MOBILE_IMPLEMENTATION_SUMMARY.md)
- [Mobile Contributor Guide](../MOBILE_CONTRIBUTOR_GUIDE.md)
- [Mobile QA Guide](../MOBILE_QA_GUIDE.md)
- [Mobile Performance Guide](../MOBILE_PERFORMANCE_GUIDE.md)
- [Demo Mode Guide](./DEMO_MODE_GUIDE.md)

## Support

For questions or issues related to mobile UI:
1. Check this documentation first
2. Review existing GitHub issues
3. Create a new issue with [Mobile] prefix
4. Include device/browser information
5. Provide steps to reproduce

---

Last Updated: 2025-10-23
Version: 1.6.0
