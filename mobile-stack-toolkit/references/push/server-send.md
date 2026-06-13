---
title: Sending push from the server
impact: HIGH
impactDescription: "Push must originate server-side to keep FCM server keys off the client; Edge Functions are the correct trigger point"
tags: push, server, edge-functions, fcm, expo-push
---

# Sending push from the server

Push sending always happens server-side — never from the mobile client (you'd expose FCM server keys). Send from an Edge Function triggered by a user action, a cron job, or a DB event.

## Via Expo Push API (if using Expo Push tokens)

```ts
// supabase/functions/send-push/index.ts
async function sendExpoPush(token: string, title: string, body: string, data?: object) {
  const res = await fetch('https://exp.host/--/api/v2/push/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify([{ to: token, title, body, data, sound: 'default', priority: 'high' }]),
  });
  const { data: [result] } = await res.json();
  if (result.status === 'error') {
    if (result.details?.error === 'DeviceNotRegistered') {
      // Token is stale — delete it from profiles
      await supabase.from('profiles').update({ push_token: null }).eq('push_token', token);
    }
  }
}
```

## Via FCM HTTP v1 API (if using FCM tokens)

```ts
// Requires a Google service account access token
// Use firebase-admin SDK or raw HTTP
import { initializeApp, cert } from 'npm:firebase-admin/app';
import { getMessaging } from 'npm:firebase-admin/messaging';

const app = initializeApp({
  credential: cert(JSON.parse(Deno.env.get('FIREBASE_SERVICE_ACCOUNT')!)),
});

async function sendFCMPush(token: string, title: string, body: string, data?: Record<string, string>) {
  await getMessaging(app).send({
    token,
    notification: { title, body },
    data,                        // string values only in FCM data payload
    android: { priority: 'high' },
    apns: { payload: { aps: { sound: 'default' } } },
  });
}
```

Store the Firebase service account JSON in `supabase secrets set FIREBASE_SERVICE_ACCOUNT='...'`.

## Triggering from a Supabase cron job

```sql
-- In a migration: create a scheduled job (uses pg_cron extension)
select cron.schedule(
  'daily-reminder',
  '0 9 * * *',    -- 9am UTC daily
  $$
    select net.http_post(
      url := 'https://<ref>.supabase.co/functions/v1/send-daily-reminders',
      headers := '{"Authorization": "Bearer <service-role-key>"}'::jsonb
    )
  $$
);
```

Or use EAS Workflows / GitHub Actions to trigger on a schedule → [../cicd/eas-workflows.md](../cicd/eas-workflows.md).

## Triggering from a DB event (Postgres trigger)

Send a push when a new row is inserted (e.g. a new message in a chat):

```sql
create function notify_new_message() returns trigger
language plpgsql security definer as $$
begin
  perform net.http_post(
    url := 'https://<ref>.supabase.co/functions/v1/send-push',
    body := json_build_object('recipient_id', new.recipient_id, 'message', new.content)::text,
    headers := '{"Content-Type": "application/json", "Authorization": "Bearer <service-role-key>"}'
  );
  return new;
end; $$;

create trigger on_new_message
  after insert on public.messages
  for each row execute procedure notify_new_message();
```

Requires the `pg_net` extension (enabled by default in Supabase).

## Fan-out: send to multiple users

```ts
// In Edge Function: fetch all tokens for a user segment then batch send
const { data: users } = await supabase
  .from('profiles')
  .select('push_token')
  .not('push_token', 'is', null)
  .eq('subscription_status', 'active');   // example filter

const tokens = users.map(u => u.push_token).filter(Boolean);

// Expo: batch up to 100 per request
for (let i = 0; i < tokens.length; i += 100) {
  const batch = tokens.slice(i, i + 100).map(token => ({
    to: token, title, body, data, sound: 'default',
  }));
  await fetch('https://exp.host/--/api/v2/push/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(batch),
  });
}
```
