---
title: RevenueCat dashboard setup
impact: MEDIUM-HIGH
impactDescription: "Products and entitlements must be created in RC dashboard before SDK init; missing this step causes empty offerings"
tags: revenuecat, dashboard, products, entitlements
---

# RevenueCat dashboard setup

## 1. Create a RevenueCat project

[app.revenuecat.com](https://app.revenuecat.com) → New Project. Add iOS App and/or Android App. Each platform gets its own **public SDK key** (`appl_...` for iOS, `goog_...` for Android). These are client-safe and go in your app config.

## 2. Connect App Store Connect (iOS)

RC needs to validate receipts with Apple.

1. **In-App Purchase Key** (recommended): App Store Connect → Users and Access → Integrations → In-App Purchase → Generate a key. Download the `.p8` file; enter the Issuer ID, Key ID, and file content into RC.
2. **App-Specific Shared Secret** (legacy): App Store Connect → My Apps → [App] → App Information → App-Specific Shared Secret. Only use this if the In-App Purchase Key isn't available.

Prefer the In-App Purchase Key — it's more granular and works across apps without per-app configuration.

## 3. Connect Play Console (Android)

RC needs a Google service account to validate Play receipts.

1. Google Play Console → Setup → API access → Link to a Google Cloud project (create one if needed).
2. In Google Cloud Console → IAM → Service Accounts → Create service account. Assign roles: **Pub/Sub Admin** + **Monitoring Viewer**.
3. Download the service account JSON key.
4. Back in Play Console → Grant access to the service account with: View financial data + Manage orders and subscriptions.
5. Paste the JSON content into RC → Android app → Configuration.

This is the most error-prone step. The Google Cloud project must be the same one linked in Play Console — a common mistake is creating the service account in a different project.

## 4. Define products in the stores first

Before RC can track them, products must exist in the stores:

- **App Store Connect**: My Apps → [App] → Subscriptions → create subscription group + products.
- **Play Console**: Monetize → Products → Subscriptions → create products.

Product IDs are arbitrary strings (`pro_monthly`, `com.yourapp.pro.monthly`) — be consistent and lowercase.

## 5. Define Entitlements → Products → Offerings in RC

In the RC dashboard (do this in order):

1. **Entitlements** → New → name it `pro` (the string your app checks).
2. **Products** → add your App Store + Play Store product IDs. RC verifies they exist.
3. **Attach products to the entitlement**.
4. **Offerings** → New → name it `default`. Add packages (`monthly`, `annual`) each pointing to a product. Set as **Current**.

Your app fetches the current offering — swap offerings remotely for A/B tests without a store release.

## Common mistakes

- **Wrong service account project** → RC can't validate Play receipts; purchases appear "invalid." The Cloud project and Play Console must be linked.
- **Product doesn't exist in the store yet** → create and save products in stores before adding to RC.
- **Forgetting to attach products to the entitlement** → purchases go through but `entitlement.isActive` is always false.
- **Sandbox vs Production** → RC auto-routes sandbox receipts to Apple's sandbox; test with Sandbox accounts only.
