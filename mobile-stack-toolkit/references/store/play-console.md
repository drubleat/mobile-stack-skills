---
title: "Google Play submission and target requirements"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Google Play submission and target requirements

Select the existing developer account and immutable package identity. Verify account verification, signing and the current target-API requirement for the app category and release date. The official policy reviewed for this audit requires API 36 for standard new apps/updates from August 31, 2026; category exceptions and extensions must be checked in Play Console before release.

For Expo, use the SDK's supported Android defaults. If an override is required, configure `expo-build-properties` with `android.targetSdkVersion`/`compileSdkVersion` under that plugin, not arbitrary top-level android app-config fields. For Flutter, update the supported Gradle/toolchain configuration. Test behavior changes introduced by the target upgrade.

New personal developer accounts subject to Google's testing gate need at least 12 opted-in closed testers for 14 continuous days before applying for production access. Internal testing alone does not satisfy that requirement. Check the account's actual eligibility and requested evidence.

Complete Data Safety, privacy policy, content rating, ads/target-audience declarations and account deletion requirements based on actual app and SDK behavior. SDK documentation is input, not a form to copy blindly. Apps supporting account creation need the applicable in-app and web deletion paths.

Build the correctly signed AAB, test through the intended track, and explicitly submit that artifact. EAS Build alone does not automatically submit unless auto-submit is configured. Verify release status and availability; review timing is external. Use staged rollout where supported and monitor Android vitals and backend compatibility.

## Sources

Reviewed 2026-10-20: [target API policy](https://support.google.com/googleplay/android-developer/answer/11926878), [personal account testing](https://support.google.com/googleplay/android-developer/answer/14151465), [account deletion](https://support.google.com/googleplay/android-developer/answer/13327111).
