---
title: "pg_cron jobs and operational checks"
impact: HIGH
impactDescription: "Match database guarantees to the operation and verify with real roles"
tags: postgres, supabase, correctness
---

# pg_cron jobs and operational checks

Enable pg_cron where supported and inspect the scheduling role/timezone. Jobs execute with the scheduling user's database permissions; they do not universally run as a superuser. Supabase commonly uses UTC, while extension configuration can differ.

```sql
-- Example requires public.posts.deleted_at and an approved retention policy.
select cron.schedule('purge-deleted-posts', '0 3 * * *',
  $$delete from public.posts where deleted_at < now() - interval '30 days'$$);
select jobid, jobname, schedule, active from cron.job;
select jobid, status, start_time, end_time, return_message
from cron.job_run_details order by start_time desc limit 20;
-- select cron.unschedule('purge-deleted-posts');
```

Bound batches and lock/statement durations. Monitor backlog and failure rather than assuming every scheduled job finishes. For user-local schedules, handle timezone and DST explicitly. Use `GET DIAGNOSTICS affected = ROW_COUNT` after a statement in PL/pgSQL; PostgreSQL has no `found_rows()` function.

Remote work requires [pg_net](ext-pg-net.md) or a [queue](ext-pgmq.md), verified endpoint authentication and idempotent processing. Store secrets in the supported secret system. Cron success confirms SQL execution, not successful downstream delivery. Keep schedules and functions in reviewed migrations and remove obsolete jobs explicitly.

## Sources

Reviewed 2026-10-20: [pg_cron](https://github.com/citusdata/pg_cron), [Supabase Cron](https://supabase.com/docs/guides/cron).
