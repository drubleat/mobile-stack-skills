---
title: Supabase Queues (pgmq) — reliable background job processing
impact: HIGH
impactDescription: "Queues provide at-least-once delivery with visibility timeouts and retries; the right tool when pg_net fire-and-forget isn't reliable enough"
tags: queues, pgmq, supabase, background-jobs, messaging, reliability
---

# Supabase Queues (pgmq)

Supabase Queues is built on `pgmq` — a Postgres-native message queue. Enable it in Dashboard → Database → Extensions → pgmq.

Use queues when you need **guaranteed processing with retries**, not just fire-and-forget (use pg_net for that).

## Mobile app patterns that benefit from queues

- **AI image generation** — queue the job, poll for completion
- **Email / push campaigns** — fan-out to thousands of users without blocking the request
- **Webhook delivery to third parties** — retry on failure
- **PDF/report generation** — heavy async work kicked off by user action
- **RevenueCat event processing** — ensure every webhook is processed exactly once

## Setup

```sql
create extension if not exists pgmq;

-- Create queues for your app
select pgmq.create('ai_jobs');
select pgmq.create('email_queue');
select pgmq.create('push_notifications');
```

## Producer: enqueue from Edge Function

```ts
// User initiates an AI image generation
Deno.serve(async (req) => {
  const { prompt, style } = await req.json();
  const userId = (await getUserFromJWT(req)).id;

  // Enqueue the job
  const { data } = await adminClient.schema('pgmq').rpc('send', {
    queue_name: 'ai_jobs',
    msg: { type: 'image_generation', user_id: userId, prompt, style },
  });

  return Response.json({ job_id: data[0], status: 'queued' });
});
```

## Consumer: Edge Function worker (called by pg_cron)

```ts
// supabase/functions/process-ai-jobs/index.ts
Deno.serve(async () => {
  // Read up to 5 messages, hide from other consumers for 60s
  const { data: messages } = await adminClient.schema('pgmq').rpc('read', {
    queue_name: 'ai_jobs',
    sleep_seconds: 60,
    n: 5,
  });

  for (const msg of messages ?? []) {
    try {
      await processAIJob(msg.message);

      // Delete on success
      await adminClient.schema('pgmq').rpc('delete', {
        queue_name: 'ai_jobs',
        msg_id: msg.msg_id,
      });
    } catch (err) {
      console.error('Job failed, will retry:', msg.msg_id, err);
      // Don't delete — message reappears after 60s visibility timeout
    }
  }

  return Response.json({ processed: messages?.length ?? 0 });
});
```

Schedule the worker via pg_cron:

```sql
select cron.schedule(
  'process-ai-jobs',
  '*/1 * * * *',  -- every minute
  $$
    select net.http_post(
      url := current_setting('app.supabase_url') || '/functions/v1/process-ai-jobs',
      headers := jsonb_build_object(
        'Authorization', 'Bearer ' || current_setting('app.service_key')
      ),
      body := '{}'::jsonb
    )
  $$
);
```

## Producer: enqueue from a DB trigger

```sql
create or replace function enqueue_welcome_email()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  perform pgmq.send(
    'email_queue',
    jsonb_build_object(
      'type', 'welcome',
      'user_id', NEW.id,
      'email', NEW.email
    )
  );
  return NEW;
end;
$$;

create trigger on_profile_created
  after insert on profiles
  for each row execute function enqueue_welcome_email();
```

## Monitor queue depth

```sql
-- All queues health check
select * from pgmq.metrics_all();
-- queue_name | queue_depth | newest_msg_age_sec | oldest_msg_age_sec | total_messages

-- If oldest_msg_age_sec > 300 on a 1-minute worker, something is stuck
```

## Delayed messages (push reminders, trial ending)

```sql
-- Send a "trial ending" push in 6 days
select pgmq.send(
  'push_notifications',
  jsonb_build_object('type', 'trial_ending', 'user_id', user_id),
  delay := 518400  -- 6 days in seconds
);
```

## Key differences: queues vs pg_net vs pg_cron

| | pgmq (Queues) | pg_net | pg_cron |
|---|---|---|---|
| Delivery guarantee | At-least-once | Fire-and-forget | At-most-once per schedule |
| Retries | Yes (visibility timeout) | No | No |
| Delay/schedule | Yes (per message) | No | Yes (cron schedule) |
| Use for | Heavy async jobs | Simple webhooks | Recurring maintenance |

## Deep reference

SQL-level API, DLQ patterns, batch sends, archive vs delete → [supabase-postgres-best-practices: ext-pgmq](../../supabase-postgres-best-practices/rules/ext-pgmq.md).
