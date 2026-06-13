---
title: FCM: React Native setup & message handling
impact: HIGH
impactDescription: "Covers FCM-specific patterns; cross-references push/ domain for token storage and APNs setup"
tags: firebase, fcm, push, react-native
---

# FCM: React Native setup & message handling

This file covers FCM-specific patterns for React Native. For the full push notification flow (token storage, Expo Push comparison, APNs) see [../push/fcm-setup.md](../push/fcm-setup.md) and [../push/handlers-state.md](../push/handlers-state.md).

## Install and configure

```bash
npx expo install @react-native-firebase/messaging expo-build-properties
```

`app.config.ts` must include:

```ts
plugins: [
  ['expo-build-properties', { ios: { useFrameworks: 'static' } }],
  '@react-native-firebase/app',
  '@react-native-firebase/messaging',
]
```

**`useFrameworks: 'static'` is mandatory on iOS.** Without it, the iOS build links Firebase as a dynamic framework and conflicts with React Native's static linking — pod install succeeds but the archive step fails.

## Permission & token

```ts
import messaging from '@react-native-firebase/messaging';

async function requestPermissionAndGetToken() {
  const status = await messaging().requestPermission();
  const granted =
    status === messaging.AuthorizationStatus.AUTHORIZED ||
    status === messaging.AuthorizationStatus.PROVISIONAL;

  if (!granted) return null;

  const token = await messaging().getToken();
  return token;
}
```

## Message handling — three states

```ts
// FOREGROUND: app is open and visible
messaging().onMessage(async (remoteMessage) => {
  // FCM does NOT show a notification automatically in the foreground.
  // Display using expo-notifications or a custom UI:
  await Notifications.scheduleNotificationAsync({
    content: {
      title: remoteMessage.notification?.title,
      body: remoteMessage.notification?.body,
      data: remoteMessage.data,
    },
    trigger: null,
  });
});

// BACKGROUND: app is in background (registered outside React — in index.js or _layout.tsx at root level)
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  // FCM auto-shows notification when data.notification is present.
  // Handle data-only messages here.
  console.log('Background message:', remoteMessage.data);
});

// KILLED: app was not running
async function checkInitialNotification() {
  const remoteMessage = await messaging().getInitialNotification();
  if (remoteMessage) {
    // Navigate to the right screen based on remoteMessage.data
    handleDeepLink(remoteMessage.data);
  }
}
```

Register `setBackgroundMessageHandler` before React renders — in `index.js` or at the very top of `app/_layout.tsx`:

```ts
// app/_layout.tsx (before component definition)
import messaging from '@react-native-firebase/messaging';
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  // background handler
});
```

## Token refresh

```ts
messaging().onTokenRefresh((newToken) => {
  // Update stored token in your backend
  saveTokenToBackend(newToken);
});
```

## Data-only vs notification messages

| Message type | Foreground | Background | Killed |
|---|---|---|---|
| `notification` payload | NOT auto-shown | Auto-shown by system | Auto-shown by system |
| `data` only | `onMessage` fires | `setBackgroundMessageHandler` fires | `getInitialNotification` has data |

For app-controlled display (custom notification UI, navigation on tap), use **data-only messages** and handle display manually in all three states.

## Android notification channel

For Android 8+, notifications must be assigned to a channel. FCM's default channel is used if you don't specify one — but you lose control over sound/vibration settings. Create a custom channel:

```ts
import * as Notifications from 'expo-notifications';

await Notifications.setNotificationChannelAsync('default', {
  name: 'Default',
  importance: Notifications.AndroidImportance.MAX,
  vibrationPattern: [0, 250, 250, 250],
  sound: 'default',
});
```

Then send messages with `android.channelId: 'default'` from your backend.

## Flutter (firebase_messaging)

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

// Top-level function (required for background — must not be in a class)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('Background message: ${message.messageId}');
}

// In main():
FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

// In your widget:
final messaging = FirebaseMessaging.instance;

// Permission
await messaging.requestPermission(alert: true, badge: true, sound: true);

// Token
final token = await messaging.getToken();

// Foreground
FirebaseMessaging.onMessage.listen((message) {
  // Show local notification
});

// Background tapped
FirebaseMessaging.onMessageOpenedApp.listen((message) {
  // Navigate based on message.data
});

// Killed state
final initial = await messaging.getInitialMessage();
```

## Gotchas

- **iOS foreground messages are silent** — FCM does not display them. You must call `expo-notifications` or another display library.
- **`setBackgroundMessageHandler` must be registered before React mounts** — if it's registered inside a component, it may not be active when the background event fires.
- **APNs token is separate from FCM token** — Firebase internally maps APNs tokens to FCM tokens. You don't need to manage APNs tokens directly; just use the FCM token.
