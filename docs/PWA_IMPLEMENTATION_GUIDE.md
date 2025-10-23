# Progressive Web App (PWA) Implementation Guide

## Overview

TritIQ Business Suite now includes complete Progressive Web App (PWA) support, enabling users to install the app on their devices and use it offline. This guide covers the implementation, deployment, and best practices.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Setup](#setup)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Features

### Core PWA Features

1. **Installable**: Users can add the app to their home screen
2. **Offline Support**: App works without internet connection
3. **Fast Loading**: Cached resources load instantly
4. **Push Notifications**: Real-time updates even when app is closed
5. **Auto Updates**: Seamless updates without app store

### Implemented Components

#### Service Worker
- **Location**: `/public/service-worker.js`
- **Features**:
  - Cache-first strategy for static assets
  - Network-first strategy for API calls
  - Offline fallback page
  - Background sync for offline actions
  - Push notification handling

#### Web App Manifest
- **Location**: `/public/manifest.json`
- **Configured**: App name, icons, colors, display mode, shortcuts

#### React Hooks

**usePWA Hook** (`src/hooks/usePWA.ts`):
```typescript
const {
  isInstallable,    // Can the app be installed?
  isInstalled,      // Is it already installed?
  isOnline,         // Is device online?
  promptInstall,    // Show install prompt
  updateAvailable,  // Is there an update?
  updateServiceWorker // Apply update
} = usePWA();
```

**useBiometric Hook** (`src/hooks/useBiometric.ts`):
```typescript
const {
  isAvailable,    // Is biometric available?
  isSupported,    // Is it supported?
  authenticate,   // Perform authentication
  error          // Any errors
} = useBiometric();
```

**useCamera Hook** (`src/hooks/useCamera.ts`):
```typescript
const {
  isSupported,   // Is camera supported?
  isActive,      // Is camera active?
  startCamera,   // Start camera
  stopCamera,    // Stop camera
  capturePhoto,  // Capture photo
  switchCamera   // Switch front/back
} = useCamera();
```

**usePushNotifications Hook** (`src/hooks/usePushNotifications.ts`):
```typescript
const {
  isSupported,        // Are notifications supported?
  permission,         // Current permission status
  subscription,       // Current subscription
  requestPermission,  // Request permission
  subscribe,          // Subscribe to notifications
  unsubscribe,        // Unsubscribe
  sendNotification   // Send test notification
} = usePushNotifications();
```

#### React Components

1. **PWAInstallPrompt**: Auto-shows install prompt after 30 seconds
2. **OfflineIndicator**: Shows banner when offline
3. **UpdatePrompt**: Notifies about available updates
4. **BiometricLoginButton**: Quick biometric login
5. **CameraCapture**: Full camera capture UI
6. **NotificationSettings**: Notification preferences management

## Architecture

### Service Worker Strategy

```
┌─────────────────────────────────────┐
│         Browser Request             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│       Service Worker                │
│  ┌──────────────────────────────┐  │
│  │   Is it an API request?      │  │
│  └──────────────────────────────┘  │
│         Yes │        │ No           │
│             ▼        ▼              │
│  ┌──────────────────────────────┐  │
│  │  Network First │ Cache First │  │
│  └──────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Response (from network/cache)   │
└─────────────────────────────────────┘
```

### Caching Strategy

**Static Assets** (Cache First):
- HTML pages
- CSS files
- JavaScript bundles
- Images and icons
- Fonts

**API Requests** (Network First):
- GET requests
- Cached as fallback
- 5-minute stale-while-revalidate

**Offline Actions** (Background Sync):
- POST/PUT/DELETE requests queued
- Synced when connection restored
- Stored in IndexedDB

## Setup

### 1. Install Dependencies

Already included in package.json. No additional dependencies needed.

### 2. Configure Next.js

Update `next.config.mjs`:

```javascript
const nextConfig = {
  // ... existing config
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Don't bundle service worker
      config.resolve.alias = {
        ...config.resolve.alias,
        'service-worker': false,
      };
    }
    return config;
  },
};
```

### 3. Add to HTML Head

In your root layout or _document:

```typescript
<head>
  <link rel="manifest" href="/manifest.json" />
  <meta name="theme-color" content="#1976d2" />
  <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
</head>
```

### 4. Initialize Service Worker

In your root layout:

```typescript
import { useEffect } from 'react';
import PWAInstallPrompt from '@/components/PWAInstallPrompt';
import OfflineIndicator from '@/components/OfflineIndicator';
import UpdatePrompt from '@/components/UpdatePrompt';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <PWAInstallPrompt />
        <OfflineIndicator />
        <UpdatePrompt />
      </body>
    </html>
  );
}
```

### 5. Generate Icons

Create PWA icons in required sizes (see `/public/icons/README.md`).

## Usage

### Install Prompt

The install prompt shows automatically after 30 seconds for installable apps:

```typescript
import PWAInstallPrompt from '@/components/PWAInstallPrompt';

// Add to app root
<PWAInstallPrompt />
```

Or trigger manually:

```typescript
import { usePWA } from '@/hooks/usePWA';

const { isInstallable, promptInstall } = usePWA();

if (isInstallable) {
  await promptInstall();
}
```

### Offline Detection

```typescript
import { usePWA } from '@/hooks/usePWA';

const { isOnline } = usePWA();

if (!isOnline) {
  showOfflineMessage();
}
```

### Update Management

```typescript
import { usePWA } from '@/hooks/usePWA';

const { updateAvailable, updateServiceWorker } = usePWA();

if (updateAvailable) {
  // Show update prompt
  updateServiceWorker(); // Apply update
}
```

### Biometric Authentication

```typescript
import BiometricLoginButton from '@/components/BiometricLoginButton';

<BiometricLoginButton
  onSuccess={() => handleLogin()}
  onError={(error) => showError(error)}
/>
```

### Camera Capture

```typescript
import CameraCapture from '@/components/CameraCapture';

<CameraCapture
  open={showCamera}
  onClose={() => setShowCamera(false)}
  onCapture={(photo) => uploadPhoto(photo)}
/>
```

### Push Notifications

```typescript
import NotificationSettings from '@/components/NotificationSettings';

// Settings page
<NotificationSettings />

// Or programmatically
import { usePushNotifications } from '@/hooks/usePushNotifications';

const { subscribe, sendNotification } = usePushNotifications();

await subscribe();
sendNotification('Welcome!', {
  body: 'You are now subscribed to notifications',
});
```

## Testing

### Local Testing

1. **Start Development Server**:
```bash
npm run dev
```

2. **Test Service Worker**:
   - Open DevTools > Application > Service Workers
   - Verify service worker is registered
   - Test offline mode by checking "Offline"

3. **Test Install Prompt**:
   - Open DevTools > Application > Manifest
   - Click "Add to Home Screen"

4. **Test Notifications**:
   - Grant notification permission
   - Use NotificationSettings test button

### Browser Testing

**Chrome/Edge (Desktop)**:
- Install prompt appears in address bar
- Install via three-dot menu > Install

**Chrome (Android)**:
- Install prompt appears as banner
- Install via three-dot menu > Add to Home Screen

**Safari (iOS)**:
- Share button > Add to Home Screen
- Note: Some PWA features limited on iOS

### Automated Testing

Run test suite:

```bash
npm test -- --testPathPatterns="(usePWA|useBiometric|PWAInstallPrompt)"
```

## Deployment

### 1. Build Production Bundle

```bash
npm run build
```

### 2. Serve with HTTPS

PWA requires HTTPS (except localhost):

```bash
# Using Next.js
npm run start

# Or with nginx
server {
  listen 443 ssl;
  server_name your-domain.com;
  
  location / {
    proxy_pass http://localhost:3000;
  }
}
```

### 3. Verify Deployment

Use Lighthouse to audit PWA:

```bash
npm install -g lighthouse
lighthouse https://your-domain.com --view
```

Check for:
- ✅ Installable
- ✅ Works offline
- ✅ Service worker registered
- ✅ HTTPS
- ✅ Splash screen
- ✅ Theme color

### 4. Monitor

Track PWA metrics:
- Install rate
- Daily active users
- Offline usage
- Update adoption
- Notification engagement

## Troubleshooting

### Service Worker Not Updating

**Problem**: Old service worker cached
**Solution**:
```javascript
// In service worker
self.addEventListener('message', (event) => {
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
```

### Install Prompt Not Showing

**Checklist**:
- [ ] HTTPS enabled (or localhost)
- [ ] Valid manifest.json
- [ ] Service worker registered
- [ ] Icons present
- [ ] Not already installed
- [ ] Engagement heuristics met (Chrome)

### Offline Mode Not Working

**Debug**:
1. Check service worker status in DevTools
2. Verify caching strategy in Network tab
3. Test with different URLs
4. Check for console errors

### iOS Limitations

**Known Issues**:
- No install prompt (manual only)
- Limited notification support
- No background sync
- Stand-alone mode detection different

**Workaround**: Show iOS-specific instructions for manual install.

## Best Practices

### 1. Cache Management

- **Version cache names**: Update on deploy
- **Limit cache size**: Remove old caches
- **Selective caching**: Don't cache everything

### 2. Update Strategy

- **Notify users**: Don't force-update silently
- **Apply on reload**: Update on next load
- **Skipwaiting carefully**: May break running app

### 3. Offline UX

- **Clear indicators**: Show offline state
- **Queue actions**: Sync when online
- **Provide feedback**: Explain limitations

### 4. Performance

- **Lazy registration**: Register SW after page load
- **Precache essentials**: Only critical resources
- **Monitor metrics**: Track cache hit rate

## Security Considerations

### HTTPS Required

PWA features require HTTPS:
- Service workers
- Push notifications
- Geolocation
- Camera/microphone

### Content Security Policy

Add to headers:
```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  worker-src 'self';
```

### Permissions

Request permissions responsibly:
- Explain why needed
- Request when needed (not on load)
- Provide value first
- Respect denial

## Resources

- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [web.dev PWA](https://web.dev/progressive-web-apps/)
- [Workbox](https://developers.google.com/web/tools/workbox)
- [PWA Builder](https://www.pwabuilder.com/)

## Support

For issues or questions:
1. Check this documentation
2. Review DevTools console
3. Test in different browsers
4. Create GitHub issue with [PWA] prefix

---

Last Updated: 2025-10-23
Version: 1.6.0
