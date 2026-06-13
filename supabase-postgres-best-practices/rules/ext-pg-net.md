---
title: pg_net — async HTTP requests from Postgres
impact: MEDIUM
impactDescription: "pg_net enables fire-and-forget HTTP calls from triggers and functions without blocking the transaction; eliminates the need for a message queue for simple webhook delivery"
tags: pg-net, postgres, http, webhooks, extensions, async
---

# pg_net: async HTTP requests from Postgres

## Enable the extension

```sql
create extension if not exists pg_net;
```

## Fire-and-forget HTTP POST (non-blocking)

```sql
-- Returns a request_id immediately; request runs asynchronously
select net.http_post(
  url     := 'https://your-service.com/webhook',
  headers := '{"Content-Type": "application/json", "Authorization": "Bearer secret"}'::jsonb,
  body    := json_build_object(
    'event', 'new_user',
    'user_id', NEW.id::text,
    'email', NEW.email
  )::jsonb
);
```

## Trigger pattern: call webhook on row insert

```sql
create or replace function notify_new_user()
returns trigger language plpgsql as $$
begin
  perform net.http_post(
    url     := 'https://[project-ref].supabase.co/functions/v1/on-new-user',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || current_setting('app.service_key', true)
    ),
    body    := jsonb_build_object('user_id', NEW.id, 'email', NEW.email)
  );
  return NEW;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function notify_new_user();
```

## Check request status

```sql
-- View all pending/completed requests
select id, method, url, status_code, error_msg, created, response_status
from net._http_response
order by created desc
limit 20;

-- Failed requests (no status code = network error)
select id, url, error_msg, created
from net._http_response
where status_code is null or status_code >= 400
order by created desc;
```

## Limitations

- **Async only** — `net.http_post` returns immediately; you can't use the response in the same transaction
- **No retry logic** — failed requests don't retry; implement idempotent handlers and use pg_cron to re-process failures
- **5 second default timeout** — adjust via `net.http_timeout_ms` GUC (requires Supabase support for configuration changes)
- **Not for high-throughput** — if you need guaranteed delivery with retries, use Supabase Queues (pgmq) instead

## GET requests

```sql
select net.http_get(
  url     := 'https://api.example.com/data?key=value',
  headers := '{"Authorization": "Bearer token"}'::jsonb
);
```

## Cleanup old response records

```sql
-- pg_net accumulates response records; prune them periodically
select cron.schedule(
  'clean-pg-net-responses',
  '0 4 * * *',
  $$delete from net._http_response where created < now() - interval '7 days'$$
);
```
