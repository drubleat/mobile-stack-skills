---
title: "Release credentials and environment boundaries"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Release credentials and environment boundaries

Classify values by where they are used, not by the variable's name:

| Value | Intended location |
|---|---|
| Supabase URL/publishable key, RevenueCat platform public SDK key | Client-readable app configuration |
| AI provider key, RevenueCat secret REST key, Supabase secret/service-role key | Trusted backend secret store |
| Store signing/API credentials, Expo token, deployment token, DB password | Scoped protected CI/build/submit environment |

Anything embedded in JavaScript, native resources or app config is readable from the installed binary. EAS secret visibility protects handling on the build service; it cannot make bundled data secret. Non-EXPO_PUBLIC values can also leak if a config plugin writes them into the app.

Use current EAS environment-variable commands (`eas env:create`, `eas env:list`) with the selected environment and documented visibility. Keep public configuration distinct from backend credentials. Do not copy legacy `eas secret:create --env` commands. Pass secrets through environment bindings or protected files, never source-controlled command arguments or logs.

Before release: verify the exact commit/build, lockfiles, version counters, runtime policy, signing, backend environment and compatible migrations. Run relevant checks, test RLS with real roles and validate restore/purchase/account-deletion flows. Local `db reset` is for a disposable local database; it is not a generic staging validation command.

Submit the exact build ID, confirm processing and reviewer access, then follow the platform's rollout controls. Processing/review times are not guaranteed. Monitor crashes, auth failures, entitlement freshness and backend errors after release.

For rotation, create a replacement, update the actual consuming environment, verify use, then revoke the old credential. Do not spread backend keys into EAS merely to keep copies synchronized. Confirm whether the runtime requires restart/redeployment for the particular secret mechanism.

## Sources

Reviewed 2026-10-20: [EAS environment variables](https://docs.expo.dev/eas/environment-variables/), [Supabase secrets](https://supabase.com/docs/guides/functions/secrets).
