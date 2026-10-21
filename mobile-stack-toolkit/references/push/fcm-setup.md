---
title: "FCM setup and token lifecycle"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# FCM setup and token lifecycle

Use [Firebase setup](../firebase/setup-cli.md), native development builds and modular React Native Firebase APIs. Configure Android Firebase credentials and iOS APNs credentials/capabilities for the correct application IDs and environment.

```ts
import { getMessaging, getToken, onTokenRefresh } from '@react-native-firebase/messaging';
const messaging = getMessaging();
// After platform permission/APNs registration setup:
const token = await getToken(messaging);
await saveInstallationToken(token); // application-owned authenticated function
const unsubscribe = onTokenRefresh(messaging, token => {
  void saveInstallationToken(token).catch(reportTokenSyncFailure);
});
```

For Android 13+, request `POST_NOTIFICATIONS` with the platform permission API; RN Firebase's messaging `requestPermission` is primarily the iOS permission flow. On iOS wait for APNs registration/token readiness before operations that require it. Handle denial, provisional permission and settings changes without repeatedly prompting.

`saveInstallationToken` upserts one installation record, not a single `profiles.push_token` or every row for a user. Include user ID, installation ID, provider, environment/project, platform and last-seen time. Enforce ownership server-side/RLS; refresh only that installation and detach it on logout/account switch. Do not assume tokens are permanent device identifiers.

Dispose token/message listeners. Use the [handlers](handlers-state.md) for foreground/background/open events and [server sends](server-send.md) for delivery errors and token cleanup.

## Sources

Reviewed 2026-10-20: [RN messaging](https://rnfirebase.io/messaging/usage), [FCM token management](https://firebase.google.com/docs/cloud-messaging/manage-tokens).
