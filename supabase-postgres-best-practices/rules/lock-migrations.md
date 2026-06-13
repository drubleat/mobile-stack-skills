---
title: Lock management — avoiding migration deadlocks and table locks
impact: MEDIUM-HIGH
impactDescription: "ALTER TABLE acquires AccessExclusiveLock and blocks all reads and writes; a migration that takes 30s on a busy table causes a visible outage"
tags: locks, migrations, postgres, concurrency, schema
---

# Lock management: avoiding migration deadlocks

## Lock hierarchy (most to least restrictive)

```
AccessExclusiveLock    ← ALTER TABLE, DROP TABLE, VACUUM FULL
ExclusiveLock          ← rare, most DDL
ShareRowExclusiveLock  ← CREATE TRIGGER
ShareLock              ← CREATE INDEX (non-concurrent)
RowExclusiveLock       ← INSERT, UPDATE, DELETE
RowShareLock           ← SELECT FOR UPDATE
AccessShareLock        ← SELECT
```

## Dangerous migration patterns

```sql
-- ❌ Blocks all reads and writes until constraint validates
alter table messages add constraint fk_user
  foreign key (user_id) references auth.users(id);

-- ✅ Add NOT VALID first — validates new rows only, no full-table scan lock
alter table messages add constraint fk_user
  foreign key (user_id) references auth.users(id) not valid;

-- Then validate in a separate transaction (takes ShareUpdateExclusiveLock, not AccessExclusiveLock)
alter table messages validate constraint fk_user;
```

## Lock timeout — fail fast rather than pile up

```sql
-- Set at the session level before dangerous DDL
set lock_timeout = '5s';
alter table messages add column ...;
-- If it can't acquire the lock in 5s, it fails instead of blocking all subsequent queries
```

## Detecting lock waits

```sql
-- See who is blocked and by whom
select blocked.pid, blocked.query, blocking.pid as blocking_pid, blocking.query as blocking_query
from pg_stat_activity blocked
join pg_stat_activity blocking
  on blocking.pid = any(pg_blocking_pids(blocked.pid))
where cardinality(pg_blocking_pids(blocked.pid)) > 0;
```

## Migration queue: avoid concurrent migrations

Never run two migrations simultaneously. In CI:

```yaml
# GitHub Actions — serialize migration deploys
concurrency:
  group: supabase-migrations
  cancel-in-progress: false
```

## Deadlock avoidance

Deadlocks occur when two transactions each hold a lock the other needs. Pattern:

```sql
-- Always lock multiple tables in the same order across all transactions
-- Transaction A: lock users then messages
-- Transaction B: lock users then messages (not messages then users)
begin;
lock table users in share row exclusive mode;
lock table messages in share row exclusive mode;
-- ... do work
commit;
```

For application-level row locking, use `SELECT ... FOR UPDATE SKIP LOCKED` for job queues instead of blocking `FOR UPDATE`.
