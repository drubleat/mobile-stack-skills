---
title: "Native builds and generated projects"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Native builds and generated projects

Expo Go contains a fixed set of native modules. A library already included there can work; custom native modules/configuration require your own development build. Do not claim any native dependency automatically breaks Expo Go.

```bash
npx expo install expo-dev-client
eas build --profile development --platform ios
# Local native tooling alternative:
npx expo run:ios
```

Configure the development profile/signing first, install the resulting binary and use Metro for JS iteration. Rebuild whenever native dependencies/config change. A device build and a simulator build are different artifacts.

For Continuous Native Generation, app config and plugins are the source and generated ios/android directories can be excluded from Git. For deliberately maintained native projects, preserve those directories and their source edits. Inspect the repository's chosen workflow before changing it.

`expo prebuild --clean` removes and regenerates native projects; use it only when those folders are disposable or their changes are preserved. It is not a generic first response to every build error. Config plugins run during prebuild; existing native projects do not magically absorb every app-config change without that step.

Use service-specific plugins and framework settings documented for the installed SDK. Check build logs, signing and platform dependencies before clearing caches. See [build profiles](eas-build.md) and [troubleshooting](troubleshooting.md).

## Sources

Reviewed 2026-10-20: [development builds](https://docs.expo.dev/develop/development-builds/introduction/), [native generation](https://docs.expo.dev/workflow/continuous-native-generation/).
