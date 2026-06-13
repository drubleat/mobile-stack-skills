---
title: Superwall — Expo/React Native paywall SDK
impact: HIGH
impactDescription: "Superwall lets you A/B test and change paywalls remotely without a release; wrong setup blocks purchases or silently skips paywalls"
tags: superwall, monetization, paywall, expo, react-native, revenuecat, iap
---

# Superwall — Expo / React Native

Superwall is a paywall management SDK: you design paywalls in the Superwall dashboard, trigger them from code via "placements", and control which users see which paywall remotely. Works with RevenueCat (recommended) or standalone.

**Package:** `expo-superwall` (replaces the deprecated `@superwall/react-native-superwall`)  
**Version:** 1.1.4 (as of June 2026)  
**Requires:** Expo SDK 53+, iOS 16.4+, Android API 21+

---

## Install

```bash
npx expo install expo-superwall
```

Requires a **Dev Build** — not compatible with Expo Go.

```bash
npx eas build --profile development --platform all
```

---

## Setup — root layout

Wrap your root layout with `SuperwallProvider`. Get your API keys from the Superwall dashboard.

```tsx
// app/_layout.tsx
import { SuperwallProvider } from 'expo-superwall';

export default function RootLayout() {
  return (
    <SuperwallProvider
      apiKeys={{
        ios: 'pk_your_ios_key',
        android: 'pk_your_android_key',
      }}
    >
      <Stack />
    </SuperwallProvider>
  );
}
```

---

## Triggering a paywall — `usePlacement`

Paywalls are shown by registering a "placement" — a named event you create in the Superwall dashboard. Superwall decides whether to show a paywall based on your campaign rules.

```tsx
import { usePlacement } from 'expo-superwall';

export function UpgradeButton() {
  const { registerPlacement } = usePlacement({
    onError: (err) => console.error('Superwall error:', err),
    onPresent: (paywallInfo) => console.log('Paywall shown:', paywallInfo),
    onDismiss: (paywallInfo, result) => console.log('Dismissed:', result),
  });

  return (
    <Button
      title="Go Pro"
      onPress={() => registerPlacement({ placement: 'upgrade_tapped' })}
    />
  );
}
```

---

## Feature gating

Pass a `feature` callback — it runs only if the user is already subscribed (or dismisses the paywall as "purchased"). This is the primary pattern for gating premium features.

```tsx
const { registerPlacement } = usePlacement({
  onError: (err) => console.error(err),
});

async function openAIFeature() {
  await registerPlacement({
    placement: 'ai_feature_gate',
    feature: () => {
      // Only called when the user has access
      router.push('/ai-feature');
    },
  });
}
```

---

## User identification

Call `identify` after login so Superwall can target by user ID and track across devices. Call `reset` on logout.

```ts
import Superwall from 'expo-superwall';

// After auth
await Superwall.shared.identify('user_uuid_here');

// Optional: send attributes for campaign targeting
await Superwall.shared.setUserAttributes({
  plan: 'free',
  daysActive: 5,
});

// On logout
await Superwall.shared.reset();
```

---

## RevenueCat integration

When using RevenueCat alongside Superwall, Superwall needs to know the subscription status. Pass a purchase controller at configuration time instead of relying on auto-detection.

```tsx
// app/_layout.tsx
import { SuperwallProvider, PurchaseController, SubscriptionStatus } from 'expo-superwall';
import Purchases, { LOG_LEVEL } from 'react-native-purchases';

class RCPurchaseController extends PurchaseController {
  async configure() {
    await Purchases.setLogLevel(LOG_LEVEL.DEBUG);
    await Purchases.configure({
      apiKey: Platform.OS === 'ios' ? 'appl_xxx' : 'goog_xxx',
    });
    Purchases.addCustomerInfoUpdateListener((info) => {
      const isActive = Object.keys(info.entitlements.active).length > 0;
      Superwall.shared.setSubscriptionStatus(
        isActive ? SubscriptionStatus.active : SubscriptionStatus.inactive,
      );
    });
  }
}

const purchaseController = new RCPurchaseController();

export default function RootLayout() {
  useEffect(() => {
    purchaseController.configure();
  }, []);

  return (
    <SuperwallProvider
      apiKeys={{ ios: 'pk_ios_key', android: 'pk_android_key' }}
      purchaseController={purchaseController}
    >
      <Stack />
    </SuperwallProvider>
  );
}
```

---

## Subscription status widget

Read live subscription status in any component:

```tsx
import { useSuperwallSubscriptionStatus } from 'expo-superwall';

export function StatusBadge() {
  const status = useSuperwallSubscriptionStatus();
  return <Text>{status === 'active' ? 'PRO' : 'Free'}</Text>;
}
```

---

## Deep linking (restore paywalls from URL)

```tsx
import Superwall from 'expo-superwall';
import * as Linking from 'expo-linking';

useEffect(() => {
  const sub = Linking.addEventListener('url', ({ url }) => {
    Superwall.shared.handleDeepLink(new URL(url));
  });
  return () => sub.remove();
}, []);
```

---

## Dashboard setup

1. Create a **placement** in Superwall dashboard (e.g. `upgrade_tapped`)
2. Create a **paywall** with your design
3. Create a **campaign** that maps the placement → paywall (with optional audience rules)
4. Deploy — no app release needed to change which paywall shows

---

## Gotchas

- `expo-superwall` requires a **Dev Build**. If your team uses Expo Go, plan the migration.
- `registerPlacement` is async. Await it; the `feature` callback fires before the promise resolves.
- In `__DEV__` mode, Superwall shows a "debug" overlay by default. Disable with `options.testModeBehavior = TestModeBehavior.never` if it's disruptive.
- If no campaign matches a placement, Superwall silently executes the `feature` callback directly — the user never sees a paywall. This is correct behavior (means they already have access, or you have no campaign configured yet).
