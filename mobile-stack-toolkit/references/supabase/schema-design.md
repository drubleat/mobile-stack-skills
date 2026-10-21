---
title: "Schema design: profiles, subscriptions, feature tables"
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
  user_id uuid not null references auth.users(id) on delete cascade,
  rc_app_user_id text,                 -- RevenueCat App User ID (align with auth uid)
  entitlement text not null,           -- e.g. 'pro'
  is_active boolean not null default false,
  product_id text,
  store text,                          -- 'app_store' | 'play_store'
  current_period_end timestamptz,       -- effective expiry incl. verified grace; null for verified lifetime
  verified_at timestamptz not null,    -- last successful server reconciliation
  updated_at timestamptz not null default now(),
  primary key (user_id, entitlement)
);
alter table public.subscriptions enable row level security;
create policy "read own entitlements" on public.subscriptions
  for select to authenticated using (user_id = (select auth.uid()));
revoke insert, update, delete on public.subscriptions from anon, authenticated;
```

Key decision: **align RevenueCat's App User ID with the Supabase auth uid** (call `Purchases.logIn(session.user.id)`). Resolve aliases/transfers and reconcile server state per entitlement; a webhook ID is not always an auth UUID. Details: [../monetization/webhooks-supabase.md](../monetization/webhooks-supabase.md).

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

Use the [quota migration](../../assets/sql/ai-quota.sql) and [guardrails](../ai/guardrails.md). The table and RPC are server-owned; clients must not set another user's counter or select their own quota limit.
