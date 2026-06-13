---
title: pg_cron — scheduled jobs for mobile app backends
impact: HIGH
impactDescription: "pg_cron handles recurring backend tasks (cleanup, reminders, digest emails, subscription checks) without external schedulers or always-on servers"
tags: pg-cron, supabase, scheduling, background-jobs, postgres
---

# pg_cron: scheduled background jobs

pg_cron is enabled by default on Supabase. It runs recurring SQL or stored procedure calls on a cron schedule, inside Postgres, with no external infrastructure.

## Common patterns for mobile app backends

### 1. Daily subscription expiry check

```sql
create or replace function check_expired_subscriptions()
returns void language plpgsql security definer set search_path = public as $$
begin
  update subscriptions
  set is_active = false
  where expires_at < now()
    and is_active = true;
end;
$$;

select cron.schedule(
  'check-expired-subscriptions',
  '*/30 * * * *',  -- every 30 minutes
  'select check_expired_subscriptions()'
);
```

### 2. Trigger daily digest emails via Edge Function

```sql
select cron.schedule(
  'daily-digest',
  '0 9 * * *',  -- 9am UTC daily
  $$
    select net.http_post(
      url := current_setting('app.supabase_url') || '/functions/v1/send-digest',
      headers := jsonb_build_object(
        'Authorization', 'Bearer ' || current_setting('app.service_key'),
        'Content-Type', 'application/json'
      ),
      body := '{}'::jsonb
    )
  $$
);
```

Set the app settings in the dashboard or via migration:

```sql
alter database postgres set app.supabase_url = 'https://[project-ref].supabase.co';
alter database postgres set app.service_key = 'sb_secret_...';
```

### 3. Soft-delete cleanup

```sql
select cron.schedule(
  'purge-deleted-content',
  '0 3 * * *',  -- 3am UTC nightly
  $$
    delete from posts where deleted_at < now() - interval '30 days';
    delete from messages where deleted_at < now() - interval '90 days';
  $$
);
```

### 4. Token / cache expiry

```sql
select cron.schedule(
  'clean-expired-tokens',
  '0 * * * *',  -- hourly
  $$delete from otp_tokens where expires_at < now()$$
);
```

## Manage jobs

```sql
-- List all jobs
select jobid, jobname, schedule, active from cron.job;

-- View recent run history
select jobname, status, start_time, end_time - start_time as duration, return_message
from cron.job_run_details
join cron.job using (jobid)
order by start_time desc
limit 20;

-- Disable a job temporarily
update cron.job set active = false where jobname = 'daily-digest';

-- Remove a job
select cron.unschedule('daily-digest');
```

## Cron expression quick reference

```
'* * * * *'       — every minute
'*/5 * * * *'     — every 5 minutes
'0 * * * *'       — every hour on the hour
'0 9 * * *'       — daily at 9am UTC
'0 9 * * 1'       — every Monday at 9am UTC
'0 0 1 * *'       — first day of each month at midnight
```

All times are **UTC**. Convert your target timezone to UTC before scheduling.

## Deep reference

SQL-level detail, DLQ patterns, advisory lock integration → [supabase-postgres-best-practices: ext-pg-cron](../../supabase-postgres-best-practices/rules/ext-pg-cron.md).
