---
title: "PostHog analytics and feature flags"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# PostHog analytics and feature flags

Install the React Native SDK and platform-compatible peer dependencies. Configure the correct ingestion host/project key; the ingestion key is client-readable, while personal/admin keys stay server-side.

```tsx
import { PostHogProvider } from 'posthog-react-native';
<PostHogProvider
  apiKey={publicProjectKey}
  options={{ host: ingestionHost }}
  autocapture={{ captureTouches: false, captureScreens: false }}
>
  <AppContent />
</PostHogProvider>
```

`autocapture` is a provider prop in this integration, not an invented nested client option. Follow the installed SDK/navigation guide for screen capture; normalize route names and avoid recording IDs/query strings. Session replay, native crash capture and other optional modules have their own setup and privacy controls.

Use `usePostHog()` for explicit events. Distinguish a purchase-button tap from a verified purchase. Identify only when the intended authenticated identity is ready, include approved properties, and reset on logout. Configure consent/collection before emitting events; do not assume an opt-out toggle alone satisfies every privacy requirement.

Feature flags can be undefined while loading or offline. Render a safe fallback; do not accidentally recursively return the same component from its enabled branch. Flags govern presentation, not paid backend authorization. Test account changes, offline cached flags and stale rollout values.

Check current pricing/limits separately instead of embedding a free-tier guarantee in an implementation guide.

## Sources

Reviewed 2026-10-20: [PostHog React Native](https://posthog.com/docs/libraries/react-native).
