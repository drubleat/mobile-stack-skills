---
title: Supabase + Firebase hybrid patterns
impact: HIGH
impactDescription: "Most production apps use both: Supabase for structured data/auth/backend logic, Firebase for observability and push"
tags: firebase, supabase, hybrid, architecture
---

# Supabase + Firebase hybrid patterns

The most common production pattern: Supabase handles structured data, auth, and backend logic; Firebase provides observability and push infrastructure.

## Recommended split

| Responsibility | Use |
|---|---|
| User authentication | **Supabase Auth** |
| Relational data (profiles, subscriptions, usage) | **Supabase Postgres** |
| AI orchestration, webhooks (RevenueCat, Stripe) | **Supabase Edge Functions** |
| File/media storage | **Supabase Storage** |
| Crash reporting | **Firebase Crashlytics** |
| Analytics + A/B testing | **Firebase Analytics + Remote Config** |
| Push notifications | **Firebase FCM** |
| Beta distribution | **Firebase App Distribution** (optional) |

You don't need Firebase Auth, Firestore, or Firebase Storage in a Supabase hybrid — those would duplicate Supabase capabilities.

## Initialization order

```ts
// app/_layout.tsx
import { supabase } from '@/lib/supabase';     // Supabase singleton
import '@react-native-firebase/app';            // RNFirebase auto-initializes

// Firebase initializes from GoogleService-Info.plist / google-services.json.
// Supabase initializes from the singleton with EXPO_PUBLIC_* env vars.
// No explicit init calls needed for either — just import the singletons.
```

## Linking Crashlytics user ID to Supabase user

```ts
import crashlytics from '@react-native-firebase/crashlytics';
import analytics from '@react-native-firebase/analytics';
import { supabase } from '@/lib/supabase';

supabase.auth.onAuthStateChange(async (event, session) => {
  if (session?.user) {
    const uid = session.user.id;
    // Link Firebase observability to the same user ID as Supabase
    await crashlytics().setUserId(uid);
    await analytics().setUserId(uid);
  } else {
    // Clear on sign-out
    await crashlytics().setUserId('');
    await analytics().setUserId('');
  }
});
```

This means crash reports and analytics events are tagged with the same ID as the Supabase user — making debugging much easier.

## Storing FCM tokens in Supabase

```ts
// After getting the FCM token, store it in Supabase
import messaging from '@react-native-firebase/messaging';
import { supabase } from '@/lib/supabase';

async function syncFcmToken() {
  const token = await messaging().getToken();
  const uid = (await supabase.auth.getUser()).data.user?.id;
  if (!token || !uid) return;

  await supabase.from('device_tokens').upsert({
    user_id: uid,
    token,
    platform: Platform.OS,
    updated_at: new Date().toISOString(),
  }, { onConflict: 'token' });
}

messaging().onTokenRefresh(async (newToken) => {
  const uid = (await supabase.auth.getUser()).data.user?.id;
  if (!uid) return;
  await supabase.from('device_tokens')
    .update({ token: newToken, updated_at: new Date().toISOString() })
    .eq('user_id', uid);
});
```

The Supabase Edge Function that sends FCM push notifications then reads from `device_tokens` — no Firebase SDK needed on the server side, just the FCM HTTP v1 API.

## Remote Config + Supabase flags

For simple feature flags, Supabase is enough (a `feature_flags` table with RLS). For A/B testing with Firebase's analytics integration, use Remote Config. They don't conflict — you can read from both:

```ts
const remoteVariant = remoteConfig().getString('paywall_variant');         // Firebase A/B test
const { data: userFlags } = await supabase.from('feature_flags').select(); // Supabase per-user flags
```

## Error attribution

When Supabase Edge Function calls fail, log them as non-fatal errors to Crashlytics:

```ts
import crashlytics from '@react-native-firebase/crashlytics';

async function callEdgeFunction(fnName: string, body: object) {
  const { data, error } = await supabase.functions.invoke(fnName, { body });
  if (error) {
    crashlytics().recordError(
      new Error(`Edge Function ${fnName} failed: ${error.message}`)
    );
    throw error;
  }
  return data;
}
```

## What NOT to add from Firebase in a hybrid

- **Firebase Auth**: conflict with Supabase Auth. Two JWT systems = token management hell.
- **Cloud Firestore**: conflict with Supabase Postgres. Two sources of truth for user data breaks consistency.
- **Firebase Storage**: Supabase Storage with RLS is simpler to secure alongside Supabase Auth.
- **Firebase Cloud Functions**: Supabase Edge Functions cover the same use cases without adding another deployment target.

Keep Firebase to its strengths: Crashlytics, Analytics, Remote Config, FCM. Let Supabase own everything else.

## Package inventory for hybrid setup

```bash
# Supabase
npx expo install @supabase/supabase-js @react-native-async-storage/async-storage expo-secure-store

# Firebase (only what you need)
npx expo install @react-native-firebase/app @react-native-firebase/crashlytics @react-native-firebase/analytics @react-native-firebase/remote-config @react-native-firebase/messaging expo-build-properties
```

`app.config.ts` plugins:
```ts
plugins: [
  ['expo-build-properties', { ios: { useFrameworks: 'static' } }],
  '@react-native-firebase/app',
  '@react-native-firebase/crashlytics',
  '@react-native-firebase/messaging',
]
```
