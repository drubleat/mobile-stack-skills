---
title: APNs key: Apple Developer → Firebase
impact: HIGH
impactDescription: "Without an APNs authentication key, FCM silently delivers to Android only; iOS push appears to work in dev then breaks in prod"
tags: push, apns, ios, firebase, certificates
---

# APNs key: Apple Developer → Firebase

Firebase needs an APNs authentication key to deliver push notifications to iOS devices via FCM. Without it, FCM can deliver to Android but silently fails on iOS.

## Step 1: Create the APNs key in Apple Developer

1. Go to [developer.apple.com](https://developer.apple.com) → Certificates, Identifiers & Profiles → **Keys**.
2. Click **+** → name it (e.g. "FCM APNs Key") → check **Apple Push Notifications service (APNs)** → Continue → Register.
3. **Download the `.p8` file immediately** — you can only download it once. If you lose it, you must create a new key.
4. Note the **Key ID** (shown after creation) and your **Team ID** (top-right of your Apple Developer account).

One APNs key works for all your apps in the same team — you don't need one per app.

## Step 2: Upload to Firebase

1. Firebase Console → Project Settings (gear icon) → **Cloud Messaging** tab.
2. Under "Apple app configuration" → **APNs Authentication Key** → Upload.
3. Upload the `.p8` file, enter the Key ID and Team ID.

Done. Firebase can now deliver to iOS through APNs.

## APNs key vs APNs certificate

Apple offers two methods:
- **APNs Auth Key** (`.p8`) — recommended. Doesn't expire, works for all apps in the team, one key covers sandbox and production.
- **APNs Certificate** (`.p12`) — legacy. Expires yearly, must be renewed and re-uploaded, separate certs for sandbox and production.

Always use the Auth Key.

## Enable Push Notifications capability

In your app's Identifier (App Store Connect → Certificates, Identifiers & Profiles → Identifiers):
1. Find your app's Bundle ID → Edit.
2. Enable **Push Notifications** capability.
3. Save.

EAS Build with managed credentials handles this automatically when you add `expo-notifications` or `@react-native-firebase/messaging` to your project.

## Verifying it works

After uploading the APNs key:
1. Build and run on a **real iOS device** (not simulator — simulators don't receive remote push).
2. Get the FCM/Expo token and send a test notification from Firebase Console → Cloud Messaging → Send test message.
3. If no notification arrives: check the APNs key is uploaded, the app has push capability enabled, and the device has push permission granted.

## Common pitfalls

- **`.p8` file lost** → you must create and upload a new key; revoke the old one in Apple Developer.
- **Wrong Team ID** → Firebase accepts the upload but all iOS deliveries silently fail. Double-check your Team ID in the Apple Developer portal (top-right corner of the account page).
- **Push Notifications capability not enabled on the Identifier** → iOS rejects the APNs connection; FCM falls back to nothing.
- **Simulator testing** → simulators never receive remote push notifications. Test on a real device.
