// Service Worker for TRITIQ BOS PWA
const CACHE_NAME = 'tritiq-erp-v1.6.3'; // Bump version to bust old caches
const RUNTIME_CACHE = 'tritiq-runtime-v1.6.3';

// Assets to cache on install (static only, no API)
const PRECACHE_ASSETS = [
  '/',
  '/mobile/dashboard',
  '/mobile/login',
  '/offline.html',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
];

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Precaching assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              // Delete any old caches starting with 'tritiq-'
              if (cacheName.startsWith('tritiq-') && cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
                console.log('[Service Worker] Deleting old cache:', cacheName);
                return true;
              }
              return false;
            })
            .map((cacheName) => caches.delete(cacheName))
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  console.log('[Service Worker] Fetch intercepted for:', url.href);

  // Skip cross-origin requests unless it's our API domain
  if (url.origin !== location.origin && !url.hostname.includes('fastapiv16-production.up.railway.app')) {
    console.log('[Service Worker] Skipping non-origin request:', url.href);
    return;
  }

  // For API requests (/api/), always use network-only - no caching, no offline fallback
  if (url.pathname.startsWith('/api/')) {
    console.log('[Service Worker] Network-only for API request:', url.href);
    event.respondWith(
      fetch(request).catch((error) => {
        console.error('[Service Worker] Network request failed for API:', error);
        // Custom offline response for API
        return new Response(JSON.stringify({ error: 'Offline - API unavailable' }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
    return;
  }

  // Handle navigation requests (HTML pages)
  if (request.mode === 'navigate') {
    console.log('[Service Worker] Navigation request:', url.href);
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Handle static assets (cache-first)
  console.log('[Service Worker] Static asset request:', url.href);
  event.respondWith(cacheFirstStrategy(request));
});

// Network-first strategy for dynamic content (e.g., navigation)
async function networkFirstStrategy(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (error) {
    console.error('[Service Worker] Network request failed:', error);
    
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);
    if (cached) {
      return cached;
    }

    // Fallback to offline page for navigation
    if (request.mode === 'navigate') {
      return await cache.match('/offline.html');
    }
    
    throw error;
  }
}

// Cache-first strategy for static assets
async function cacheFirstStrategy(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    if (response.status === 200 && response.type === 'basic') {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('[Service Worker] Fetch failed:', error);
    
    // Fallback for navigation if applicable
    if (request.mode === 'navigate') {
      return await cache.match('/offline.html');
    }
    
    throw error;
  }
}

// Remove background sync and IndexedDB - not needed for API, simplifies SW
// If offline actions are required in future, re-add with HTTPS enforcement

// Push notification handler (keep if needed)
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View',
        icon: '/icons/icon-96x96.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/icon-96x96.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('TRITIQ BOS', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked');
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});