---
title: App Store Connect: setup, credentials, TestFlight
impact: HIGH
impactDescription: "Bundle ID, certificates, and provisioning profiles must be configured in App Store Connect before first EAS Build"
tags: store, app-store, ios, testflight, certificates
---

# App Store Connect: setup, credentials, TestFlight

## 1. Create the app record

App Store Connect → My Apps → **+** → New App:
- **Bundle ID**: must match exactly what's in `app.config.ts` (`ios.bundleIdentifier`). Create it in Certificates, Identifiers & Profiles first if it doesn't exist.
- **SKU**: internal unique string (use the bundle ID or a variation).
- **Name**: the public app name (can be changed before release, harder after).
- **Primary language**.

## 2. Credentials: let EAS manage them

EAS handles iOS credentials automatically:
- **Distribution certificate**: identifies you as the developer. EAS creates and manages it.
- **Provisioning profile**: ties the certificate to your app's bundle ID + devices. EAS generates App Store and Ad Hoc profiles automatically.

```bash
eas credentials              # inspect/manage credentials
eas build:configure          # sets up EAS project and credentials
```

You only need to touch credentials manually if your organization requires it or if you need to add specific devices to an Ad Hoc profile. Otherwise: let EAS own it.

## 3. App Store Connect API Key (for EAS Submit)

To automate submission without Apple ID 2FA prompts:
1. App Store Connect → Users and Access → Integrations → **App Store Connect API**.
2. Generate a key with **App Manager** role. Download the `.p8` file (once only).
3. Store in EAS:
```bash
eas secret:create --scope project --name APP_STORE_CONNECT_API_KEY_ID --value "XXXXXXXXXX"
eas secret:create --scope project --name APP_STORE_CONNECT_ISSUER_ID --value "xxx-xxx-..."
```
Or configure in `eas.json`:
```json
"submit": {
  "production": {
    "ios": {
      "appleId": "you@example.com",
      "ascAppId": "1234567890"
    }
  }
}
```

## 4. TestFlight

TestFlight distributes builds to testers before public release.

- **Internal Testing**: up to 100 Apple ID testers, no review needed, available within minutes of upload.
- **External Testing**: up to 10,000 testers, requires Beta App Review (usually ~1 day).

Workflow:
1. `eas build --profile production` → EAS uploads to App Store Connect automatically.
2. App Store Connect → TestFlight → the build appears (processing takes 5–15 min).
3. Add internal testers → they get an invite email.

For CI/CD auto-distribution on every `main` merge → [../cicd/eas-workflows.md](../cicd/eas-workflows.md).

## 5. App review submission

Before submitting for review:
- Fill in "App Information" (category, age rating, content rights).
- Add screenshots for all required device sizes → [aso-assets.md](aso-assets.md).
- Complete "Privacy" section (data collection, privacy policy URL).
- If the app has a login requirement: provide demo account credentials to the reviewer.
- If the app uses push notifications, payments, camera, etc.: add notes to the reviewer explaining why.

Submit: App Store Connect → [Your App] → App Review → Submit for Review.

Average review time: 24–48 hours for first submission; faster for updates.

## Common mistakes

- **Bundle ID mismatch** between `app.config.ts`, EAS, and ASC → build rejected at upload or wrong provisioning profile used.
- **No demo account for reviewer** → reviewer can't test; app gets rejected with "we were unable to sign in."
- **Missing reviewer notes** for features that aren't obvious (e.g. "this requires a physical scan of a receipt to function").
- **Submitting before screenshots are done** → rejected immediately; reviewer doesn't test, just rejects.
