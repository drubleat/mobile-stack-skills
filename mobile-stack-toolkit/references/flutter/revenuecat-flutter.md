---
title: RevenueCat Flutter: purchases_flutter 10.x
impact: HIGH
impactDescription: "Same logIn requirement as RN SDK: call before purchase or lose attribution; entitlement check pattern is identical"
tags: flutter, revenuecat, iap, subscriptions, purchases
---

# RevenueCat Flutter: purchases_flutter

Version: `purchases_flutter: ^10.2.3`

## Configuration

```dart
import 'package:purchases_flutter/purchases_flutter.dart';
import 'dart:io' show Platform;

Future<void> configureRevenueCat(String? userId) async {
  await Purchases.setLogLevel(LogLevel.debug); // Remove in production

  final config = PurchasesConfiguration(
    Platform.isIOS ? 'appl_YOUR_IOS_KEY' : 'goog_YOUR_ANDROID_KEY',
  )..appUserID = userId;  // CRITICAL: set Supabase user ID for webhook alignment

  await Purchases.configure(config);
}
```

Call after Supabase initializes so you have the user ID available. If the user isn't signed in yet, call `Purchases.logIn(userId)` after sign-in:

```dart
// After sign-in
final session = await supabase.auth.signIn(...);
await Purchases.logIn(session.user.id);
```

## Fetch offerings and display paywall

```dart
Future<Offerings?> getOfferings() async {
  try {
    return await Purchases.getOfferings();
  } on PlatformException catch (e) {
    debugPrint('Offerings error: $e');
    return null;
  }
}

// In widget
final offerings = await getOfferings();
final currentOffering = offerings?.current;
final packages = currentOffering?.availablePackages ?? [];

// Display packages
for (final package in packages) {
  final product = package.storeProduct;
  Text('${product.title} — ${product.priceString}');
}
```

## Purchase

```dart
Future<bool> purchase(Package package) async {
  try {
    final result = await Purchases.purchasePackage(package);
    final entitlements = result.customerInfo.entitlements.active;
    return entitlements.containsKey('pro');
  } on PlatformException catch (e) {
    final errorCode = PurchasesErrorHelper.getErrorCode(e);
    if (errorCode == PurchasesErrorCode.purchaseCancelledError) {
      return false;  // User cancelled — not an error
    }
    rethrow;
  }
}
```

## Check entitlement (client-side UI gating)

```dart
Future<bool> hasPro() async {
  final info = await Purchases.getCustomerInfo();
  return info.entitlements.active.containsKey('pro');
}
```

## Listen for entitlement changes

```dart
// In a Riverpod notifier or StatefulWidget
Purchases.addCustomerInfoUpdateListener((info) {
  final isPro = info.entitlements.active.containsKey('pro');
  ref.read(subscriptionStateProvider.notifier).update(isPro);
});

// Clean up
@override
void dispose() {
  Purchases.removeCustomerInfoUpdateListener(listener);
  super.dispose();
}
```

## Riverpod provider

```dart
// features/paywall/providers/entitlement_provider.dart
@riverpod
Future<bool> hasPro(Ref ref) async {
  final info = await Purchases.getCustomerInfo();
  return info.entitlements.active.containsKey('pro');
}

// Refreshable — call after purchase
ref.invalidate(hasProProvider);
```

## Restore purchases

```dart
Future<void> restorePurchases() async {
  try {
    final info = await Purchases.restorePurchases();
    final isPro = info.entitlements.active.containsKey('pro');
    // Show result to user
  } on PlatformException catch (e) {
    // Show error
  }
}
```

A visible **Restore Purchases** button is required by Apple App Store guidelines. Place it on the paywall screen.

## RevenueCat Paywalls (remote UI)

```bash
flutter pub add purchases_ui_flutter
```

```dart
import 'package:purchases_ui_flutter/purchases_ui_flutter.dart';

// Present a remote paywall
await RevenueCatUI.presentPaywall();

// Or embed in a widget
RevenueCatUI.presentPaywallIfNeeded('pro')
```

Remote paywalls let you update paywall copy and pricing display without a new app release.

## Server-side validation

Never trust the client alone for feature access. The RC webhook updates a `subscriptions` table in Supabase. Gate backend actions there:

```dart
// Before calling AI Edge Function, the Edge Function itself checks:
// SELECT is_active FROM subscriptions WHERE user_id = auth.uid()
// Client doesn't need to pass subscription state — server checks it directly.
```

See [../monetization/webhooks-supabase.md](../monetization/webhooks-supabase.md) for the webhook setup.

## Gotchas

- **`appUserID` must be set before configure** — if set after, the anonymous user's purchase history won't transfer to the logged-in user correctly. Set during configure, or call `logIn()` immediately after sign-in.
- **`purchaseCancelledError` is not an error** — always handle it silently (user tapped Cancel).
- **Sandbox on iOS**: use a Sandbox tester Apple ID, not your developer account, for test purchases.
- **`is_active` in webhooks**: `CANCELLATION` event keeps `is_active = true` until the billing period ends. Only `EXPIRATION` sets it false. See [../monetization/webhooks-supabase.md](../monetization/webhooks-supabase.md).
