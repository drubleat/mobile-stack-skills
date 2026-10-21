---
title: "Firebase App Distribution"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Firebase App Distribution

Use App Distribution for authorized prerelease testers. iOS builds still require suitable Apple signing/provisioning; ad-hoc distribution requires registered device IDs. Tester limits, retention and review times vary—check the service documentation before choosing a rollout path.

```bash
# Existing signed artifact; authenticate the CLI with a scoped account first.
npx firebase appdistribution:distribute ./app-release.apk \
  --app "$FIREBASE_ANDROID_APP_ID" --groups qa \
  --release-notes-file ./release-notes.txt
```

For iOS pass the signed `.ipa` and corresponding Firebase app ID. Android AAB distribution requires the documented Play integration; an APK is the simpler direct install artifact. Confirm the group and release before notifying testers.

In CI, build first and retain the exact artifact/build ID. A remote EAS build does not write a local APK merely because `--output` is supplied; that option belongs to local-build workflows. Retrieve the documented artifact URL for the completed build and verify it before distribution. Use a protected job with scoped credentials; do not run a secret-bearing distribution job on untrusted PR code.

Flutter Android artifact: `flutter build apk --release`, then distribute `build/app/outputs/flutter-apk/app-release.apk`. Test the store path separately before production because ad-hoc installation does not reproduce every store entitlement or purchase behavior.

## Sources

Reviewed 2026-10-20: [App Distribution CLI](https://firebase.google.com/docs/app-distribution/android/distribute-cli), [iOS distribution](https://firebase.google.com/docs/app-distribution/ios/distribute-cli).
