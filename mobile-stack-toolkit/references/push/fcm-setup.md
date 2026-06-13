---
title: FCM setup: @react-native-firebase/messaging
impact: HIGH
impactDescription: "useFrameworks: 'static' is REQUIRED on iOS for @react-native-firebase — without it the iOS build fails at link time"
tags: push, fcm, firebase, ios, android, react-native
---

# FCM setup: @react-native-firebase/messaging

## Install

```bash
npx expo install @react-native-firebase/app @react-native-firebase/messaging
```

Both require native code → **Dev Build required**. Expo Go will not work after this install.

## Add to app.config.ts

```ts
plugins: [
  '@react-native-firebase/app',
  '@react-native-firebase/messaging',
  // Required for iOS: Firebase uses static frameworks
  ['expo-build-properties', {
    ios: { useFrameworks: 'static' },
  }],
]
```

`useFrameworks: 'static'` is mandatory for RN Firebase on iOS. Forgetting it causes a pod install crash that looks unrelated to Firebase.

## Android: google-services.json

1. Firebase Console → Project Settings → Your Android app → Download `google-services.json`.
2. Place at: `android/app/google-services.json` (after prebuild) — or configure via config plugin so it's auto-placed during `eas build`.

If using EAS Build (managed, no committed native folders): set the file content as an EAS secret or use the `expo-google-services` plugin pattern to inject it at build time without committing the file.

## iOS: GoogleService-Info.plist

1. Firebase Console → Project Settings → Your iOS app → Download `GoogleService-Info.plist`.
2. For managed EAS builds: same pattern — either commit the file (it's not a secret) or inject via EAS Environment Variables.

## Get the FCM token

```ts
import messaging from '@react-native-firebase/messaging';

export async function getFCMToken(): Promise<string | null> {
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;

  if (!enabled) return null;

  const token = await messaging().getToken();
  return token;   // store this in your backend
}
```

Always request permission before getting the token (iOS requires explicit permission; Android 13+ also requires it).

## Listen for token refresh

```ts
useEffect(() => {
  const unsubscribe = messaging().onTokenRefresh(async (token) => {
    // Update token in your backend
    await supabase.from('profiles').update({ push_token: token }).eq('id', userId);
  });
  return unsubscribe;
}, []);
```

## Common pitfalls

- **`useFrameworks: 'static'` missing** → iOS build fails with cryptic pod errors. Always add it.
- **`google-services.json` not found** → Android build error; check the path or injection setup.
- **Requesting permission before `messaging()` is initialized** → call `getFCMToken()` after the app is fully mounted, not in a module-level initializer.
- **No `@react-native-firebase/app` installed** → messaging depends on the core app package.

FCM token handling for foreground/background/killed states → [handlers-state.md](handlers-state.md).
iOS APNs key setup (required for FCM on iOS) → [apns-ios.md](apns-ios.md).
