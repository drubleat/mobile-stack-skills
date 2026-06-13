---
title: Zero to App Store: full build sequence
impact: HIGH
impactDescription: "Ordered phase sequence from scaffold to submission with clear exit criteria; prevents skipping steps that cause late failures"
tags: playbooks, workflow, expo, supabase, revenuecat, store
---

# Zero to App Store: full build sequence

The ordered sequence from idea to shipped app. Each phase has a clear exit criterion before moving to the next.

## Phase 1: Foundation (Day 1–2)

**Exit: app runs on physical device with auth working end-to-end.**

1. **Create Supabase project** (staging + production projects).
2. `npx create-expo-app@latest myapp --template tabs` — start from SDK 56 template, not bare.
3. `eas build:configure` — sets up EAS project, credentials, `eas.json`.
4. Write initial migration: `profiles` table + `handle_new_user` trigger → `supabase/migrations/`.
5. `supabase db push` to staging.
6. Implement Supabase auth (OTP email or native Google/Apple sign-in).
7. Test auth on physical device via dev build: `eas build --profile development --platform ios`.

## Phase 2: Core feature (Day 3–7)

**Exit: the core user action works (AI call returns, content displays, data saves).**

1. Design schema for core feature tables. Write migration. `supabase db push`.
2. Implement Supabase Edge Function for AI proxy (`/functions/v1/ai-proxy`). Set secrets.
3. Build the main screen + core feature UI.
4. Wire up TanStack Query (or Riverpod for Flutter) for data fetching.
5. Add basic RLS policies to all new tables.
6. Test on device: end-to-end flow from sign-in → core action → result displayed.

## Phase 3: Monetization (Day 8–10)

**Exit: test purchase completes in sandbox and updates subscription in Supabase.**

1. RevenueCat dashboard: create project, add iOS/Android apps, create products + offering.
2. App Store Connect / Play Console: create in-app purchase products (match RC identifiers exactly).
3. Install RevenueCat SDK + `Purchases.logIn(userId)`.
4. Build paywall screen with `getOfferings()` + `purchasePackage()`.
5. Implement webhook Edge Function (`/functions/v1/revenuecat-webhook` with `--no-verify-jwt`).
6. Deploy webhook; configure in RC dashboard; test with RC sandbox.
7. Verify `subscriptions` table updates correctly for INITIAL_PURCHASE and EXPIRATION events.
8. Gate core feature behind entitlement check (both client UI + Edge Function server check).

## Phase 4: Push notifications (Day 11–12)

**Exit: test push notification received on physical device from server send.**

1. FCM: upload APNs Auth Key (.p8) to Firebase Console.
2. Install `@react-native-firebase/messaging` + `expo-build-properties` (with `useFrameworks: 'static'`).
3. Rebuild dev build (native change): `eas build --profile development`.
4. Implement token registration + storage in `device_tokens` table.
5. Implement foreground message handler (FCM doesn't auto-display in foreground).
6. Write Edge Function or Supabase scheduled job that sends FCM pushes.
7. Test: trigger notification from server; confirm receipt in all three app states.

## Phase 5: Crash reporting + analytics (Day 13)

**Exit: test crash appears in Crashlytics dashboard; custom event in Firebase Analytics.**

1. Add `@react-native-firebase/crashlytics` + `@react-native-firebase/analytics`.
2. Set `crashlytics().setUserId(supabaseUserId)` on sign-in.
3. Add `logEvent` calls at key conversion points (sign_up, paywall_viewed, purchase_started).
4. Add Remote Config for any feature flags you plan to A/B test.
5. Build production: `eas build --profile production`.

## Phase 6: Store submission (Day 14–21)

**Exit: app live in both stores.**

1. Capture screenshots on physical device (6.9" iPhone + Pixel device).
2. Write App Store metadata (name, subtitle, keywords, description).
3. Fill in Privacy Policy URL, age rating, data disclosures.
4. App Store Connect: fill all required fields → Submit for Review.
5. Play Console: complete Data Safety form → Internal Testing → Production.
6. RevenueCat → configure ASC In-App Purchase Key (preferred over shared secret).
7. Set up EAS Workflows or GitHub Actions for future CI/CD.

## Phase 7: Post-launch (Week 3+)

1. Monitor Crashlytics daily for 7 days after release.
2. Monitor RevenueCat dashboard for subscription events + RC↔Supabase sync.
3. Check Analytics for funnel drop-offs (sign_up → paywall_viewed → purchase_completed).
4. Respond to App Store reviews.
5. First update: fix top crash + implement most-requested feature. Target within 2 weeks.

## Critical order dependencies

- Schema migrations **before** Edge Functions (functions may depend on new columns).
- RevenueCat `logIn(userId)` **before** first purchase (anonymous → identified user drift).
- `useFrameworks: 'static'` **before** native build with Firebase (pod config change requires rebuild).
- APNs key uploaded to Firebase **before** testing iOS push (FCM won't deliver without it).
- Data Safety form completed **before** Play Console submission (blocks publication if missing).
