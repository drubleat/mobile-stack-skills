---
title: Permissions, privacy policy & data disclosures
impact: HIGH
impactDescription: "Missing NSPhotoLibraryUsageDescription or incorrect ATT prompt cause immediate App Review rejection"
tags: store, permissions, privacy, ios, android, att
---

# Permissions, privacy policy & data disclosures

## iOS: permission usage strings (Info.plist)

Every permission your app requests must have a usage description string. Apple rejects apps that request permissions without them, or with placeholder text like "We need access."

Set them in `app.config.ts` under `ios.infoPlist`:

```ts
ios: {
  infoPlist: {
    NSCameraUsageDescription: 'We use the camera to scan your meal for nutritional analysis.',
    NSPhotoLibraryUsageDescription: 'We access your photo library to let you upload meal photos.',
    NSMicrophoneUsageDescription: 'We use the microphone for voice input to log meals hands-free.',
    NSLocationWhenInUseUsageDescription: 'We use your location to find nearby restaurants.',
    NSUserTrackingUsageDescription: 'We use tracking to provide personalized offers and measure ad performance.',   // ATT
    NSSpeechRecognitionUsageDescription: 'We use speech recognition to transcribe your voice notes.',
  },
}
```

**Write real reasons, not generic ones.** The reviewer reads these. "We need access" → rejection. "We use the camera to scan receipts for expense tracking" → approved.

## App Tracking Transparency (ATT — iOS)

If you use any analytics SDK that tracks users across apps (Firebase Analytics, Meta SDK, etc.) you must request ATT permission before initializing those SDKs:

```bash
npx expo install expo-tracking-transparency
```

```ts
import { requestTrackingPermissionsAsync } from 'expo-tracking-transparency';
const { status } = await requestTrackingPermissionsAsync();
// Only initialize tracking SDKs if status === 'granted'
```

Also add `NSUserTrackingUsageDescription` to `infoPlist` (above). **Omitting ATT and using tracking = App Store rejection.**

## Android: permissions in AndroidManifest

Set via `app.config.ts` under `android.permissions`:

```ts
android: {
  permissions: [
    'CAMERA',
    'READ_MEDIA_IMAGES',          // Android 13+ (replaces READ_EXTERNAL_STORAGE)
    'POST_NOTIFICATIONS',         // Android 13+ (required to show push notifications)
    'RECORD_AUDIO',
    'ACCESS_FINE_LOCATION',
  ],
}
```

## Privacy Policy — mandatory, not optional

Apple and Google both require a privacy policy URL if your app:
- Collects any user data (name, email, device ID)
- Uses analytics or crash reporting
- Has AI features that process user input
- Has subscriptions (even if you don't collect much)

In practice: **every real app needs a privacy policy.** Host it at a stable URL (e.g. `yourapp.com/privacy`) — reviewers check that the link works.

**Minimum content for an AI app:**
- What data is collected (email, usage data, content submitted to AI)
- How it's used (to provide the service, improve the model, send notifications)
- Third-party processors (OpenAI, Gemini, Supabase, RevenueCat, Firebase)
- Data retention and deletion policy
- Contact for data requests (GDPR if EU users)

## AI-specific Apple requirements (2026)

Apple has added requirements for apps using AI:
- Disclose that AI-generated content is AI-generated when shown to users.
- If the AI can generate harmful content, you need content moderation in place (not just a disclaimer).
- AI features that generate images of real people require extra scrutiny.
- Apps using AI for health/financial/legal advice face higher scrutiny — add professional advice disclaimers.

## Children's privacy

If your app's age rating includes under-13:
- **COPPA (US)**: no targeted advertising, no third-party analytics SDKs without parental consent.
- **GDPR-K (EU)**: similar restrictions.
- Firebase Analytics, Meta SDK etc. are off-limits without consent mechanisms. Consider opting out of ad personalization for all users in these apps.
