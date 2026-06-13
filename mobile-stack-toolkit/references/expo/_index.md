---
title: Expo — domain index
impact: MEDIUM-HIGH
impactDescription: "Routes to bootstrap, architecture, EAS Build, dev builds, OTA updates, and troubleshooting"
tags: expo, react-native, index
---

# Expo & EAS — index

Everything about scaffolding, building, shipping JS updates, and debugging the local toolchain. Pick the file that matches your task.

## Router

| Task | File |
|---|---|
| Start a project, choose SDK 54 vs 56, lay out folders & expo-router | [bootstrap-structure.md](bootstrap-structure.md) |
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

## The one decision that drives everything

**Are you using any library with native code?** (RevenueCat, RN Firebase, anything touching `ios/`/`android/`.)

- **No** → Expo Go works; you can stay in the managed flow with zero native builds.
- **Yes** → Expo Go is dead for you. You need a **Dev Build** (`expo-dev-client`) for development and EAS builds for distribution. This is the normal state for any real production app. Details: [native-dev-builds.md](native-dev-builds.md).

Almost every app in this toolkit (RevenueCat + push) lands in the "Yes" bucket, so plan for Dev Builds from day one.

## Mental model of the three "build" verbs

- **`npx expo run:ios|android`** — compiles a debug build *on your machine*. Needs Xcode/Android Studio locally. Auto-runs `prebuild` if no native folders exist.
- **`eas build`** — compiles in the cloud (or locally with `--local`). This is what produces installable/submittable artifacts.
- **`eas update`** — ships **JS/asset-only** changes to already-installed builds. No native compile, no store review. Cannot change native code.

Knowing which verb applies to a change saves hours: a new icon or screen → `eas update`; a new native module → rebuild with `eas build` and bump the runtime version.
