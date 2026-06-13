---
title: Deep linking: notification tap → correct screen
impact: MEDIUM-HIGH
impactDescription: "Notification data payload must match expo-router path format; cold-start navigation requires useLastNotificationResponse"
tags: push, deep-linking, expo-router, navigation
---

# Deep linking: notification tap → correct screen

The goal: user taps a push notification → app opens (or foregrounds) → navigates to the specific screen indicated in the notification's `data` payload.

## The data payload convention

Put navigation intent in `data`, not in `notification.body`:

```json
{
  "to": "<token>",
  "title": "New message from Ali",
  "body": "Hey, are you free tonight?",
  "data": {
    "screen": "chat",
    "params": "{\"roomId\":\"abc123\",\"recipientId\":\"user456\"}"
  }
}
```

Keep `data` values as strings (FCM requirement). Parse `params` with `JSON.parse` in the handler.

## With expo-router + FCM

```ts
// app/_layout.tsx or a top-level useEffect
import { useRouter } from 'expo-router';
import messaging from '@react-native-firebase/messaging';

export function useNotificationNavigation() {
  const router = useRouter();

  function handleNotificationData(data?: Record<string, string>) {
    if (!data?.screen) return;
    const params = data.params ? JSON.parse(data.params) : {};
    switch (data.screen) {
      case 'chat':     return router.push({ pathname: '/chat/[roomId]', params });
      case 'profile':  return router.push({ pathname: '/profile/[userId]', params });
      case 'offer':    return router.push('/paywall');
      default:         return router.push('/');
    }
  }

  useEffect(() => {
    // Killed state: app opened by notification
    messaging().getInitialNotification().then(msg => {
      if (msg) handleNotificationData(msg.data);
    });

    // Background state: app foregrounded by notification tap
    const unsubscribe = messaging().onNotificationOpenedApp(msg => {
      handleNotificationData(msg.data);
    });
    return unsubscribe;
  }, []);
}
```

Call `useNotificationNavigation()` from the root layout after the router is ready.

## With expo-router + Expo Notifications

```ts
import * as Notifications from 'expo-notifications';
import { useRouter } from 'expo-router';

export function useExpoNotificationNavigation() {
  const router = useRouter();

  useEffect(() => {
    // User tapped a notification (foreground or background)
    const sub = Notifications.addNotificationResponseReceivedListener(response => {
      const data = response.notification.request.content.data;
      handleNotificationData(data, router);
    });

    // Killed state
    Notifications.getLastNotificationResponseAsync().then(response => {
      if (response) handleNotificationData(response.notification.request.content.data, router);
    });

    return () => sub.remove();
  }, []);
}
```

## Timing: wait for navigation to be ready

A common race condition: the deep link handler fires before expo-router's navigation tree is mounted. Solution:

```ts
// Use a ref to queue the pending route
const pendingRoute = useRef<string | null>(null);
const [isReady, setIsReady] = useState(false);

useEffect(() => {
  if (isReady && pendingRoute.current) {
    router.push(pendingRoute.current);
    pendingRoute.current = null;
  }
}, [isReady]);
```

Or leverage expo-router's `Slot` mounting with a small delay — `router.push` works only after the root `Slot` is rendered.

## URL-based deep linking (alternative)

Expo supports URL scheme deep links (`myapp://chat/abc123`) which also work for web-to-app links. Set up in `app.config.ts`:

```ts
scheme: 'myapp',
// for universal links (iOS) / app links (Android), configure in app.config too
```

Then push a URL in the notification data and use `Linking.openURL` or let expo-router handle it via the `expo-linking` package. URL-based linking is better for marketing links and email campaigns; data-payload routing is better for in-app notifications.

## Common pitfalls

- **Navigation fires before router is mounted** → app crashes or navigates to wrong screen; add an `isReady` gate.
- **`data` values not strings** → FCM silently drops non-string `data` values; stringify complex params.
- **Foreground tap not handled** → `onMessage` fires for foreground; you need `onNotificationOpenedApp` for background taps (different listeners).
- **Deep link goes to tab root instead of nested screen** → ensure the full pathname is correct for expo-router's file structure.
