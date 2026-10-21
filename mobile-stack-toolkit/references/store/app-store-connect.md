---
title: "App Store Connect and exact-build submission"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# App Store Connect and exact-build submission

Create/select the app record with the exact bundle ID, SKU and supported platforms. Native capabilities, signing certificate and provisioning profile must match the release. EAS can manage credentials; use the organization's existing signing policy where one exists.

For automated submission, configure EAS's supported App Store Connect credential flow. Key ID and issuer ID alone are insufficient: the private `.p8` key must also be securely available. If configuring file-based submission, use the documented `ascApiKeyPath`, `ascApiKeyId` and `ascApiKeyIssuerId` fields, plus `ascAppId`, and exclude private files from Git.

Build and submit are separate operations unless auto-submit is explicitly enabled. Submit the exact successful iOS build ID, then inspect App Store Connect processing, export-compliance questions and TestFlight availability. Internal and external testing have different eligibility/review requirements; do not promise a fixed processing time.

Before App Review, supply accurate metadata/screenshots, privacy disclosures, account-deletion support where required, and a working reviewer account/backend. Explain features requiring special hardware or setup. Verify the current Xcode/SDK submission requirements and the actual release version/build number.

See [assets](aso-assets.md), [privacy](permissions-privacy.md) and [review checks](rejection-redflags.md). Store upload, beta approval, review approval and public release are different states; report the state actually observed.

## Sources

Reviewed 2026-10-20: [EAS iOS submit](https://docs.expo.dev/submit/ios/), [submit config](https://docs.expo.dev/submit/eas-json/), [App Store Connect](https://developer.apple.com/help/app-store-connect/).
