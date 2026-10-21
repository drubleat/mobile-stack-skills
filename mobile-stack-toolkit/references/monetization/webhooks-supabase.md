---
title: "RevenueCat webhook reconciliation"
impact: CRITICAL
impactDescription: "Prevent unauthorized access and incorrect state transitions"
tags: security, correctness
---

# RevenueCat webhook reconciliation

A webhook signals that server-side entitlement state may have changed. Do not derive access with an event-type allowlist: cancellation can leave paid access active, billing issues can include grace periods, transfers affect multiple identities, and events may be duplicated or arrive out of order.

## Receiver and worker contract

1. Accept POST only. Require a configured secret and compare the configured Authorization value before parsing. Reject malformed envelopes; validate `event.id`, `event.type`, and environment.
2. Persist the event durably with a unique event ID before returning HTTP 200. On storage failure return a non-200 status so RevenueCat retries. Process asynchronously only after durable acceptance; an in-memory fire-and-forget promise is insufficient.
3. Resolve RevenueCat IDs/aliases to internal accounts. Anonymous IDs are not UUIDs. A `TRANSFER` event uses transferred identity lists and needs reconciliation of both sides. Record unresolved mappings for retry; never default an unknown product or identity to `pro`.
4. Serialize reconciliation per customer. Fetch current subscriber state from RevenueCat using a server-only API key, rather than applying event fields as truth. Honor HTTP errors, timeouts, 429 backoff, and environment separation. Serialize the fetch **and** write, or use a fenced lease/version check to prevent an older fetch from overwriting a newer one.
5. Replace that customer's entitlement projection atomically, including removals. Store one row per `(user_id, entitlement)` with expiry/grace information and the last successful verification time. Mark the inbox event processed only after the projection commit succeeds.

This is a workflow contract, not a ready-to-deploy receiver. Implement the inbox, identity mapping, and worker for the project's database and RevenueCat API version, then test failure/replay behavior.

## Access semantics

- `CANCELLATION`: inspect current entitlement state; neither unconditional revocation nor unconditional activation is safe (refunds differ from stopping renewal).
- `BILLING_ISSUE`: do not revoke solely on the event; grace depends on the store configuration and current state.
- `EXPIRATION`: reconcile all entitlements; another purchase or grant may still provide access.
- Non-renewing purchases, promotional entitlements, product changes, refunds, and transfers require the same reconciliation path.
- Keep sandbox events/projections separate from production paid access.

## Supabase deployment

External webhooks do not carry a Supabase user JWT. Configure only this function with `verify_jwt = false`, and authenticate the webhook in its handler. Keep `RC_WEBHOOK_SECRET`, RevenueCat secret API credentials, and the Supabase admin key on the server.

The client can read its own projection through RLS, but cannot insert/update it. For paid actions, enforce the expected entitlement, valid expiry (or explicitly verified lifetime access), and a bounded freshness policy. On an unavailable/stale projection, reconcile or return a retryable error; never grant indefinite access from an old boolean.

## Required scenario checks

Purchase → cancellation before expiry; billing retry with grace; eventual expiry; refund; lifetime grant; duplicate event; reversed event order; two concurrent events; database/API failure; TEST event; anonymous ID; account transfer; sandbox isolation. Test a successful durable enqueue separately from a successful entitlement update.

Related: [Server gating](entitlement-checks.md), [schema design](../supabase/schema-design.md).

## Sources

Reviewed 2026-10-20: [RevenueCat webhook handling](https://www.revenuecat.com/docs/integrations/webhooks), [grace periods](https://www.revenuecat.com/docs/subscription-guidance/how-grace-periods-work).
