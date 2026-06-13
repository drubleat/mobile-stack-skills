---
name: mobile-stack-toolkit
version: "1.0.0"
author: Eren Öz <eren@qoodly.com>
description: >-
  Production-grade playbook for shipping AI-first mobile apps with Expo (React
  Native) or Flutter, Supabase, RevenueCat, and Firebase. Use this whenever the
  task involves building, scaffolding, or extending a mobile app and mentions any
  of: Expo / React Native / EAS, Flutter, Supabase (Postgres, Auth, Edge
  Functions, RLS, Realtime, Storage), RevenueCat or in-app purchases /
  subscriptions / paywalls, push notifications (Expo Notifications / FCM / APNs),
  AI features via OpenAI or Gemini, App Store / Play Store submission, or mobile
  CI/CD. Triggers on requests like "build an Expo + Supabase app with a paywall",
  "add RevenueCat subscriptions", "set up push notifications", "call OpenAI safely
  from a mobile app", or "submit my app to the App Store". Gives the correct
  2025-2026 order, commands, and current SDK versions, and routes to deep
  reference files per topic.
---

# Mobile Stack Toolkit

A battle-tested stack and step order for going from PRD to App Store in weeks, optimized for **AI-first, paywalled, indie/agency mobile apps**. This file is the map: read the relevant section, then jump to the linked reference for depth.

## Stack philosophy (the default, opinionated choices)

| Layer | Default | When to deviate |
|---|---|---|
| **Frontend** | **Expo (React Native)**, managed + EAS Build, expo-router | Flutter only if the client/team mandates it or you need heavy pixel-perfect custom rendering → see [flutter/](references/flutter/project-setup.md) |
| **Backend/DB** | **Supabase** (Postgres + Auth + Edge Functions + Storage + Realtime) | — |
| **Push + crash** | **Firebase** (FCM + Crashlytics) | Expo Push API is fine for simple cases; see [push/_index.md](references/push/_index.md) |
| **Monetization** | **RevenueCat** (`react-native-purchases` v10) | — |
| **AI layer** | OpenAI / Gemini, **always via Supabase Edge Functions** — never call model APIs directly from the client | Never. Client-side keys = leaked keys. See [ai/edge-proxy-architecture.md](references/ai/edge-proxy-architecture.md) |

**Golden rule:** the client holds only public keys (Supabase anon key, RevenueCat public SDK key). Every secret (model API keys, RevenueCat webhook secret, Supabase service role key) lives in an Edge Function.

## Verified current versions (June 2026 — re-check before pinning)

- **Expo SDK 56** (React Native 0.85, React 19.2). `create-expo-app@latest` still scaffolds **SDK 54** by default for Expo Go compatibility; pass `--template default@sdk-56` for SDK 56.
- **RevenueCat** `react-native-purchases` **v10.2.x**, paywalls via `react-native-purchases-ui`.
- **OpenAI** `gpt-5.5` (frontier), `gpt-5.4-mini` / `gpt-5.4-nano` (cheap/fast).
- **Gemini** `gemini-3.5-flash` (flagship), `gemini-2.5-flash-lite` (cheapest).
- **Supabase** Edge Functions on Deno-based Edge Runtime (`Deno.serve` handler).

> Exact model IDs and minor SDK versions belong in the topic reference files, which are verified at write time.

## Decision tree → where to go

**Starting a brand-new project?** → run Bootstrap below, then follow the [Build order](#build-order). Want the full guided sequence? → [playbooks/zero-to-store.md](references/playbooks/zero-to-store.md). Building the canonical AI-first paywalled app? → [playbooks/ai-app-recipe.md](references/playbooks/ai-app-recipe.md).

**Adding a capability to an existing app?** Jump straight to the topic:

| You want to… | Go to |
|---|---|
| Set up builds, dev clients, EAS, OTA, fix emulator issues | [expo/_index.md](references/expo/_index.md) |
| Structure the app, state management, navigation/auth gating | [expo/architecture.md](references/expo/architecture.md) |
| Set up DB, auth, RLS, Edge Functions, Realtime, Storage | [supabase/_index.md](references/supabase/_index.md) |
| Add AI features safely (OpenAI/Gemini, streaming, tools) | [ai/_index.md](references/ai/_index.md) |
| Add subscriptions / paywalls / entitlements | [monetization/_index.md](references/monetization/_index.md) |
| Add push notifications | [push/_index.md](references/push/_index.md) |
| Submit to App Store / Play Store | [store/_index.md](references/store/_index.md) |
| Automate builds & deploys (CI/CD) | [cicd/eas-workflows.md](references/cicd/eas-workflows.md) |
| E2E test the real app UI (Maestro flows) | [cicd/maestro.md](references/cicd/maestro.md) |
| Do any of the above in **Flutter** | [flutter/project-setup.md](references/flutter/project-setup.md) |
| Debug a weird cross-component issue | [playbooks/cross-cutting-gotchas.md](references/playbooks/cross-cutting-gotchas.md) |

## Bootstrap (new Expo project)

```bash
# Scaffold (omit the template for an Expo Go-compatible SDK 54 app)
npx create-expo-app@latest my-app --template default@sdk-56
cd my-app

# Core dependencies — always use `expo install` so versions match the SDK
npx expo install @supabase/supabase-js @react-native-async-storage/async-storage
npx expo install react-native-purchases react-native-purchases-ui
npx expo install expo-notifications expo-router expo-secure-store

# Backend
npm i -g supabase            # or use npx supabase
supabase init
```

Anything needing native code (RevenueCat, RN Firebase, many others) means **Expo Go no longer works** — you need a Dev Build. See [expo/native-dev-builds.md](references/expo/native-dev-builds.md).

## Recommended folder structure

```
my-app/
├── app/                  # expo-router routes (file-based). (auth)/ and (tabs)/ groups
├── components/           # reusable UI
├── lib/                  # clients & singletons: supabase.ts, revenuecat.ts, ai.ts
├── hooks/                # useUser, useEntitlement, useCustomerInfo, ...
├── constants/            # theme, config
├── supabase/
│   ├── migrations/       # SQL migrations (version-controlled schema)
│   └── functions/        # Edge Functions (ai-proxy, revenuecat-webhook, send-push)
├── assets/
├── app.config.ts         # dynamic config + plugins + env wiring
└── eas.json              # build profiles
```

## Env / secrets — who sees what

| Secret | Where it lives | Exposed to client? |
|---|---|---|
| Supabase URL + **publishable** key (`sb_publishable_…`, was `anon`) | `app.config.ts` / `EXPO_PUBLIC_*` | ✅ Yes (RLS protects data) |
| Supabase **secret** key (`sb_secret_…`, was `service_role`) | Edge Function secret only | ❌ Never |
| RevenueCat **public SDK** key (per platform) | client (`Purchases.configure`) | ✅ Yes (public by design) |
| RevenueCat **webhook** auth header / secret | Edge Function secret | ❌ Never |
| OpenAI / Gemini API key | Edge Function secret (`supabase secrets set`) | ❌ Never |
| Firebase config (`google-services.json`, `GoogleService-Info.plist`) | committed/native config | ✅ Client (not secret) |
| EAS project ID | `app.config.ts` | ✅ Yes |

`EXPO_PUBLIC_`-prefixed vars are bundled into the client — **never** put a real secret there. Server secrets go to EAS Secrets / Supabase secrets / GitHub Secrets — see [cicd/secrets-release.md](references/cicd/secrets-release.md).

## Build order

Build in this order; each step assumes the previous one works:

1. **Schema + migrations** — `profiles`, `subscriptions`, feature tables → [supabase/schema-design.md](references/supabase/schema-design.md)
2. **Auth** + RLS (owner-based access) → [supabase/auth.md](references/supabase/auth.md), [supabase/rls-policies.md](references/supabase/rls-policies.md)
3. **Core feature loop** (the thing the app is for), including AI via Edge Functions → [ai/_index.md](references/ai/_index.md)
4. **Paywall** + entitlements + RevenueCat→Supabase webhook → [monetization/_index.md](references/monetization/_index.md)
5. **Push notifications** → [push/_index.md](references/push/_index.md)
6. **CI/CD** → [cicd/eas-workflows.md](references/cicd/eas-workflows.md)
7. **Store submission** → [store/_index.md](references/store/_index.md)

## Cross-cutting gotchas (the ones that burn weeks)

- **Adding a native module breaks Expo Go.** Switch to a Dev Build the moment you add RevenueCat / RN Firebase / any native dep.
- **RevenueCat ↔ Supabase drift.** Treat the RevenueCat webhook as the source of truth for `subscriptions`; never trust client-reported entitlement state for server gating.
- **AI key leakage.** A key in the bundle is a public key. All model calls go through an Edge Function with per-user rate limiting.
- **Android emulator stale state** (lock files, "device offline") after a crash — see the cleanup recipe in [expo/troubleshooting.md](references/expo/troubleshooting.md).

Full list with fixes: [playbooks/cross-cutting-gotchas.md](references/playbooks/cross-cutting-gotchas.md).
