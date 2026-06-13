---
title: PostHog — product analytics for Expo/React Native
impact: MEDIUM
impactDescription: "PostHog provides event analytics, feature flags, and session replay without Firebase dependency; React Navigation v7 breaks auto screen tracking"
tags: posthog, analytics, feature-flags, expo, react-native, product-analytics
---

# PostHog — Expo / React Native

PostHog is an open-source product analytics platform: event tracking, funnels, session replay, feature flags, and A/B tests — all without sending data to Google. It's the self-hostable alternative to Firebase Analytics + Remote Config.

**Package:** `posthog-react-native`

---

## Install

```bash
# Expo (managed or bare)
npx expo install posthog-react-native expo-file-system expo-application expo-device expo-localization
```

---

## Setup

Wrap your root layout with `PostHogProvider`:

```tsx
// app/_layout.tsx
import { PostHogProvider } from 'posthog-react-native';

export default function RootLayout() {
  return (
    <PostHogProvider
      apiKey="phc_your_project_api_key"
      options={{
        host: 'https://us.i.posthog.com',  // or 'https://eu.i.posthog.com'
        // Autocapture settings:
        autocapture: {
          captureTouches: true,
          captureScreens: false,  // disable for React Navigation v7 (see below)
        },
      }}
    >
      <Stack />
    </PostHogProvider>
  );
}
```

Get your `apiKey` from the PostHog dashboard under Project Settings → API Keys. It's `phc_...` (public — safe to commit).

---

## Capture events

```tsx
import { usePostHog } from 'posthog-react-native';

export function PurchaseButton() {
  const posthog = usePostHog();

  function handlePurchase() {
    posthog.capture('purchase_tapped', {
      plan: 'pro',
      price: 9.99,
      currency: 'USD',
    });
    // ...actual purchase logic
  }

  return <Button title="Buy Pro" onPress={handlePurchase} />;
}
```

---

## Identify users

Call `identify` after login to attach events to a known user:

```ts
posthog.identify(user.id, {
  email: user.email,
  name: user.fullName,
  plan: 'free',
});
```

On logout, reset to an anonymous identity:

```ts
posthog.reset();
```

---

## Screen tracking

### React Navigation v7 (manual)

React Navigation v7 restricts navigation hooks to components inside a `Screen` — auto screen capture doesn't work. Track screens manually:

```tsx
// In each screen component
import { usePostHog } from 'posthog-react-native';
import { useFocusEffect } from 'expo-router';
import { useCallback } from 'react';

export function HomeScreen() {
  const posthog = usePostHog();

  useFocusEffect(
    useCallback(() => {
      posthog.screen('Home');
    }, [posthog]),
  );

  return <View />;
}
```

### Expo Router (file-based routing)

Use a layout-level listener if you want automatic screen tracking:

```tsx
// app/_layout.tsx
import { usePathname } from 'expo-router';
import { useEffect } from 'react';

function ScreenTracker() {
  const pathname = usePathname();
  const posthog = usePostHog();

  useEffect(() => {
    posthog.screen(pathname);
  }, [pathname]);

  return null;
}
```

---

## Feature flags

Feature flags let you roll out features to specific users without a release:

```tsx
import { useFeatureFlag } from 'posthog-react-native';

export function NewCheckoutButton() {
  const enabled = useFeatureFlag('new-checkout-flow');

  if (!enabled) return <OldCheckoutButton />;
  return <NewCheckoutButton />;
}
```

Check a flag value (multivariate flags):

```ts
const variant = posthog.getFeatureFlag('checkout-variant');
// variant === 'control' | 'v2' | 'v3' | undefined
```

Force feature flag evaluation after user identification (flags are evaluated on identify):

```ts
await posthog.reloadFeatureFlags();
```

---

## Opt out (GDPR)

For GDPR compliance, allow users to opt out of tracking:

```ts
posthog.optOut();   // stops all tracking
posthog.optIn();    // re-enables
posthog.isOptedOut(); // boolean
```

---

## Autocapture

PostHog can auto-capture:

| Event | Config | Notes |
|---|---|---|
| App lifecycle | always on | installed, opened, backgrounded, updated |
| Touch interactions | `captureTouches: true` | taps on Pressable, Button, TouchableOpacity |
| Screen views | `captureScreens: true` | **broken in React Navigation v7** — use manual |
| Exceptions | automatic | unhandled JS errors |

---

## vs Firebase Analytics

| | PostHog | Firebase Analytics |
|---|---|---|
| Self-hostable | ✅ | ❌ |
| Feature flags | ✅ Built-in | ⚠️ Remote Config (separate) |
| Session replay | ✅ | ❌ |
| Funnels / retention | ✅ | ✅ |
| Requires Google account | ❌ | ✅ |
| Free tier | 1M events/month | Unlimited |

---

## Gotchas

- **React Navigation v7 breaks `captureScreens: true`** — set it to `false` and track manually.
- **`posthog.identify()` triggers feature flag reload** — call it once after login, not on every render.
- **The `phc_` API key is public** — it's safe in `app.config.ts` as `EXPO_PUBLIC_POSTHOG_KEY`. PostHog uses it to route events to your project only.
- **Expo Go works** for development — `posthog-react-native` has no native code. Autocapture works in Expo Go too.
