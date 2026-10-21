---
title: "Connectivity hints and request failures"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Connectivity hints and request failures

`Connectivity().checkConnectivity()` and `onConnectivityChanged` return a list of network types. A connected interface does not prove internet or backend availability. Use it for UI hints and handle real request failures regardless of the reported status.

```dart
final results = await Connectivity().checkConnectivity();
final hasInterface = !results.contains(ConnectivityResult.none);
final subscription = Connectivity().onConnectivityChanged.listen((results) {
  // Publish an interface-status hint to application state.
});
// On disposal:
await subscription.cancel();
```

Check initial state, recheck on resume and guard async widget updates with mounted/disposal state. Do not block every request based on a possibly stale hint. DNS lookup of google.com is not an HTTP reachability test for your backend and uses dart:io APIs unavailable on web.

When a reachability probe is useful, use a small bounded HTTPS request to an endpoint you control and distinguish auth/server errors from loss of connectivity. Avoid constant polling. For offline mutations, design a queue with conflict resolution and idempotency rather than blindly replaying requests.

Render a simple status widget or a MaterialBanner with its required actions; do not label Wi-Fi availability as confirmed online access.

## Sources

Reviewed 2026-10-20: [connectivity_plus](https://pub.dev/packages/connectivity_plus).
