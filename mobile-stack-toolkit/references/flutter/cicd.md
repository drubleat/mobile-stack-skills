---
title: Flutter CI/CD: Codemagic vs GitHub Actions
impact: MEDIUM-HIGH
impactDescription: "Codemagic has Flutter-native signing workflows; GitHub Actions is cheaper at scale with proper Fastlane setup"
tags: flutter, cicd, codemagic, github-actions, fastlane
---

# Flutter CI/CD: Codemagic vs GitHub Actions

## Build commands

```bash
# Debug
flutter build apk --debug
flutter build ios --debug --no-codesign

# Release
flutter build appbundle --release \
  --dart-define=SUPABASE_URL=https://... \
  --dart-define=SUPABASE_ANON_KEY=sb_publishable_...

flutter build ipa --release \
  --dart-define=SUPABASE_URL=https://... \
  --dart-define=SUPABASE_ANON_KEY=sb_publishable_...
```

## Codemagic

Codemagic is the most Flutter-native CI option — it has a UI workflow builder, handles code signing out of the box, and uploads to stores directly. Best for teams that want minimal YAML.

### codemagic.yaml

```yaml
workflows:
  flutter-production:
    name: Production build
    environment:
      flutter: stable
      xcode: latest
      cocoapods: default
      vars:
        SUPABASE_URL: $SUPABASE_URL         # from Codemagic environment variables
        SUPABASE_ANON_KEY: $SUPABASE_ANON_KEY
    triggering:
      events: [push]
      branch_patterns:
        - pattern: main
    scripts:
      - name: Get Flutter packages
        script: flutter pub get
      - name: Generate code
        script: dart run build_runner build --delete-conflicting-outputs
      - name: Run tests
        script: flutter test
      - name: Build Android
        script: |
          flutter build appbundle --release \
            --dart-define=SUPABASE_URL=$SUPABASE_URL \
            --dart-define=SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
      - name: Build iOS
        script: |
          flutter build ipa --release \
            --dart-define=SUPABASE_URL=$SUPABASE_URL \
            --dart-define=SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY \
            --export-options-plist=/Users/builder/export_options.plist
    artifacts:
      - build/app/outputs/bundle/release/*.aab
      - build/ios/ipa/*.ipa
    publishing:
      app_store_connect:
        api_key: $APP_STORE_CONNECT_PRIVATE_KEY
        key_id: $APP_STORE_CONNECT_KEY_IDENTIFIER
        issuer_id: $APP_STORE_CONNECT_ISSUER_ID
        submit_to_testflight: true
      google_play:
        credentials: $GCLOUD_SERVICE_ACCOUNT_CREDENTIALS
        track: internal
```

Codemagic manages iOS code signing automatically when you connect your Apple Developer account in the dashboard.

## GitHub Actions

More control, more setup. Required if you're already using GitHub Actions for other workflows (Supabase migrations, etc.).

```yaml
# .github/workflows/flutter-build.yml
name: Flutter build

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: 'stable'
          cache: true
      - run: flutter pub get
      - run: dart run build_runner build --delete-conflicting-outputs
      - run: flutter test

  build-android:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: 'stable'
          cache: true
      - run: flutter pub get
      - run: dart run build_runner build --delete-conflicting-outputs
      - name: Build AAB
        run: |
          flutter build appbundle --release \
            --dart-define=SUPABASE_URL=${{ secrets.SUPABASE_URL }} \
            --dart-define=SUPABASE_ANON_KEY=${{ secrets.SUPABASE_ANON_KEY }}
      - name: Upload to Play Internal
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.GCLOUD_SERVICE_ACCOUNT }}
          packageName: com.yourcompany.app
          releaseFiles: build/app/outputs/bundle/release/app-release.aab
          track: internal

  build-ios:
    runs-on: macos-latest           # iOS build requires macOS runner
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: 'stable'
          cache: true
      - run: flutter pub get
      - run: dart run build_runner build --delete-conflicting-outputs
      - name: Install certificates (from GitHub Secrets)
        uses: apple-actions/import-codesign-certs@v3
        with:
          p12-file-base64: ${{ secrets.DISTRIBUTION_CERTIFICATE_P12 }}
          p12-password: ${{ secrets.DISTRIBUTION_CERTIFICATE_PASSWORD }}
      - name: Build IPA
        run: |
          flutter build ipa --release \
            --dart-define=SUPABASE_URL=${{ secrets.SUPABASE_URL }} \
            --dart-define=SUPABASE_ANON_KEY=${{ secrets.SUPABASE_ANON_KEY }}
      - name: Upload to TestFlight
        uses: apple-actions/upload-testflight-build@v1
        with:
          app-path: build/ios/ipa/*.ipa
          issuer-id: ${{ secrets.ASC_ISSUER_ID }}
          api-key-id: ${{ secrets.ASC_KEY_ID }}
          api-private-key: ${{ secrets.ASC_PRIVATE_KEY }}
```

**macOS runner is required for iOS builds** — GitHub Actions charges more for macOS runners than Linux. Codemagic builds iOS on dedicated Mac infrastructure at a fixed monthly price, which is often cheaper for active projects.

## Codemagic vs GitHub Actions

| | Codemagic | GitHub Actions |
|---|---|---|
| iOS signing | Auto (UI config) | Manual (certs as secrets) |
| Cost model | Per-build minutes | Per-runner minutes |
| Flutter support | First-class | Via subosito/flutter-action |
| macOS runners | Dedicated Mac Minis | Standard (limited) |
| Integration with GH PR checks | Yes | Native |
| Best for | iOS-heavy Flutter teams | Teams already on GitHub Actions |

## Code generation in CI

Always run `dart run build_runner build` in CI before building. Generated files (`*.g.dart`, `*.freezed.dart`) should be in `.gitignore` — regenerate them in every build rather than committing them.

```bash
dart run build_runner build --delete-conflicting-outputs
```

## Versioning

Flutter uses `version: 1.0.0+1` in `pubspec.yaml` (version + build number). Automate build number increment in CI:

```bash
# Get commit count as build number
BUILD_NUMBER=$(git rev-list --count HEAD)
flutter build appbundle --release --build-number=$BUILD_NUMBER
```
