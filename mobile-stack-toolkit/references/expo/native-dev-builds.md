---
title: Expo Go vs Dev Builds, prebuild & config plugins
impact: HIGH
impactDescription: "Switching from Expo Go to Dev Build is required the moment any native module is added; not understanding this costs hours"
tags: expo, dev-builds, prebuild, config-plugins, native
---

# Expo Go vs Dev Builds, prebuild & config plugins

## The core distinction

- **Expo Go** — a prebuilt sandbox app on the stores. It contains a fixed set of native modules. You can run *only* JS that depends on those modules. Great for prototypes and learning.
- **Development Build (Dev Build)** — *your own* debug build that includes `expo-dev-client` plus whatever native modules you added. It looks like Expo Go (dev menu, loads from Metro) but it's yours, so any native dependency works.

**The moment you install a library with native code, Expo Go can no longer run your app.** You'll see a red error about a missing native module. The fix is never "downgrade" — it's "move to a Dev Build." For this toolkit, RevenueCat and RN Firebase both force this, so expect to be on Dev Builds for essentially every real project.

## Making a Dev Build

```bash
npx expo install expo-dev-client
eas build --profile development --platform ios      # or android / all
```

Once installed, `npx expo start` automatically targets the Dev Build instead of Expo Go (it prints "Using development build"). Install the resulting build on a simulator/device once; after that you only rebuild when **native** code changes — JS changes still hot-reload from Metro.

For purely local debug builds without EAS: `npx expo run:ios` / `npx expo run:android` (needs Xcode / Android Studio installed).

## Prebuild & Continuous Native Generation (CNG)

Expo's managed flow doesn't keep `ios/` and `android/` folders in your repo. Instead, **prebuild** generates them on demand from your `app.config.ts` + config plugins. This is "Continuous Native Generation" — native projects are an *output*, not source.

- `eas build` and `npx expo run:*` **auto-run prebuild** when no native folders exist. You usually never type `prebuild` yourself.
- Run `npx expo prebuild --clean` manually when you want to regenerate native folders after changing native config/plugins, or to inspect generated native code.
- **Don't commit `ios/`/`android/`** unless you've deliberately gone "bare." Committing them while also using plugins leads to drift where plugin changes silently don't apply. Keep them in `.gitignore` and let CNG own them.

## Config plugins — how native config happens without writing native code

A **config plugin** is a function that mutates the native project during prebuild (adds permissions, entitlements, Gradle/Pod deps, `Info.plist` keys, etc.). You add them to the `plugins` array:

```ts
plugins: [
  'expo-router',
  '@react-native-firebase/app',
  '@react-native-firebase/messaging',
  ['expo-build-properties', { ios: { useFrameworks: 'static' } }],
  ['expo-camera', { cameraPermission: 'We use the camera to scan receipts.' }],
]
```

Notes:
- A plugin entry is either a string (no options) or `[name, optionsObject]`.
- Permission strings set here become the `Info.plist`/manifest entries the stores require — see [../store/permissions-privacy.md](../store/permissions-privacy.md).
- RN Firebase requires `expo-build-properties` with `useFrameworks: 'static'` on iOS; this is a classic "build fails until you add it" gotcha → [../push/fcm-setup.md](../push/fcm-setup.md).

## When to go "bare" (eject)

Almost never. Modern config plugins cover the vast majority of native customization. Only adopt bare workflow if you must hand-edit native code that no plugin exposes, and accept that you now maintain `ios/`/`android/` yourself. Prefer writing a **local config plugin** (a small JS file in your repo) over ejecting.

## Quick decision

| Situation | Do this |
|---|---|
| Pure JS / Expo SDK modules only | Expo Go is fine |
| Added any native dependency | Dev Build (`expo-dev-client` + `eas build --profile development`) |
| Build fails after adding a native lib | Check its config plugin + `expo-build-properties`; `prebuild --clean` |
| Need to read generated native code | `npx expo prebuild --clean`, inspect, but keep folders gitignored |

Next: configure build profiles → [eas-build.md](eas-build.md).
