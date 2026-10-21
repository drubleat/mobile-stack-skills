---
title: "Maestro flows and reproducible test builds"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Maestro flows and reproducible test builds

Install a reviewed Maestro release using its official setup guide. Inspect the running device's hierarchy before choosing selectors; use stable IDs for icon/localized controls and text for user-visible behavior. Accessibility labels are normally matched through documented text selectors, not an invented `description` property.

```yaml
appId: ${APP_ID}
---
- launchApp:
    clearState: true
- tapOn:
    id: email-input
- inputText: ${TEST_EMAIL}
- tapOn:
    id: password-input
- inputText: ${TEST_PASSWORD}
- tapOn: Sign In
- extendedWaitUntil:
    visible: Dashboard
    timeout: 10000
- takeScreenshot: signed-in
```

Run `maestro test -e APP_ID=com.example.app -e TEST_EMAIL=test@example.com -e TEST_PASSWORD=test-password flows/login.yaml` against a disposable test account and installed test app. Do not put real credentials in flows. `assertTrue` evaluates an expression inside `${...}`, for example `${output.title === 'Home'}`; interpolation followed by literal comparison text is not equivalent.

CI must boot a supported simulator/emulator, wait for readiness, build/download the correct platform artifact, install it and then run flows. An iOS simulator requires a simulator `.app`, not a device `.ipa`. Capture logs/screenshots on failure and pin the device/runtime/tool versions. Do not present an uninstalled placeholder path as a working CI pipeline.

Expo Go and a custom development build are different binaries. Prefer an app-owned test build; account for Metro/dev-client startup if using one. Release-like embedded-JS builds remove that dependency. Deep links can test navigation when intentionally configured; UI tests need not avoid them universally.

Clear-state behavior differs by platform and does not guarantee deletion of backend data or every secure credential. Reset fixtures explicitly. Test denied permissions, offline recovery and account switching in addition to the happy path.

## Sources

Reviewed 2026-10-20: [Maestro selectors](https://docs.maestro.dev/api-reference/selectors), [assertTrue](https://docs.maestro.dev/api-reference/commands/asserttrue).
