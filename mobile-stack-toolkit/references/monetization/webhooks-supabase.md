---
title: RevenueCat webhook → Supabase Edge Function → subscriptions table
impact: HIGH
impactDescription: "CANCELLATION keeps is_active=true (grace period); only EXPIRATION sets it false — getting this wrong blocks paying users"
tags: revenuecat, webhook, supabase, edge-functions, subscriptions
---

# Webhook → Supabase Edge Function → subscriptions table

RevenueCat sends purchase events (new subscription, renewal, cancellation, expiry) to an HTTPS endpoint you control. This is how your server learns about subscription state without trusting the client.

## Set up the webhook in RC

RC Dashboard → Project → Integrations → Webhooks → Add:
- **URL**: `https://<ref>.supabase.co/functions/v1/revenuecat-webhook`
- **Authentication header**: set a secret header (e.g. `Authorization: Bearer <your-webhook-secret>`) — you generate this string.
- **Events**: at minimum: `INITIAL_PURCHASE`, `RENEWAL`, `CANCELLATION`, `EXPIRATION`, `UNCANCELLATION`, `BILLING_ISSUE`.

## Edge Function

```ts
// supabase/functions/revenuecat-webhook/index.ts
import { createClient } from 'jsr:@supabase/supabase-js@2';

const WEBHOOK_SECRET = Deno.env.get('RC_WEBHOOK_SECRET')!;

Deno.serve(async (req) => {
  // 1. Verify it's actually from RevenueCat
  const auth = req.headers.get('Authorization');
  if (auth !== `Bearer ${WEBHOOK_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  const event = await req.json();
  const { event: { type, app_user_id, product_id, expiration_at_ms, store } } = event;

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,   // bypasses RLS — this is a server-only function
  );

  // 2. Determine entitlement status
  const isActive = ['INITIAL_PURCHASE', 'RENEWAL', 'UNCANCELLATION'].includes(type);

  // 3. Upsert into subscriptions
  await supabase.from('subscriptions').upsert({
    user_id: app_user_id,               // works because we called Purchases.logIn(user.id)
    rc_app_user_id: app_user_id,
    entitlement: 'pro',                 // map from product_id if you have multiple tiers
    is_active: isActive,
    product_id,
    store,
    current_period_end: expiration_at_ms ? new Date(expiration_at_ms).toISOString() : null,
    updated_at: new Date().toISOString(),
  }, { onConflict: 'user_id' });

  return new Response('ok', { status: 200 });
});
```

Deploy with JWT verification off (RC doesn't send a Supabase JWT):
```bash
supabase functions deploy revenuecat-webhook --no-verify-jwt
supabase secrets set RC_WEBHOOK_SECRET=your-generated-secret
```

## Event types and what they mean

| Event | `is_active` | Meaning |
|---|---|---|
| `INITIAL_PURCHASE` | ✅ true | First purchase / trial start |
| `RENEWAL` | ✅ true | Subscription renewed successfully |
| `UNCANCELLATION` | ✅ true | User re-enabled after cancelling |
| `CANCELLATION` | ⚠️ still true | User cancelled but period hasn't ended yet |
| `EXPIRATION` | ❌ false | Period ended, subscription lapsed |
| `BILLING_ISSUE` | ❌ false | Payment failed; RC will retry (grace period) |
| `PRODUCT_CHANGE` | depends | User changed plan |

**Important:** `CANCELLATION` does not mean access is revoked — it means the next renewal won't happen. The user keeps access until `EXPIRATION`. Set `is_active = true` on CANCELLATION; only set it false on EXPIRATION / BILLING_ISSUE.

## Multiple entitlement tiers

If you have `pro` and `enterprise` tiers, map `product_id` → entitlement in the webhook:

```ts
const PRODUCT_TO_ENTITLEMENT: Record<string, string> = {
  'pro_monthly': 'pro',
  'pro_annual': 'pro',
  'enterprise_monthly': 'enterprise',
};
const entitlement = PRODUCT_TO_ENTITLEMENT[product_id] ?? 'pro';
```

## Without Supabase

Same pattern works with any server: Firebase Cloud Function, a Next.js API route, any HTTP endpoint. Replace the Supabase client with your DB client. The RC webhook payload and authentication logic stay identical.
