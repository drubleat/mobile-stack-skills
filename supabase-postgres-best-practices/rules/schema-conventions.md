---
title: Schema conventions — naming, types, defaults, soft delete
impact: HIGH
impactDescription: "Consistent schema conventions make RLS policies simpler, PostgREST queries predictable, and migrations less risky"
tags: schema, postgres, conventions, migrations, types
---

# Schema conventions

## Standard column set for every table

```sql
create table public.items (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  -- your columns here
);
```

- **`uuid` PKs** via `gen_random_uuid()` — no sequential ID leakage, globally unique
- **`timestamptz` not `timestamp`** — always store with timezone; `timestamp` silently loses timezone info
- **`on delete cascade`** on user_id — when the auth user is deleted, orphan rows are cleaned up automatically
- **`not null` with defaults** — prevents NULL surprises from application bugs

## Auto-update `updated_at`

```sql
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger set_updated_at
  before update on items
  for each row execute function public.set_updated_at();
```

## Soft delete pattern

```sql
alter table posts add column deleted_at timestamptz;

-- Partial index — only index non-deleted rows
create index on posts(user_id, created_at desc) where deleted_at is null;

-- RLS policy excludes soft-deleted rows
create policy "select active posts" on posts
  for select using (
    deleted_at is null
    and user_id = (select auth.uid())
  );
```

## Enum columns

Prefer Postgres enums for constrained value sets — enforced at the DB level:

```sql
create type subscription_status as enum ('trialing', 'active', 'past_due', 'canceled', 'expired');

alter table subscriptions add column status subscription_status not null default 'trialing';
```

## JSONB for flexible metadata

```sql
-- Use jsonb for unstructured/extensible data; index the fields you query
alter table events add column metadata jsonb not null default '{}';
create index on events using gin(metadata);
```

## Naming conventions

| Pattern | Example |
|---|---|
| Tables | `snake_case` plural: `user_profiles`, `subscription_events` |
| Columns | `snake_case`: `created_at`, `is_active` |
| Indexes | `idx_{table}_{columns}`: `idx_messages_user_id_created_at` |
| Functions | `snake_case` verbs: `handle_new_user()`, `set_updated_at()` |
| Policies | Descriptive strings: `"users can read own messages"` |
