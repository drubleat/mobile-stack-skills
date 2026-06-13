---
title: OTA updates with EAS Update
impact: MEDIUM-HIGH
impactDescription: "OTA ships JS fixes in minutes without store review; channel management prevents staging updates reaching production users"
tags: expo, ota, eas-update, channels
---

# OTA updates with EAS Update

EAS Update ships **JS and asset changes** to already-installed builds without a store review. It cannot change native code. Use it for bug fixes, copy/UI tweaks, and feature flags between store releases.

## Install & configure

```bash
npx expo install expo-updates
eas update:configure
```

This wires `expo-updates` and sets a `runtimeVersion` in your config. Builds also carry a **channel** (set per build profile in `eas.json`, e.g. `"channel": "production"`).

## The three concepts you must keep straight

- **Runtime version** — describes the *native* JS-native interface. An update only loads on a build whose runtime version **matches exactly**. Bump it whenever native code changes (new native module, SDK upgrade, edited `app.config` native bits).
- **Branch** — a line of updates (like a git branch of JS bundles).
- **Channel** — what a *build* points at. Channels map to branches. Default: a channel is linked to the branch of the same name.

So: a `production` build has `channel: production` → linked to the `production` branch → receives updates published there, *if* runtime versions match.

## Runtime version policy — use `fingerprint`

Set the policy in config instead of hand-managing version strings:

```jsonc
// app.config.ts → expo.runtimeVersion
{ "runtimeVersion": { "policy": "fingerprint" } }
```

`fingerprint` hashes your native dependency graph and auto-changes the runtime version exactly when native code changes — so you can't accidentally push a JS update that assumes a native module the installed build doesn't have. This is the modern default; the older `appVersion`/`sdkVersion` policies are coarser and easier to footgun.

## Publishing updates

```bash
eas update --branch production --message "Fix paywall copy"
eas update --branch preview --message "Try new onboarding"
```

To map a branch to a channel explicitly: `eas channel:edit production --branch production`.

## Rollouts & rollbacks

- **Gradual rollout:** publish to a branch and roll out to a percentage, increasing as it proves stable (manage via the dashboard or `eas update:roll-out`).
- **Rollback:** `eas update:rollback` (or republish a known-good update / repoint the branch). Because there's no store review, recovery from a bad JS bug is minutes, not days.
- **Inspect:** `eas update:list --branch production`, `eas update:view <id>`.

## What CANNOT go through OTA

- New native modules or any change to `ios/`/`android/`.
- SDK upgrades.
- Changes to `app.config` native config (permissions, plugins, bundle ID).

All of those require a new `eas build` and a new store release. If you try to OTA them, the fingerprint runtime version changes and the update simply won't be delivered to old builds — by design.

## Sane workflow

1. Native-affecting change → `eas build` + store submit (runtime version moves automatically with `fingerprint`).
2. JS/asset-only change → `eas update --branch <env>`.
3. Keep `preview` and `production` branches separate so testers get changes first.
4. Wire `eas update` into CI so merges to `main` publish automatically → [../cicd/eas-workflows.md](../cicd/eas-workflows.md).

> Store policy note: OTA is for incremental fixes, not for shipping a materially different app to dodge review. Keep substantive feature changes in store builds.
