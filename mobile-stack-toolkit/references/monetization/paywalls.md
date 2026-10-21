---
title: "Paywall presentation and purchase state"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Paywall presentation and purchase state

Use RevenueCat's UI SDK or a custom screen populated from Offerings. The React Native UI module has a default `RevenueCatUI` export; its component is `RevenueCatUI.Paywall`, not `PaywallView`.

```ts
import RevenueCatUI from 'react-native-purchases-ui';
await RevenueCatUI.presentPaywallIfNeeded({ requiredEntitlementIdentifier: 'pro' });
```

Configure Purchases first and handle presentation/purchase errors. For custom UI, show loading, empty offerings and retry states; disable duplicate purchase taps. Read localized price and billing/trial terms from store product metadata, not `packageType.toLowerCase()` or hardcoded prices. Determine offer eligibility before displaying a trial claim.

After purchase/restore, inspect the returned CustomerInfo for the intended entitlement and update UI. A dismissed paywall does not imply a purchase. Keep a working restore flow and provide subscription management, terms and privacy links as required. Handle pending/deferred purchases and cancellation without misleading error messages.

Gate paid backend operations using verified server entitlement state and quota, not a client boolean. Account sign-in requirements vary by distribution policy; email-only login does not automatically require Apple Sign-In. See [store rules](../store/rejection-redflags.md) and [entitlement checks](entitlement-checks.md).

## Sources

Reviewed 2026-10-20: [displaying paywalls](https://www.revenuecat.com/docs/tools/paywalls/displaying-paywalls).
