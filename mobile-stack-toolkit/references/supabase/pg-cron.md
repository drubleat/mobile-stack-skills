---
title: "pg_cron: recurring backend work"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# pg_cron: recurring backend work

Enable the extension in the intended project; do not assume it is enabled everywhere. Jobs run with database privileges, so review the SQL and role. Keep work bounded and monitor failures and overlap.

```sql
-- Example assumes posts.deleted_at and an approved retention policy.
select cron.schedule('purge-deleted-posts', '0 3 * * *',
  $$delete from public.posts where deleted_at < now() - interval '30 days'$$);
select jobid, jobname, schedule, active from cron.job;
select jobid, status, start_time, end_time, return_message
from cron.job_run_details order by start_time desc limit 20;
-- When removing this task:
-- select cron.unschedule('purge-deleted-posts');
```

Inspect the configured cron timezone (Supabase commonly uses UTC). Per-user local reminders need timezone/DST-aware scheduling rather than a fixed UTC offset. Large cleanup jobs should process bounded batches and respect lock/statement timeouts.

For remote work, combine cron with [pg_net](pg-net.md) or a durable [queue](queues.md). Store credentials in Vault or the supported secret system; never in `ALTER DATABASE ... SET app.service_key`. Authenticate worker endpoints and make external side effects idempotent. Cron execution success is not confirmation that a queued HTTP request succeeded.

Subscriptions require expiry, grace-period and provider reconciliation logic from [webhooks](../monetization/webhooks-supabase.md). Do not blindly flip access using an `expires_at` column absent from the schema, or rely solely on a scheduled boolean update to enforce expiry.

## Sources

Reviewed 2026-10-20: [Supabase Cron](https://supabase.com/docs/guides/cron), [pg_cron](https://github.com/citusdata/pg_cron).
