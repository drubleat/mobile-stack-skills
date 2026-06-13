---
title: EAS Build & eas.json
impact: HIGH
impactDescription: "eas.json profile inheritance and `EXPO_PUBLIC_*` env var discipline prevent credentials from leaking into builds"
tags: expo, eas-build, ci, credentials
---

# EAS Build & `eas.json`

EAS Build compiles your app in the cloud (or locally) and produces installable/submittable artifacts. Configure it once in `eas.json`, then everything is a one-liner.

## Setup

```bash
npm i -g eas-cli          # or npx eas-cli@latest
eas login
eas build:configure       # creates eas.json + links the project (writes the EAS project ID)
```

## `eas.json` — the three standard profiles

```jsonc
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "development": {
      "developmentClient": true,        // builds with expo-dev-client
      "distribution": "internal",       // installable via link, not a store
      "channel": "development"
    },
    "preview": {
      "distribution": "internal",       // QA / stakeholder builds
      "channel": "preview",
      "ios": { "simulator": true }      // optional: simulator-runnable build
    },
    "production": {
      "autoIncrement": true,            // bumps build number each build
      "channel": "production"
    }
  },
  "submit": { "production": {} }         // see store/_index.md
}
```

What each profile is *for*:
- **development** — your day-to-day Dev Build. Has the dev menu, loads from Metro. Never goes to a store.
- **preview** — a release-like build you can hand to testers via an internal link (or TestFlight) without going to production. Best for "does this actually work on a real device" checks.
- **production** — the artifact you submit. `autoIncrement` keeps build numbers monotonic so stores don't reject duplicates.

The `channel` field links a build to an EAS Update channel so OTA updates reach the right builds → [ota-updates.md](ota-updates.md).

## Running builds

```bash
eas build --profile development --platform ios
eas build --profile preview --platform all
eas build --profile production --platform android
eas build --profile production --platform all --auto-submit   # build then submit
```

- Omitting `--profile` defaults to `production`.
- `--platform all` builds iOS + Android in parallel.
- `eas build --local` compiles on your machine (useful for debugging cloud failures or avoiding queue time) but needs the platform toolchains installed.

## Credentials — let EAS manage them

For most teams, answer "yes" when EAS offers to **manage credentials remotely**. It will:
- iOS: create/maintain the distribution certificate and provisioning profiles (needs your Apple Developer account; `eas credentials` to inspect).
- Android: generate and store the upload keystore.

Hand-managing keystores/certs is a common source of "works on my machine" pain. Only manage them yourself if your org requires it; if so, `eas credentials` is the management UI. App-specific store details (bundle IDs, App Store Connect API key) live in [../store/app-store-connect.md](../store/app-store-connect.md).

## Environment variables per profile

Prefer **EAS Environment Variables** over committed `.env` files:

```bash
eas env:create --name EXPO_PUBLIC_SUPABASE_URL --value "https://..." --environment production
eas env:list
```

Set `"environment": "production"` (etc.) on a build profile to bind which env set it uses. `EXPO_PUBLIC_*` vars get inlined into the bundle (non-secrets only); true secrets used at *build* time can be marked sensitive. Runtime secrets still belong in Edge Functions, not the build → [../cicd/secrets-release.md](../cicd/secrets-release.md).

## Common build failures

- **iOS "useFrameworks" / pod errors** after adding RN Firebase → add `expo-build-properties` with `ios.useFrameworks: "static"`.
- **Android "duplicate build number"** on submit → ensure `autoIncrement` (or `appVersionSource: "remote"`) is set.
- **Version mismatch / native module not found** → you changed JS but not the native build; rebuild, and if it's an OTA-only change push it via `eas update` instead.
- **Wrong SDK deps** → `npx expo install --fix`.

Automating these in CI → [../cicd/eas-workflows.md](../cicd/eas-workflows.md).
