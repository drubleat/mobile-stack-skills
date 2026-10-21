---
title: "Advisory locks and transaction boundaries"
impact: CRITICAL
impactDescription: "Prevent unauthorized access and incorrect state transitions"
tags: security, correctness
---

# Advisory locks and transaction boundaries

Advisory locks provide cooperative mutual exclusion; every writer must follow the same convention. They are not optimistic concurrency control and do not enforce uniqueness after a transaction ends.

```sql
begin;
select pg_advisory_xact_lock(hashtextextended('job:' || 'example-user-id', 0));
-- Perform ALL protected database work here, on this same connection.
commit;
```

Use `pg_try_advisory_xact_lock` when the caller should fail promptly instead of waiting. Check its boolean result before doing work. Hash collisions can serialize unrelated work; use stable collision-aware keys for critical systems.

A PostgREST RPC transaction ends when the RPC response returns. A `try_lock_user_job` RPC followed by an HTTP call in an Edge Function provides **no lock protection** for that call. For external work use a durable job/lease with an expiry, owner token, heartbeat/fencing strategy, and idempotent effects. For a database-only operation, combine lock acquisition and the operation in one RPC.

Session-level locks (`pg_advisory_lock`) survive transactions until released or the connection ends. Do not use them through transaction poolers; a later request may get a different backend. Use a dedicated session when session-level semantics are necessary.

Inspect `pg_locks` for `locktype = 'advisory'`; configure lock/statement timeouts and test concurrent callers.

## Sources

Reviewed 2026-10-20: [PostgreSQL advisory locks](https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS).
