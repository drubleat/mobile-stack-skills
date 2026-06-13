---
title: Advisory locks — distributed mutex without a lock table
impact: MEDIUM
impactDescription: "pg_try_advisory_lock gives distributed mutual exclusion with zero overhead compared to a lock table or Redis"
tags: locks, concurrency, postgres, advisory-locks, distributed
---

# Advisory locks: distributed mutex in Postgres

## When to use

Advisory locks are application-defined locks — Postgres stores them but doesn't assign them meaning. Use them to:

- Prevent duplicate cron jobs from running concurrently
- Serialize expensive per-user operations (e.g., "only one AI image generation per user at a time")
- Implement optimistic concurrency control

## Session-level vs transaction-level

```sql
-- Session-level: held until explicitly released or connection closed
select pg_advisory_lock(12345);         -- blocking
select pg_try_advisory_lock(12345);     -- non-blocking, returns bool
select pg_advisory_unlock(12345);

-- Transaction-level: auto-released on COMMIT/ROLLBACK
select pg_advisory_xact_lock(12345);
select pg_try_advisory_xact_lock(12345);
```

**Prefer transaction-level** in Supabase Edge Functions — they're automatically released even if the function errors.

## Naming convention: use `hashtext()`

```sql
-- Convert a string key to a bigint for the lock
select pg_try_advisory_xact_lock(hashtext('process_user_' || user_id::text));
```

## Edge Function pattern: prevent duplicate processing

```ts
// In Supabase Edge Function
const { data: locked } = await adminClient
  .rpc('try_lock_user_job', { p_user_id: userId });

if (!locked) {
  return new Response(JSON.stringify({ status: 'already_running' }), { status: 409 });
}

// ... do work — lock is held for this transaction
```

```sql
create or replace function try_lock_user_job(p_user_id uuid)
returns boolean language plpgsql as $$
begin
  return pg_try_advisory_xact_lock(hashtext('user_job_' || p_user_id::text));
end;
$$;
```

## Viewing active advisory locks

```sql
select locktype, classid, objid, mode, granted
from pg_locks
where locktype = 'advisory';
```
