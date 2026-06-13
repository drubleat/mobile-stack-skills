---
title: Firebase App Distribution: pre-release builds to testers
impact: MEDIUM
impactDescription: "Faster tester feedback loop than TestFlight; tester groups can be managed without Apple Developer account setup"
tags: firebase, app-distribution, testing, testers
---

# Firebase App Distribution

App Distribution lets you distribute pre-release builds to testers without going through TestFlight or Play Internal Testing. It's most useful for:
- **Client demos**: share a link, testers install without needing an Apple Developer account invite.
- **QA cycles**: faster than TestFlight's processing; available within minutes.
- **Firebase-only projects**: if you're not using EAS, App Distribution is the native path for build sharing.

If you're using EAS, TestFlight (iOS) and Play Internal Testing (Android) are usually better choices — they test the same distribution path as production. Use App Distribution when you need to share quickly outside the store ecosystem.

## Setup

1. Firebase Console → your project → App Distribution → Get started.
2. Register iOS and Android apps (if not already done for Crashlytics/Analytics).
3. Install the App Distribution CLI plugin:

```bash
npm install -g firebase-tools
# For Expo/EAS: use the firebase-appdistribution EAS build runner or the CLI
```

## Distribute a build via CLI

```bash
# iOS (.ipa)
firebase appdistribution:distribute MyApp.ipa \
  --app 1:123456789:ios:abcdef \
  --groups "internal-testers,qa-team" \
  --release-notes "$(git log -1 --pretty=%B)"

# Android (.apk or .aab)
firebase appdistribution:distribute app-release.apk \
  --app 1:123456789:android:abcdef \
  --groups "internal-testers" \
  --release-notes "Build $(date +%Y%m%d)"
```

The `--app` flag uses the App ID from Firebase Console → Project settings → Your apps.

## Tester groups

Create tester groups in Firebase Console → App Distribution → Testers & Groups. Groups can be referenced by name in CLI commands and the dashboard.

Add testers by email:

```bash
firebase appdistribution:testers:add tester@example.com --app <APP_ID>
```

Testers receive an email with a download link. First-time iOS testers must install the Firebase App Distribution profile (one-time setup).

## GitHub Actions integration

```yaml
# .github/workflows/distribute.yml
name: Distribute to testers

on:
  push:
    branches: [develop]

jobs:
  distribute-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - name: Build Android (preview APK)
        run: eas build --platform android --profile preview --non-interactive --output ./app.apk
      - name: Distribute to testers
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{ secrets.FIREBASE_ANDROID_APP_ID }}
          serviceCredentialsFileContent: ${{ secrets.FIREBASE_SERVICE_CREDENTIALS }}
          groups: internal-testers
          file: ./app.apk
          releaseNotes: ${{ github.event.head_commit.message }}
```

## EAS Build + App Distribution

EAS doesn't have native App Distribution support, but the output artifacts can be passed directly to the Firebase CLI:

```bash
# Download the artifact from EAS and pass to firebase CLI
eas build:download --id <BUILD_ID> --output ./build.apk
firebase appdistribution:distribute ./build.apk --app <APP_ID> --groups qa
```

Or use the EAS build webhook to trigger distribution automatically after a build completes.

## vs TestFlight / Play Internal Testing

| Feature | Firebase App Distribution | TestFlight | Play Internal Testing |
|---|---|---|---|
| iOS reviewer required? | No | No (internal) / Yes (external) | N/A |
| Tests same install path as production? | No (ad-hoc/enterprise) | Yes | Yes |
| Processing time | Minutes | 5–30 min | Minutes |
| Max testers | Unlimited | 100 (internal) / 10k (external) | 100 |
| Tester setup friction | Low (email link + profile) | Low (email link) | Low |

For client demos or fast QA: App Distribution wins on speed. For final pre-release testing: TestFlight/Play Internal Testing win because they test the same code path as production.

## Flutter

```bash
# Build first
flutter build apk --release

# Distribute
firebase appdistribution:distribute build/app/outputs/flutter-apk/app-release.apk \
  --app <ANDROID_APP_ID> \
  --groups "testers"
```

The `flutterfire_cli` and App Distribution are separate tools — `flutterfire configure` doesn't affect App Distribution setup.
