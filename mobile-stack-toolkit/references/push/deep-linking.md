---
title: "Notification deep links"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Notification deep links

Treat notification payloads and incoming URLs as untrusted input. Prefer a small typed payload such as `{type: "item_updated", item_id: "..."}` and map it to known routes. Do not call router navigation directly with arbitrary payload URLs.

Validate scheme/host/path, identifier syntax and size. Reject external schemes, unexpected routes and malformed encoding. Store a pending navigation intent while session restoration/router initialization completes; do not use an arbitrary timeout to guess readiness. After sign-in, fetch the target under the current user's authorization and show an unavailable state if access is denied.

Deduplicate opens using a stable notification/event identifier. Handle the initial launch response and later response listeners through the same dispatcher, and clear consumed responses where the SDK supports it. Dispose subscriptions so rerenders do not register multiple handlers.

Expo Router accepts mapped internal routes; use typed route objects for parameters. Flutter GoRouter should receive the same validated intent through a retained router/controller, not a global widget context. Universal/App Links also require the correct server association files and native configuration, not only a URL scheme in app config.

Test a signed-out cold launch, account switch, deleted item, malformed payload, external URL, duplicate response and denied access. See [handlers](handlers-state.md).

## Sources

Reviewed 2026-10-20: [Expo linking](https://docs.expo.dev/linking/into-your-app/), [Firebase message handling](https://firebase.google.com/docs/cloud-messaging/flutter/receive).
