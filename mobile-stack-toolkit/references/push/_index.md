---
title: "Push notifications — domain index"
impact: MEDIUM-HIGH
impactDescription: "Routes to FCM setup, APNs, Expo Push, handlers, server send, and deep linking"
tags: push, fcm, apns, expo-notifications, index
---

# Push notifications — index

Choose Expo Push for a unified delivery service or direct FCM/APNs when the app needs those integrations. Crashlytics does not require FCM messaging. Both approaches need native credentials; data-only background delivery is subject to OS limits.

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

## Shared lifecycle

Store tokens per installation/provider/environment with ownership checks. Refresh only the matching installation and detach it on logout. Validate notification routing and process provider errors/receipts. Test physical-device delivery and permission-denied behavior.
