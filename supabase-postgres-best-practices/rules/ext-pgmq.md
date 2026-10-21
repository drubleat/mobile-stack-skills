---
title: "pgmq: retry, visibility and acknowledgement"
impact: HIGH
impactDescription: "Match database guarantees to the operation and verify with real roles"
tags: postgres, supabase, correctness
---

# pgmq: retry, visibility and acknowledgement

Create logged queues for durable work. Direct SQL extension calls use `pgmq`; optional Data API wrappers use `pgmq_public` with their own parameter names and explicit grants.

```sql
select pgmq.create('email_notifications');
select pgmq.send('email_notifications', '{"event_id":"example"}'::jsonb);
select * from pgmq.read('email_notifications', 30, 10);
-- After successfully processing a returned msg_id:
-- select pgmq.delete('email_notifications', 123::bigint);
select * from pgmq.metrics_all();
```

Read temporarily hides messages; it does not execute work. Workers must authenticate, validate payloads, implement idempotency and check acknowledgement results. A crash after an external side effect and before delete can cause duplicate execution. Extend visibility when needed, limit retry counts and monitor age/depth.

For Data API workers, configure exposure/grants deliberately and use `adminClient.schema('pgmq_public').rpc('read', {queue_name, sleep_seconds, n})`; the delete wrapper uses `message_id`. Do not expose privileged queues to every authenticated mobile user.

A dead-letter queue is application logic. Move exhausted jobs and acknowledge originals transactionally with explicit payload/metadata mapping; do not `INSERT SELECT *` between queue tables or assume a DLQ exists automatically. Preserve an event ID for replay without repeating effects. Archive processed messages only according to an appropriate retention policy.

## Sources

Reviewed 2026-10-20: [Supabase Queues API](https://supabase.com/docs/guides/queues/api), [pgmq](https://github.com/pgmq/pgmq).
