# ADR-004: Mobile Workforce Application Strategy

## Status
Proposed

## Context

The Service CRM integration requires a mobile application solution for field technicians to manage their daily assignments, update service status, and document work completion. Field technicians need reliable, offline-capable access to:

- Daily assignment schedules
- Customer information and service history
- Work documentation and photo capture
- Time tracking and status updates
- Navigation and route optimization
- Parts inventory and ordering

### Current Technology Landscape
- **Existing Frontend**: Next.js 15 with React and TypeScript
- **Mobile Expertise**: Team has React experience but limited mobile development
- **Deployment Requirements**: Multi-platform (iOS and Android) with app store distribution
- **Performance Needs**: Offline operation, low-bandwidth optimization, real-time sync

### Constraints
- **Development Timeline**: Need to deliver mobile app within 6 months
- **Team Resources**: Frontend team of 3 developers, no dedicated mobile developers
- **Budget Limitations**: Prefer leveraging existing skills over hiring specialized mobile teams
- **Maintenance Overhead**: Must be maintainable by existing development team

## Decision

We will implement a **Progressive Web App (PWA)** strategy with **React Native fallback** for app store distribution, providing a hybrid approach that balances development efficiency with user experience.

### Primary Solution: Progressive Web App (PWA)

```typescript
// PWA Architecture
Mobile Browser → PWA Shell → Service Worker → IndexedDB (Offline Storage)
                     ↓
              Background Sync ← → FastAPI Backend
                     ↓
              Push Notifications → Firebase/OneSignal
```

**Implementation Approach**:
1. **PWA-First Development**: Build mobile-optimized web application with offline capabilities
2. **App Store Wrapper**: Use tools like Capacitor or PWABuilder for app store distribution
3. **Native Feature Access**: Camera, GPS, push notifications through PWA APIs and polyfills
4. **Offline-First Architecture**: Service workers with background sync for reliable operation

### Fallback Solution: React Native (If Required)

```typescript
// React Native Architecture (If PWA limitations encountered)
React Native App → AsyncStorage → Background Jobs → REST API
        ↓
Native Modules → Camera, GPS, Push → Platform Services
```

## Technical Implementation Details

### PWA Architecture

#### Core Technologies
```json
{
  "framework": "Next.js 15 PWA",
  "ui_library": "React + Tailwind CSS",
  "offline_storage": "IndexedDB + Dexie.js", 
  "service_worker": "Workbox",
  "app_wrapper": "Capacitor 5",
  "push_notifications": "Firebase Cloud Messaging",
  "mapping": "Google Maps API",
  "camera": "WebRTC + Camera API"
}
```

#### Offline-First Data Strategy
```typescript
// Service Worker Background Sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'assignment-updates') {
    event.waitUntil(syncAssignmentUpdates());
  }
});

// IndexedDB Schema for Offline Storage
interface OfflineStore {
  assignments: Assignment[];
  customers: Customer[];
  services: Service[];
  sync_queue: SyncOperation[];
  photos: PhotoRecord[];
}

// Optimistic Updates with Conflict Resolution
class AssignmentManager {
  async updateAssignmentStatus(assignmentId: string, status: string) {
    // Update local state immediately
    await this.localDB.updateAssignment(assignmentId, { status });
    
    // Queue for background sync
    await this.syncQueue.add({
      operation: 'update_assignment',
      data: { assignmentId, status },
      timestamp: Date.now()
    });
  }
}
```

#### Mobile-Optimized UI Components
```typescript
// Touch-friendly interface components
const MobileAssignmentCard = ({ assignment }: { assignment: Assignment }) => (
  <div className="touch-target-48px bg-white rounded-lg shadow-md p-4 mb-4">
    <div className="flex justify-between items-center">
      <h3 className="text-lg font-semibold">{assignment.customer.name}</h3>
      <StatusBadge status={assignment.status} />
    </div>
    
    <div className="mt-2 grid grid-cols-2 gap-2">
      <TouchButton
        icon={<PhoneIcon />}
        label="Call Customer"
        onClick={() => window.open(`tel:${assignment.customer.phone}`)}
      />
      <TouchButton
        icon={<NavigationIcon />}
        label="Navigate"
        onClick={() => openNavigation(assignment.address)}
      />
    </div>
    
    <div className="mt-4 flex space-x-2">
      <ActionButton
        variant="primary"
        onClick={() => startAssignment(assignment.id)}
        disabled={assignment.status !== 'scheduled'}
      >
        Start Work
      </ActionButton>
      <ActionButton
        variant="secondary"
        onClick={() => viewDetails(assignment.id)}
      >
        Details
      </ActionButton>
    </div>
  </div>
);
```

### Native Feature Integration

#### Camera and Photo Capture
```typescript
// PWA Camera Implementation
class PhotoCapture {
  async capturePhoto(assignmentId: string): Promise<PhotoRecord> {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' } // Rear camera
    });
    
    const video = document.createElement('video');
    video.srcObject = stream;
    video.play();
    
    // Capture photo logic
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d')!;
    context.drawImage(video, 0, 0);
    
    const blob = await new Promise<Blob>(resolve => 
      canvas.toBlob(resolve!, 'image/jpeg', 0.8)
    );
    
    // Store locally and queue for sync
    const photoRecord = await this.storePhoto(assignmentId, blob);
    await this.queuePhotoSync(photoRecord);
    
    return photoRecord;
  }
}

// Capacitor Native Camera (Fallback)
import { Camera, CameraResultType } from '@capacitor/camera';

class NativePhotoCapture {
  async capturePhoto(): Promise<string> {
    const image = await Camera.getPhoto({
      quality: 80,
      allowEditing: false,
      resultType: CameraResultType.Base64
    });
    
    return image.base64String!;
  }
}
```

#### GPS and Location Services
```typescript
// Location tracking for technician positioning
class LocationService {
  async getCurrentLocation(): Promise<GeolocationCoordinates> {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (position) => resolve(position.coords),
        (error) => reject(error),
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });
  }
  
  async startLocationTracking(assignmentId: string) {
    const watchId = navigator.geolocation.watchPosition(
      (position) => this.updateTechnicianLocation(assignmentId, position.coords),
      (error) => console.error('Location tracking error:', error),
      { enableHighAccuracy: true, maximumAge: 30000 }
    );
    
    return watchId;
  }
}
```

#### Push Notifications
```typescript
// PWA Push Notification Setup
class NotificationService {
  async requestPermission(): Promise<boolean> {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }
  
  async subscribeToPush(): Promise<PushSubscription> {
    const registration = await navigator.serviceWorker.ready;
    return registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: this.vapidPublicKey
    });
  }
  
  // Handle incoming push notifications
  async handlePushMessage(event: PushEvent) {
    const data = event.data?.json();
    
    if (data.type === 'assignment_update') {
      await this.showNotification(
        'Assignment Update',
        `Your assignment for ${data.customer_name} has been updated`,
        { 
          icon: '/icons/assignment-icon.png',
          badge: '/icons/badge-icon.png',
          data: { assignmentId: data.assignment_id }
        }
      );
    }
  }
}
```

### Offline Data Synchronization

#### Sync Queue Management
```typescript
interface SyncOperation {
  id: string;
  operation: 'create' | 'update' | 'delete';
  entity: 'assignment' | 'note' | 'photo' | 'time_entry';
  data: any;
  timestamp: number;
  retries: number;
}

class SyncManager {
  private syncQueue: SyncOperation[] = [];
  
  async addToQueue(operation: SyncOperation) {
    this.syncQueue.push(operation);
    await this.persistSyncQueue();
    
    if (navigator.onLine) {
      this.processSyncQueue();
    }
  }
  
  async processSyncQueue() {
    for (const operation of this.syncQueue) {
      try {
        await this.executeSync(operation);
        this.removeSyncOperation(operation.id);
      } catch (error) {
        operation.retries++;
        if (operation.retries > 3) {
          this.moveTFailedQueue(operation);
        }
      }
    }
  }
  
  // Background sync via Service Worker
  async backgroundSync() {
    await this.registration.sync.register('background-sync');
  }
}
```

#### Conflict Resolution Strategy
```typescript
class ConflictResolver {
  async resolveAssignmentConflict(
    localAssignment: Assignment,
    serverAssignment: Assignment
  ): Promise<Assignment> {
    // Server wins for status changes from admin
    if (serverAssignment.updated_by_admin) {
      return serverAssignment;
    }
    
    // Technician wins for field updates
    if (localAssignment.field_updates) {
      return {
        ...serverAssignment,
        status: localAssignment.status,
        notes: localAssignment.notes,
        completion_time: localAssignment.completion_time
      };
    }
    
    // Merge non-conflicting changes
    return this.mergeAssignments(localAssignment, serverAssignment);
  }
}
```

## App Store Distribution Strategy

### PWA to Native App Conversion

```typescript
// Capacitor Configuration
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.tritiq.fieldservice',
  appName: 'TRITIQ Field Service',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    Camera: {
      permissions: ['camera', 'photos']
    },
    Geolocation: {
      permissions: ['location']
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert']
    }
  }
};
```

### Build and Deployment Pipeline

```yaml
# CI/CD Pipeline for Mobile App
name: Mobile App Build and Deploy

on:
  push:
    paths: 
      - 'mobile/**'
    branches: [main, develop]

jobs:
  build-pwa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Build PWA
        run: npm run build:mobile
      - name: Generate service worker
        run: npm run sw:generate
  
  build-ios:
    runs-on: macos-latest
    needs: build-pwa
    steps:
      - name: Setup Xcode
        uses: maxim-lobanov/setup-xcode@v1
      - name: Build iOS app
        run: |
          npx cap add ios
          npx cap sync ios
          npx cap build ios
  
  build-android:
    runs-on: ubuntu-latest
    needs: build-pwa
    steps:
      - name: Setup Android SDK
        uses: android-actions/setup-android@v2
      - name: Build Android app
        run: |
          npx cap add android
          npx cap sync android
          npx cap build android
```

## Performance Optimization

### Bundle Size Optimization
```typescript
// Code splitting for mobile-specific features
const MobileCamera = lazy(() => import('./components/MobileCamera'));
const OfflineSync = lazy(() => import('./services/OfflineSync'));

// Service worker caching strategy
workbox.routing.registerRoute(
  ({ request }) => request.destination === 'image',
  new workbox.strategies.CacheFirst({
    cacheName: 'assignment-photos',
    plugins: [{
      cacheKeyWillBeUsed: async ({ request }) => {
        return `${request.url}?version=${this.cacheVersion}`;
      }
    }]
  })
);
```

### Network Optimization
```typescript
// Bandwidth-aware data fetching
class NetworkOptimizer {
  async fetchAssignments(technicianId: string) {
    const connection = (navigator as any).connection;
    const isSlowConnection = connection?.effectiveType === '2g';
    
    const fields = isSlowConnection 
      ? 'id,customer_name,service_name,address,start_time,status'
      : 'id,customer,service,address,start_time,end_time,status,notes,photos';
    
    return this.api.get(`/mobile/technician/${technicianId}/assignments`, {
      params: { fields, compress: isSlowConnection }
    });
  }
}
```

## Security Considerations

### Mobile-Specific Security
```typescript
// Secure token storage
class SecureStorage {
  async storeAuthToken(token: string) {
    if (this.isCapacitorApp()) {
      // Use Capacitor secure storage
      await Preferences.set({
        key: 'auth_token',
        value: token
      });
    } else {
      // Use browser secure storage with encryption
      const encrypted = await this.encrypt(token);
      localStorage.setItem('encrypted_token', encrypted);
    }
  }
  
  async getAuthToken(): Promise<string | null> {
    if (this.isCapacitorApp()) {
      const result = await Preferences.get({ key: 'auth_token' });
      return result.value;
    } else {
      const encrypted = localStorage.getItem('encrypted_token');
      return encrypted ? await this.decrypt(encrypted) : null;
    }
  }
}

// Certificate pinning for API calls
class SecureApiClient {
  constructor() {
    if (this.isCapacitorApp()) {
      // Configure certificate pinning for native app
      this.setupCertificatePinning();
    }
  }
}
```

## Testing Strategy

### Mobile Testing Approach
```typescript
// PWA Testing with Puppeteer
describe('Mobile PWA Tests', () => {
  beforeEach(async () => {
    await page.emulate(devices['iPhone 12']);
    await page.goto('http://localhost:3000/technician');
  });
  
  test('should capture photo and store offline', async () => {
    // Mock camera permissions
    await page.evaluate(() => {
      Object.defineProperty(navigator, 'mediaDevices', {
        value: { getUserMedia: jest.fn().mockResolvedValue(mockStream) }
      });
    });
    
    await page.click('[data-testid="capture-photo-button"]');
    await page.waitForSelector('[data-testid="photo-preview"]');
    
    // Verify photo stored in IndexedDB
    const photos = await page.evaluate(() => {
      return window.indexedDB.open('photos').result;
    });
    
    expect(photos).toHaveLength(1);
  });
});

// Device Testing Matrix
const testDevices = [
  { name: 'iPhone 12', viewport: { width: 390, height: 844 } },
  { name: 'Samsung Galaxy S21', viewport: { width: 384, height: 854 } },
  { name: 'iPad', viewport: { width: 768, height: 1024 } }
];
```

### Performance Testing
```typescript
// Lighthouse CI for PWA performance
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000/technician'],
      settings: {
        chromeFlags: '--no-sandbox --disable-storage-reset'
      }
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:pwa': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }]
      }
    }
  }
};
```

## Implementation Timeline

### Phase 1: PWA Foundation (4 weeks)
- [ ] Next.js PWA setup with offline capabilities
- [ ] Basic technician dashboard and assignment list
- [ ] Service worker implementation for caching
- [ ] IndexedDB storage for offline data

### Phase 2: Core Features (6 weeks)
- [ ] Assignment status management
- [ ] Photo capture and documentation
- [ ] Location services integration
- [ ] Push notification system

### Phase 3: App Store Distribution (4 weeks)
- [ ] Capacitor integration and native builds
- [ ] iOS App Store submission and approval
- [ ] Google Play Store submission and approval
- [ ] App store metadata and screenshots

### Phase 4: Advanced Features (4 weeks)
- [ ] Offline sync optimization
- [ ] Route optimization and navigation
- [ ] Advanced reporting and analytics
- [ ] Performance optimization and testing

## Consequences

### Positive
- **Development Speed**: Leverages existing React skills and codebase
- **Code Reuse**: Shares components and logic with web application
- **Maintenance**: Single codebase for web and mobile interfaces
- **Feature Parity**: Easier to maintain consistency across platforms
- **Offline Capability**: Robust offline-first architecture
- **Cost Effective**: No need for specialized mobile development team

### Negative
- **Performance**: May not match fully native app performance
- **App Store Limitations**: PWA features limited in some app store contexts
- **Native Integration**: Some advanced native features may be harder to access
- **Battery Usage**: Web-based apps may consume more battery than native
- **Platform Differences**: Need to handle iOS/Android differences in PWA wrapper

### Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PWA performance issues | Medium | High | Performance monitoring, optimization, React Native fallback |
| App store rejection | Low | High | Thorough testing, compliance review, appeal process |
| Offline sync conflicts | Medium | Medium | Robust conflict resolution, user feedback mechanisms |
| Battery drain complaints | Medium | Low | Performance optimization, background task limits |

## Success Metrics

### Technical Metrics
- **App Performance**: Lighthouse PWA score > 90
- **Offline Capability**: 100% functionality when offline
- **Sync Reliability**: 99.5% successful background sync rate
- **App Store Rating**: > 4.5 stars average rating

### Business Metrics
- **Technician Adoption**: 95% of technicians using mobile app daily
- **Assignment Completion**: 15% faster assignment completion
- **Customer Satisfaction**: Improved through better technician communication
- **Operational Efficiency**: 20% reduction in administrative overhead

## Alternatives Considered

### 1. React Native from Start
- **Pros**: Better performance, full native feature access
- **Cons**: Longer development time, requires specialized skills
- **Decision**: Too complex for current team and timeline

### 2. Native iOS/Android Development
- **Pros**: Best performance and platform integration
- **Cons**: Duplicate development effort, specialized teams needed
- **Decision**: Resource intensive and unnecessary for MVP

### 3. Hybrid Framework (Ionic, Cordova)
- **Pros**: Cross-platform development, web technologies
- **Cons**: Performance limitations, deprecated technologies
- **Decision**: PWA provides better modern alternative

### 4. Web-Only Mobile Site
- **Pros**: Simplest development, no app store needed
- **Cons**: Limited offline capability, poor user experience
- **Decision**: Insufficient for field technician requirements

## Review and Updates

This ADR should be reviewed:
- After PWA MVP completion (3 months)
- If performance issues arise during testing
- After app store approval process
- When considering React Native migration

## Related ADRs
- ADR-001: Multi-Tenant Service CRM Architecture
- ADR-003: API Design Patterns for Service Endpoints
- ADR-006: Authentication and Authorization for Service Module
- ADR-007: Notification and Communication System