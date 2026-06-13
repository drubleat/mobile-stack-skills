---
title: Sentry — crash & error monitoring for Expo/React Native
impact: MEDIUM-HIGH
impactDescription: "Sentry catches JS and native crashes with stack traces and breadcrumbs; without it, production crashes are invisible"
tags: sentry, crash-reporting, error-monitoring, expo, react-native, observability
---

# Sentry — Expo / React Native

Sentry captures JS exceptions, native crashes (iOS/Android), performance traces, and breadcrumbs. It's the alternative to Firebase Crashlytics for teams not using Firebase, or a complement when you want richer error context.

**Package:** `@sentry/react-native`  
**Requires:** Expo SDK 50+ (older Expo uses the deprecated `sentry-expo` package)

---

## Install — use the wizard

The wizard installs the package, adds the Expo config plugin, patches Metro, sets up Android Gradle, adds iOS build phases, and handles auth tokens.

```bash
npx @sentry/wizard@latest -i reactNative
```

This is the correct path. Do not install manually first — the wizard may overwrite conflicting config.

The wizard will:
1. Prompt for your Sentry org/project
2. Add `@sentry/react-native` to `package.json`
3. Add the plugin to `app.json`
4. Create/patch `metro.config.js`
5. Ask to store your Sentry auth token in `.env.local`

---

## app.json plugin

After the wizard runs, this is in your `app.json`:

```json
{
  "expo": {
    "plugins": [
      [
        "@sentry/react-native/expo",
        {
          "url": "https://sentry.io/",
          "project": "your-project-slug",
          "organization": "your-org-slug"
        }
      ]
    ]
  }
}
```

---

## Initialize Sentry

For **Expo Router**, initialize before the root layout and wrap the component with `Sentry.wrap`:

```tsx
// app/_layout.tsx
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: 'https://<key>@o<orgId>.ingest.sentry.io/<projectId>',
  tracesSampleRate: 1.0,      // 1.0 = 100% in dev; lower in prod (0.1–0.2)
  profilesSampleRate: 1.0,    // optional profiling
  enabled: !__DEV__,          // disable in dev to avoid noise
  environment: __DEV__ ? 'development' : 'production',
  sendDefaultPii: true,
});

function RootLayout() {
  return <Stack />;
}

export default Sentry.wrap(RootLayout);
```

Store the DSN in your Expo config or as an env var — it's not secret but should be per-environment.

---

## Auth token for EAS builds

For EAS cloud builds, add the auth token as an EAS secret:

```bash
eas secret:create --scope project --name SENTRY_AUTH_TOKEN --value <token>
```

For local builds, keep it in `.env.local` (wizard sets this up):

```
SENTRY_AUTH_TOKEN=sntrys_xxx
```

---

## Capture errors manually

```ts
import * as Sentry from '@sentry/react-native';

// Capture an error with context
try {
  await riskyOperation();
} catch (err) {
  Sentry.captureException(err, {
    tags: { feature: 'ai-chat' },
    extra: { userId: user.id },
  });
}

// Capture a message (non-error)
Sentry.captureMessage('User reached step 3 of onboarding', 'info');
```

---

## Identify users

Set user context so errors are linked to specific users:

```ts
// After login
Sentry.setUser({
  id: user.id,
  email: user.email,
});

// On logout
Sentry.setUser(null);
```

---

## Breadcrumbs

Add manual breadcrumbs to trail events leading to a crash:

```ts
Sentry.addBreadcrumb({
  category: 'navigation',
  message: 'User navigated to /checkout',
  level: 'info',
});
```

---

## Error boundary (React)

Wrap screens or features to catch rendering errors:

```tsx
import * as Sentry from '@sentry/react-native';

export function FeatureScreen() {
  return (
    <Sentry.ErrorBoundary
      fallback={<Text>Something went wrong. We've been notified.</Text>}
      onError={(error) => console.error(error)}
    >
      <MyFeature />
    </Sentry.ErrorBoundary>
  );
}
```

---

## Performance tracing

Sentry can trace slow screens. With `tracesSampleRate > 0`, Sentry auto-instruments React Navigation / Expo Router navigation transactions.

Manual spans:

```ts
const span = Sentry.startSpan({ name: 'ai-inference' }, async (span) => {
  const result = await callAI();
  return result;
});
```

---

## vs Firebase Crashlytics

| | Sentry | Firebase Crashlytics |
|---|---|---|
| JS exceptions | ✅ Full stack trace | ✅ |
| Native crashes | ✅ | ✅ |
| Performance | ✅ Traces + profiling | ⚠️ Basic (APM separate) |
| Breadcrumbs | ✅ Rich | ⚠️ Limited |
| Error grouping | ✅ Advanced (fingerprinting) | ✅ |
| Requires Firebase | ❌ | ✅ |
| Pricing | Free (5k errors/month) | Free (unlimited) |

Choose Crashlytics if you're already fully on Firebase. Choose Sentry if you want richer debug context, non-Firebase apps, or performance tracing.

---

## Gotchas

- **Do not use `sentry-expo`** — deprecated in 2024. The correct package is `@sentry/react-native` with the expo plugin.
- **`Sentry.wrap(RootLayout)` is required for Expo Router** — without it, unhandled promise rejections are not captured.
- **`enabled: !__DEV__`** is recommended — dev errors pollute your Sentry project and waste event quota.
- **Source maps upload automatically** during `eas build`. For local builds, the auth token in `.env.local` triggers upload on `expo export`.
- **`tracesSampleRate: 1.0` in production** can get expensive at scale — lower to 0.1 before launch.
