---
title: RevenueCat SDK integration (react-native-purchases v10)
impact: CRITICAL
impactDescription: "Purchases.logIn(userId) MUST be called before any purchase; skipping this loses attribution and webhook correlation"
tags: revenuecat, sdk, iap, purchases, react-native
---

# RevenueCat SDK integration (react-native-purchases v10)

## Install

```bash
npx expo install react-native-purchases react-native-purchases-ui
```

Both packages require native code → Dev Build required. Add to `app.config.ts` plugins if a config plugin is provided (check RC docs — as of v10 it may be auto-linked).

## Configure (once, at app startup)

```ts
// lib/revenuecat.ts
import Purchases, { LOG_LEVEL, PurchasesConfiguration } from 'react-native-purchases';
import { Platform } from 'react-native';

const API_KEYS = {
  ios:     'appl_xxxxxxxxxxxxxxxxxxxxxxxxxxxx',
  android: 'goog_xxxxxxxxxxxxxxxxxxxxxxxxxxxx',
};

export function configureRevenueCat(userId?: string) {
  const apiKey = Platform.OS === 'ios' ? API_KEYS.ios : API_KEYS.android;

  Purchases.setLogLevel(LOG_LEVEL.DEBUG);   // remove in production or set to ERROR

  const config = PurchasesConfiguration.builder(apiKey)
    .setAppUserID(userId ?? null)           // null = RC generates anonymous ID
    .build();

  Purchases.configure(config);
}
```

Call `configureRevenueCat()` early in your app lifecycle — before any purchase or entitlement check. If you have a logged-in user at startup, pass their ID immediately.

## Align RC App User ID with your auth ID

```ts
// After the user signs in (Supabase, Firebase, or any auth)
const { data: { user } } = await supabase.auth.getSession();
if (user) {
  await Purchases.logIn(user.id);   // aligns RC identity with your backend
}

// On sign out
await Purchases.logOut();           // RC resets to anonymous ID
```

`logIn` is the critical call. Without it, RC uses an anonymous ID that can't be matched to your user records when the webhook fires. With it, `webhook.app_user_id === supabase_user.id` — trivial upsert.

## Fetch the current offering

```ts
import Purchases, { PurchasesOffering } from 'react-native-purchases';

export async function getCurrentOffering(): Promise<PurchasesOffering | null> {
  const offerings = await Purchases.getOfferings();
  return offerings.current;
}
```

The offering contains packages; each package has `product.priceString`, `product.title`, `packageType` (`MONTHLY`, `ANNUAL`, `LIFETIME`). Use this to build your paywall UI.

## Purchase a package

```ts
import Purchases, { PurchasesPackage } from 'react-native-purchases';

export async function purchasePackage(pkg: PurchasesPackage) {
  try {
    const { customerInfo } = await Purchases.purchasePackage(pkg);
    const isPro = customerInfo.entitlements.active['pro'] !== undefined;
    return { success: true, isPro };
  } catch (e: any) {
    if (!e.userCancelled) {
      // real error — show to user
      throw e;
    }
    return { success: false, isPro: false };
  }
}
```

Always check `e.userCancelled` — a cancelled purchase is not an error; don't show an error dialog for it.

## Restore purchases

Required by App Store guideline (must have a "Restore Purchases" button):

```ts
const customerInfo = await Purchases.restorePurchases();
const isPro = customerInfo.entitlements.active['pro'] !== undefined;
```

## Key types

```ts
CustomerInfo        // the main object — always use .entitlements.active to check access
PurchasesOffering   // current offering with its packages
PurchasesPackage    // one package (monthly, annual, etc.) with a StoreProduct inside
StoreProduct        // title, description, priceString, currencyCode, price
```

## Common pitfalls

- **Not calling `logIn` after auth** → RC creates a separate anonymous profile; webhook can't match users.
- **Checking `customerInfo.activeSubscriptions` instead of `entitlements.active`** → product-level check breaks if you rename products or add trial periods. Always use entitlements.
- **Not handling `userCancelled`** → showing "Purchase failed" when the user just tapped Cancel is a common bad UX.
- **Calling `configure` multiple times** → once per app launch only; subsequent calls are no-ops but messy.
