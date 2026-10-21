---
title: "Expo bootstrap and project structure"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Expo bootstrap and project structure

Inspect an existing app's package.json, lockfile, app config and native directories before changing its stack. For a new app:

```bash
npx create-expo-app@latest my-app
cd my-app
npx expo install --check
npx expo-doctor
```

Scaffold defaults change during SDK transitions. Inspect the generated Expo/React Native/React versions and current release guide; do not promise a fixed SDK from `@latest`. Use an explicit supported template when needed. Keep lockfiles and choose the project's package manager consistently.

Use `expo install` for Expo/native dependencies with compatibility mappings; ordinary JS dependencies can use the package manager. It does not guarantee compatibility for every third-party package. Review `--fix` changes and rebuild after native changes.

Keep routes in `app/` or the project's existing `src/app/`, shared UI in components, feature logic in features, and configured clients in lib. Route groups organize navigation; they are not authorization. Use [architecture](architecture.md) for session lifecycle and [Expo Router](expo-router.md) for routing.

Dynamic app config should preserve nested settings:

```ts
import type { ConfigContext, ExpoConfig } from 'expo/config';
export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: config.name ?? 'MyApp',
  slug: config.slug ?? 'my-app',
  ios: { ...config.ios, bundleIdentifier: 'com.example.myapp' },
  android: { ...config.android, package: 'com.example.myapp' },
  extra: { ...config.extra, eas: { ...config.extra?.eas, projectId: 'EAS_PROJECT_ID' } },
});
```

`EXPO_PUBLIC_*` and values included in client config/bundles are public. Use them for publishable config only. Secret visibility in a build service cannot keep a value secret after code embeds it into an app. See [release secrets](../cicd/secrets-release.md). Confirm startup on the chosen [development build](native-dev-builds.md) and each target platform.

## Sources

Reviewed 2026-10-20: [create project](https://docs.expo.dev/get-started/create-a-project/), [app config](https://docs.expo.dev/workflow/configuration/).
