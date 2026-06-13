---
title: Paywalls: RC remote vs custom UI
impact: HIGH
impactDescription: "RC remote paywalls update without App Review; custom UI gives full design control but requires manual A/B testing"
tags: revenuecat, paywall, ui, conversion
---

# Paywalls: RC remote vs custom UI

Two approaches to showing a paywall. Pick one; don't mix them in the same app.

## Option A — RC remote Paywalls (react-native-purchases-ui)

RC's built-in paywall system lets you design and update paywalls from the RC dashboard without a code change or store release.

```tsx
import RevenueCatUI, { PAYWALL_RESULT } from 'react-native-purchases-ui';

export async function presentPaywall(): Promise<boolean> {
  const result = await RevenueCatUI.presentPaywall();
  return result === PAYWALL_RESULT.PURCHASED || result === PAYWALL_RESULT.RESTORED;
}

// Or as a component (for embedding in a screen)
import { RevenueCatUI } from 'react-native-purchases-ui';
<RevenueCatUI.PaywallView onDismiss={() => navigation.goBack()} />
```

**When to use RC Paywalls:**
- You want to A/B test paywall designs without code deploys.
- You want non-developers (marketing, design) to update copy and pricing display.
- You need to ship fast and don't have a design system for a paywall yet.
- The default RC paywall templates fit your app's style.

**Limitations:**
- Less control over layout — you're constrained to RC's templates.
- Harder to integrate deeply with your app's design system/theme.
- RC Paywalls requires `react-native-purchases-ui` (separate package).

## Option B — Custom paywall UI

Build the paywall yourself using RC data to drive the content:

```tsx
import { useEffect, useState } from 'react';
import Purchases, { PurchasesOffering, PurchasesPackage } from 'react-native-purchases';

export function CustomPaywall({ onSuccess }: { onSuccess: () => void }) {
  const [offering, setOffering] = useState<PurchasesOffering | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Purchases.getOfferings().then(o => setOffering(o.current));
  }, []);

  const handlePurchase = async (pkg: PurchasesPackage) => {
    setLoading(true);
    try {
      const { customerInfo } = await Purchases.purchasePackage(pkg);
      if (customerInfo.entitlements.active['pro']) onSuccess();
    } catch (e: any) {
      if (!e.userCancelled) alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      {offering?.availablePackages.map(pkg => (
        <TouchableOpacity key={pkg.identifier} onPress={() => handlePurchase(pkg)}>
          <Text>{pkg.product.title}</Text>
          <Text>{pkg.product.priceString} / {pkg.packageType.toLowerCase()}</Text>
        </TouchableOpacity>
      ))}
      <TouchableOpacity onPress={() => Purchases.restorePurchases()}>
        <Text>Restore Purchases</Text>
      </TouchableOpacity>
    </View>
  );
}
```

**When to use custom UI:**
- Your app has a strong visual identity the RC templates can't match.
- You need complex layout (video, animated illustrations, feature comparison).
- You want full control over the conversion flow.

## Paywall UX must-haves (App Store compliance)

- **"Restore Purchases" button** — required by Apple. Must be visible and functional before purchase.
- **Price clearly displayed** — show the exact price and billing period (e.g. "£4.99/month").
- **Subscription terms visible** — "Subscription automatically renews unless cancelled" — link to terms/privacy.
- **Free trial clearly labeled** — "7-day free trial, then £4.99/month" on the button, not hidden.
- **Sign in with Apple** — if you show Google/email login behind the paywall, you must also offer Apple Sign-In (if on iOS).

Violating these is a common review rejection cause → [../store/rejection-redflags.md](../store/rejection-redflags.md).

## Entitlement → where to gate

```
Before paywall:  show teaser / preview
After purchase:  customerInfo.entitlements.active['pro'] → unlock UI
Server actions:  verify subscriptions table (not customerInfo from client)
```
