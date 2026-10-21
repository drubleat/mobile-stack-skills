---
title: "Firebase AI Logic"
impact: HIGH
impactDescription: "Avoid incompatible APIs and unsafe mobile integration defaults"
tags: mobile, integration, correctness
---

# Firebase AI Logic

Firebase AI Logic provides a managed client route to supported Google models without embedding a Gemini secret API key. App Check attests the client; Firebase Authentication identifies the user. Neither automatically enforces your subscription entitlement or arbitrary business authorization.

## Setup

Enable the chosen provider through the Firebase console or the documented CLI workflow for the installed CLI. Use the supported model catalog rather than inventing a model-list command. Configure billing, quotas, and App Check enforcement; initialization alone is monitoring, not enforcement.

For Flutter add compatible versions with `flutter pub add firebase_core firebase_ai firebase_app_check`, run `flutterfire configure`, initialize Firebase, then activate App Check before AI requests. Check the installed package's provider constructors. Do not combine old App Check pins with new Firebase core majors.

For React Native the package is `@react-native-firebase/ai`:

```ts
import { getApp } from '@react-native-firebase/app';
import { getAI, getGenerativeModel, GoogleAIBackend } from '@react-native-firebase/ai';
const ai = getAI(getApp(), { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: configuredModelName });
const result = await model.generateContent('Explain this feature briefly.');
const text = result.response.text();
```

Use the matching native Firebase setup and development build. Set a safe fallback if Remote Config provides the model; reject empty/unsupported values. Do not rely on a mutable client-selected model as the sole cost control.

Use your trusted backend when requests require paid entitlement checks, secret business logic, cross-provider calls, or stronger per-user enforcement. See [proxy architecture](../ai/edge-proxy-architecture.md). Test App Check enforcement, debug/release attestation, quota failures, rejected content, and model retirement.

## Sources

Reviewed 2026-10-20: [RN Firebase AI Logic](https://rnfirebase.io/ai/usage), [Firebase AI Logic](https://firebase.google.com/docs/ai-logic/get-started).
