---
title: Play Console: setup, Data Safety, release tracks
impact: HIGH
impactDescription: "Data Safety section is required before any production release; missing declarations cause policy violations"
tags: store, play-store, android, data-safety, release
---

# Play Console: setup, Data Safety, release tracks

## Initial setup

1. **Developer account**: one-time $25 fee. Use a Google account dedicated to the app/studio (not your personal account).
2. **Create app**: Play Console → All apps → Create app. Set default language, app or game, free or paid.
3. **Bundle ID (package name)**: set in `app.config.ts` as `android.package`. Must be globally unique (reverse-domain format: `com.yourcompany.appname`). **Cannot be changed after first release.**

## Target API level (2026 requirement)

Google requires new apps to target **API level 35** (Android 15) as of 2026. Updates to existing apps must also meet this target.

```ts
// app.config.ts
android: {
  targetSdkVersion: 35,
  compileSdkVersion: 35,
  minSdkVersion: 24,         // covers ~99%+ of active devices
}
```

EAS Build picks these up from `app.config.ts` and sets them in the Gradle files during prebuild.

## Data Safety form (mandatory)

Every app must complete the Data Safety section before publishing. This is the biggest source of "stuck in review" issues for first-time publishers.

Navigate to: Play Console → [App] → Policy → App content → Data safety.

Answer based on what your app and its SDKs actually do:

| Category | Collected if... |
|---|---|
| Name, email | You have user accounts / sign-up |
| Device or other IDs | You use Firebase, analytics SDKs |
| App interactions | Firebase Analytics, Crashlytics |
| Crash logs | Firebase Crashlytics |
| Financial info | RevenueCat / in-app purchases |
| Audio | You record voice / use STT |
| Photos / videos | You allow image upload |

**Firebase SDKs collect data even if you don't explicitly call collection methods.** Crashlytics collects crash data; Analytics collects device info and interaction data. Include these.

RevenueCat's privacy documentation lists exactly what it collects — copy it into the form.

## Release tracks

| Track | Audience | Review |
|---|---|---|
| **Internal testing** | Up to 100 Google accounts you specify | No review, available in minutes |
| **Closed testing (Alpha)** | Specific testers or groups | Brief review (~hours) |
| **Open testing (Beta)** | Anyone who opts in | Brief review |
| **Production** | Everyone | Full review (1–3 days typically) |

Workflow: Internal → Production (or Internal → Closed → Production for more validation). Always test on the Internal track before hitting Production.

## Staged rollout

Play Console lets you roll out a Production release to a percentage of users:

```
Production → 1% → 5% → 20% → 100%
```

Monitor crash rate and ANR rate (Play Console → Android vitals) at each stage. If crash rate spikes, halt the rollout before it reaches all users.

## Android App Bundle (AAB)

EAS Build produces a `.aab` (Android App Bundle) for production — not an APK. Play Console requires `.aab` for new apps. EAS Submit handles the upload automatically.

## Common Play Console mistakes

- **Data Safety form incomplete or inaccurate** → app rejected or removed. Fill it out carefully; Google cross-checks SDK libraries.
- **Package name changed** → you can't update an existing app with a different package name; you'd have to publish as a new app, losing all reviews.
- **Target API not updated** → Play blocks updates if you fall behind the required target SDK.
- **Signing key lost** → the Play App Signing service (enabled by default for new apps) holds the signing key on Google's side — you only upload the upload key. Use this; don't manage signing keys yourself.
