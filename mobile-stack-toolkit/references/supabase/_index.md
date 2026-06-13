---
title: Supabase — domain index
impact: MEDIUM-HIGH
impactDescription: "Routes to auth, RLS, Edge Functions, Storage, Realtime — load first when any Supabase topic is mentioned"
tags: supabase, index, postgres, auth
---

# Supabase — index

Postgres + Auth + Edge Functions + Storage + Realtime. You can adopt any subset — RLS and Auth are the parts you must not get wrong.

## Router

| Task | File |
|---|---|
| `supabase init`, local Docker stack, migrations workflow | [local-dev-migrations.md](local-dev-migrations.md) |
| Email/OTP, native Apple/Google sign-in, session persistence | [auth.md](auth.md) |
| Design `profiles`, `subscriptions`, feature tables | [schema-design.md](schema-design.md) |
| Write correct, performant Row Level Security policies | [rls-policies.md](rls-policies.md) |
| Write/test/deploy Edge Functions, manage secrets | [edge-functions.md](edge-functions.md) |
| Live-updating UI (Realtime subscriptions) | [realtime.md](realtime.md) |
| File/photo upload, signed URLs, validation | [storage.md](storage.md) |
| Semantic search, RAG, AI embeddings with pgvector | [pgvector.md](pgvector.md) |
| Scheduled background jobs (cleanup, digests, reminders) | [pg-cron.md](pg-cron.md) |
| Fire-and-forget HTTP from DB triggers | [pg-net.md](pg-net.md) |
| Reliable async job queues with retries (pgmq) | [queues.md](queues.md) |
| Connect Claude Code directly to your Supabase project | [mcp-mode.md](mcp-mode.md) |

AI proxy functions → [../ai/edge-proxy-architecture.md](../ai/edge-proxy-architecture.md). RevenueCat webhook → [../monetization/webhooks-supabase.md](../monetization/webhooks-supabase.md). Deep Postgres rules (indexes, locking, pooling) → [supabase-postgres-best-practices](../../../supabase-postgres-best-practices/SKILL.md).

## Non-negotiables

1. **RLS on every table in `public`.** A table without RLS is world-readable/writable by anyone holding the publishable key. This is the #1 Supabase security incident. See [rls-policies.md](rls-policies.md).
2. **Service/secret key never leaves the server.** The client gets the **publishable** key only. The **secret** key (full bypass of RLS) lives in Edge Functions / server env.
3. **Schema lives in migrations**, not in the dashboard. Click-ops in the Studio UI drift from your repo and break teammates/CI.

## API keys (2026 change)

Supabase is moving from `anon` / `service_role` keys to **`sb_publishable_...`** (client-safe) and **`sb_secret_...`** (server-only). Legacy keys are deprecated by end of 2026. Map your mental model:

| Old | New | Where |
|---|---|---|
| `anon` | `sb_publishable_...` | client (`EXPO_PUBLIC_*`) |
| `service_role` | `sb_secret_...` | Edge Functions / server only |

Both still work during the transition; prefer the new names in new projects.

## Minimal client init (any framework)

```ts
import { createClient } from '@supabase/supabase-js';
export const supabase = createClient(URL, PUBLISHABLE_KEY, {
  auth: { storage: AsyncStorage, persistSession: true, autoRefreshToken: true },
});
```

The RN-specific session/storage details are in [auth.md](auth.md).
