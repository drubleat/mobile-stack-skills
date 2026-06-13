---
title: Local storage: shared_preferences + flutter_secure_storage
impact: HIGH
impactDescription: "Tokens go in flutter_secure_storage (Keychain/Keystore); preferences go in shared_preferences — mixing them creates security holes"
tags: flutter, storage, shared-preferences, secure-storage, keychain
---

# Local storage: shared_preferences + flutter_secure_storage

Two complementary packages for on-device persistence:
- `shared_preferences` — non-sensitive user preferences, settings, simple state.
- `flutter_secure_storage` — sensitive data: tokens, keys, PINs.

## shared_preferences

Backed by `NSUserDefaults` (iOS) and `SharedPreferences` (Android). Synchronous reads after the initial async load.

```yaml
dependencies:
  shared_preferences: ^2.3.5
```

### Basic usage

```dart
import 'package:shared_preferences/shared_preferences.dart';

// Read (use SharedPreferencesAsync for async reads, or get the instance)
final prefs = await SharedPreferences.getInstance();

// Write
await prefs.setString('theme', 'dark');
await prefs.setBool('onboarding_complete', true);
await prefs.setInt('notification_badge', 3);
await prefs.setStringList('recent_searches', ['flutter', 'dart']);

// Read (synchronous after getInstance)
final theme = prefs.getString('theme') ?? 'system';
final onboardingDone = prefs.getBool('onboarding_complete') ?? false;

// Delete
await prefs.remove('theme');
await prefs.clear();  // clear all
```

### Riverpod integration

```dart
// providers/preferences_provider.dart
@riverpod
Future<SharedPreferences> sharedPreferences(Ref ref) =>
    SharedPreferences.getInstance();

@riverpod
class ThemeMode extends _$ThemeMode {
  @override
  Future<String> build() async {
    final prefs = await ref.watch(sharedPreferencesProvider.future);
    return prefs.getString('theme') ?? 'system';
  }

  Future<void> setTheme(String theme) async {
    final prefs = await ref.read(sharedPreferencesProvider.future);
    await prefs.setString('theme', theme);
    state = AsyncData(theme);
  }
}
```

### What NOT to store here

- Auth tokens — use `flutter_secure_storage`.
- Large data (> 1MB) — use `sqflite` or `isar`.
- Binary data — use the file system.

---

## flutter_secure_storage

Backed by iOS Keychain and Android Keystore. Values are encrypted at rest. Use for anything you'd put in a password manager.

```yaml
dependencies:
  flutter_secure_storage: ^9.2.4
```

### iOS setup

Add `Keychain Sharing` capability in Xcode if you get Keychain errors on real devices. In `app.config.ts` / EAS, this is set via the `@expo/config-plugins` keychain plugin (for Expo) or directly in Xcode entitlements for pure Flutter.

### Basic usage

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const storage = FlutterSecureStorage(
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
);

// Write
await storage.write(key: 'api_key', value: 'sk-...');

// Read
final apiKey = await storage.read(key: 'api_key');

// Delete
await storage.delete(key: 'api_key');

// Check existence
final exists = await storage.containsKey(key: 'api_key');

// Read all
final all = await storage.readAll();
```

`encryptedSharedPreferences: true` uses Android's EncryptedSharedPreferences — required for Android API 23+.

### Singleton pattern

```dart
// lib/core/storage/secure_storage.dart
class SecureStorage {
  SecureStorage._();
  static const SecureStorage instance = SecureStorage._();

  static const _storage = FlutterSecureStorage(
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  Future<void> saveToken(String token) =>
      _storage.write(key: 'auth_token', value: token);

  Future<String?> getToken() =>
      _storage.read(key: 'auth_token');

  Future<void> clearAll() =>
      _storage.deleteAll();
}
```

### When to use secure storage vs shared_preferences

| Data | Use |
|---|---|
| Auth tokens (Supabase session) | `flutter_secure_storage` — `supabase_flutter` handles this automatically |
| User preferences (theme, language) | `shared_preferences` |
| API keys (AI keys on client — AVOID) | Neither — keep keys on server |
| Biometric auth PIN | `flutter_secure_storage` |
| Onboarding state | `shared_preferences` |
| Cached AI responses | File system or `sqflite` |

Note: `supabase_flutter` uses `flutter_secure_storage` internally to persist the auth session on iOS and `SharedPreferences` on Android. You don't need to manually persist Supabase tokens.

## Gotchas

- `flutter_secure_storage` on iOS stores data in Keychain, which **persists across app reinstalls** by default. Call `deleteAll()` on first launch after fresh install if you want a clean state.
- On Android, `encryptedSharedPreferences: true` requires API level 23+. If you support lower API levels, add a fallback.
- `shared_preferences` is NOT suitable for sensitive data — values are stored in plain XML (Android) or plist (iOS).
