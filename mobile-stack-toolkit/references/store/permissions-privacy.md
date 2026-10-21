---
title: "Permissions and accurate privacy disclosures"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Permissions and accurate privacy disclosures

Inventory data collected by the app, embedded SDKs and backend processors. Record purpose, retention, deletion, sharing and consent. Include an accessible privacy policy and functioning account/data deletion paths where required. An age rating alone does not determine children's privacy obligations; evaluate audience, distribution and applicable policy.

Request permissions at the relevant user action and provide specific usage strings. Add only permissions the feature needs. A system photo picker may avoid broad media access; camera, microphone, location and notifications have separate platform/version requirements. Test denial, limited access and settings changes.

ATT applies when the app performs tracking as Apple defines it; the mere presence of an analytics SDK does not establish that requirement. Configure collection and advertising features intentionally, obtain required permission before tracking, and ensure denial does not trigger a workaround. Privacy manifests and required-reason API declarations are separate checks.

Before sharing personal data with third-party AI, clearly disclose the destination/use and obtain required permission. Do not assert that a provider trains on data unless the actual service agreement/settings say so. Bound retention and avoid logging raw prompts, audio, images or tokens by default.

App Store privacy and Play Data Safety answers must reflect the shipped build and current configuration. Verify SDK disclosures and re-evaluate when adding analytics, AI, advertising, crash reporting or payment integrations. Policy requirements vary by region/app type; use the linked current official rules instead of a frozen universal checklist.

## Sources

Reviewed 2026-10-20: [Apple review/privacy](https://developer.apple.com/app-store/review/guidelines/), [Apple privacy manifests](https://developer.apple.com/documentation/bundleresources/privacy_manifest_files), [Play user data](https://support.google.com/googleplay/android-developer/answer/10144311).
