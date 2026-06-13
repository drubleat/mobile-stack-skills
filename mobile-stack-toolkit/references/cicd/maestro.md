---
title: Maestro — mobile E2E testing with YAML flows
impact: MEDIUM
impactDescription: "Maestro tests the real app UI without code instrumentation; wrong selectors or missing testID props cause all assertions to fail"
tags: maestro, e2e-testing, testing, expo, react-native, automation
---

# Maestro — Mobile E2E Testing

Maestro is a black-box UI testing framework for iOS and Android. Tests are YAML files called "Flows". No code instrumentation needed — Maestro drives the app through the same accessibility layer as a real user.

**Website:** [docs.maestro.dev](https://docs.maestro.dev)  
**Supported Android API levels:** 29, 30, 31, 33, 34 (API 35+ support arriving later in 2026)

---

## Install

Download **Maestro Studio** from [studio.maestro.dev](https://studio.maestro.dev):
- macOS: `.dmg`
- Windows: `.exe`
- Linux: `.AppImage`

Or install the CLI via shell:

```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
```

Verify:

```bash
maestro --version
```

---

## Flow structure

A Flow is a YAML file. The `---` separator divides the header (metadata) from the commands.

```yaml
# flows/login.yaml
appId: com.yourcompany.yourapp   # iOS bundle ID or Android package name
---
- launchApp:
    clearState: true             # fresh app start (clears AsyncStorage/MMKV)
- tapOn: "Continue with Email"
- tapOn:
    id: "email-input"
- inputText: "test@example.com"
- tapOn:
    id: "password-input"
- inputText: "password123"
- tapOn: "Sign In"
- assertVisible: "Welcome back"
```

---

## Selectors

Maestro selects elements by multiple strategies:

### Text (simplest)
```yaml
- tapOn: "Sign In"
- assertVisible: "Welcome"
```

### testID → id (recommended for robustness)

Set `testID` on React Native components — Maestro maps it to the `id` selector:

```tsx
<Pressable testID="login-button">
  <Text>Sign In</Text>
</Pressable>
```

```yaml
- tapOn:
    id: "login-button"
```

### Accessibility label (description)
```yaml
- tapOn:
    description: "Close modal"
```

### Index (when multiple elements match)
```yaml
- tapOn:
    text: "Delete"
    index: 1    # second match (0-indexed)
```

### Coordinates (last resort)
```yaml
- tapOn:
    point: "50%,50%"   # center of screen
```

---

## Core commands

### Input

```yaml
- inputText: "hello world"     # types into focused field
- tapOn:
    id: "search-field"
- inputText: "coffee shops"
- pressKey: Return             # submit
```

### Scroll

```yaml
- scroll                       # scroll down
- scrollUntilVisible:
    element:
      text: "Load more"
    direction: DOWN
    timeout: 5000              # ms
```

### Assert

```yaml
- assertVisible: "Dashboard"
- assertNotVisible: "Error"
- assertTrue:
    condition: "${title} == 'Home'"
```

### Wait

```yaml
- waitForAnimationToEnd
- extendedWaitUntil:
    visible:
      text: "Ready"
    timeout: 10000
```

### Take screenshot

```yaml
- takeScreenshot: after-login
```

---

## Run flows

```bash
# Run a single flow (device/simulator must be running)
maestro test flows/login.yaml

# Run all flows in a directory
maestro test flows/

# Pass environment variables (for dynamic appId or test data)
maestro test --env APP_ID=com.yourcompany.app flows/login.yaml
```

---

## Dynamic appId with env vars

```yaml
appId: ${APP_ID}
---
- launchApp
```

```bash
maestro test --env APP_ID=com.yourcompany.app flows/onboarding.yaml
```

---

## Run against an Expo dev build

Start your dev build on the simulator:

```bash
npx expo run:ios --simulator "iPhone 16"
# or
npx eas build --profile development --platform ios --local
```

Then run flows against it using the bundle ID from `app.config.ts`:

```bash
maestro test --env APP_ID=com.yourcompany.yourapp flows/
```

For Expo Go development builds, use the Expo Go bundle ID:
```yaml
appId: host.exp.exponent
---
- openLink: exp://127.0.0.1:8081
```

---

## Reusable sub-flows

Break repeated steps (login, navigation) into sub-flows and call them from other flows:

```yaml
# flows/sub/login.yaml
appId: ${APP_ID}
---
- tapOn: "Sign In"
- tapOn:
    id: "email-input"
- inputText: "${EMAIL}"
- tapOn:
    id: "password-input"
- inputText: "${PASSWORD}"
- tapOn: "Submit"
- assertVisible: "Dashboard"
```

```yaml
# flows/checkout.yaml
appId: ${APP_ID}
---
- runFlow:
    file: sub/login.yaml
    env:
      EMAIL: "test@example.com"
      PASSWORD: "password123"
- tapOn: "Shop"
- tapOn: "Add to cart"
- tapOn: "Checkout"
- assertVisible: "Order confirmed"
```

---

## CI integration (GitHub Actions)

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push]

jobs:
  e2e:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Maestro
        run: curl -Ls "https://get.maestro.mobile.dev" | bash

      - name: Start iOS Simulator
        run: xcrun simctl boot "iPhone 16" && open -a Simulator

      - name: Build dev app
        run: npx eas build --profile development --platform ios --local

      - name: Install app on simulator
        run: xcrun simctl install booted path/to/YourApp.app

      - name: Run flows
        run: maestro test flows/ --env APP_ID=com.yourcompany.app
```

---

## Gotchas

- **`testID` is the most reliable selector.** Text-based selectors break when copy changes. Add `testID` to all interactive elements in production code.
- **Flows are sequential.** If step 3 fails, the rest of the flow doesn't run. Keep flows short and focused on one user journey.
- **`clearState: true` in `launchApp`** resets AsyncStorage/MMKV between runs — essential for deterministic tests; skip it if you need to test state persistence.
- **Android API 35 (Pixel 9)** is not supported yet as of June 2026.
- **Expo Router file-based navigation** — Maestro doesn't know about routes. Navigate by tapping buttons/links, not by directly opening URLs.
- **Slow animations** can cause assertions to fail before elements appear — use `waitForAnimationToEnd` after navigation or modals.
