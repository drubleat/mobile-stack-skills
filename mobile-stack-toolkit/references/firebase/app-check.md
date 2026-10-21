---
title: "Firebase App Check"
impact: HIGH
impactDescription: "Avoid incompatible APIs and unsafe mobile integration defaults"
tags: mobile, integration, correctness
---

# Firebase App Check

App Check adds app/device attestation to supported backend services. It complements user authentication and Security Rules; it does not prove a human is trusted or prevent all abuse. Requests without valid tokens are rejected only for services with enforcement enabled.

Initialize the Firebase app first, then configure App Check before protected service calls. For native React Native Firebase the default app is initialized by native configuration; web/secondary apps may need explicit initialization. Use modular APIs for modern RN Firebase:

```ts
import { getApp } from '@react-native-firebase/app';
import { initializeAppCheck, ReactNativeFirebaseAppCheckProvider } from '@react-native-firebase/app-check';
const provider = new ReactNativeFirebaseAppCheckProvider();
provider.configure({
  android: { provider: __DEV__ ? 'debug' : 'playIntegrity' },
  apple: { provider: __DEV__ ? 'debug' : 'appAttestWithDeviceCheckFallback' },
});
await initializeAppCheck(getApp(), { provider, isTokenAutoRefreshEnabled: true });
```

Follow the installed SDK's debug-token setup, register the development token, and treat that token as a secret. Never ship it in a release bundle or a shared `EXPO_PUBLIC_*` value. Do not log live attestation tokens.

For Flutter initialize Firebase, then activate `FirebaseAppCheck.instance` using the providers supported by the installed version. Select production providers according to platform support, signing, distribution channel, and fallback needs. SafetyNet is retired; use Play Integrity on Android.

Inspect attestation metrics before enabling enforcement so existing valid builds are not locked out. Test production-signing/device paths, not only debug tokens. Configure custom backend verification explicitly; attaching a header alone does not verify it. See [AI Logic](ai-logic.md) for the managed AI path.

## Sources

Reviewed 2026-10-20: [RN Firebase App Check](https://rnfirebase.io/app-check/usage), [Firebase App Check](https://firebase.google.com/docs/app-check).
