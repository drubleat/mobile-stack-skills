---
title: Push notification handlers: foreground / background / killed
impact: HIGH
impactDescription: "Behavior differs across three app states and between Expo Push and FCM; missing a handler silently drops notifications"
tags: push, handlers, foreground, background, fcm, expo
---

# Push notification handlers: foreground / background / killed

The hardest part of push setup isn't delivery — it's handling the message correctly across all three app states. The behavior differs by state and by whether you're using Expo Push or FCM.

## The three app states

| State | App is... | Handler fires |
|---|---|---|
| **Foreground** | Open and active | Immediate, on the JS thread |
| **Background** | In memory but not focused | Background handler (limited JS context) |
| **Killed** | Not running | Notification opens the app; check `getInitialNotification` |

## FCM handlers (@react-native-firebase/messaging)

### Foreground

```ts
useEffect(() => {
  const unsubscribe = messaging().onMessage(async remoteMessage => {
    // App is open — FCM does NOT auto-show a notification banner
    // You must display it yourself (or use a local notification)
    console.log('Foreground message:', remoteMessage);
    // Show a local notification or update in-app UI
  });
  return unsubscribe;
}, []);
```

**FCM suppresses the system banner in foreground.** You must show it yourself with `@notifee/react-native` or `expo-notifications` local notification API if you want a visible alert.

### Background (app suspended, not killed)

```ts
// Outside any component — top level of index.js or App.tsx
messaging().setBackgroundMessageHandler(async remoteMessage => {
  // Limited context: no React, no hooks, no navigation
  // Safe to do: AsyncStorage reads, fetch calls, simple logging
  console.log('Background message:', remoteMessage.data);
});
```

The background handler runs in a headless JS context. No UI updates here.

### Killed → initial notification

```ts
useEffect(() => {
  messaging()
    .getInitialNotification()
    .then(remoteMessage => {
      if (remoteMessage) {
        // App was opened by tapping a notification from killed state
        handleNotificationNavigation(remoteMessage.data);
      }
    });

  // Also handle when app is backgrounded (not killed) and user taps
  const unsubscribe = messaging().onNotificationOpenedApp(remoteMessage => {
    handleNotificationNavigation(remoteMessage.data);
  });
  return unsubscribe;
}, []);
```

## Expo notifications handlers

```ts
// Foreground received
Notifications.addNotificationReceivedListener(notification => {
  console.log('Foreground notification:', notification);
  // Expo DOES show the banner if setNotificationHandler returns shouldShowAlert: true
});

// User tapped notification (any state)
Notifications.addNotificationResponseReceivedListener(response => {
  const data = response.notification.request.content.data;
  handleNotificationNavigation(data);
});

// Killed state — check on launch
Notifications.getLastNotificationResponseAsync().then(response => {
  if (response) handleNotificationNavigation(response.notification.request.content.data);
});
```

## Notification data payload

Use `data` (not `notification`) for reliable cross-state delivery. A **notification** payload (title/body) is handled by the OS and may not wake your background handler. A **data-only message** always goes to your background handler.

```json
// Server payload for FCM (data-only for reliable background)
{
  "to": "<fcm_token>",
  "data": {
    "title": "New message",
    "body": "You have a new message",
    "screen": "chat",
    "roomId": "123"
  }
}
```

Parse `data.title`/`data.body` in your background handler and show a local notification manually.

## Android notification channels

Required on Android 8+ for foreground and local notifications:

```ts
// With @notifee/react-native (recommended for FCM)
await notifee.createChannel({
  id: 'default',
  name: 'Default Channel',
  importance: AndroidImportance.HIGH,
  sound: 'default',
});
```

Or set `channelId` in your FCM server payload.

## Common pitfalls

- **No foreground banner (FCM)** → FCM doesn't auto-show banners when the app is open. Show a local notification from the `onMessage` handler.
- **Background handler crashes** → accessing React context or navigation in the background handler; it's headless JS only.
- **`getInitialNotification` always null** → called too early (before Firebase initializes) or the notification was a data-only message with no `notification` object.
- **Android silent notifications on battery saver** → doze mode kills background processing; use FCM high-priority messages and data-only payloads.
