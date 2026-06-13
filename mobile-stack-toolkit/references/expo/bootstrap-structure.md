---
title: Bootstrap & project structure
impact: HIGH
impactDescription: "Correct folder layout and app.json config prevents native build failures and config plugin conflicts"
tags: expo, scaffold, project-structure, expo-router
---

# Bootstrap & project structure

## Scaffold

```bash
npx create-expo-app@latest my-app            # Expo Go-friendly SDK (currently 54)
npx create-expo-app@latest my-app --template default@sdk-56   # latest SDK 56
```

**SDK 54 vs 56 trap (June 2026):** `create-expo-app@latest` *without* a template still scaffolds **SDK 54**, because Expo Go on the stores tracks the SDK that the public Expo Go app supports. **SDK 56** (RN 0.85, React 19.2) is current but you reach it with `--template default@sdk-56`. If you'll add native modules anyway (you will), pick 56 and plan for Dev Builds — Expo Go compatibility stops mattering.

The default template already includes **expo-router** (file-based routing) and TypeScript. Don't fight it; embrace file-based routing.

## Install dependencies the right way

Always `npx expo install <pkg>` instead of `npm install <pkg>`. `expo install` pins versions that are **compatible with your SDK**; raw `npm install` pulls `latest` and silently breaks the native build. Run `npx expo install --check` / `--fix` to audit drift.

## Folder structure (opinionated, scales well)

```
my-app/
├── app/                      # expo-router routes — the URL map of your app
│   ├── (auth)/               # route group: login, signup (no URL segment)
│   ├── (tabs)/               # route group: the main tab navigator
│   │   ├── _layout.tsx       # <Tabs> definition
│   │   └── index.tsx         # first tab
│   ├── _layout.tsx           # root layout: providers + auth gate live here
│   └── +not-found.tsx
├── components/               # dumb, reusable UI
├── features/                 # optional: feature-sliced (chat/, paywall/, ...)
├── lib/                      # singletons & clients
│   ├── supabase.ts
│   ├── revenuecat.ts
│   └── ai.ts                 # thin client that calls your Edge Function
├── hooks/                    # useUser, useEntitlement, ...
├── constants/                # theme, colors, config
├── supabase/                 # migrations/ and functions/ (if using Supabase)
├── assets/
├── app.config.ts             # dynamic config (see below)
├── eas.json
└── tsconfig.json             # set up the "@/*" path alias
```

**Route groups** `(name)/` organize files without adding a URL segment — perfect for separating an authenticated stack from the auth screens. Put the auth redirect logic in the root `app/_layout.tsx`; see [architecture.md](architecture.md).

## `app.config.ts` over `app.json`

Switch to a dynamic **`app.config.ts`** as soon as you need env-driven values (different bundle IDs per build profile, plugin args, secrets wiring). It's plain TypeScript that returns the config object, so you can read `process.env`:

```ts
export default ({ config }) => ({
  ...config,
  name: process.env.APP_VARIANT === 'dev' ? 'MyApp (Dev)' : 'MyApp',
  ios: { bundleIdentifier: 'com.you.myapp' },
  android: { package: 'com.you.myapp' },
  extra: { easProjectId: 'your-eas-project-id' },
  plugins: ['expo-router', 'expo-secure-store', /* native plugins */],
});
```

## Env vars

- `EXPO_PUBLIC_*` vars are **inlined into the JS bundle** — readable by anyone with the APK/IPA. Use only for non-secrets (Supabase URL + anon key, RevenueCat public key).
- Real secrets never touch the client. They live in Edge Function secrets / EAS Secrets — see [../cicd/secrets-release.md](../cicd/secrets-release.md).
- For build-time env across profiles, use **EAS Environment Variables** (`eas env:create`) rather than committing `.env` files.

## What "done with bootstrap" looks like

You can `npx expo start`, open the app (Expo Go or a Dev Build), see the router working, and `lib/supabase.ts` (or whichever backend client you chose) is initialized. Next: pick your build flow → [native-dev-builds.md](native-dev-builds.md).
