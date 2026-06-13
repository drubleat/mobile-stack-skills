---
title: Navigation: go_router 17.x
impact: HIGH
impactDescription: "go_router ShellRoute pattern is required for bottom nav with nested stacks; wrong setup breaks back-button behavior"
tags: flutter, navigation, go_router, routing
---

# Navigation: go_router

Version: `go_router: ^17.3.0`

go_router is the Flutter team's recommended navigation package. It supports declarative routing, deep links, URL-based navigation, and route guards.

## Basic setup

```dart
// lib/app.dart
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final isLoggedIn = authState.valueOrNull?.session != null;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');

      if (!isLoggedIn && !isAuthRoute) return '/auth/login';
      if (isLoggedIn && isAuthRoute) return '/';
      return null;
    },
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/auth/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/paywall',
        builder: (context, state) => const PaywallScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
        routes: [
          GoRoute(
            path: 'profile',
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/post/:id',
        builder: (context, state) {
          final id = state.pathParameters['id']!;
          return PostScreen(id: id);
        },
      ),
    ],
  );
});

// In app.dart
class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      routerConfig: router,
    );
  }
}
```

## Navigation

```dart
// Push a named route
context.go('/post/123');
context.push('/paywall');    // push adds to stack; go replaces

// With query parameters
context.go('/search?q=flutter');

// Read path parameters in the destination
final id = GoRouterState.of(context).pathParameters['id'];

// Read query parameters
final query = GoRouterState.of(context).uri.queryParameters['q'];
```

## Shell routes (bottom navigation / tabs)

```dart
ShellRoute(
  builder: (context, state, child) => ScaffoldWithBottomNav(child: child),
  routes: [
    GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
    GoRoute(path: '/discover', builder: (_, __) => const DiscoverScreen()),
    GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
  ],
)
```

`ShellRoute` persists a common shell widget (like a bottom nav bar) while swapping the child as routes change.

## Auth guard with Riverpod

```dart
final routerProvider = Provider<GoRouter>((ref) {
  // Router listens to auth state and rebuilds when it changes
  ref.listen(authStateProvider, (_, __) {});

  return GoRouter(
    refreshListenable: GoRouterRefreshStream(
      Supabase.instance.client.auth.onAuthStateChange,
    ),
    redirect: (context, state) {
      final isAuthenticated = Supabase.instance.client.auth.currentUser != null;
      if (!isAuthenticated && !state.matchedLocation.startsWith('/auth')) {
        return '/auth/login';
      }
      return null;
    },
    routes: [...],
  );
});
```

`GoRouterRefreshStream` converts a Stream into a `Listenable` that triggers router rebuilds.

## Deep link handling

go_router handles deep links automatically when configured in `AndroidManifest.xml` (intent filters) and `Info.plist` (`CFBundleURLTypes`). For Supabase auth email redirects:

```dart
GoRoute(
  path: '/auth/callback',
  builder: (context, state) {
    // Supabase handles the callback token exchange automatically via deep link
    return const AuthCallbackScreen();
  },
)
```

## Page transitions

```dart
GoRoute(
  path: '/paywall',
  pageBuilder: (context, state) => CustomTransitionPage(
    key: state.pageKey,
    child: const PaywallScreen(),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      return SlideTransition(
        position: animation.drive(
          Tween(begin: const Offset(0, 1), end: Offset.zero)
              .chain(CurveTween(curve: Curves.easeOut)),
        ),
        child: child,
      );
    },
  ),
)
```

## Gotchas

- `context.go()` replaces the entire stack; `context.push()` adds to it. Use `go()` for tab navigation, `push()` for drill-down.
- The `redirect` function is called on every navigation. Keep it fast — no async calls, just read already-loaded state.
- Nested `GoRoute`s under a parent use relative paths — `/settings/profile`, not `profile`.
- go_router v17 requires Dart 3.0+ and Flutter 3.22+.
