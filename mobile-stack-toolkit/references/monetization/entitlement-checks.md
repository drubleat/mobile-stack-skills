---
title: "Entitlement checks & feature gating"
impact: CRITICAL
impactDescription: "Client-only entitlement checks can be bypassed; server-side verification via subscriptions table is required for paywalled AI features"
tags: revenuecat, entitlements, feature-gating, security, subscriptions
---

# Entitlement checks & feature gating

## The two-layer model

| Layer | What checks | Source of truth |
|---|---|---|
| **Client (UI gating)** | Show/hide features, navigate to paywall | `CustomerInfo.entitlements.active` from RC SDK |
| **Server (action gating)** | Actually execute premium functionality | `subscriptions` table in your DB (written by webhook) |

Never collapse these. The client layer is UX; the server layer is security.

## Client-side hook pattern

```ts
// hooks/useEntitlement.ts
import { useEffect, useState } from 'react';
import Purchases, { CustomerInfo } from 'react-native-purchases';

export function useEntitlement(entitlementId: string) {
  const [isActive, setIsActive] = useState(false);
  const [customerInfo, setCustomerInfo] = useState<CustomerInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch current state
    let disposed = false;
    Purchases.getCustomerInfo().then(info => {
      if (disposed) return;
      setCustomerInfo(info);
      setIsActive(!!info.entitlements.active[entitlementId]);
      setLoading(false);
    }).catch(() => {
      if (!disposed) { setIsActive(false); setLoading(false); }
      // Surface a retry state in the screen; failure does not grant access.
    });

    // Subscribe to changes (purchase, restore, expiry)
    const listener = (info: CustomerInfo) => {
      if (disposed) return;
      setCustomerInfo(info);
      setIsActive(!!info.entitlements.active[entitlementId]);
    };
    Purchases.addCustomerInfoUpdateListener(listener);
    return () => { disposed = true; Purchases.removeCustomerInfoUpdateListener(listener); };
  }, [entitlementId]);

  return { isActive, customerInfo, loading };
}
```

```tsx
// Usage
const { isActive: isPro, loading } = useEntitlement('pro');

if (loading) return <ActivityIndicator />;
if (!isPro) return <PaywallPrompt />;
return <PremiumFeature />;
```

## What to gate (and what not to)

**Gate in UI (client):**
- Navigation to premium screens
- Showing/hiding premium UI elements
- Triggering a paywall modal

**Gate on the server (Edge Function / Cloud Function):**
- AI API calls
- Generating exportable content
- Any feature that consumes server-side resources or costs money

**Don't gate on the server:**
- Read-only queries that are equally available to all users
- Pure UI cosmetics

## Server-side gate example (Supabase Edge Function)

```ts
// In ai-proxy/index.ts — before calling OpenAI
const { data: sub, error } = await supabase
  .from('subscriptions')
  .select('is_active, entitlement, current_period_end, verified_at')
  .eq('user_id', user.id)
  .eq('entitlement', 'pro')
  .maybeSingle();

if (error) return new Response('Entitlements unavailable', { status: 503, headers: cors });
const expiry = sub?.current_period_end ? Date.parse(sub.current_period_end) : null;
const verified = sub?.verified_at ? Date.parse(sub.verified_at) : NaN;
const fresh = Number.isFinite(verified) && Date.now() - verified < 5 * 60_000;
// Null expiry means lifetime only when explicitly verified by the server projection.
if (!fresh) return new Response('Entitlement refresh required', { status: 503, headers: cors });
if (!sub?.is_active || (expiry !== null && !(expiry > Date.now()))) {
  return new Response('Subscription required', { status: 403, headers: cors });
}
```

The `subscriptions` table is written by the RevenueCat webhook → [webhooks-supabase.md](webhooks-supabase.md). If not using Supabase, the equivalent is a Firestore doc, a Postgres row in your own DB, or a Redis key — same principle.

## CustomerInfo fields worth knowing

```ts
customerInfo.entitlements.active           // { 'pro': EntitlementInfo } if active
customerInfo.entitlements.all              // includes expired
customerInfo.activeSubscriptions           // Array of active product IDs (don't use for gating)
customerInfo.latestExpirationDate          // ISO date string | null
customerInfo.firstSeen                     // when this RC user was first seen
customerInfo.originalAppUserId            // the ID passed to logIn(), or RC's anonymous ID
```

Use `entitlements.active` for gating, not `activeSubscriptions`. Entitlements survive product renames, free trials, and promotional grants; product IDs don't.

## Expiration & grace period

If a subscription lapses (failed payment), the store may apply a configured grace period. During grace, `entitlement.isActive` stays `true` — the user keeps access while the store retries billing. After the grace period, the entitlement expires. Handle the expiry gracefully in UI; don't hard-block immediately.

## Promotional entitlements

RC can grant entitlements manually (for support, beta testers, comp subscriptions) from the dashboard without a store purchase. These show up in `entitlements.active` just like real purchases — your gating code needs no changes.
