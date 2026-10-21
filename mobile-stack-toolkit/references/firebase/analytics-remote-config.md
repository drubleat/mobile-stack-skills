---
title: "Analytics and Remote Config"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Analytics and Remote Config

Use modular React Native Firebase APIs and gate collection according to the application's consent policy. ATT is required for tracking as Apple defines it, not automatically for every analytics installation. Avoid personal data, auth tokens, prompt contents and raw route parameters in events.

```ts
import { getAnalytics, logEvent } from '@react-native-firebase/analytics';
import { getRemoteConfig, setDefaults, fetchAndActivate, getValue } from '@react-native-firebase/remote-config';
await logEvent(getAnalytics(), 'paywall_opened', { placement: 'settings' });
const rc = getRemoteConfig();
await setDefaults(rc, { feature_voice_enabled: false });
try { await fetchAndActivate(rc); } catch { /* retain safe cached/default values */ }
const voiceEnabled = getValue(rc, 'feature_voice_enabled').asBoolean();
```

ConfigValue is an object: convert with `asBoolean`, `asString` or `asNumber`; casting it to a generic type does not convert the value. Publish updates into application state after activation. Choose fetch intervals and timeouts appropriate to the app and keep startup usable when offline. Check current service quotas rather than hardcoding old parameter/rate limits.

Flutter uses `FirebaseRemoteConfig.instance`, `setDefaults`, `fetchAndActivate` and typed getters. Analytics screen events should use normalized route names and avoid duplicating automatic purchase or screen events.

Remote Config is client-readable. It may choose UI variants or a supported managed AI model; it must not store secrets or decide server-side entitlements, quotas or arbitrary provider access. A proxy validates allowed model/cost policy independently. Test rollback and old-client compatibility before activating a production template.

## Sources

Reviewed 2026-10-20: [Remote Config](https://rnfirebase.io/remote-config/usage), [Analytics](https://rnfirebase.io/analytics/usage), [Apple privacy](https://developer.apple.com/app-store/user-privacy-and-data-use/).
