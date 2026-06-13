---
title: pgmq / Supabase Queues — reliable message queuing in Postgres
impact: HIGH
impactDescription: "pgmq provides durable, at-least-once message delivery with visibility timeouts; replaces Redis/SQS for most mobile app background job patterns"
tags: pgmq, queues, postgres, extensions, background-jobs, messaging
---

# pgmq / Supabase Queues: reliable message queuing

## Enable via Supabase Dashboard

Dashboard → Database → Extensions → Search "pgmq" → Enable.

Or via SQL:
```sql
create extension if not exists pgmq;
```

## Core concepts

- **Queue** — named FIFO message store
- **Message** — JSON payload with metadata
- **Visibility timeout (vt)** — message is hidden from other consumers for N seconds after read; if not deleted, it reappears (at-least-once delivery)
- **Dead letter queue (DLQ)** — messages that fail too many times go here

## Create a queue

```sql
select pgmq.create('email_notifications');
select pgmq.create('image_processing');
```

## Send a message

```sql
-- Returns the message_id
select pgmq.send(
  'email_notifications',
  '{"user_id": "uuid-here", "template": "welcome", "to": "user@example.com"}'::jsonb
);

-- Send with delay (seconds)
select pgmq.send(
  'email_notifications',
  '{"user_id": "uuid-here", "template": "trial_ending"}'::jsonb,
  delay := 86400  -- send in 24 hours
);

-- Send batch
select pgmq.send_batch(
  'image_processing',
  array[
    '{"image_id": "a1"}'::jsonb,
    '{"image_id": "a2"}'::jsonb
  ]
);
```

## Read and process messages (Edge Function worker)

```ts
// Supabase Edge Function — poll and process
export default async function handler(_req: Request) {
  const { data: messages } = await adminClient.schema('pgmq').rpc('read', {
    queue_name: 'email_notifications',
    sleep_seconds: 30,  // visibility timeout
    n: 10,             // max messages per poll
  });

  for (const msg of messages ?? []) {
    try {
      await sendEmail(msg.message);
      // Delete on success
      await adminClient.schema('pgmq').rpc('delete', {
        queue_name: 'email_notifications',
        msg_id: msg.msg_id,
      });
    } catch (err) {
      // Don't delete — message reappears after visibility timeout for retry
      console.error('Failed to process message', msg.msg_id, err);
    }
  }
}
```

## Read with archive (keeps processed messages for audit)

```sql
-- Archive instead of delete — message moves to pgmq.a_{queue_name}
select pgmq.archive('email_notifications', msg_id);
```

## Queue depth and dead letter monitoring

```sql
-- Queue metrics
select * from pgmq.metrics('email_notifications');
-- Returns: queue_name, queue_depth, newest_msg_age_sec, oldest_msg_age_sec, total_messages

-- All queues overview
select * from pgmq.metrics_all();

-- Dead letter queue (messages that were never deleted after max reads)
-- pgmq doesn't have built-in DLQ; implement via pg_cron:
select cron.schedule(
  'move-failed-messages',
  '*/10 * * * *',
  $$
    with failed as (
      delete from pgmq.q_email_notifications
      where read_ct >= 5
        and vt < now()
      returning *
    )
    insert into pgmq.q_email_notifications_dlq
    select * from failed
  $$
);
```

## Trigger-driven producer pattern

```sql
-- Enqueue a message whenever a new order is placed
create or replace function enqueue_order_processing()
returns trigger language plpgsql as $$
begin
  perform pgmq.send(
    'order_processing',
    jsonb_build_object('order_id', NEW.id, 'user_id', NEW.user_id)
  );
  return NEW;
end;
$$;

create trigger on_new_order
  after insert on orders
  for each row execute function enqueue_order_processing();
```

## pgmq vs pg_net vs pg_cron

| Need | Use |
|---|---|
| Fire-and-forget webhook | pg_net |
| Reliable background job with retries | pgmq |
| Recurring scheduled job | pg_cron |
| High-throughput event stream | Consider Supabase Realtime or external queue |
