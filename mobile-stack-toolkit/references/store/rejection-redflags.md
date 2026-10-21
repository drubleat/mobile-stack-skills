---
title: "Store review checks"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Store review checks

Check the actual distribution region, app category and current policy before submission. Payment-link/IAP requirements and alternative distribution programs are not identical everywhere. Apple's login guideline has eligibility conditions and exceptions; email-only authentication does not automatically require Apple Sign-In.

Review the submitted build for:

- Working fresh-install, signed-out, new-user and returning-user flows; reviewer credentials and reachable backend.
- Accurate localized price, billing period, renewal/trial terms and eligibility; working restore and subscription management.
- Account deletion, privacy policy, data disclosures, purpose-specific permissions and any required tracking consent.
- Correct target SDK, supported native dependencies, signing and current store toolchain requirements.
- Screenshots and descriptions matching real features; no fabricated scarcity, reviews or functionality.
- Appropriate handling/reporting of generated or user-submitted content and disclosure/permission before third-party personal-data sharing.

A disclaimer alone does not satisfy requirements for medical, financial, legal or other regulated functionality. Evaluate the actual feature and policy. Avoid claiming every AI output must carry a specific label unless the applicable rule says so.

Run [purchase tests](../monetization/testing.md), [privacy checks](permissions-privacy.md) and the platform-specific [Play](play-console.md)/[Apple](app-store-connect.md) submission guide. Record evidence for the exact build. Approval times and thresholds can change; a checklist does not guarantee acceptance.

## Sources

Reviewed 2026-10-20: [Apple review rules](https://developer.apple.com/app-store/review/guidelines/), [Google Play policy](https://play.google/developer-content-policy/).
