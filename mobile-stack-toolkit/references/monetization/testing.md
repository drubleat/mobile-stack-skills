---
title: Testing purchases without real money
impact: MEDIUM-HIGH
impactDescription: "Sandbox testing on iOS requires a separate Apple ID; StoreKit 2 local config enables offline purchase testing"
tags: revenuecat, testing, sandbox, storekit, iap
---

# Testing purchases (without real money)

## iOS — Sandbox accounts

1. **App Store Connect** → Users and Access → Sandbox Testers → Create tester (use a fake email you control; it doesn't need to be a real Apple ID).
2. On the device: Settings → App Store → Sandbox Account → sign in with the sandbox tester.
3. Run the app via TestFlight or a dev build. Purchases go through the sandbox; no real charges.

Sandbox behavior:
- Subscriptions renew at accelerated rates (monthly → every 5 min, annual → every 1 hour) for testing renewals and RENEWAL webhooks.
- Cancelled subscriptions expire quickly too — good for testing EXPIRATION flow.
- `BILLING_ISSUE` can be simulated by removing the payment method from the sandbox account.

**StoreKit Testing (Xcode / local dev):**
Create a `.storekit` configuration file in Xcode (File → New → File → StoreKit Configuration). Add your products, set prices, enable it in the scheme (Edit Scheme → Run → Options → StoreKit Configuration). This works in the iOS Simulator with no real Apple ID needed — great for rapid iteration without TestFlight.

## Android — Play Console license testing

1. **Play Console** → Monetize → Testing → License Testing → add email addresses.
2. Those accounts can make test purchases without being charged. Purchases are marked as test and can be immediately cancelled from the Play Console.
3. For subscriptions, Play billing offers accelerated renewal in test mode (configurable to minutes).

**Internal App Sharing:** share an APK via Play Console → Internal App Sharing for quick testing without a full release track.

## RevenueCat Sandbox view

In the RC dashboard, switch to **Sandbox** mode (top of the customer list). All sandbox/test purchases appear there, separate from production. You can inspect CustomerInfo, entitlements, and purchase history per user.

Use `Purchases.setLogLevel(LOG_LEVEL.DEBUG)` during development to see every RC SDK call in the console.

## Testing the webhook flow

Sandbox purchases fire RC webhooks to your configured URL — your Edge Function will receive real events. To test:

1. Make a sandbox purchase on device.
2. Watch RC dashboard (Customers → [user] → History) for the event.
3. Check your Supabase `subscriptions` table for the upserted row.
4. RC also has a **Webhook Delivery Logs** view to inspect payloads and retry failed deliveries.

If the webhook doesn't arrive: check the URL, authentication header, and that the function is deployed with `--no-verify-jwt`.

## Testing cancellation + expiry flow

1. Make a sandbox purchase (subscription).
2. Immediately cancel it on device (App Store → Account → Subscriptions → [App] → Cancel).
3. RC fires `CANCELLATION` — verify `is_active` stays `true` in your DB.
4. Wait for the sandbox period to expire (minutes in sandbox).
5. RC fires `EXPIRATION` — verify `is_active` becomes `false`.

Testing this flow end-to-end before launch saves production incidents.

## Common testing pitfalls

- **Production keys in a dev build** → sandbox purchases go to production RC; pollutes real data.
- **Sandbox account signed in at system level, not Settings → App Store** → on newer iOS, sign in under Settings → App Store (not iCloud) for sandbox to work.
- **Webhook fires but `user_id` is RC's anonymous ID** → you forgot `Purchases.logIn(userId)` before purchase. The webhook can't match to your user.
- **Simulator can't complete purchases** → StoreKit config file not enabled in scheme, or using real App Store (not sandbox) on simulator. Use `.storekit` files for simulator.
