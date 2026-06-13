---
title: connectivity_plus 7.1.1 — network type detection
impact: MEDIUM
impactDescription: "Returns connectivity type not actual internet access; always pair with a real HTTP probe for offline detection"
tags: flutter, connectivity, network, offline
---

# connectivity_plus — network type detection

**Version:** 7.1.1  
**Platforms:** Android, iOS, macOS, Web, Windows, Linux

```yaml
dependencies:
  connectivity_plus: ^7.1.1
```

## Check current connectivity

```dart
import 'package:connectivity_plus/connectivity_plus.dart';

final connectivity = Connectivity();

// Returns a list — device can have multiple active connections (WiFi + mobile)
final List<ConnectivityResult> results = await connectivity.checkConnectivity();

if (results.contains(ConnectivityResult.wifi)) {
  print('Connected via WiFi');
} else if (results.contains(ConnectivityResult.mobile)) {
  print('Connected via mobile data');
} else if (results.contains(ConnectivityResult.none)) {
  print('No connection');
}
```

## Stream: listen for changes

```dart
import 'dart:async';
import 'package:flutter/services.dart';

late StreamSubscription<List<ConnectivityResult>> _subscription;

@override
void initState() {
  super.initState();
  _subscription = Connectivity().onConnectivityChanged.listen(_onConnectivityChanged);
}

void _onConnectivityChanged(List<ConnectivityResult> results) {
  final isOnline = !results.contains(ConnectivityResult.none);
  setState(() => _isOnline = isOnline);
}

@override
void dispose() {
  _subscription.cancel();
  super.dispose();
}
```

## ConnectivityResult values

| Value | Meaning |
|---|---|
| `wifi` | Connected via WiFi |
| `mobile` | Connected via cellular |
| `ethernet` | Connected via ethernet |
| `bluetooth` | Connected via Bluetooth tethering |
| `vpn` | Connected via VPN |
| `other` | Connected via unknown type |
| `none` | No network connection |

## Riverpod integration

```dart
// providers/connectivity_provider.dart
@riverpod
Stream<List<ConnectivityResult>> connectivityStream(Ref ref) {
  return Connectivity().onConnectivityChanged;
}

@riverpod
Future<bool> isOnline(Ref ref) async {
  final results = await Connectivity().checkConnectivity();
  return !results.contains(ConnectivityResult.none);
}

// In widget — shows banner when offline
Consumer(
  builder: (context, ref, _) {
    final connectivity = ref.watch(connectivityStreamProvider);
    return connectivity.whenData(
      (results) => results.contains(ConnectivityResult.none)
          ? const MaterialBanner(content: Text('No internet connection'))
          : const SizedBox.shrink(),
    ).value ?? const SizedBox.shrink();
  },
)
```

## Offline-aware API calls

```dart
class NetworkAwareRepository {
  Future<T> call<T>(Future<T> Function() request) async {
    final results = await Connectivity().checkConnectivity();
    if (results.contains(ConnectivityResult.none)) {
      throw const SocketException('No network connection');
    }
    return request();
  }
}

// Usage
await networkRepo.call(() => supabase.from('posts').select());
```

## Important: connectivity ≠ internet access

`connectivity_plus` tells you the **network type** — not whether the internet is actually reachable. A device can be connected to WiFi but have no internet (captive portal, disconnected router).

To verify actual internet access, make a lightweight HTTP request:

```dart
Future<bool> hasInternetAccess() async {
  try {
    final result = await InternetAddress.lookup('google.com')
        .timeout(const Duration(seconds: 5));
    return result.isNotEmpty && result.first.rawAddress.isNotEmpty;
  } catch (_) {
    return false;
  }
}
```

Use connectivity status for **UI feedback** (show "you appear to be offline"), and handle actual `SocketException` from dio/http for true network errors.

## Gotchas

- Returns `List<ConnectivityResult>` (not a single value) — a device can have WiFi and mobile active simultaneously.
- The stream does NOT emit on initial subscription — call `checkConnectivity()` separately to get the current state, then listen for changes.
- On Android, platform messages are asynchronous. Check `if (mounted)` before calling `setState()` inside the listener.
- macOS requires the `com.apple.security.network.client` entitlement in the macOS sandbox config.
