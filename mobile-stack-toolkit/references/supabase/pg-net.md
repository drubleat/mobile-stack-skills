---
title: pg_net — async HTTP calls from Postgres triggers and functions
impact: MEDIUM
impactDescription: "pg_net enables fire-and-forget webhook delivery and Edge Function triggers from database events without external infrastructure"
tags: pg-net, supabase, http, webhooks, triggers, postgres
---

# pg_net: async HTTP from the database

pg_net lets Postgres make outbound HTTP requests asynchronously — the request is queued and executed in the background, without blocking the transaction.

## When to use pg_net

| Use case | Right tool |
|---|---|
| Fire webhook on row insert/update | pg_net |
| Trigger Edge Function from a DB event | pg_net |
| Simple one-shot notification | pg_net |
| Reliable delivery with retries | pgmq (see [queues.md](queues.md)) |
| Recurring scheduled calls | pg_cron (see [pg-cron.md](pg-cron.md)) |

## Trigger an Edge Function on new user signup

```sql
create or replace function handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  perform net.http_post(
    url     := current_setting('app.supabase_url') || '/functions/v1/on-new-user',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || current_setting('app.service_key')
    ),
    body    := jsonb_build_object(
      'user_id', NEW.id,
      'email', NEW.email,
      'created_at', NEW.created_at
    )
  );
  return NEW;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();
```

## Trigger on subscription state change

```sql
create or replace function notify_subscription_change()
returns trigger language plpgsql as $$
begin
  if OLD.is_active != NEW.is_active or OLD.plan != NEW.plan then
    perform net.http_post(
      url     := current_setting('app.supabase_url') || '/functions/v1/subscription-changed',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' || current_setting('app.service_key')
      ),
      body    := jsonb_build_object(
        'user_id', NEW.user_id,
        'old_plan', OLD.plan,
        'new_plan', NEW.plan,
        'is_active', NEW.is_active
      )
    );
  end if;
  return NEW;
end;
$$;

create trigger on_subscription_update
  after update on subscriptions
  for each row execute function notify_subscription_change();
```

## Check request status

```sql
-- See recent HTTP calls and their outcomes
select id, method, url, status_code, error_msg,
       response_status, created
from net._http_response
order by created desc
limit 20;

-- Failed requests (may need retry)
select id, url, error_msg, created
from net._http_response
where status_code is null or status_code >= 400
order by created desc;
```

## Limitations to know

- **No retry logic** — failed requests don't automatically retry; design your Edge Functions to be idempotent so you can re-call them safely
- **Async only** — you can't read the HTTP response inside the same transaction
- **5s default timeout** — large payloads or slow endpoints may time out

## Cleanup (add via pg_cron)

```sql
select cron.schedule(
  'clean-pg-net-log',
  '0 4 * * *',
  $$delete from net._http_response where created < now() - interval '7 days'$$
);
```

## Deep reference

Status monitoring, GET requests, production patterns → [supabase-postgres-best-practices: ext-pg-net](../../supabase-postgres-best-practices/rules/ext-pg-net.md).
