---
title: Push notifications: firebase_messaging + flutter_local_notifications
impact: HIGH
impactDescription: "Background isolate handler must be a top-level function; iOS requires explicit permission request"
tags: flutter, push, firebase-messaging, fcm, ios, android
---

# Push notifications: firebase_messaging + flutter_local_notifications

Versions: `firebase_messaging: ^16.3.0`, `flutter_local_notifications` (latest stable)

## Setup

```yaml
dependencies:
  firebase_messaging: ^16.3.0
  flutter_local_notifications: ^18.0.0
```

Ensure `firebase_core` is initialized before using any Firebase service. The `AndroidManifest.xml` and `Info.plist` configs are handled by `flutterfire configure`.

## Permission + token

```dart
final messaging = FirebaseMessaging.instance;

// Request permission (iOS shows system prompt; Android 13+ requires this for notifications)
final settings = await messaging.requestPermission(
  alert: true,
  badge: true,
  sound: true,
);

if (settings.authorizationStatus == AuthorizationStatus.authorized) {
  final token = await messaging.getToken();
  // Store token in Supabase/backend
  await supabase.from('device_tokens').upsert({
    'user_id': supabase.auth.currentUser!.id,
    'token': token,
    'platform': Platform.isIOS ? 'ios' : 'android',
  }, onConflict: 'token');
}

// Handle token refresh
messaging.onTokenRefresh.listen((newToken) async {
  await supabase.from('device_tokens').update({
    'token': newToken,
    'updated_at': DateTime.now().toIso8601String(),
  }).eq('user_id', supabase.auth.currentUser!.id);
});
```

## Background handler (top-level function)

```dart
// Must be a top-level function, not inside a class
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  // Handle data-only messages
  print('Background message: ${message.data}');
}

// In main(), before runApp:
FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
```

## Foreground messages with flutter_local_notifications

FCM does NOT show notifications automatically when the app is in the foreground. Use `flutter_local_notifications`:

```dart
// Initialize local notifications
final flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();

const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
const iosInit = DarwinInitializationSettings();
const initSettings = InitializationSettings(android: androidInit, iOS: iosInit);

await flutterLocalNotificationsPlugin.initialize(
  initSettings,
  onDidReceiveNotificationResponse: (details) {
    // Handle notification tap
    handleDeepLink(details.payload);
  },
);

// Create Android notification channel
const channel = AndroidNotificationChannel(
  'high_importance_channel',
  'High Importance Notifications',
  importance: Importance.high,
);
await flutterLocalNotificationsPlugin
    .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
    ?.createNotificationChannel(channel);

// Listen for foreground messages
FirebaseMessaging.onMessage.listen((message) {
  final notification = message.notification;
  if (notification == null) return;

  flutterLocalNotificationsPlugin.show(
    notification.hashCode,
    notification.title,
    notification.body,
    NotificationDetails(
      android: AndroidNotificationDetails(
        channel.id,
        channel.name,
        channelDescription: channel.description,
        icon: '@mipmap/ic_launcher',
      ),
      iOS: const DarwinNotificationDetails(),
    ),
    payload: message.data['route'],  // for deep linking
  );
});
```

## Handle notification taps (all states)

```dart
// Background → tapped
FirebaseMessaging.onMessageOpenedApp.listen((message) {
  handleDeepLink(message.data);
});

// Killed state → app opened from notification
final initialMessage = await FirebaseMessaging.instance.getInitialMessage();
if (initialMessage != null) {
  handleDeepLink(initialMessage.data);
}

void handleDeepLink(Map<String, dynamic> data) {
  final route = data['route'] as String?;
  if (route != null) {
    context.go(route);  // go_router navigation
  }
}
```

## iOS: APNs configuration

Firebase handles APNs internally. Upload your APNs Auth Key (.p8) in Firebase Console → Project settings → Cloud Messaging → iOS app config. One .p8 key covers all apps in your Apple Developer team and never expires — prefer it over certificates.

## Android: POST_NOTIFICATIONS permission (API 33+)

```dart
import 'package:permission_handler/permission_handler.dart';

if (Platform.isAndroid) {
  final status = await Permission.notification.request();
  if (status.isDenied) {
    // Notifications blocked — show rationale
  }
}
```

## Riverpod integration

```dart
@riverpod
Stream<String> fcmToken(Ref ref) {
  return FirebaseMessaging.instance.onTokenRefresh;
}

@riverpod
Future<String?> initialFcmToken(Ref ref) async {
  return FirebaseMessaging.instance.getToken();
}
```

## Gotchas

- **Background handler must be top-level** and annotated `@pragma('vm:entry-point')`. If placed inside a class, it won't work.
- **Foreground notifications are silent by default** — always use `flutter_local_notifications` for foreground display.
- **iOS requires real device** for push notification testing. Simulator doesn't support APNs.
- **Android channel required for API 26+** — create it before showing notifications.
