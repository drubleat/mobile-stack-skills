---
title: "Expo — domain index"
impact: MEDIUM-HIGH
impactDescription: "Routes to bootstrap, architecture, EAS Build, dev builds, OTA updates, and troubleshooting"
tags: expo, react-native, index
---

# Expo & EAS — index

Everything about scaffolding, building, shipping JS updates, and debugging the local toolchain. Pick the file that matches your task.

## Router

| Task | File |
|---|---|
| Start a project, select a compatible SDK, lay out folders & expo-router | [bootstrap-structure.md](bootstrap-structure.md) |
| Understand Expo Go vs Dev Build, `prebuild`, config plugins, native modules | [native-dev-builds.md](native-dev-builds.md) |
| Configure `eas.json`, run cloud/local builds, manage credentials | [eas-build.md](eas-build.md) |
| Ship JS-only updates over the air (channels, runtime version, rollbacks) | [ota-updates.md](ota-updates.md) |
| App structure: state management, navigation, auth gating | [architecture.md](architecture.md) |
| File-based navigation deep dive: routes, params, modals, Stack.Protected auth | [expo-router.md](expo-router.md) |
| Build forms with validation (react-hook-form + zod) | [forms-validation.md](forms-validation.md) |
| Pick, compress & upload images to Supabase Storage; render with caching | [image-pipeline.md](image-pipeline.md) |
| Fix emulator/simulator problems (ADB lock, "device offline", pods) | [troubleshooting.md](troubleshooting.md) |
| Use Tailwind utility classes in React Native (NativeWind v4) | [nativewind.md](nativewind.md) |
| Fetch, cache, and sync server data (TanStack Query v5) | [tanstack-query.md](tanstack-query.md) |
| Client-side state management + fast persistence (Zustand + MMKV) | [zustand-mmkv.md](zustand-mmkv.md) |
| Crash & error monitoring — alternative to Crashlytics (Sentry) | [sentry.md](sentry.md) |
| Product analytics & feature flags — alternative to Firebase (PostHog) | [posthog.md](posthog.md) |

For store submission don't look here → [../store/_index.md](../store/_index.md). For CI builds → [../cicd/eas-workflows.md](../cicd/eas-workflows.md).

## Native compatibility

Use Expo Go only when the required native modules/configuration are already included. Custom native changes require a development build. `expo run:*` builds locally; `eas build` builds a binary; `eas update` publishes compatible JS/assets. App icons and other native config require a binary rebuild. See the focused guides above.
