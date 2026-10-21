---
title: "Firebase — domain index"
impact: MEDIUM-HIGH
impactDescription: "Routes to setup, FCM, Crashlytics, Auth, Firestore, Analytics, Storage, App Distribution, and hybrid patterns"
tags: firebase, index
---

# Firebase domain index

Firebase provides a suite of services that complement (or replace) Supabase depending on the use case. This domain covers Firebase in two configurations:
- **Firebase-standalone**: no Supabase, using Firebase Auth + Firestore + FCM as the full backend.
- **Supabase + Firebase hybrid**: Supabase for auth/database/edge functions, Firebase added for Crashlytics, Analytics, FCM, or Remote Config.

Preserve the app's existing services. Native RN Firebase initializes its default app from platform config; Flutter initializes Firebase explicitly. File placement and plugins depend on the native/CNG workflow. Use the setup reference before adding services. App Check complements authentication and authorization; it does not replace them.

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
