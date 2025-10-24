import { useState, useEffect } from 'react';

interface PushNotificationState {
  isSupported: boolean;
  permission: NotificationPermission;
  subscription: PushSubscription | null;
  requestPermission: () => Promise<boolean>;
  subscribe: () => Promise<PushSubscription | null>;
  unsubscribe: () => Promise<void>;
  sendNotification: (title: string, options?: NotificationOptions) => void;
}

export function usePushNotifications(): PushNotificationState {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [subscription, setSubscription] = useState<PushSubscription | null>(null);

  const isSupported = 'Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window;

  useEffect(() => {
    if (isSupported) {
      setPermission(Notification.permission);
      checkSubscription();
    }
  }, [isSupported]);

  const checkSubscription = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const existingSubscription = await registration.pushManager.getSubscription();
      setSubscription(existingSubscription);
    } catch (error) {
      console.error('Error checking subscription:', error);
    }
  };

  const requestPermission = async (): Promise<boolean> => {
    if (!isSupported) {
      return false;
    }

    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result === 'granted';
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      return false;
    }
  };

  const subscribe = async (): Promise<PushSubscription | null> => {
    if (!isSupported) {
      console.error('Push notifications are not supported');
      return null;
    }

    if (permission !== 'granted') {
      const granted = await requestPermission();
      if (!granted) {
        return null;
      }
    }

    try {
      const registration = await navigator.serviceWorker.ready;

      // In production, use your VAPID public key
      const vapidPublicKey = 'YOUR_VAPID_PUBLIC_KEY_HERE';
      const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);

      const pushSubscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedVapidKey,
      });

      setSubscription(pushSubscription);

      // Send subscription to your backend
      await sendSubscriptionToBackend(pushSubscription);

      return pushSubscription;
    } catch (error) {
      console.error('Error subscribing to push notifications:', error);
      return null;
    }
  };

  const unsubscribe = async () => {
    if (!subscription) {
      return;
    }

    try {
      await subscription.unsubscribe();
      setSubscription(null);

      // Notify backend about unsubscription
      await removeSubscriptionFromBackend(subscription);
    } catch (error) {
      console.error('Error unsubscribing from push notifications:', error);
    }
  };

  const sendNotification = (title: string, options?: NotificationOptions) => {
    if (!isSupported || permission !== 'granted') {
      console.warn('Notifications are not enabled');
      return;
    }

    const defaultOptions: NotificationOptions = {
      icon: '/icons/icon-192x192.png',
      badge: '/icons/icon-72x72.png',
      vibrate: [200, 100, 200],
      ...options,
    };

    new Notification(title, defaultOptions);
  };

  return {
    isSupported,
    permission,
    subscription,
    requestPermission,
    subscribe,
    unsubscribe,
    sendNotification,
  };
}

// Helper function to convert VAPID key
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Helper function to send subscription to backend
async function sendSubscriptionToBackend(subscription: PushSubscription): Promise<void> {
  try {
    // In production, send to your backend API
    await fetch('/api/push-subscription', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(subscription),
    });
  } catch (error) {
    console.error('Error sending subscription to backend:', error);
  }
}

// Helper function to remove subscription from backend
async function removeSubscriptionFromBackend(subscription: PushSubscription): Promise<void> {
  try {
    // In production, send to your backend API
    await fetch('/api/push-subscription', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(subscription),
    });
  } catch (error) {
    console.error('Error removing subscription from backend:', error);
  }
}
