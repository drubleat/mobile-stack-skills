---
title: "GitHub Actions: trusted checks and releases"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# GitHub Actions: trusted checks and releases

Run PR checks without deployment credentials. Do not use `pull_request_target` to execute untrusted PR code, and do not expose publish tokens to a PR merely because it comes from the same repository. Dependencies and lifecycle scripts are executable code too.

```yaml
name: Checks
on: [pull_request]
permissions:
  contents: read
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: actions/setup-node@v7.1.0
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
      - run: npm run typecheck
      - run: npm test
```

This example assumes those scripts and a supported version in `.nvmrc` exist. Pin actions to reviewed full commit SHAs in production and update them intentionally. `setup-node` caches npm's download cache, not `node_modules`.

For a trusted preview/release job, use a protected environment, minimal token permissions and a concurrency group scoped to the target environment. Avoid cancelling an in-progress database migration. With `expo/expo-github-action`, use `eas-version`, not `expo-version`, to install EAS CLI. Resolve and pin a tested CLI release rather than floating on every run.

Never interpolate PR titles, branch names or commit messages directly into `run`. Pass untrusted text through an environment variable and quote its expansion; do not `eval` it. Approve the exact commit before any job executes its code with secrets.

Build with an explicit platform/profile; capture the resulting build ID and pass that exact ID to submission. `eas submit --platform ios --id "$BUILD_ID" --profile production --non-interactive` avoids submitting another concurrent build. Repeat separately for Android. Native signing and store credentials must already be configured.

Use [Supabase deployment](supabase-deploy.md) for compatible schema/function changes. EAS Workflows also supports custom steps and tests; choose the CI host based on project integrations rather than a false capability restriction.

## Sources

Reviewed 2026-10-20: [GitHub secure use](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions), [Expo GitHub Action](https://github.com/expo/expo-github-action).

Action versions reviewed 2026-10-21: [checkout releases](https://github.com/actions/checkout/releases), [setup-node releases](https://github.com/actions/setup-node/releases). Pin reviewed commit SHAs when the project requires immutable action dependencies.
