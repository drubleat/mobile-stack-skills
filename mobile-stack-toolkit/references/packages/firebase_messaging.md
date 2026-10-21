---
title: "firebase_messaging 16.3.0 — FCM push notifications"
impact: HIGH
impactDescription: "Background handler must be top-level function; iOS foreground notifications need explicit display options"
tags: flutter, firebase, fcm, push, ios, android
---

# firebase_messaging — FCM push notifications

**Historical example baseline:** 16.3.0   — resolve a compatible installed version before using these snippets.
**Platforms:** Android, iOS, macOS, Web

```yaml
dependencies:
  firebase_core: ^4.10.0
  firebase_messaging: ^16.3.0
```

> Configure Firebase using [setup](../firebase/setup-cli.md) and [APNs](../push/apns-ios.md).

## Setup: background handler (top-level, before runApp)

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

// MUST be top-level (not inside a class), MUST have this annotation
@pragma('vm:entry-point')
Future<void> _backgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  print('Background message: ${message.messageId}');
  // Handle data-only messages here
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  FirebaseMessaging.onBackgroundMessage(_backgroundHandler);  // Register before runApp
  runApp(const MyApp());
}
```

## Request permission + get token

```dart
final messaging = FirebaseMessaging.instance;

// Request permission (required on iOS; Android 13+ also needs this)
final settings = await messaging.requestPermission(
  alert: true,
  announcement: false,
  badge: true,
  carPlay: false,
  criticalAlert: false,
  provisional: false,
  sound: true,
);

if (settings.authorizationStatus == AuthorizationStatus.authorized) {
  // Get FCM token
  final token = await messaging.getToken();
  // Store the token for this installation; avoid logging it.
  // Store token in your backend (Supabase, Firestore, etc.)
}

// Listen for token refresh
messaging.onTokenRefresh.listen((newToken) {
  // Update stored token in backend
});
```

## Message handlers

```dart
// FOREGROUND: app is open and in focus
// FCM does NOT show a notification UI automatically — handle manually
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  print('Foreground message: ${message.notification?.title}');
  // Show with flutter_local_notifications or a custom SnackBar
});

// BACKGROUND → TAP: user tapped notification while app was in background
FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
  _handleNavigationFromMessage(message);
});

// KILLED STATE: app was launched from a notification tap
final RemoteMessage? initialMessage = await messaging.getInitialMessage();
if (initialMessage != null) {
  _handleNavigationFromMessage(initialMessage);
}

void _handleNavigationFromMessage(RemoteMessage message) {
  final route = message.data['route'];
  // Validate/map route, queue until auth/router readiness, then deduplicate and navigate.
}
```

## RemoteMessage structure

```dart
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  // Notification payload (shown automatically in background/killed on Android)
  message.notification?.title;
  message.notification?.body;
  message.notification?.android?.imageUrl;
  message.notification?.apple?.imageUrl;

  // Data payload (always available, for custom handling)
  message.data;           // Map<String, dynamic>
  message.data['route'];  // custom deep-link
  message.data['type'];   // custom action type

  // Message ID
  message.messageId;
  message.sentTime;
});
```

## Topics

```dart
// Subscribe — all devices subscribed to 'news' receive broadcasts
await messaging.subscribeToTopic('news');

// Unsubscribe
await messaging.unsubscribeFromTopic('news');
```

Send to a topic from your backend:
```json
{ "message": { "topic": "news", "notification": { "title": "Breaking" } } }
```

## APNs token (iOS)

```dart
// iOS only — Firebase internally maps APNs → FCM tokens
// Wait for a non-null APNs token before dependent FCM API calls on Apple platforms
final apnsToken = await messaging.getAPNSToken();
```

## Notification presentation options (iOS foreground)

```dart
// Control whether FCM shows alert/sound/badge in iOS foreground
await messaging.setForegroundNotificationPresentationOptions(
  alert: true,     // Show alert banner
  badge: true,     // Update badge count
  sound: true,     // Play sound
);
```

This is the iOS-only way to show notifications in foreground without `flutter_local_notifications`.

## Android notification channel

Create the channel before FCM delivers messages to it:

```dart
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

const channel = AndroidNotificationChannel(
  'high_importance',
  'High Importance Notifications',
  importance: Importance.high,
);

await FlutterLocalNotificationsPlugin()
    .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
    ?.createNotificationChannel(channel);
```

Specify `message.android.notification.channel_id: 'high_importance'` when sending from your backend.

## Gotchas

- `@pragma('vm:entry-point')` on the background handler is **required** — without it, the Dart compiler may tree-shake the function, causing background messages to silently fail.
- iOS foreground messages: `setForegroundNotificationPresentationOptions` shows the system notification; alternatively use `flutter_local_notifications`. One or the other — not both.
- `getInitialMessage()` should be called after the widget tree is ready (inside a `StatefulWidget.initState` or after a `WidgetsBinding.instance.addPostFrameCallback`), not at the very start of main.
- Android 13+ requires `POST_NOTIFICATIONS` runtime permission — `requestPermission()` handles this on Firebase 16.x.
- iOS: test push notifications on a **real device** — simulator support varies by host/runtime; physical-device release testing remains necessary.

Retain and cancel listeners, detach tokens on logout, and store one token per installation/environment. Topic subscriptions are not a private per-user authorization boundary.
