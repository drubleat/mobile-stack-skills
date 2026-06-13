---
title: Cross-cutting gotchas
impact: CRITICAL
impactDescription: "High-impact issues that span multiple domains; each one has caused production incidents or days of debugging"
tags: playbooks, gotchas, debugging, production, security
---

# Cross-cutting gotchas

High-impact issues that span multiple domains and are easy to miss. Each one has caused production incidents or wasted days of debugging.

## 1. RevenueCat ↔ Supabase user ID drift

**The bug**: RC creates an anonymous user ID when the app first launches (before sign-in). If you call `purchasePackage()` while the user is anonymous, the webhook fires with the RC anonymous ID — not the Supabase UID. Your `subscriptions` table has no matching row, so the user's purchase is invisible to your backend.

**The fix**: always call `Purchases.logIn(supabaseUserId)` immediately after Supabase sign-in, before the user can reach any purchase flow:

```ts
supabase.auth.onAuthStateChange(async (event, session) => {
  if (session?.user) {
    await Purchases.logIn(session.user.id);
  }
});
```

This merges the anonymous user's purchase history with the identified user. Do this before any paywall can be reached.

**How to detect**: RC dashboard shows purchases under `$RCAnonymousID:...` instead of your UID. Check RC → Customer page and search for the Supabase UID.

## 2. CANCELLATION doesn't mean lost access

**The bug**: treating `CANCELLATION` webhook event as "subscription ended" and setting `is_active = false`. The user cancels but still has active access until the end of their paid period — and now they're locked out.

**The correct model**:
- `CANCELLATION` → set `cancelled_at`, keep `is_active = true`.
- `EXPIRATION` → set `is_active = false`.

The `CANCELLATION` event means "user won't renew" — not "subscription is over." Only `EXPIRATION` signals the paid period has ended.

See [../monetization/webhooks-supabase.md](../monetization/webhooks-supabase.md) for the full event table.

## 3. `useFrameworks: 'static'` missing for RN Firebase

**The bug**: adding any `@react-native-firebase/*` package and running `eas build` — the iOS build links Firebase as a dynamic framework and conflicts with React Native's static library linking. The pod install succeeds, but the archive step fails with `Multiple commands produce ...` or linker errors.

**The fix**: always add this to `app.config.ts` before the first build that includes RN Firebase:

```ts
['expo-build-properties', { ios: { useFrameworks: 'static' } }]
```

This affects ALL pods (not just Firebase). If another package requires dynamic linking, there's a conflict. The workaround is to use `expo-modules-core` with the framework setting — check Expo docs for the current guidance.

## 4. AI API key in the mobile bundle

**The bug**: setting `EXPO_PUBLIC_OPENAI_KEY=sk-...` and calling OpenAI directly from the client. The key is visible in the JS bundle — anyone with a decompiler can extract it and rack up your bill.

**The fix**: AI keys live ONLY in Supabase Edge Function secrets. The app calls `supabase.functions.invoke('ai-proxy')` — the Edge Function holds the key.

```bash
# Safe — server only
supabase secrets set OPENAI_API_KEY=sk-...

# NEVER in app.config.ts
EXPO_PUBLIC_OPENAI_API_KEY=sk-...  # ← this is in the bundle
```

## 5. Expo Go breaking native modules

**The bug**: adding a package with native code (Firebase, RevenueCat, anything requiring `npx expo install`), running `npx expo start`, and opening in Expo Go. The app crashes with "Native module not found" or the feature silently doesn't work.

**The rule**: Expo Go cannot load custom native modules. Any package that requires a config plugin or native code requires a development build:

```bash
eas build --profile development --platform ios
```

Once a native module is added, switch your team from Expo Go to dev builds. Never go back.

## 6. AVD lock files (Android emulator)

**The symptom**: Android emulator shows "This AVD is already running" even when it's not. Build hangs or metro fails to connect.

**The fix**:

```bash
rm ~/.android/avd/<avd-name>.avd/*.lock
```

Then restart the emulator. If it still hangs: `adb kill-server && adb start-server`.

## 7. Supabase `auth.uid()` without `select`

**The bug**: writing RLS policies using bare `auth.uid()`:

```sql
-- SLOW — re-evaluates for every row
using (user_id = auth.uid())
```

**The fix**: always wrap in `(select ...)`:

```sql
-- FAST — evaluates once per query
using (user_id = (select auth.uid()))
```

This is a correctness-by-default performance fix — it changes from O(rows) evaluation to O(1) per query. The difference is invisible on small tables and catastrophic on large ones.

## 8. Gemini `thinking_budget` → `thinking_level`

**The bug**: copying code from Gemini 2.5 docs or tutorials that uses `thinking_budget: 8000` (an integer). Gemini 3.5 removed this entirely — it now uses `thinking_level: 'high'` (a string enum: `'none'`, `'low'`, `'medium'`, `'high'`). The old parameter is silently ignored.

```ts
// Gemini 3.5 — CORRECT
generationConfig: { thinking_level: 'high' }

// Gemini 2.5 — silently ignored on 3.5
config: { thinking_config: { thinking_budget: 8000 } }
```

## 9. RevenueCat webhook endpoint needs `--no-verify-jwt`

**The bug**: deploying the RevenueCat webhook Edge Function without `--no-verify-jwt`. RevenueCat sends requests without a Supabase JWT, so the function returns 401 and never processes events. Subscriptions appear in RC dashboard but `subscriptions` table stays empty.

**The fix**:

```bash
supabase functions deploy revenuecat-webhook --no-verify-jwt
```

Validate identity with the RC webhook shared secret in the header instead of JWT.

## 10. Supabase new API key names (end of 2026)

The old `anon` and `service_role` key names are deprecated. New format: `sb_publishable_` (replaces `anon`) and `sb_secret_` (replaces `service_role`). Both work during the transition, but all new code should use the new names. Update env variables before the deprecation deadline.
