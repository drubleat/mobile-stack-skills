---
title: "Superwall for Flutter"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Superwall for Flutter

Select the SDK matching the framework (`expo-superwall` or `superwallkit_flutter`) and resolve a compatible version. Configure platform public keys once, identify/reset according to the authenticated user's lifecycle, and test native builds on supported platforms.

A placement controls presentation and can run its feature callback when no campaign matches or when a paywall is configured as non-gating. That callback is not proof of a paid entitlement. Backend authorization remains independent. Never detect active state with `status.toString().contains('active')`: it also matches “inactive”. Use the SDK's typed status and the specific entitlement.

When integrating RevenueCat, choose one documented purchase owner: an observer/completed-by-app configuration or a complete custom PurchaseController. A class containing only configure/status-listening methods does not implement purchasing/restoration. Map success, cancellation, pending and failure results, seed initial subscription status, retain callback references and remove listeners on disposal.

Keep server entitlements synchronized through [verified webhooks](webhooks-supabase.md). Do not union arbitrary unverified client flags into premium access. Use the official SDK-specific sample for the installed version; do not mix native singleton calls, Expo hooks and Flutter classes in one integration.

Test missing campaign, presentation failure, restore, pending purchase, account switch, expired access and offline behavior. Validate incoming deep links before forwarding them to the SDK. Remote paywall changes still need review for accurate price, eligibility and terms.

## Sources

Reviewed 2026-10-20: [SDK integration](https://superwall.com/docs/flutter/guides/using-revenuecat).
