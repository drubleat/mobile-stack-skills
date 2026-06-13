---
title: Firebase Crashlytics: crash reporting & non-fatals
impact: HIGH
impactDescription: "Custom keys and non-fatal logging attached before a crash make the difference between a 10-minute fix and a 2-day investigation"
tags: firebase, crashlytics, monitoring, crashes
---

# Firebase Crashlytics

Crashlytics provides real-time crash reporting, non-fatal error logging, and custom metadata attached to crash reports.

## Setup (React Native / Expo)

```bash
npx expo install @react-native-firebase/crashlytics
```

Add to `app.config.ts`:
```ts
plugins: [
  '@react-native-firebase/app',
  '@react-native-firebase/crashlytics',
]
```

No additional initialization code is needed — Crashlytics automatically captures unhandled JS exceptions and native crashes after you rebuild with the plugin.

## Capturing non-fatal errors

```ts
import crashlytics from '@react-native-firebase/crashlytics';

// Log a non-fatal error (shows in Crashlytics dashboard without crashing the app)
try {
  await riskyOperation();
} catch (error) {
  crashlytics().recordError(error as Error);
  // Handle gracefully...
}
```

## Custom keys and logs

Attach metadata to crash reports to make them easier to debug:

```ts
// Runs on app start / user sign-in
async function setCrashlyticsUser(userId: string, plan: string) {
  await crashlytics().setUserId(userId);
  await crashlytics().setAttribute('plan', plan);
  await crashlytics().setAttribute('appVersion', Constants.expoConfig?.version ?? 'unknown');
}

// Log events leading up to a crash (last 64 lines retained)
crashlytics().log('User opened paywall');
crashlytics().log('Tapping purchase button');
```

## Breadcrumbs pattern

```ts
// lib/crashlytics.ts
import crashlytics from '@react-native-firebase/crashlytics';

export function logBreadcrumb(event: string, params?: Record<string, string>) {
  const paramStr = params ? ` ${JSON.stringify(params)}` : '';
  crashlytics().log(`[${new Date().toISOString()}] ${event}${paramStr}`);
}

// Usage
logBreadcrumb('navigation', { screen: 'Paywall', from: 'HomeTab' });
logBreadcrumb('purchase.start', { productId: 'pro_monthly' });
```

## Testing Crashlytics

```ts
// Force a test crash (use only in dev/debug builds)
crashlytics().crash();
```

Test crashes appear in the Crashlytics dashboard under "Debugger" within a few minutes. **Production builds can take up to 5 minutes** to appear; non-fatal errors may take longer.

## Disabling in development

Crashlytics uploads are suppressed in debug builds by default. If you want to explicitly disable it:

```ts
if (__DEV__) {
  crashlytics().setCrashlyticsCollectionEnabled(false);
}
```

## dSYM upload (iOS symbolication)

For Expo managed workflow with EAS Build, dSYMs are uploaded automatically. If you see unsymbolicated iOS crashes, check that the `@react-native-firebase/crashlytics` plugin is in your `app.config.ts` plugins array — it configures the build phase that uploads dSYMs.

## Flutter

```dart
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:flutter/foundation.dart';

// In main(), after Firebase.initializeApp():
FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;

// Catch async errors not caught by Flutter framework:
PlatformDispatcher.instance.onError = (error, stack) {
  FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
  return true;
};

// Non-fatal:
FirebaseCrashlytics.instance.recordError(error, stackTrace);

// Custom keys:
await FirebaseCrashlytics.instance.setUserIdentifier(userId);
await FirebaseCrashlytics.instance.setCustomKey('plan', plan);

// Log:
FirebaseCrashlytics.instance.log('User opened paywall');
```

## Gotchas

- Crashlytics only uploads crash reports on the **next app launch** after a crash. Crashes are buffered and sent when the app restarts.
- In Expo Go / development builds without the native module built in, Crashlytics won't work — it requires a native build.
- Obfuscated Android builds (R8/ProGuard) need the Crashlytics Gradle plugin to upload mapping files. This is handled automatically by the `@react-native-firebase/crashlytics` config plugin for EAS Build.
