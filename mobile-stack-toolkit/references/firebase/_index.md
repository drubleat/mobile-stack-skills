---
title: Firebase — domain index
impact: MEDIUM-HIGH
impactDescription: "Routes to setup, FCM, Crashlytics, Auth, Firestore, Analytics, Storage, App Distribution, and hybrid patterns"
tags: firebase, index
---

# Firebase domain index

Firebase provides a suite of services that complement (or replace) Supabase depending on the use case. This domain covers Firebase in two configurations:
- **Firebase-standalone**: no Supabase, using Firebase Auth + Firestore + FCM as the full backend.
- **Supabase + Firebase hybrid**: Supabase for auth/database/edge functions, Firebase added for Crashlytics, Analytics, FCM, or Remote Config.

## When to use which

| Need | Firebase-standalone | Hybrid (Supabase + Firebase) |
|---|---|---|
| Database | Firestore | Supabase (Postgres) |
| Auth | Firebase Auth | Supabase Auth |
| Push notifications | FCM | FCM (Firebase excels here) |
| Crash reporting | Crashlytics | Crashlytics |
| Analytics | Firebase Analytics | Firebase Analytics |
| Feature flags | Remote Config | Remote Config or custom |
| AI / Gemini calls | Firebase AI Logic + App Check | Supabase Edge proxy |
| File storage | Firebase Storage | Supabase Storage |

**Verdict**: Supabase + Firebase hybrid is the most common production pattern — Supabase handles structured data + auth + payments orchestration, Firebase handles observability (Crashlytics, Analytics) and push (FCM). Firebase AI Logic is a legitimate alternative to Supabase Edge proxy for Gemini when you're Firebase-native.

## Non-negotiables

1. `google-services.json` (Android) and `GoogleService-Info.plist` (iOS) must be in the project root and referenced in `app.config.ts` config plugins.
2. `@react-native-firebase/messaging` requires `useFrameworks: 'static'` in `expo-build-properties` on iOS — without it, pods fail to link.
3. Always call `firebase.initializeApp()` (or FlutterFire's `Firebase.initializeApp()`) before any Firebase SDK call.

## Files in this domain

| Task | File |
|---|---|
| Project setup, CLI, config files, Firebase MCP | [setup-cli.md](setup-cli.md) |
| Firebase Auth — email, Google, Apple (+ google_sign_in 7.x guide) | [auth.md](auth.md) |
| Cloud Firestore — data model, security rules, queries | [firestore.md](firestore.md) |
| FCM push (React Native) | [fcm.md](fcm.md) |
| Crashlytics — crash reporting, custom keys, non-fatal logging | [crashlytics.md](crashlytics.md) |
| Analytics + Remote Config (incl. CLI template management) | [analytics-remote-config.md](analytics-remote-config.md) |
| **App Check — protect backend resources from unauthorized clients** | [app-check.md](app-check.md) |
| **Firebase AI Logic — call Gemini directly with App Check security** | [ai-logic.md](ai-logic.md) |
| App Distribution — beta testing builds | [app-distribution.md](app-distribution.md) |
| Firebase Storage | [storage.md](storage.md) |
| Supabase + Firebase hybrid architecture | [supabase-hybrid.md](supabase-hybrid.md) |
