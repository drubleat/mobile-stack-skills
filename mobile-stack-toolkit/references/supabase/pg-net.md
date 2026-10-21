---
title: "pg_net: asynchronous HTTP"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# pg_net: asynchronous HTTP

`net.http_post` queues a request whose execution begins after commit. Its returned bigint is a request ID, not an HTTP response. A successful enqueue does not establish delivery; use a durable queue/outbox when the side effect must survive failures.

```sql
-- Example payload only: the receiver must authenticate the request.
select net.http_post(
  url := 'https://example.com/webhook',
  headers := '{"Content-Type":"application/json"}'::jsonb,
  body := jsonb_build_object('event_id', gen_random_uuid())
);

select id, status_code, timed_out, error_msg, created
from net._http_response
order by created desc limit 20;
```

`method`, `url` and `response_status` are not response-table columns. Track the returned ID and your own event identifier when correlation is needed. Response retention is bounded by pg_net configuration; it is not a permanent audit log. Check timeout and HTTP status, and use idempotent receivers for retries.

Store outbound credentials in the project's supported secret system such as Supabase Vault; restrict access to decrypted secrets. Do not place service-role keys in migrations or database settings. Match the receiving function's authentication contract—new Supabase secret API keys are not user JWTs.

Keep triggers lightweight. Prefer a transactional outbox insert over an external side effect in signup logic, use unique function/trigger names and a fixed search_path for privileged functions, and revoke public execution where applicable. See [queues](queues.md) and [cron](pg-cron.md).

## Sources

Reviewed 2026-10-20: [pg_net](https://supabase.com/docs/guides/database/extensions/pg_net), [scheduled function calls](https://supabase.com/docs/guides/functions/schedule-functions).
