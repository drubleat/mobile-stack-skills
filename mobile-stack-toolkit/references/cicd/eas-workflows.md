---
title: EAS Workflows: native CI + auto-versioning
impact: HIGH
impactDescription: "EAS Workflows replaces GitHub Actions for native builds; YAML-driven version bumps eliminate manual version management"
tags: cicd, eas, expo, workflows, versioning
---

# EAS Workflows: native CI + auto-versioning

EAS Workflows is Expo's built-in CI — YAML files in `.eas/workflows/` that trigger EAS Builds and EAS Updates without needing GitHub Actions or a third-party CI. If you're already on EAS, start here before adding GitHub Actions.

## Workflow file location

```
.eas/
  workflows/
    build-and-submit.yml   # production build + submit
    pr-preview.yml         # OTA preview on PRs
```

## Build + submit on merge to main

```yaml
# .eas/workflows/build-and-submit.yml
name: Build and submit to stores

on:
  push:
    branches: [main]

jobs:
  build-ios:
    type: build
    params:
      platform: ios
      profile: production

  build-android:
    type: build
    params:
      platform: android
      profile: production
    needs: [build-ios]         # optional: run sequentially to control concurrency

  submit-ios:
    type: submit
    params:
      platform: ios
      profile: production
    needs: [build-ios]

  submit-android:
    type: submit
    params:
      platform: android
      profile: production
    needs: [build-android]
```

## OTA preview on PRs

```yaml
# .eas/workflows/pr-preview.yml
name: PR preview update

on:
  pull_request:
    branches: [main]

jobs:
  update:
    type: update
    params:
      branch: pr-${{ github.event.pull_request.number }}
      message: 'PR #${{ github.event.pull_request.number }} preview'
```

This pushes a JS-only OTA update to a per-PR channel. Reviewers can load it on a dev build without waiting for a native build.

## Auto-increment build numbers

EAS can auto-increment `buildNumber` (iOS) and `versionCode` (Android) on every build, so you never touch them manually:

```json
// eas.json
{
  "build": {
    "production": {
      "autoIncrement": true
    }
  }
}
```

With `autoIncrement: true`, EAS reads the current value from App Store Connect / Play Console (or from its own counter) and increments it. You only manage `version` (semver) in `app.config.ts`; EAS handles the build counter.

```ts
// app.config.ts — manage only the user-visible version
export default {
  version: '1.2.0',
  // ios.buildNumber and android.versionCode intentionally omitted — EAS auto-sets them
}
```

## Runtime version strategy

Set a fixed `runtimeVersion` policy in `app.json` so OTA updates only land on compatible builds:

```json
{
  "expo": {
    "runtimeVersion": {
      "policy": "fingerprint"
    }
  }
}
```

`fingerprint` mode: EAS computes a hash of all native code. OTA updates only go to builds with a matching fingerprint. This is the modern default — it prevents JS updates from landing on incompatible native builds.

## Triggering workflows

Three ways to trigger:
1. **Git push** — via `on.push` in the YAML (shown above).
2. **EAS dashboard** — manual trigger from expo.dev.
3. **CLI**: `eas workflow:run build-and-submit.yml`

## When to add GitHub Actions instead

EAS Workflows handles build + submit well. Add GitHub Actions when you need:
- Supabase migration deployment before the native build.
- Linting, type-checking, or unit tests as a PR gate.
- Custom notification (Slack, email) when a build fails.
- Multi-repo orchestration.

EAS Workflows + GitHub Actions complement each other — see [github-actions.md](github-actions.md).
