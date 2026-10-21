---
title: "Supabase Queues: durable jobs"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Supabase Queues: durable jobs

Use a durable logged queue for jobs requiring retry. Visibility timeouts permit redelivery; they do not make an external side effect exactly-once. Every worker needs idempotency, bounded retries, lease handling and a dead-letter policy.

Supabase's Data API wrappers use the exposed `pgmq_public` schema. Do not invoke the underlying `pgmq` extension schema as if it were automatically exposed. Configure API exposure and least-privilege grants for the trusted worker only.

```ts
// Server-side fragment after worker authentication.
const { data: messages, error } = await adminClient.schema('pgmq_public').rpc('read', {
  queue_name: 'ai_jobs', sleep_seconds: 60, n: 5,
});
if (error) throw error;
for (const job of messages ?? []) {
  await processIdempotently(job.msg_id, job.message); // application implementation
  const { data: deleted, error: ackError } = await adminClient.schema('pgmq_public').rpc('delete', {
    queue_name: 'ai_jobs', message_id: job.msg_id,
  });
  if (ackError || deleted !== true) throw ackError ?? new Error('Acknowledgement failed');
}
```

The worker endpoint must reject unauthorized callers before reading a queue. `processIdempotently` must validate payloads and user/resource ownership, enforce quota and deduplicate effects. Set/extend visibility to cover processing, otherwise two workers may execute the same job. A crash after the external side effect and before acknowledgement must be safe.

Producers authenticate the user, validate and size-bound payloads, check enqueue errors and return a stable job ID. Keep client-visible job status in an owner-protected table; do not expose queue internals to mobile users.

Use `pgmq.metrics_all()` for queue depth/age. Move exhausted jobs to a DLQ and acknowledge the original in one transaction with explicit column mapping; do not copy entire rows into differently shaped queue tables. [Cron](pg-cron.md) can trigger polling; it does not provide automatic reliable processing by itself.

## Sources

Reviewed 2026-10-20: [queue quickstart](https://supabase.com/docs/guides/queues/quickstart), [queue API](https://supabase.com/docs/guides/queues/api).
