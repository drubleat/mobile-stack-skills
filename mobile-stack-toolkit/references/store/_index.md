---
title: Store submission — domain index
impact: MEDIUM-HIGH
impactDescription: "Routes to App Store Connect, Play Console, ASO assets, permissions, and rejection red flags"
tags: store, app-store, play-store, index
---

# Store submission — index

## Router

| Task | File |
|---|---|
| App Store Connect: bundle ID, certs, TestFlight, submit | [app-store-connect.md](app-store-connect.md) |
| Permission strings, Privacy Policy, AI/data disclosures | [permissions-privacy.md](permissions-privacy.md) |
| Screenshots, icons, ASO (name/subtitle/keywords) | [aso-assets.md](aso-assets.md) |
| Play Console: Data Safety form, target API level, release tracks | [play-console.md](play-console.md) |
| Common rejection reasons (Apple and Google) | [rejection-redflags.md](rejection-redflags.md) |

## Submission checklist (quick scan)

Before you submit, verify:

- [ ] Bundle ID / package name matches what's in EAS + RevenueCat + Firebase
- [ ] All permission usage strings filled in (`NSCameraUsageDescription`, etc.)
- [ ] Privacy Policy URL live and accessible
- [ ] Screenshots at required sizes for all device families
- [ ] App icon at all required sizes (EAS generates from a single 1024×1024 source)
- [ ] Subscription terms visible in paywall + "Restore Purchases" button
- [ ] "Sign in with Apple" implemented if any other third-party login exists (iOS)
- [ ] Play Data Safety form completed (Android)
- [ ] Target SDK ≥ API 35 (Android, 2026 requirement)
- [ ] Age rating selected and accurate
- [ ] TestFlight / Internal Testing build tested by at least one real person other than you

## EAS Submit

After building with `eas build --profile production`:

```bash
eas submit --platform ios      # submits to App Store Connect
eas submit --platform android  # submits to Play Console
eas submit --platform all      # both
```

Or chain with the build: `eas build --profile production --platform all --auto-submit`.

EAS Submit handles the App Store Connect API and Play Console upload automatically using credentials you set in `eas.json`'s `submit` section or interactively. Much faster than manual Transporter/Play upload.
