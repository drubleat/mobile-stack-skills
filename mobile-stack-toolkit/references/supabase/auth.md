---
title: Auth: email/OTP + native Apple/Google sign-in
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

## Native sign-in (the production path)

For Apple and Google, prefer **native sign-in → `signInWithIdToken`** over the web OAuth redirect. The native flow gives the real OS sheet, no browser bounce, and works reliably in a Dev Build. (The `signInWithOAuth` + `expo-auth-session` web flow is fine for quick prototypes, but is clunkier in production.)

**Apple** (required on iOS if you offer any other social login — App Store guideline):

```ts
import * as AppleAuthentication from 'expo-apple-authentication';

const cred = await AppleAuthentication.signInAsync({
  requestedScopes: [AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
                    AppleAuthentication.AppleAuthenticationScope.EMAIL],
});
await supabase.auth.signInWithIdToken({ provider: 'apple', token: cred.identityToken! });
```

**Google** (via `@react-native-google-signin/google-signin`, needs a Dev Build):

```ts
import { GoogleSignin } from '@react-native-google-signin/google-signin';
GoogleSignin.configure({ webClientId: '<web-client-id>' });
const { data } = await GoogleSignin.signIn();
await supabase.auth.signInWithIdToken({ provider: 'google', token: data.idToken! });
```

Configure the matching provider client IDs in the Supabase dashboard (Auth → Providers). Apple requires the Sign in with Apple capability + a Services ID; Google requires the **web** client ID for token verification even on native.

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
- **Apple rejection** → you ship Google login but not Apple; Apple requires Sign in with Apple when other third-party logins exist → [../store/rejection-redflags.md](../store/rejection-redflags.md).
- **Google "DEVELOPER_ERROR"** → wrong/missing SHA-1 (Android) or using the Android client ID instead of the **web** client ID for `signInWithIdToken`.
- **Deep-link redirect not returning** (web OAuth flow) → scheme/redirect URL mismatch; another reason to prefer the native flow.
