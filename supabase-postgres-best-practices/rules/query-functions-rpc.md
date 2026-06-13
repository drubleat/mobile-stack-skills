---
title: Postgres functions & RPC — when to use and how to design them
impact: MEDIUM-HIGH
impactDescription: "Server-side functions reduce round-trips, enforce business logic at the DB level, and expose complex queries safely via PostgREST RPC"
tags: functions, rpc, postgres, postgrest, performance, security
---

# Postgres functions & RPC

## When to use a function vs a query

| Situation | Approach |
|---|---|
| Simple CRUD | PostgREST client `.select()` / `.insert()` |
| Multi-step atomic operation | Postgres function in a transaction |
| Complex aggregation or JOIN | Postgres function or view |
| Security-sensitive write (server enforced) | Postgres function with `security definer` |
| Avoid N+1 on computed fields | Postgres function returning a table |

## Basic function

```sql
create or replace function get_user_stats(p_user_id uuid)
returns json language plpgsql stable security invoker as $$
declare
  result json;
begin
  select json_build_object(
    'message_count', count(m.id),
    'last_active', max(m.created_at)
  ) into result
  from messages m
  where m.user_id = p_user_id;
  
  return result;
end;
$$;
```

```ts
const { data } = await supabase.rpc('get_user_stats', { p_user_id: userId });
```

## `security invoker` vs `security definer`

```sql
-- security invoker (default) — runs as the calling user; RLS applies
-- Use for most functions

-- security definer — runs as the function owner (postgres); bypasses RLS
-- Use ONLY when you genuinely need to cross RLS boundaries (e.g., system writes)
-- Always narrow what the function can do to minimize risk

create or replace function create_user_profile()
returns void language plpgsql security definer
set search_path = public  -- prevent search_path hijacking
as $$
begin
  insert into profiles(id, username)
  values (auth.uid(), 'user_' || left(auth.uid()::text, 8));
end;
$$;
```

## Returning a table (for PostgREST filtering/pagination)

```sql
create or replace function search_posts(search_term text)
returns setof posts language sql stable security invoker as $$
  select * from posts
  where to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', search_term)
    and user_id = (select auth.uid())
  order by created_at desc;
$$;
```

PostgREST exposes table-returning functions with the same filtering syntax as tables:

```ts
const { data } = await supabase
  .rpc('search_posts', { search_term: 'flutter' })
  .order('created_at', { ascending: false })
  .limit(20);
```

## Transaction wrapping

```sql
create or replace function transfer_credits(
  from_user uuid,
  to_user uuid,
  amount int
) returns void language plpgsql security definer set search_path = public as $$
begin
  update user_credits set balance = balance - amount where user_id = from_user;
  update user_credits set balance = balance + amount where user_id = to_user;
  -- Both updates succeed or both roll back (atomic by default in a function)
end;
$$;
```

## Grant execute

By default, functions in `public` schema are executable by `authenticated` and `anon` roles. Be explicit:

```sql
-- Restrict to authenticated users only
revoke execute on function get_user_stats(uuid) from anon;
grant execute on function get_user_stats(uuid) to authenticated;
```
