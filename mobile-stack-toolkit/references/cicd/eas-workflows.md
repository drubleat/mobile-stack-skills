---
title: "EAS Workflows: build identity and versioning"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# EAS Workflows: build identity and versioning

Store workflow YAML under `.eas/workflows/`. A submit job must consume the ID emitted by its build job:

```yaml
name: Build and submit iOS
on:
  workflow_dispatch:
jobs:
  build_ios:
    type: build
    params:
      platform: ios
      profile: production
  submit_ios:
    needs: [build_ios]
    type: submit
    params:
      build_id: ${{ needs.build_ios.outputs.build_id }}
      profile: production
```

Configure signing and the submit profile first. Android uses a separate build job with `platform: android` and its own resulting ID. Store submission is a separate step from store review/release.

With remote app-version management, configure `cli.appVersionSource: remote` in eas.json and `build.production.autoIncrement: true`. Initialize/synchronize counters intentionally; do not assume every build reads the store's latest number. Keep the user-visible version under release control.

Select a runtime-version strategy, such as `fingerprint`, and validate compatibility against the installed binary. Fingerprint is a configured policy, not an assertion that all projects already use it. Branches hold updates; channels route installed builds to branches. A PR branch update is not automatically visible to a production binary.

Use custom jobs for lint, unit tests and deployment commands when suitable; EAS Workflows is not restricted to native builds. Check the documented EAS expression contexts before copying GitHub Actions expressions. Run with `eas workflow:run build-and-submit.yml` after reviewing the target and credentials.

## Sources

Reviewed 2026-10-20: [pre-packaged jobs](https://docs.expo.dev/eas/workflows/pre-packaged-jobs/), [app versions](https://docs.expo.dev/build-reference/app-versions/).
