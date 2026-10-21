---
name: mobile-stack-toolkit
description: Build, debug, or ship Expo/React Native and Flutter apps, including mobile auth, subscriptions, AI, push notifications, and store releases. Use for mobile integration work; use the Postgres skill for standalone SQL tuning.
metadata:
  version: "1.1.0"
  author: "Eren Öz"
---

# Mobile Stack Toolkit

## Working approach

- Inspect the existing framework, manifests, lockfiles, native folders, and repository instructions before choosing commands. Preserve the user's stack and scope; a feature request does not authorize adding an entire backend, payment system, or deployment.
- Read the matching domain index, then only the leaf reference needed for the immediate task. Start with one or two leaves; expand when a dependency or unresolved issue requires it. Do not preload every high-impact reference.
- Treat version numbers in examples as historical baselines, not current recommendations. Verify the affected API against official documentation and the installed version before changing dependencies, model IDs, prices, or store requirements. Record the source and date when updating a reference.
- Keep a compact continuation note for long work: objective, decisions, changed files, validation, unresolved issues, next action. Do not duplicate full reference text or logs.
- A partial code example is a pattern, not a deployable application. Resolve its imports, authorization, error handling, and configuration before use; test the changed behavior.

## Routing

| Task | Read |
|---|---|
| Expo setup, builds, routing, state, OTA, debugging | [Expo index](references/expo/_index.md) |
| Supabase auth, schema, RLS, storage, functions | [Supabase index](references/supabase/_index.md) |
| Mobile AI integration, streaming, structured output, tools | [AI index](references/ai/_index.md) |
| RevenueCat, paywalls, server entitlements, Superwall | [Monetization index](references/monetization/_index.md) |
| Expo Push, FCM, APNs, notification deep links | [Push index](references/push/_index.md) |
| Firebase setup, Auth, Firestore, App Check, diagnostics | [Firebase index](references/firebase/_index.md) |
| Flutter setup, UI, navigation, networking, integrations | [Flutter index](references/flutter/_index.md) |
| A specific Dart/Flutter package | [Package index](references/packages/_index.md) |
| App Store / Play submission and privacy | [Store index](references/store/_index.md) |
| CI, releases, migration deployment, Maestro | [CI/CD index](references/cicd/_index.md) |
| A complete new app or cross-component diagnosis | [Playbook index](references/playbooks/_index.md) |

If the exact leaf is already known, open it directly and skip the index. The standalone `supabase-postgres-best-practices` skill can provide deeper SQL guidance when installed; this skill must still work without it.

## Integration boundaries

- Keep provider secret keys and Supabase privileged keys on a trusted server. Public client keys still need RLS, rules, and service-specific authorization. EAS secret visibility does not prevent a value from leaking if build code embeds it in the app.
- Use the existing trusted backend for AI. Firebase AI Logic with App Check or a provider's short-lived client credential can be appropriate; never embed a long-lived provider secret in the app.
- Verify user identity before privileged work. Server-side paid actions require server-verified entitlement state; local UI gates are only presentation.
- A development build is needed for native modules absent from Expo Go. Rebuild for native changes; OTA must match the installed native runtime.
- Respect current authorization before deployments, store releases, paid operations, or destructive migrations. Report checks actually run and any platform or service behavior that remains untested.
