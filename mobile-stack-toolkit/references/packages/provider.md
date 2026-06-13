---
title: provider 6.1.5+1 — InheritedWidget state management
impact: MEDIUM-HIGH
impactDescription: "Simplest state management for small/medium apps; MultiProvider at root is the standard pattern"
tags: flutter, state, provider, inherited-widget
---

# provider — InheritedWidget state management

**Version:** 6.1.5+1  
**Platforms:** all (no native code)

```yaml
dependencies:
  provider: ^6.1.5+1
```

> **Stack note:** This skill defaults to Riverpod for new projects — see [../flutter/project-setup.md](../flutter/project-setup.md). Use `provider` when working with existing codebases or packages that expose `ChangeNotifier`.

## Setup

```dart
import 'package:provider/provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthNotifier()),
        ChangeNotifierProvider(create: (_) => CartNotifier()),
        // Lazy-loaded by default — only instantiated when first used
      ],
      child: const MyApp(),
    ),
  );
}
```

## ChangeNotifier model

```dart
class CartNotifier extends ChangeNotifier {
  final List<CartItem> _items = [];
  List<CartItem> get items => List.unmodifiable(_items);
  int get count => _items.length;
  double get total => _items.fold(0, (sum, item) => sum + item.price);

  void add(CartItem item) {
    _items.add(item);
    notifyListeners();  // triggers rebuild of all watchers
  }

  void remove(CartItem item) {
    _items.remove(item);
    notifyListeners();
  }

  Future<void> checkout() async {
    await someApi.checkout(_items);
    _items.clear();
    notifyListeners();
  }
}
```

## Read vs Watch

```dart
// context.watch<T>() — rebuild this widget whenever T notifies
// Use in build() method
class CartButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final count = context.watch<CartNotifier>().count;
    return Badge(label: Text('$count'), child: const Icon(Icons.shopping_cart));
  }
}

// context.read<T>() — access without subscribing to changes
// Use in callbacks (onTap, onPressed, etc.)
ElevatedButton(
  onPressed: () => context.read<CartNotifier>().add(item),
  child: const Text('Add to cart'),
)

// context.select<T, R>() — rebuild only when selected value changes
final total = context.select<CartNotifier, double>((cart) => cart.total);
```

## Consumer widget (for partial rebuilds)

```dart
// Only rebuilds the Badge, not the whole screen
Consumer<CartNotifier>(
  builder: (context, cart, child) {
    return Badge(
      label: Text('${cart.count}'),
      child: child!,
    );
  },
  child: const Icon(Icons.shopping_cart),  // 'child' doesn't rebuild
)
```

## Provider types

| Type | Use case |
|---|---|
| `Provider<T>` | Provide an immutable value |
| `ChangeNotifierProvider<T>` | Mutable model with `notifyListeners()` |
| `FutureProvider<T>` | Async value that loads once |
| `StreamProvider<T>` | Stream of values (e.g. auth state) |
| `ProxyProvider<A, B>` | B depends on A |

```dart
// StreamProvider — auth state
StreamProvider<User?>(
  create: (_) => FirebaseAuth.instance.authStateChanges(),
  initialData: null,
)

// ProxyProvider — one provider depends on another
ProxyProvider<AuthNotifier, ApiService>(
  update: (_, auth, __) => ApiService(token: auth.token),
)
```

## Access from anywhere (without context)

For accessing providers outside the widget tree (from services, repositories):

```dart
// Define a global key
final navigatorKey = GlobalKey<NavigatorState>();

// Access provider via navigator context
final cart = Provider.of<CartNotifier>(
  navigatorKey.currentContext!,
  listen: false,
);
```

Or restructure so providers are only accessed from widgets.

## Gotchas

- `context.watch<T>()` **must** be called inside `build()` — not in `initState`, callbacks, or async functions.
- `context.read<T>()` in `build()` looks like it works but won't rebuild — always use `watch` in build, `read` in callbacks.
- Placing a `ChangeNotifierProvider` inside a widget that rebuilds frequently recreates the notifier on every rebuild. Always place providers above the widget that needs them, typically near the root.
- `notifyListeners()` after `dispose()` throws. Guard with `if (!hasListeners)` or use `mounted` checks in async methods.
- `MultiProvider` order matters for `ProxyProvider` — the dependency must come before the dependent.
