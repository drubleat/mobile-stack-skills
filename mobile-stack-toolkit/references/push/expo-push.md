---
title: Expo Push: expo-notifications + Expo Push API
impact: HIGH
impactDescription: "Simplest push setup for Expo apps; single token works for both iOS and Android via Expo's relay service"
tags: push, expo-notifications, expo-push-api
---

# Expo Push: expo-notifications + Expo Push API

The simplest push setup: one token, one API, no Firebase needed.

## Install & configure

```bash
npx expo install expo-notifications expo-device
```

Add to `app.config.ts` plugins:
```ts
plugins: [
  ['expo-notifications', {
    icon: './assets/notification-icon.png',  // white on transparent, Android
    color: '#ffffff',
    sounds: ['./assets/notification.wav'],
  }],
]
```

## Get the push token

```ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) return null;   // simulators don't get real tokens

  const { status: existing } = await Notifications.getPermissionsAsync();
  const { status } = existing === 'granted'
    ? { status: existing }
    : await Notifications.requestPermissionsAsync();

  if (status !== 'granted') return null;

  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const token = await Notifications.getExpoPushTokenAsync({ projectId });
  return token.data;   // 'ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]'
}
```

**`projectId` is required** — without it tokens are invalid and the Push API rejects them silently.

## Store the token on your backend

```ts
const token = await registerForPushNotifications();
if (token && user) {
  await supabase.from('profiles').update({ push_token: token }).eq('id', user.id);
}
```

Re-register on every app launch — tokens rotate on reinstall/OS rotation.

## Foreground display handler (set at app start)

```ts
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});
```

Without this, foreground notifications are silently dropped.

## Send via Expo Push API (from your server)

```ts
// From a Supabase Edge Function
const messages = [{
  to: pushToken,
  title: 'New message',
  body: 'You have a new message!',
  data: { screen: 'chat', roomId: '123' },
  sound: 'default',
  badge: 1,
  priority: 'high',
}];

const res = await fetch('https://exp.host/--/api/v2/push/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify(messages),
});
const { data } = await res.json();
// data[0].status === 'ok' | 'error'
// if error: data[0].details.error === 'DeviceNotRegistered' → delete stale token
```

Batch up to 100 messages per request. Handle `DeviceNotRegistered` by removing the token from your DB.

## Limitations vs FCM direct

- Expo Push relay adds one hop (your server → Expo → APNs/FCM → device).
- Silent/data-only messages are less reliable.
- Less priority and TTL control.
- Tokens can change unexpectedly — always handle `DeviceNotRegistered`.

For more control → [fcm-setup.md](fcm-setup.md).
