---
title: "AI app: access, quota and release sequence"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# AI app: access, quota and release sequence

Choose trial/free/paid behavior from the product requirement; a hard paywall is not a universal default. Preserve the existing backend and select models through measured quality, latency and cost tests rather than unsourced price ratios.

1. Implement the core feature with [server credentials](../ai/edge-proxy-architecture.md), bounded inputs/output and cancellation.
2. Add [guardrails](../ai/guardrails.md), using its single quota SQL asset. Do not create another function with the same signature and an incompatible return type. Paid users still need spend limits.
3. Configure [RevenueCat identity](../monetization/sdk-integration.md) and [webhook reconciliation](../monetization/webhooks-supabase.md). Distinguish subscription entitlement from usage quota.
4. Enforce paid access on the server before reserving quota/calling the provider. Treat dependency failures as unavailable, not free access. Use explicit 401/403/429/503 responses with a stable app error contract.
5. Build a paywall using localized store prices and actual offer eligibility. Test purchase, restore, cancellation, grace period, refund and delayed/reordered webhooks.
6. Measure completion, latency, failure and cost with redacted events. Separate purchase intent, verified purchase and consumption metrics.

Sharing is opt-in and should preview the content. Referrals need server-validated eligibility, fraud controls and atomic reward deduplication. Show only genuine usage counts, reviews, discounts and deadlines. Schedule reminders from actual entitlement dates and user preferences, not fixed guesses from install day.

Before release, run the [store sequence](zero-to-store.md). No duplicate schema or pseudo-complete proxy lives in this playbook: load only the domain reference needed for the next step.

## Sources

Reviewed 2026-10-20: [RevenueCat webhooks](https://www.revenuecat.com/docs/integrations/webhooks), [OpenAI production practices](https://developers.openai.com/api/docs/guides/production-best-practices).
