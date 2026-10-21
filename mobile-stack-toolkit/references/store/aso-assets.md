---
title: "Store assets and accurate metadata"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Store assets and accurate metadata

Create assets from the actual submitted build and supported device families. Use the live App Store Connect screenshot specifications: accepted iPhone size classes can substitute for one another, so do not assume both 6.9-inch and 6.7-inch uploads are always required. iPad screenshots depend on support. Check Google Play's current dimensions, counts and feature-graphic requirements separately.

For Expo, configure the app icon and Android adaptive-icon foreground/background according to the SDK. Preserve safe areas and test cropping/masks on device. App icons are native assets and generally require a new binary; updating an in-app image through OTA is a different case.

Lead screenshots with a real core workflow, keep text readable, localize supported markets and avoid misleading simulated features. Test variants with store experiments instead of claiming universal conversion percentages.

Write concise app names, subtitles/descriptions and keywords within the limits shown by the current console. Avoid competitor trademarks, fabricated reviews, unsupported health/outcome claims and keyword stuffing. Align pricing/trial statements with actual eligible store products and locales.

Keep editable asset sources, exported files and a record of the build/locale/device used. Verify privacy-policy/support links and accessibility of marketing text. Compare rendered uploads in the console before submitting.

## Sources

Reviewed 2026-10-20: [Apple screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications), [Google preview assets](https://support.google.com/googleplay/android-developer/answer/9866151).
