---
title: "Sentry integration and release verification"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Sentry integration and release verification

Use `@sentry/react-native` with the supported Expo integration. The setup wizard is useful for new integrations; inspect its diff in an existing app and preserve Metro/plugin settings from other packages. Resolve the SDK against the app's Expo/native versions.

Initialize early with the correct environment/DSN and wrap the root as documented. Choose tracing/profiling integrations and sampling from actual requirements and installed SDK support; a sampling number alone does not configure every navigation integration. Start without default PII collection and add only explicitly approved data. Clear user identity on logout and redact request/user content.

The DSN is public client configuration. `SENTRY_AUTH_TOKEN` is a build/upload credential; keep it in the protected CI/EAS environment using current environment-variable tooling. Never embed it in app config. Verify debug identifiers, source maps, native symbols and release matching using a known test error from the actual build/update.

A successful build or a configured plugin does not prove source-map upload worked. OTA updates need their own matching source-map upload flow. Validate readable stack traces in the dashboard, and monitor upload failures without exposing the token.

Use error boundaries for rendering failures and capture handled errors only when actionable. Keep a user-facing recovery state. Evaluate current pricing and data-retention settings separately from SDK setup.

## Sources

Reviewed 2026-10-20: [Sentry Expo](https://docs.sentry.io/platforms/react-native/manual-setup/expo/), [Expo Sentry guide](https://docs.expo.dev/guides/using-sentry/).
