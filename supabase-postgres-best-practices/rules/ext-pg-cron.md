---
title: pg_cron — scheduled jobs inside Postgres
impact: HIGH
impactDescription: "pg_cron runs recurring SQL or stored procedures on a cron schedule without external schedulers; eliminates infrastructure for cleanup, aggregation, and reminder jobs"
tags: pg-cron, postgres, scheduling, extensions, background-jobs
---

# pg_cron: scheduled jobs in Postgres

## Enable the extension

```sql
create extension if not exists pg_cron;
grant usage on schema cron to postgres;
```

Supabase enables pg_cron by default. Jobs run as the `postgres` superuser.

## Schedule a job

```sql
-- Every day at 2am UTC: delete soft-deleted rows older than 30 days
select cron.schedule(
  'purge-deleted-rows',        -- job name (unique)
  '0 2 * * *',                 -- cron expression (UTC)
  $$delete from posts where deleted_at < now() - interval '30 days'$$
);

-- Every hour: aggregate analytics
select cron.schedule(
  'hourly-analytics',
  '0 * * * *',
  $$call aggregate_hourly_stats()$$
);

-- Every 5 minutes: send pending push notifications
select cron.schedule(
  'send-pending-push',
  '*/5 * * * *',
  $$select send_pending_notifications()$$
);
```

## Cron expression reference

```
┌─ minute (0-59)
│  ┌─ hour (0-23)
│  │  ┌─ day of month (1-31)
│  │  │  ┌─ month (1-12)
│  │  │  │  ┌─ day of week (0-7, 0 and 7 = Sunday)
│  │  │  │  │
*  *  *  *  *
```

## List and manage jobs

```sql
-- All scheduled jobs
select jobid, jobname, schedule, command, active
from cron.job
order by jobid;

-- Job run history (last 10 per job)
select jobid, job_pid, run_id, status, return_message,
       start_time, end_time,
       end_time - start_time as duration
from cron.job_run_details
order by start_time desc
limit 50;

-- Unschedule a job
select cron.unschedule('purge-deleted-rows');

-- Disable without deleting
update cron.job set active = false where jobname = 'send-pending-push';
```

## Best practice: call a stored procedure, not inline SQL

```sql
-- ✅ Better — keeps logic in a versioned function
create or replace function purge_deleted_posts()
returns void language plpgsql as $$
begin
  delete from posts where deleted_at < now() - interval '30 days';
  -- log the purge
  insert into maintenance_log(operation, rows_affected, ran_at)
  values ('purge_deleted_posts', found_rows(), now());
end;
$$;

select cron.schedule('purge-deleted-posts', '0 3 * * *', 'select purge_deleted_posts()');
```

## Triggering Edge Functions on schedule via pg_cron + pg_net

```sql
-- Call an Edge Function on a schedule (requires pg_net)
select cron.schedule(
  'daily-digest-emails',
  '0 9 * * *',
  $$
    select net.http_post(
      url := 'https://[project-ref].supabase.co/functions/v1/send-digest',
      headers := '{"Authorization": "Bearer ' || current_setting('app.service_key') || '"}'::jsonb,
      body := '{}'::jsonb
    )
  $$
);
```

## Timezone handling

pg_cron always runs in UTC. Convert if your schedule should align to a specific timezone:

```sql
-- 9am US Eastern = 14:00 UTC (EST) or 13:00 UTC (EDT)
-- Use '0 14 * * 1-5' as a conservative UTC time for business hours
```
