---
title: Firebase App Check — protect backend resources from unauthorized clients
impact: CRITICAL
impactDescription: "Without App Check, anyone with your Firebase config can hit your Firestore, Storage, and AI Logic quota; App Check restricts access to your genuine app binaries"
tags: firebase, app-check, security, ios, android, flutter
---

# Firebase App Check

App Check verifies that requests come from your legitimate app binary, not a script, emulator exploit, or stolen config. It is **required** for Firebase AI Logic and strongly recommended for any production app using Firestore, Storage, or Cloud Functions.

## How it works

App Check uses platform attestation providers:
- **iOS**: App Attest (production) / DeviceCheck
- **Android**: Play Integrity (production) / SafetyNet (legacy)
- **Debug**: Fake debug token for local development

Each request from the app carries an App Check token. Firebase backend services verify this token server-side. Requests without a valid token are rejected.

## Setup — React Native (`@react-native-firebase/app-check`)

```bash
npx expo install @react-native-firebase/app-check
```

### app.config.ts

```ts
plugins: [
  ['@react-native-firebase/app', {}],
  ['@react-native-firebase/app-check', {
    // iOS — App Attest is the production provider (iOS 14+)
    // Android — Play Integrity is the production provider
  }],
]
```

### Initialize in app entry point

```ts
import appCheck from '@react-native-firebase/app-check';
import { Platform } from 'react-native';

// Call before any Firebase service usage
async function initAppCheck() {
  const provider = appCheck().newReactNativeFirebaseAppCheckProvider();
  
  provider.configure({
    apple: {
      provider: __DEV__ ? 'debug' : 'appAttest',
      debugToken: __DEV__ ? process.env.EXPO_PUBLIC_APP_CHECK_DEBUG_TOKEN : undefined,
    },
    android: {
      provider: __DEV__ ? 'debug' : 'playIntegrity',
      debugToken: __DEV__ ? process.env.EXPO_PUBLIC_APP_CHECK_DEBUG_TOKEN : undefined,
    },
  });

  await appCheck().initializeAppCheck({
    provider,
    isTokenAutoRefreshEnabled: true,
  });
}
```

Call `initAppCheck()` before `Firebase.initializeApp()` or right after in your root component.

## Setup — Flutter (`firebase_app_check`)

```yaml
# pubspec.yaml
dependencies:
  firebase_app_check: ^0.3.2+2
```

```dart
// main.dart — after Firebase.initializeApp()
await FirebaseAppCheck.instance.activate(
  androidProvider: kDebugMode ? AndroidProvider.debug : AndroidProvider.playIntegrity,
  appleProvider: kDebugMode ? AppleProvider.debug : AppleProvider.appAttest,
);
```

## Debug tokens (local dev)

Generate a debug token in Firebase Console → App Check → Apps → (your app) → Manage debug tokens. Add it to your `.env.local`:

```
EXPO_PUBLIC_APP_CHECK_DEBUG_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Never commit debug tokens or use them in production builds.

## Enforce App Check on Firebase services

After registering your apps, enable enforcement in Firebase Console → App Check → Apps → Enable enforcement for each service (Firestore, Storage, Functions, AI Logic).

**Start in monitoring mode first** (tracks which traffic would be blocked) → after confirming your app passes, switch to enforced mode.

```
Monitoring mode → observe for 24-48 hours → enable enforcement
```

## iOS: register App Attest capability

In Xcode → Signing & Capabilities → add **App Attest**. Without this, App Attest attestation fails silently in production.

Also add to your `app.config.ts` entitlements:

```ts
ios: {
  entitlements: {
    'com.apple.developer.devicecheck.appattest-environment': 'production',
  },
}
```

## Android: Play Integrity setup

Play Integrity requires your app to be published on Play Console (even in internal testing track). The SHA-256 fingerprint of your signing key must be registered in Firebase Console → Project Settings → Your apps → Android → SHA certificate fingerprints.

```bash
# Get your EAS release key fingerprint
eas credentials --platform android
```

## Verify App Check is working

```ts
const token = await appCheck().getToken(/* forceRefresh */ false);
console.log('App Check token:', token.token ? 'obtained' : 'failed');
```

## App Check + Firebase AI Logic (required pairing)

Firebase AI Logic **requires** App Check in production. The `firebase_ai` / `@react-native-firebase/firebase-ai` packages check for an App Check token before making Gemini API calls. Without it you get `PERMISSION_DENIED` errors when enforcement is enabled.

See [ai-logic.md](ai-logic.md) for the complete Firebase AI Logic setup.
