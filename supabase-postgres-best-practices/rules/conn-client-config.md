---
title: Supabase client configuration — keys, timeouts, retries
impact: HIGH
impactDescription: "Wrong key (secret vs publishable) or missing auth config causes silent RLS bypass or session loss"
tags: connections, client, supabase-js, auth, keys, configuration
---

# Supabase client configuration: keys, timeouts, retries

## Key hierarchy (2026 naming)

```
sb_publishable_...  ← client-safe (was: anon key)
sb_secret_...       ← server-only, bypasses RLS (was: service_role key)
```

**The `sb_secret_` key must never appear in client code, env vars prefixed `EXPO_PUBLIC_*`, or bundled JS.** It bypasses all RLS — exposure = full database read/write for anyone.

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
const userClient = createClient(url, publishableKey, {
  global: { headers: { Authorization: authHeader! } },
  auth: { persistSession: false },
});
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

`supabase-js` does not auto-retry failed requests. Implement retries at the call site for idempotent reads:

```ts
async function fetchWithRetry<T>(fn: () => Promise<{ data: T; error: unknown }>, retries = 3) {
  for (let i = 0; i < retries; i++) {
    const { data, error } = await fn();
    if (!error) return data;
    if (i === retries - 1) throw error;
    await new Promise(r => setTimeout(r, 2 ** i * 500));
  }
}
```
