---
title: auth.uid() and auth.jwt() — correct usage in SQL
impact: CRITICAL
impactDescription: "Bare auth.uid() is volatile and re-evaluated per row; wrong JWT claim paths return NULL silently instead of blocking access"
tags: security, rls, auth, postgres, jwt
---

# `auth.uid()` and `auth.jwt()` — correct usage in SQL

## Always wrap in `(select ...)`

```sql
-- ❌ Volatile — called once per row
user_id = auth.uid()

-- ✅ Stable — called once per query
user_id = (select auth.uid())
```

See [query-rls-performance.md](query-rls-performance.md) for the full performance explanation.

## Extracting JWT claims

```sql
-- Role claim (set via Supabase Auth or custom JWT)
(select auth.jwt() ->> 'role')

-- Custom app_metadata claim (set server-side via service key)
(select auth.jwt() -> 'app_metadata' ->> 'org_id')

-- user_metadata claim (set by the user — treat as untrusted)
(select auth.jwt() -> 'user_metadata' ->> 'display_name')
```

**Security note**: `user_metadata` is writable by the user via `supabase.auth.updateUser()`. Never use it for access control. Use `app_metadata` (only writable via service key) for trusted role/org claims.

## Setting custom JWT claims via Database Hook

```sql
-- Create a hook function that adds org_id to the JWT
create or replace function public.custom_access_token_hook(event jsonb)
returns jsonb language plpgsql as $$
declare
  claims jsonb;
  org_id text;
begin
  select o.id::text into org_id
  from org_members om
  join organizations o on o.id = om.org_id
  where om.user_id = (event->>'user_id')::uuid
  limit 1;

  claims := event->'claims';
  if org_id is not null then
    claims := jsonb_set(claims, '{app_metadata,org_id}', to_jsonb(org_id));
  end if;
  return jsonb_set(event, '{claims}', claims);
end;
$$;

-- Grant execute to supabase_auth_admin
grant execute on function public.custom_access_token_hook to supabase_auth_admin;
```

Then register in Supabase Dashboard → Authentication → Hooks → Custom Access Token.

## Null safety in policies

`auth.uid()` returns `NULL` for anonymous (unauthenticated) requests. A policy like `user_id = (select auth.uid())` correctly blocks anonymous users because `NULL = anything` is always `FALSE` in SQL.

But be explicit for clarity:

```sql
create policy "authenticated only" on messages
  for select using (
    (select auth.uid()) is not null
    and user_id = (select auth.uid())
  );
```
