---
title: "pg_net asynchronous request semantics"
impact: HIGH
impactDescription: "Match database guarantees to the operation and verify with real roles"
tags: postgres, supabase, correctness
---

# pg_net asynchronous request semantics

Enable the extension in the intended database. `net.http_post` queues a request and returns its ID; outbound execution starts after commit. It does not provide durable retries or proof of delivery.

```sql
select net.http_post(
  url := 'https://example.com/webhook',
  headers := '{"Content-Type":"application/json"}'::jsonb,
  body := jsonb_build_object('event_id', gen_random_uuid()),
  timeout_milliseconds := 5000
);
select id, status_code, timed_out, error_msg, created
from net._http_response order by created desc limit 20;
```

The payload is JSONB. `method`, `url` and `response_status` are not columns of this response table. Correlate request IDs to your own event log and account for the extension's retention window. Check both timeout/error and HTTP status.

Authenticate the receiver, keep credentials in a restricted secret store such as Vault, and never hardcode service keys in SQL/settings. Use a durable outbox/queue for required side effects and idempotency for retries. A trigger that enqueues HTTP successfully can still fail to deliver later. See [queues](ext-pgmq.md).

## Sources

Reviewed 2026-10-20: [pg_net](https://supabase.com/docs/guides/database/extensions/pg_net).
