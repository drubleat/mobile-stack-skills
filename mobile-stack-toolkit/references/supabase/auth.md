---
title: "Auth: email/OTP + native Apple/Google sign-in"
impact: CRITICAL
impactDescription: "Session persistence bugs log users out silently; native sign-in misconfiguration blocks App Store approval"
tags: supabase, auth, oauth, apple, google, session
---

# Auth: email/OTP + native Apple/Google

## Contents
- [Client setup & session persistence](#client-setup--session-persistence)
- [Email + OTP](#email--otp)
- [Native sign-in (the production path)](#native-sign-in-the-production-path)
- [Reacting to auth state](#reacting-to-auth-state)
- [Pitfalls](#pitfalls)

## Client setup & session persistence

In React Native you **must** give supabase-js a storage adapter and start token auto-refresh tied to app foreground state:

```ts
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AppState } from 'react-native';

export const supabase = createClient(URL, PUBLISHABLE_KEY, {
  auth: {
    storage: AsyncStorage,
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: false,   // RN has no URL bar
  },
});

// Refresh only while app is active (prevents background token churn)
AppState.addEventListener('change', (s) => {
  s === 'active' ? supabase.auth.startAutoRefresh() : supabase.auth.stopAutoRefresh();
});
```

## Email + OTP

```ts
// Magic link / OTP code to email
await supabase.auth.signInWithOtp({ email });
// Verify the 6-digit code the user typed
await supabase.auth.verifyOtp({ email, token: code, type: 'email' });
// Classic password
await supabase.auth.signInWithPassword({ email, password });
```

OTP (code or magic link) avoids password storage entirely and is the lowest-friction email option for mobile.

## Native or browser sign-in

Choose a documented flow supported by the target platform. Native Google/Apple token exchange and browser OAuth are both valid production approaches. Configure provider IDs, native signing/capabilities and redirect allowlists before testing.

Modern React Native Google Sign-In returns a discriminated result; check success/cancellation and a non-null `result.data.idToken` before calling Supabase `signInWithIdToken`. For Apple, follow the platform's nonce contract: fresh cryptographic raw nonce, SHA-256 hash in the Apple request where required, and raw nonce in Supabase verification. Do not assert non-null tokens after a cancelled request.

Apple login requirements have conditions/exceptions; see [store checks](../store/rejection-redflags.md). Use [Supabase native sign-in guidance](https://supabase.com/docs/guides/auth/social-login/auth-apple) and the installed provider SDK's API rather than mixing version-specific snippets.

## Reacting to auth state

Drive your UI off the subscription, not a one-shot `getSession`:

```ts
const { data: { subscription } } =
  supabase.auth.onAuthStateChange((_event, session) => setSession(session));
// remember to subscription.unsubscribe() on unmount
```

Feed this into the root-layout auth gate → [../expo/architecture.md](../expo/architecture.md). Create a `profiles` row on first sign-in via a DB trigger → [schema-design.md](schema-design.md).

## Pitfalls

- **Session lost on restart** → missing `storage: AsyncStorage` / `persistSession`.
- **Token silently expires** → forgot the `AppState` auto-refresh wiring above.
- **Login policy mismatch** → check the applicable platform rules and exceptions → [../store/rejection-redflags.md](../store/rejection-redflags.md).
- **Google "DEVELOPER_ERROR"** → wrong/missing SHA-1 (Android) or using the Android client ID instead of the **web** client ID for `signInWithIdToken`.
- **Deep-link redirect not returning** (web OAuth flow) → scheme/redirect URL mismatch; another reason to prefer the native flow.

Retain/remove AppState listeners and initialize refresh from the current app state. Check auth errors, handle session-restoration loading, and avoid awaiting another Supabase auth operation inside the auth-state callback. Never treat a client session object as server verification.
