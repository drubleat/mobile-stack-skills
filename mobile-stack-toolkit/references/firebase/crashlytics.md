---
title: "Crashlytics reporting and symbol verification"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Crashlytics reporting and symbol verification

Configure native Crashlytics for the installed Firebase SDK and rebuild. For RN Firebase, use modular APIs:

```ts
import { getCrashlytics, recordError, log } from '@react-native-firebase/crashlytics';
const reporter = getCrashlytics();
log(reporter, 'Checkout opened');
try { await operation(); }
catch (error) {
  recordError(reporter, error instanceof Error ? error : new Error('Operation failed'));
  throw error;
}
```

Attach only approved non-sensitive metadata; clear user identifiers on logout. Respect configured collection/consent behavior. Avoid assuming every debug build uploads or that every JS exception is automatically captured with the right classification.

For Flutter, wire framework errors via `FlutterError.onError` and asynchronous errors via `PlatformDispatcher.instance.onError` after Firebase initialization. Import `dart:ui` for PlatformDispatcher. Preserve existing error handlers as appropriate and classify fatal/nonfatal errors deliberately.

Verify symbolication for a known release test crash: iOS dSYM, Android mapping files and any relevant JS source maps. A config plugin is not proof that a particular upload succeeded. Use a dedicated test build, restart after the crash, detach the debugger as the platform guide requires, and inspect the resulting dashboard event. Do not claim a fixed arrival time or deliberately crash user production sessions.

## Sources

Reviewed 2026-10-20: [RN Crashlytics](https://rnfirebase.io/crashlytics/usage), [Flutter Crashlytics](https://firebase.google.com/docs/crashlytics/get-started?platform=flutter).
