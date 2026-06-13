---
title: Push notifications — domain index
impact: MEDIUM-HIGH
impactDescription: "Routes to FCM setup, APNs, Expo Push, handlers, server send, and deep linking"
tags: push, fcm, apns, expo-notifications, index
---

# Push notifications — index

## Expo Push vs FCM — which do you need?

| Scenario | Use |
|---|---|
| Simple notifications, no native Firebase dependency | **Expo Push** (simpler) |
| Already using `@react-native-firebase` (e.g. Crashlytics) | **FCM** (already installed) |
| Data messages, silent pushes, background processing | **FCM** |
| Need iOS critical alerts or notification service extensions | **FCM** |
| Maximum delivery control + analytics | **FCM** |

**Expo Push** wraps both APNs and FCM behind the Expo Push API — you get one token, one API call. Great for apps that don't need native Firebase otherwise.

**FCM direct** gives you raw APNs + FCM with full control. Required if you use other Firebase services (adding `@react-native-firebase` for Crashlytics means FCM is already in your native layer — add messaging too at zero extra cost).

For most serious apps in this toolkit: if you have `@react-native-firebase/crashlytics`, add `@react-native-firebase/messaging` too.

## Router

| Task | File |
|---|---|
| Expo Push: get token, send via Expo API | [expo-push.md](expo-push.md) |
| FCM: `@react-native-firebase/messaging` setup | [fcm-setup.md](fcm-setup.md) |
| iOS APNs key setup, upload to Firebase | [apns-ios.md](apns-ios.md) |
| Foreground / background / killed state handlers | [handlers-state.md](handlers-state.md) |
| Send push from Edge Function / cron / DB trigger | [server-send.md](server-send.md) |
| Deep link: tap notification → correct screen | [deep-linking.md](deep-linking.md) |

**Flutter push?** → [../flutter/push-firebase.md](../flutter/push-firebase.md)

## The two non-negotiables

1. **Store the push token server-side** (Supabase `profiles.push_token`, Firestore doc, etc.) when the user grants permission. Without it, you can't target a specific user's device.
2. **APNs key uploaded to Firebase** (if using FCM on iOS). Without the key, FCM can't deliver to iOS. → [apns-ios.md](apns-ios.md)
