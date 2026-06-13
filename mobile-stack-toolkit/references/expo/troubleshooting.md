---
title: Local toolchain troubleshooting
impact: MEDIUM
impactDescription: "Covers the recurring Xcode/Android Studio/Metro failures that cost hours of debugging"
tags: expo, troubleshooting, xcode, android, metro
---

# Local toolchain troubleshooting

The emulator/simulator and native toolchain cause more lost hours than actual code. These are the recurring ones and their fixes.

## Contents
- [Android: emulator / ADB](#android-emulator--adb)
- [Android: build & Gradle](#android-build--gradle)
- [iOS: simulator](#ios-simulator)
- [iOS: pods & build](#ios-pods--build)
- [Metro & JS layer](#metro--js-layer)
- [Nuclear options](#nuclear-options)

## Android: emulator / ADB

- **"device offline" / device not listed:**
  ```bash
  adb kill-server && adb start-server
  adb devices            # should now list the emulator
  ```
- **Emulator won't boot / stuck, or "lock" files after a crash:** a hard-killed emulator leaves stale `*.lock` files in the AVD dir. Delete them:
  ```bash
  rm ~/.android/avd/<AvdName>.avd/*.lock
  # then cold boot:
  emulator -avd <AvdName> -no-snapshot-load
  ```
  List AVDs with `emulator -list-avds`.
- **Wipe a corrupted emulator state:** cold boot or `emulator -avd <name> -wipe-data` (resets the virtual device).
- **App installed but won't update / weird native cache:** `adb uninstall com.you.myapp` then reinstall the Dev Build.

## Android: build & Gradle

- **Gradle daemon weirdness / stale cache:**
  ```bash
  cd android && ./gradlew clean && cd ..
  ```
- **After changing native deps/plugins:** regenerate native folders — `npx expo prebuild --clean` (only if you manage them; otherwise let `eas build` do it).
- **`JAVA_HOME` / JDK errors:** ensure a compatible JDK (17+) is active; mismatched Java is a top Android build failure.

## iOS: simulator

- **Simulator unresponsive / app won't launch:** `xcrun simctl shutdown all` then reopen, or **Device → Erase All Content and Settings** in the Simulator app.
- **List & boot specific simulators:** `xcrun simctl list devices`, `xcrun simctl boot "iPhone 16"`.
- **Stale install:** `xcrun simctl uninstall booted com.you.myapp`.

## iOS: pods & build

- **Pod install errors after adding a native lib (esp. RN Firebase):**
  - Ensure `expo-build-properties` sets `ios.useFrameworks: "static"`.
  - Then: `npx expo prebuild --clean` (regenerates `ios/` + reinstalls pods).
  - Manual fallback: `cd ios && pod install --repo-update && cd ..`.
- **"Multiple commands produce…" / signing errors locally:** prefer `eas build` (cloud, managed credentials) over fighting Xcode signing on your machine.

## Metro & JS layer

- **Module resolution / "unable to resolve" after install:** restart Metro with a clean cache:
  ```bash
  npx expo start --clear
  ```
- **Dependency/version drift:** `npx expo install --check` then `--fix`.
- **Native module "not found" in a build that used to work:** you added a native dep but didn't rebuild — make a new Dev Build; this is *not* an OTA-able change → [ota-updates.md](ota-updates.md).

## Nuclear options

In rough order, escalate only as needed:
1. `npx expo start --clear` (Metro cache).
2. `rm -rf node_modules && npm install` (or your package manager's clean install).
3. `npx expo prebuild --clean` (regenerate native projects).
4. `watchman watch-del-all` (stale file-watcher state, macOS).
5. Cold-boot/erase the emulator/simulator.
6. Last resort: build in the cloud with `eas build` to rule out local toolchain entirely.

> Rule of thumb: if it "worked yesterday" and you only changed JS, suspect Metro cache. If you changed native deps, suspect the build — rebuild rather than reload.
