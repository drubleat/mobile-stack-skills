---
title: "Server-side push delivery"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Server-side push delivery

Use a trusted server or worker. Authenticate the initiating actor and authorize the event/recipient set; an endpoint accepting arbitrary user IDs and message bodies must not be public. Store provider credentials server-side and keep staging/production token namespaces separate.

Delivery workflow:

1. Write a stable event/job ID and intended recipients to a durable outbox/queue.
2. Read active installation tokens for those recipients.
3. Send bounded batches through Expo Push Service or FCM HTTP v1 with the correct token type and credentials.
4. Check HTTP status and each provider result. Persist accepted IDs, retryable failures and permanent failures separately.
5. Poll Expo receipts where applicable; remove only tokens specifically reported invalid. Retry transient failures with bounded backoff and provider retry hints.

A provider acceptance is not proof of display/read. Record the distinction in metrics. Do not delete tokens for a general auth/configuration error. Deduplicate jobs and client opens; external push delivery cannot be made exactly-once merely by acknowledging a queue row.

For database-triggered work, enqueue an outbox row transactionally. [pg_net](../supabase/pg-net.md) accepts a JSONB body, not a JSON string cast to text, and does not itself supply reliable retry. Use [queues](../supabase/queues.md) for durable processing. Avoid service-role keys in SQL settings or migrations.

Keep payloads small and avoid private content on lock screens. Send an authorized resource identifier for the app to resolve after opening. A worker endpoint needs its own verified authentication; a cron schedule does not protect it.

## Sources

Reviewed 2026-10-20: [Expo sends/receipts](https://docs.expo.dev/push-notifications/sending-notifications/), [FCM HTTP v1](https://firebase.google.com/docs/cloud-messaging/migrate-v1).
