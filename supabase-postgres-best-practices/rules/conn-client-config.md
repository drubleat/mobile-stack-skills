---
title: "Supabase client configuration — keys, timeouts, retries"
impact: HIGH
impactDescription: "Wrong key (secret vs publishable) or missing auth config causes silent RLS bypass or session loss"
tags: connections, client, supabase-js, auth, keys, configuration
---

# Supabase client configuration: keys, timeouts, retries

## Key hierarchy (2026 naming)

```
sb_publishable_...  ← client-safe; replacement for legacy JWT anon keys
sb_secret_...       ← server-only, bypasses RLS; replacement for legacy JWT service_role keys
```

**The `sb_secret_` key must never appear in client code, env vars prefixed `EXPO_PUBLIC_*`, or bundled JS.** It bypasses all RLS — exposure = full database read/write for anyone.

Opaque API keys are not user JWTs. Pass them as the SDK key / `apikey` header; use a user access token for bearer authentication. Review gateway configuration when migrating Edge Functions from legacy keys.

## Correct client init (React Native / Expo)

```ts
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const supabase = createClient(
  process.env.EXPO_PUBLIC_SUPABASE_URL!,
  process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
  {
    auth: {
      storage: AsyncStorage,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false, // required for React Native
    },
  }
);
```

## Edge Function client (server-side, with secret key)

```ts
// Deno Edge Function — secret key is safe here
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, // or SUPABASE_SECRET_KEY
  { auth: { persistSession: false } }
);
```

## Acting as the authenticated user in Edge Functions

```ts
// Prefer this over service key for user-scoped operations
const authHeader = req.headers.get('Authorization');
if (!authHeader?.startsWith('Bearer ')) return new Response('Unauthorized', { status: 401 });
const userClient = createClient(url, publishableKey, {
  global: { headers: { Authorization: authHeader } },
  auth: { persistSession: false },
});
const { data: { user }, error: authError } = await userClient.auth.getUser();
if (authError || !user) return new Response('Unauthorized', { status: 401 });
// Now queries run under the user's RLS context
const { data } = await userClient.from('messages').select('*');
```

## Realtime timeout / heartbeat config

```ts
export const supabase = createClient(url, key, {
  realtime: {
    timeout: 10000,     // 10s connect timeout
    heartbeatIntervalMs: 30000,
  },
});
```

## Network retries (supabase-js v2)

Retry behavior differs across Auth, Realtime and HTTP clients. Inspect the installed SDK and any query library before adding another layer. Retry only bounded transient failures on idempotent operations, with backoff/jitter and cancellation. Do not retry validation, authorization or quota failures blindly; honor Retry-After when appropriate. Retrying a write after a lost response can duplicate it, so use an idempotency key/unique constraint or reconcile the result first.

Reviewed 2026-10-21: [Supabase API keys](https://supabase.com/docs/guides/api/api-keys).
