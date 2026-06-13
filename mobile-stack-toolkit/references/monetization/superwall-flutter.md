---
title: Superwall — Flutter paywall SDK
impact: HIGH
impactDescription: "Superwall enables remote paywall A/B testing without app releases; RevenueCat integration requires correct subscription status sync or entitlements break"
tags: superwall, monetization, paywall, flutter, revenuecat, iap
---

# Superwall — Flutter

Superwall for Flutter works the same as the RN version: create placements in the dashboard, trigger them from code, and control paywall logic remotely.

**Package:** `superwallkit_flutter: ^2.4.12`  
**Requires:** iOS 14+, Android SDK 26+ (AGP 8.4+, Gradle 8.6+)  
**Source:** [github.com/superwall/Superwall-Flutter](https://github.com/superwall/Superwall-Flutter)

---

## Install

```yaml
# pubspec.yaml
dependencies:
  superwallkit_flutter: ^2.4.12
```

```bash
flutter pub get
```

---

## Setup (basic — no RevenueCat)

Call `Superwall.configure` once, before `runApp` or in `initState` of your root widget.

```dart
import 'package:superwallkit_flutter/superwallkit_flutter.dart';
import 'dart:io';

Future<void> configureSuperwall() async {
  final apiKey = Platform.isIOS
      ? 'pk_your_ios_key'
      : 'pk_your_android_key';

  Superwall.configure(apiKey);
}
```

---

## Triggering a paywall — `registerPlacement`

```dart
import 'package:superwallkit_flutter/superwallkit_flutter.dart';

await Superwall.shared.registerPlacement('upgrade_tapped');
```

With a presentation handler to observe lifecycle:

```dart
final handler = PaywallPresentationHandler();
handler
  ..onPresent((paywallInfo) async {
    final name = await paywallInfo.name;
    print('Paywall shown: $name');
  })
  ..onDismiss((paywallInfo) async {
    print('Paywall dismissed');
  })
  ..onError((error) {
    print('Error: $error');
  });

await Superwall.shared.registerPlacement('upgrade_tapped', handler: handler);
```

---

## Feature gating

Pass a `feature` callback — it executes only when the user has access.

```dart
ElevatedButton(
  child: const Text('Launch Pro Feature'),
  onPressed: () async {
    await Superwall.shared.registerPlacement(
      'pro_feature_gate',
      feature: () {
        Navigator.pushNamed(context, '/pro-feature');
      },
    );
  },
),
```

---

## User identification

```dart
// After login
await Superwall.shared.identify('user_uuid');

// Optional targeting attributes
await Superwall.shared.setUserAttributes({
  'plan': 'free',
  'days_active': 7,
});

// On logout
await Superwall.shared.reset();
```

---

## Subscription status widget

Use `SuperwallBuilder` to reactively read subscription status anywhere in the tree:

```dart
SuperwallBuilder(
  builder: (context, status) {
    return Text(
      status.toString().contains('active') ? 'PRO' : 'Free',
    );
  },
),
```

---

## RevenueCat integration

When using RevenueCat, implement `PurchaseController` so Superwall delegates purchase actions to RC and stays in sync with entitlement state.

### Purchase controller

```dart
import 'dart:io';
import 'package:purchases_flutter/purchases_flutter.dart'
    show Purchases, PurchasesConfiguration, LogLevel, CustomerInfo,
         StoreProduct, PurchaseParams;
import 'package:superwallkit_flutter/superwallkit_flutter.dart'
    hide LogLevel, StoreProduct, CustomerInfo;
import 'package:superwallkit_flutter/superwallkit_flutter.dart' as sw
    show Entitlement;

class RCPurchaseController extends PurchaseController {
  Future<void> configure() async {
    await Purchases.setLogLevel(LogLevel.debug);
    final config = Platform.isIOS
        ? PurchasesConfiguration('appl_your_ios_key')
        : PurchasesConfiguration('goog_your_android_key');
    await Purchases.configure(config);
  }

  /// Keep Superwall subscription status in sync with RevenueCat + web entitlements.
  void syncSubscriptionStatus() {
    Purchases.addCustomerInfoUpdateListener((customerInfo) async {
      final rcEntitlements = customerInfo.entitlements.active.keys
          .map((id) => sw.Entitlement(id: id))
          .toSet();
      await _updateStatus(rcEntitlements);
    });

    // Also sync when Superwall gets web entitlements (web purchases)
    Superwall.shared.customerInfoStream.listen((_) async {
      try {
        final info = await Purchases.getCustomerInfo();
        final rcEntitlements = info.entitlements.active.keys
            .map((id) => sw.Entitlement(id: id))
            .toSet();
        await _updateStatus(rcEntitlements);
      } catch (_) {}
    });
  }

  Future<void> _updateStatus(Set<sw.Entitlement> rcEntitlements) async {
    final entitlements = await Superwall.shared.getEntitlements();
    final all = sw.Entitlement.mergePrioritized(
      rcEntitlements.union(entitlements.web),
    );
    if (all.isNotEmpty) {
      await Superwall.shared.setSubscriptionStatus(
        SubscriptionStatusActive(entitlements: all),
      );
    } else {
      await Superwall.shared.setSubscriptionStatus(SubscriptionStatusInactive());
    }
  }
}
```

### Wire it up in main

```dart
void main() {
  runApp(const MyApp());
}

class _MyAppState extends State<MyApp> {
  final _purchaseController = RCPurchaseController();

  @override
  void initState() {
    super.initState();
    _configureSuperwall();
  }

  Future<void> _configureSuperwall() async {
    final apiKey = Platform.isIOS ? 'pk_ios_key' : 'pk_android_key';

    // Step 1 — configure Superwall first, passing the purchase controller
    Superwall.configure(apiKey, purchaseController: _purchaseController);

    // Step 2 — configure RevenueCat after Superwall
    await _purchaseController.configure();

    // Step 3 — start syncing subscription status
    _purchaseController.syncSubscriptionStatus();
  }
}
```

**Order matters:** Superwall → RevenueCat → syncSubscriptionStatus.

---

## Deep linking

```dart
import 'package:app_links/app_links.dart';

final appLinks = AppLinks();
appLinks.uriLinkStream.listen((Uri uri) {
  Superwall.shared.handleDeepLink(uri);
});
```

---

## SuperwallOptions

```dart
final options = SuperwallOptions();
options.paywalls.shouldPreload = false; // disable if you have many paywalls
options.paywalls.shouldShowWebRestorationAlert = false;
// options.testModeBehavior = TestModeBehavior.always; // force paywall in debug

Superwall.configure(apiKey, purchaseController: controller, options: options);
```

---

## Gotchas

- **AGP 8.4+ and Gradle 8.6+ required** on Android. If your project is older, upgrade before adding Superwall.
- **Configure Superwall BEFORE RevenueCat.** The purchase controller must be passed at configure time; you cannot attach it later.
- **`syncSubscriptionStatus` must be called after** `purchaseController.configure()` — otherwise the RevenueCat listener fires before RC is initialized.
- If `registerPlacement` finds no matching campaign, it executes `feature` directly without showing a paywall. This is intentional (subscriber bypass), not a bug.
- `hide LogLevel, StoreProduct, CustomerInfo` in imports — both packages export these names; without the hide clause you get compile errors.
