---
title: "Purchase testing and webhook failure cases"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Purchase testing and webhook failure cases

Use RevenueCat Test Store for early UI iteration and platform sandboxes before release. The Test Store key is separate; normal platform public SDK keys handle store sandbox/production purchases according to the store environment. A development build does not need an invented separate Apple/Google sandbox SDK key.

For Apple, distinguish local StoreKit configuration, development sandbox accounts and TestFlight. They do not all exercise identical server receipt behavior. Renewal timing and account settings are configurable/version-sensitive; use the current store test controls. For Google, configure license testers and the intended test track/account. Verify that transactions are marked test before proceeding.

Exercise: initial purchase, renewal, cancellation while access remains, expiry, grace/billing recovery, refund/revocation, restore, anonymous-to-identified transition, account switch and transfer. Test missing offerings, pending payment, network loss and app termination. Use actual offer eligibility and localized prices.

For the backend, replay duplicate and reordered events, fail processing after durable acceptance, retry a failed reconciliation, and deliver an old event after a newer one. Verify aliases cannot grant another account access, sandbox cannot grant production benefits, expired cached access is bounded, and failed dependencies do not silently unlock paid work. See [webhook design](webhooks-supabase.md).

Inspect event IDs and delivery logs without logging secrets/receipts. Confirm the exact installed build and store account; test store purchases and real production transactions must remain distinguishable.

## Sources

Reviewed 2026-10-20: [sandbox testing](https://www.revenuecat.com/docs/test-and-launch/sandbox), [webhooks](https://www.revenuecat.com/docs/integrations/webhooks).
