---
title: "Flutter preferences and credential storage"
impact: HIGH
impactDescription: "Avoid incompatible APIs and unsafe mobile integration defaults"
tags: mobile, integration, correctness
---

# Flutter preferences and credential storage

Use preferences for theme, onboarding, and non-sensitive settings. Use platform-backed secure storage for user session credentials where required. Neither protects a long-lived AI/server key embedded in the application; those belong on a trusted server.

```dart
import 'package:shared_preferences/shared_preferences.dart';
final prefs = SharedPreferencesAsync();
await prefs.setString('theme', 'dark');
final theme = await prefs.getString('theme') ?? 'system';
```

Choose `SharedPreferencesAsync` or the cache-backed API based on the workload, particularly with multiple isolates/engines. Do not use preferences as a critical transactional database.

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
const storage = FlutterSecureStorage();
await storage.write(key: 'session_token', value: sessionToken);
final token = await storage.read(key: 'session_token');
await storage.delete(key: 'session_token');
```

Check installed-version Android backup/encryption and iOS Keychain accessibility requirements before choosing platform options. Old `encryptedSharedPreferences` flags and deployment targets are not universal requirements. Test device-lock behavior, restore from backup, reinstall, biometric changes, and sign-out cleanup.

Supabase Flutter v2 defaults to SharedPreferences-based persistence; do not assume it uses secure storage on iOS. To require encrypted session storage, implement the version's `LocalStorage` adapter and configure it through `FlutterAuthClientOptions(localStorage: ...)`. Preserve SDK token refresh rather than creating a second competing persistence/refresh system.

Keychain entries can survive reinstall. Define cleanup by your product/account policy; do not unconditionally delete unrelated Keychain data on first launch. Flutter uses its own native project configuration; Expo config plugins do not configure a Flutter app.

## Sources

Reviewed 2026-10-20: [shared_preferences](https://pub.dev/packages/shared_preferences), [flutter_secure_storage](https://pub.dev/packages/flutter_secure_storage), [Supabase Flutter](https://pub.dev/packages/supabase_flutter).
