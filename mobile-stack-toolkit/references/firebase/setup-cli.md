---
title: "Firebase setup and agent tooling"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Firebase setup and agent tooling

Create/select the Firebase project and register the exact iOS bundle ID and Android application ID. Analytics can be enabled later; enabling a client SDK does not provision every backend service.

Use a tested Firebase CLI version via a project dev dependency (`npm install --save-dev firebase-tools`, then `npx firebase ...`) or an existing managed installation. Commit the lockfile. Inspect `npx firebase --help` before using service-specific init commands.

For Expo continuous native generation, keep downloaded `GoogleService-Info.plist` and `google-services.json` at stable paths referenced by `ios.googleServicesFile` and `android.googleServicesFile`. For manually maintained native projects, follow native platform file-placement instructions instead. Do not overwrite native changes by casually running clean prebuild.

Install matching `@react-native-firebase/*` releases and use their modular APIs. Configure the app plugin and only the service plugins documented by the installed packages; apply required iOS static-framework configuration. Rebuild the development client after native changes. The native default Firebase app initializes from platform config; access it with `getApp()` from `@react-native-firebase/app`.

Flutter uses `flutterfire configure`, then `Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform)` after `WidgetsFlutterBinding.ensureInitialized()`. Resolve compatible FlutterFire packages with `flutter pub add`; do not mix unrelated historical version pins.

For agent access, follow the official Firebase MCP setup for the selected client. The CLI's current server command is `firebase mcp`; do not copy the old `experimental:mcp` or put a long-lived CI token in repository settings. Configure Codex through its supported MCP settings/CLI, authenticate with the intended account and select the project explicitly. Inspect available tools before mutations; installing a skill does not authorize deployment.

## Sources

Reviewed 2026-10-20: [Firebase MCP](https://firebase.google.com/docs/ai-assistance/mcp-server), [React Native Firebase](https://rnfirebase.io/), [Flutter setup](https://firebase.google.com/docs/flutter/setup).
