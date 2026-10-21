---
title: "Flutter routing and auth state"
impact: HIGH
impactDescription: "Avoid incompatible APIs and unsafe mobile integration defaults"
tags: mobile, integration, correctness
---

# Flutter routing and auth state

Use the installed go_router version and platform link configuration. Keep a long-lived router; recreating it on every auth event can reset navigation. Read current auth state in redirects and notify the router on changes.

## Stream to router refresh adapter

`GoRouterRefreshStream` is not a current built-in API. Define an adapter and dispose both it and the router:

```dart
import 'dart:async';
import 'package:flutter/foundation.dart';

class RouterRefresh extends ChangeNotifier {
  RouterRefresh(Stream<Object?> events) {
    _subscription = events.listen((_) => notifyListeners(),
      onError: (Object error, StackTrace stack) => notifyListeners());
  }
  late final StreamSubscription<Object?> _subscription;
  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}
```

Pass the adapter as `refreshListenable` to `GoRouter`. Track auth loading/error separately; do not treat a restoration-in-progress state as signed out. Redirect signed-out users away from protected routes, allow auth callbacks to complete, and return users to a validated internal destination after sign-in. Route guards do not replace backend authorization.

## Navigation shape

- `context.go('/settings')` changes the declarative route location; `context.push('/detail/123')` adds an imperative page.
- Child route path `profile` under `/settings` produces `/settings/profile`.
- Use `ShellRoute` for a shared shell; use `StatefulShellRoute.indexedStack` when each tab must preserve its own navigator stack.
- Parse query parameters via `state.uri.queryParameters`; validate incoming IDs/routes. Avoid constructing URLs by raw string concatenation.
- Auth callbacks need matching Supabase redirect allowlists, native intent filters/URL schemes, and a configured callback exchange. A route by itself does not guarantee the session is restored.

Test cold-start links, auth restoration, sign-out, back navigation, tab stacks, and malformed/unauthorized deep links. In Riverpod 3 use current `AsyncValue` APIs (such as `.value`) rather than removed `.valueOrNull`.

## Sources

Reviewed 2026-10-20: [go_router](https://pub.dev/packages/go_router), [Riverpod 3 migration](https://riverpod.dev/docs/3.0_migration).
