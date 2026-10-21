---
title: "Expo push setup and receipts"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Expo push setup and receipts

Expo Push Service uses Expo push tokens and still requires native APNs/FCM credentials. Use a development build for remote push testing; Expo Go availability is SDK/platform-dependent and is not a release validation environment.

```ts
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
if (Platform.OS === 'android') {
  await Notifications.setNotificationChannelAsync('default', {
    name: 'Default', importance: Notifications.AndroidImportance.DEFAULT,
  });
}
const permission = await Notifications.requestPermissionsAsync();
if (!permission.granted) throw new Error('Notifications not enabled');
const projectId = Constants.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId;
if (!projectId) throw new Error('Missing EAS project ID');
const { data: token } = await Notifications.getExpoPushTokenAsync({ projectId });
```

This is a registration fragment; request permission at a relevant user action and gracefully support denial. Store the token per installation with ownership and environment. Handle refresh and account switching. Do not pass Expo tokens to the FCM HTTP API or FCM tokens to Expo's push endpoint.

Configure the foreground notification handler with the fields supported by the installed SDK; recent SDKs use `shouldShowBanner` and `shouldShowList`, plus sound/badge decisions. Remove received/response listeners on cleanup. Handle initial notification responses only after navigation/auth restoration and deduplicate them.

A push ticket acknowledges acceptance, not device delivery. Retain ticket IDs, fetch push receipts, handle errors such as DeviceNotRegistered and remove only the affected installation. Respect documented batching, limits and retry/backoff rules. See [server send](server-send.md).

## Sources

Reviewed 2026-10-20: [Expo push setup](https://docs.expo.dev/push-notifications/push-notifications-setup/), [sending notifications](https://docs.expo.dev/push-notifications/sending-notifications/).
