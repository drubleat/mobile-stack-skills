---
title: Monetization — domain index (RevenueCat)
impact: MEDIUM-HIGH
impactDescription: "Routes to SDK integration, entitlement checks, paywalls, webhooks, dashboard setup, and testing"
tags: revenuecat, monetization, iap, subscriptions, index
---

# Monetization — RevenueCat index

RevenueCat abstracts App Store/Play Store IAP complexity: receipt validation, entitlements, webhooks, A/B testing — all in one SDK. Use it even if your backend is Supabase, Firebase, or anything else.

## Core concepts

```
Product (App Store/Play) → Package (RC grouping) → Offering (what you show) → Entitlement (what's unlocked)
```

- **Product**: defined in App Store Connect / Play Console (e.g. `pro_monthly_4.99`).
- **Package**: RC wraps a product with a semantic label (`monthly`, `annual`, `lifetime`).
- **Offering**: a named set of packages you show in your paywall. The *current* offering is what your app fetches and displays. You can change it remotely without a release.
- **Entitlement**: the access level a user has (e.g. `pro`). RC maps products → entitlements. Your app checks the entitlement, not the product SKU.

This indirection is the key value: you never hardcode product IDs in gating logic. Check `entitlement("pro").isActive`, and RC handles which product gave it.

## Router

| Task | File |
|---|---|
| Connect App Store Connect + Play Console to RC | [dashboard-setup.md](dashboard-setup.md) |
| Initialize `react-native-purchases` (v10) in the app | [sdk-integration.md](sdk-integration.md) |
| Show a paywall (RC remote vs custom UI) | [paywalls.md](paywalls.md) |
| Gate features on entitlements in code | [entitlement-checks.md](entitlement-checks.md) |
| Sync subscription events to Supabase (or any backend) | [webhooks-supabase.md](webhooks-supabase.md) |
| Test purchases without spending real money | [testing.md](testing.md) |
| Remote paywall A/B testing (Expo/RN) with Superwall | [superwall.md](superwall.md) |
| Remote paywall A/B testing (Flutter) with Superwall | [superwall-flutter.md](superwall-flutter.md) |

**Flutter / purchases_flutter?** → [../flutter/revenuecat-flutter.md](../flutter/revenuecat-flutter.md)

## Without Supabase

RevenueCat works independently of your backend. If you're not using Supabase, skip `webhooks-supabase.md`. The SDK handles entitlement state client-side. You only need a webhook receiver if you want server-side gating (Edge Function, Firebase Cloud Function, or any HTTPS endpoint RevenueCat can POST to).

## The golden rule

> **Never trust client-reported entitlement state for server-side decisions.**

The mobile SDK is for UI gating only. For any server action that costs you money (AI call, premium feature execution), verify against your server's subscription record — not `CustomerInfo` the client sent.
