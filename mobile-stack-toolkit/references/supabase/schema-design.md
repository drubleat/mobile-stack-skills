---
title: Schema design: profiles, subscriptions, feature tables
impact: HIGH
impactDescription: "Correct table shape halves RLS complexity and makes RevenueCat webhooks and AI feature tables trivial to wire"
tags: supabase, postgres, schema, migrations, rls
---

# Schema design: profiles, subscriptions, feature tables

Conventions that make RLS simple and keep RevenueCat/AI features wired correctly.

## `profiles` — the public mirror of `auth.users`

Never expose `auth.users` directly. Create a `profiles` table keyed by the auth user id, auto-populated by a trigger on signup:

```sql
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique,
  avatar_url text,
  created_at timestamptz not null default now()
);
alter table public.profiles enable row level security;

-- Auto-create a profile row when a user signs up
create function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  insert into public.profiles (id) values (new.id);
  return new;
end; $$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
```

`security definer` + `set search_path = ''` is the safe trigger pattern (runs as owner, immune to search_path attacks). Use fully-qualified names (`public.profiles`) inside such functions.

## `subscriptions` — RevenueCat's projection, server-owned

This table is written **only** by the RevenueCat webhook (an Edge Function), never by the client. It's the source of truth your server checks before doing paid work.

```sql
create table public.subscriptions (
  user_id uuid primary key references auth.users(id) on delete cascade,
  rc_app_user_id text,                 -- RevenueCat App User ID (align with auth uid)
  entitlement text,                    -- e.g. 'pro'
  is_active boolean not null default false,
  product_id text,
  store text,                          -- 'app_store' | 'play_store'
  current_period_end timestamptz,
  updated_at timestamptz not null default now()
);
alter table public.subscriptions enable row level security;
-- SELECT-own policy for the client (read-only); writes happen via service key in the webhook.
```

Key decision: **align RevenueCat's App User ID with the Supabase auth uid** (call `Purchases.logIn(session.user.id)`). That makes the webhook a trivial upsert keyed by `user_id`. Details: [../monetization/webhooks-supabase.md](../monetization/webhooks-supabase.md).

## Feature tables — the owner pattern

Every user-owned table carries a `user_id` so RLS is a one-liner:

```sql
create table public.items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade default auth.uid(),
  title text not null,
  created_at timestamptz not null default now()
);
alter table public.items enable row level security;
create index on public.items (user_id);   -- RLS filters by user_id; index it
```

`default auth.uid()` means inserts auto-stamp the owner; the RLS policy then just checks `user_id = (select auth.uid())` → [rls-policies.md](rls-policies.md).

## Conventions worth standardizing

- **`uuid` PKs** via `gen_random_uuid()` (don't leak row counts with serial ids).
- **`timestamptz` everywhere**, `default now()`; add `updated_at` maintained by a trigger if you need it.
- **Always index foreign keys / `user_id`** — RLS adds a `where user_id = ...` to most queries; an unindexed `user_id` makes every read a seq scan.
- **`on delete cascade`** from `auth.users` so deleting a user cleans up their data (GDPR-friendly).
- **Enums** for small fixed sets (status, store), or a `check` constraint.
- **Money/credits**: store integers (cents, token counts), never floats.

## AI quota tables

For per-user rate limiting, a tiny table the AI Edge Function reads/increments:

```sql
create table public.usage_counters (
  user_id uuid references auth.users(id) on delete cascade,
  day date not null default current_date,
  ai_calls int not null default 0,
  primary key (user_id, day)
);
```

See [../ai/guardrails.md](../ai/guardrails.md) for the increment-and-check logic.
