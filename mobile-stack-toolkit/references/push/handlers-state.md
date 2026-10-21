---
title: "Notification lifecycle handlers"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Notification lifecycle handlers

Separate receipt, display and navigation. Register one handler for each lifecycle event and dispose listeners. Never assume a data-only message will wake a suspended or force-stopped app; OS power policies, payload priority and user settings affect delivery.

For RN Firebase use modular `onMessage`, `setBackgroundMessageHandler`, `onNotificationOpenedApp` and `getInitialNotification`. Register the background handler at the app entrypoint; it performs bounded non-UI work. If Notifee handles display/open events in the installed integration, use its documented event APIs and avoid duplicate navigation.

FCM HTTP v1 payload shape:

```json
{
  "message": {
    "token": "DEVICE_FCM_TOKEN",
    "notification": { "title": "Update ready", "body": "Open to view details" },
    "data": { "type": "item_updated", "item_id": "123" }
  }
}
```

Data values are strings. This is sent by a trusted server with an OAuth access token to the project-specific v1 endpoint, not the retired legacy `to` endpoint. See [server send](server-send.md).

Foreground display is an application decision. iOS presentation options or a local notification library can show a banner; avoid showing both. Android local display needs a configured channel. In background, notification payloads may be displayed by the OS; a separate local notification can duplicate them.

On open, use [validated deep links](deep-linking.md) after authentication/navigation readiness. Fetch authorized content from the server; do not trust payload text as current state or authority. Test foreground, background, terminated, denied permission, account switch and duplicate delivery.

## Sources

Reviewed 2026-10-20: [FCM message types](https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type), [RN messaging](https://rnfirebase.io/messaging/usage).
