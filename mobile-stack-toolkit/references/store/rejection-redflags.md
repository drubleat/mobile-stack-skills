---
title: Common rejection reasons (Apple & Google)
impact: HIGH
impactDescription: "Covers the recurring patterns that cause review rejections; most are avoidable with a pre-submission checklist"
tags: store, rejection, apple, google, review
---

# Common rejection reasons (Apple & Google)

These are the recurring patterns that cause review rejections, slow approvals, and post-launch removals. Most are avoidable with a checklist.

## Apple App Store

### Subscription & payments
- **No "Restore Purchases" button** — Apple guideline 3.1.1. Must be visible and functional. Placing it only in Settings doesn't pass review if it's not accessible from the paywall.
- **Subscription terms not clearly visible** — the billing period, amount, and auto-renewal notice must be visible *before* the user taps purchase. "You'll be charged £4.99/month" must be on the button or immediately adjacent.
- **Free trial not disclosed upfront** — "7-day free trial then £4.99/month" must appear on the purchase button/screen, not buried in fine print.
- **Using a non-Apple payment system for digital goods** — any in-app digital purchase must go through Apple IAP. External payment links for digital goods = rejection (except limited exceptions under court orders).

### Authentication
- **Social login without Sign in with Apple** — guideline 4.8. If your app offers Google Sign-In, Facebook login, or any third-party account login, you **must also offer Sign in with Apple**. Missing this = rejection.
- **Mandatory account creation for features that don't need it** — if the core feature works without an account, don't require sign-up on first launch.

### Content & AI
- **AI-generated content without disclosure** — if AI can generate content the user sees (text, images, audio), Apple expects a disclosure. "Powered by AI" label or similar.
- **AI for medical/legal/financial advice without disclaimer** — add "consult a professional" notice; reviewers test these.
- **Inappropriate AI-generated content with no moderation** — if the AI can produce offensive content, you need visible moderation. A "report" button + filters is minimum.

### Technical
- **Crashes or blank screen for reviewer** — the most common rejection. Test on a fresh install with no account. The reviewer starts from zero.
- **Demo account not provided** (for apps requiring login) — include test credentials in the reviewer notes.
- **Misleading screenshots** — if the screenshots show features not in the version being reviewed, Apple rejects for "misleading metadata."
- **Using private/undocumented APIs** — Apple scans binaries. Even indirect use through a third-party SDK can cause rejection.

### Privacy
- **Missing or invalid privacy policy URL** — the URL must load. A 404 = immediate rejection.
- **ATT not implemented** but analytics SDKs present — Apple detects IDFA usage in the binary.
- **Permission usage strings that don't match actual use** — "We need this to function" → rejection. Must state the *specific* purpose.

## Google Play Store

### Policy violations
- **Data Safety inaccurate or missing** — most common reason for removal of live apps. Google audits SDKs against declared data. If Firebase Analytics is present but you didn't declare "device IDs" and "app interactions" as collected → violation.
- **Deceptive behavior** — screenshots or descriptions that don't match the actual app.
- **Subscription without accessible cancellation** — users must be able to cancel without contacting support. Link to subscription management.

### Technical
- **Target SDK below requirement** — Play blocks updates. Keep `targetSdkVersion: 35` (2026).
- **64-bit requirement** — all APKs must include 64-bit native libraries. EAS Build handles this, but third-party SDKs may not.
- **Crash rate > 1.09%** in Play's vitals → Play may reduce discoverability of your app.

### Content
- **AI-generated content impersonating real people** — high scrutiny.
- **Gambling/financial promotion without required license declaration**.
- **Apps targeting children with ads** — COPPA compliance required; ad SDKs must be in "children's" mode.

## Prevention checklist before submission

- [ ] Fresh install + test all critical flows (no account, new account, returning user).
- [ ] Test on physical device (both platforms).
- [ ] All permission strings are specific and accurate.
- [ ] Privacy policy URL loads.
- [ ] Restore Purchases works.
- [ ] Sign in with Apple present (if other social logins exist).
- [ ] Subscription terms visible before purchase.
- [ ] Screenshots match current build.
- [ ] Reviewer notes filled for any non-obvious feature.
- [ ] Data Safety form complete (Android).
