---
title: Firebase Analytics & Remote Config
impact: MEDIUM
impactDescription: "Remote Config enables A/B tests and feature flags that update without a release; Analytics provides funnel data"
tags: firebase, analytics, remote-config, ab-testing
---

# Firebase Analytics & Remote Config

## Firebase Analytics

### Setup

```bash
npx expo install @react-native-firebase/analytics
```

No plugin config needed beyond `@react-native-firebase/app`. Analytics auto-collects session data, first_open, and screen_view events.

### Log custom events

```ts
import analytics from '@react-native-firebase/analytics';

// Track a purchase
await analytics().logPurchase({
  currency: 'USD',
  value: 4.99,
  items: [{ item_id: 'pro_monthly', item_name: 'Pro Monthly', quantity: 1 }],
});

// Track screen views
await analytics().logScreenView({
  screen_name: 'Paywall',
  screen_class: 'PaywallScreen',
});

// Custom events
await analytics().logEvent('ai_prompt_sent', {
  model: 'gpt-5.4-mini',
  input_length: messageLength,
});
```

### User properties

```ts
// Set user properties for segmentation in Firebase Console
await analytics().setUserId(uid);
await analytics().setUserProperty('plan', 'pro');
await analytics().setUserProperty('ai_provider', 'openai');
```

### Auto screen tracking with Expo Router

Expo Router's navigation state can be auto-sent as screen views:

```ts
// app/_layout.tsx
import { usePathname } from 'expo-router';
import analytics from '@react-native-firebase/analytics';
import { useEffect } from 'react';

function AnalyticsTracker() {
  const pathname = usePathname();
  useEffect(() => {
    analytics().logScreenView({ screen_name: pathname });
  }, [pathname]);
  return null;
}
```

### Disable in development

```ts
if (__DEV__) {
  analytics().setAnalyticsCollectionEnabled(false);
}
```

### ATT compliance (iOS)

Firebase Analytics collects device identifiers. If you use it, you must request ATT permission before initializing and declare it in Data Safety. See [../store/permissions-privacy.md](../store/permissions-privacy.md).

---

## Remote Config

Remote Config lets you change app behavior without a new release — feature flags, A/B test copy, API URLs, paywall variants.

### Setup

```bash
npx expo install @react-native-firebase/remote-config
```

### Define defaults and fetch

```ts
import remoteConfig from '@react-native-firebase/remote-config';

async function initRemoteConfig() {
  await remoteConfig().setDefaults({
    ai_model: 'gpt-5.4-mini',
    paywall_variant: 'A',
    max_free_requests: 5,
    feature_voice_enabled: false,
  });

  await remoteConfig().setConfigSettings({
    minimumFetchIntervalMillis: __DEV__ ? 0 : 3600000,  // 0 in dev, 1hr in prod
  });

  await remoteConfig().fetchAndActivate();
}
```

Call `initRemoteConfig()` at app startup, before rendering UI that depends on config values.

### Read values

```ts
const rc = remoteConfig();

const model = rc.getString('ai_model');
const paywallVariant = rc.getString('paywall_variant');
const maxFreeRequests = rc.getNumber('max_free_requests');
const voiceEnabled = rc.getBoolean('feature_voice_enabled');
```

### React hook

```ts
// hooks/useRemoteConfig.ts
import remoteConfig from '@react-native-firebase/remote-config';
import { useState, useEffect } from 'react';

export function useRemoteConfig<T>(key: string, defaultValue: T): T {
  const [value, setValue] = useState<T>(defaultValue);

  useEffect(() => {
    const v = remoteConfig().getValue(key);
    if (v.getSource() !== 'static') {
      // 'static' means the key doesn't exist — use default
      setValue(v as unknown as T);
    }
  }, [key]);

  return value;
}
```

### A/B testing

Set up experiments in Firebase Console → Remote Config → A/B testing. Firebase randomly assigns users to control/treatment groups and reports conversion metrics. Use this for paywall copy, onboarding flow, or pricing display variants.

### CLI template management (version control)

Manage Remote Config as code — version-controlled JSON that can be reviewed and rolled back:

```bash
# Pull current template to a local file
npx -y firebase-tools@latest remoteconfig:get -o remote_config.json

# Edit remote_config.json locally, then deploy:
# 1. Add to firebase.json:
#    { "remoteconfig": { "template": "remote_config.json" } }

# 2. Deploy
npx -y firebase-tools@latest deploy --only remoteconfig

# 3. Verify — list version history
npx -y firebase-tools@latest remoteconfig:versions:list

# Roll back to a specific version
npx -y firebase-tools@latest remoteconfig:rollback --version-number 5
```

**Always ask for user review before deploying Remote Config changes** — a bad config value can affect all users simultaneously.

### Use Remote Config for AI model names

Never hardcode AI model names in your app binary. Use Remote Config to update them without a release:

```ts
// React Native
const model = remoteConfig().getString('ai_model');  // 'gpt-5.4-mini'
const geminiModel = remoteConfig().getString('gemini_model');  // 'gemini-2.5-flash'
```

```dart
// Flutter
final modelName = rc.getString('ai_model');
// Pass to Edge Function call or Firebase AI Logic
```

Remote Config values:
```json
{
  "ai_model": "gpt-5.4-mini",
  "gemini_model": "gemini-2.5-flash",
  "max_free_ai_requests": "5",
  "paywall_variant": "A"
}
```

## Flutter

```dart
// Analytics
import 'package:firebase_analytics/firebase_analytics.dart';

final analytics = FirebaseAnalytics.instance;
await analytics.logEvent(name: 'ai_prompt_sent', parameters: {'model': 'gpt-5.4-mini'});
await analytics.setUserId(id: uid);

// Remote Config
import 'package:firebase_remote_config/firebase_remote_config.dart';

final rc = FirebaseRemoteConfig.instance;
await rc.setDefaults({'ai_model': 'gpt-5.4-mini', 'max_free_requests': 5});
await rc.setConfigSettings(RemoteConfigSettings(
  fetchTimeout: const Duration(minutes: 1),
  minimumFetchInterval: kDebugMode ? Duration.zero : const Duration(hours: 1),
));
await rc.fetchAndActivate();

final model = rc.getString('ai_model');
final maxFree = rc.getInt('max_free_requests');
```

## Gotchas

- Remote Config values are cached. `fetch()` returns cached values if called within `minimumFetchIntervalMillis`. Always use `fetchAndActivate()` on startup — it fetches if the cache is stale.
- Set `minimumFetchIntervalMillis: 0` in dev only. Firebase throttles apps that fetch too frequently (max 5 times/hour in production).
- Remote Config has a limit of 300 parameters per project. Don't use it as a general-purpose database.
