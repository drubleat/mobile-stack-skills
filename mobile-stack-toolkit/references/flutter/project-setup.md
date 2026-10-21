---
title: "Flutter setup and compatible dependencies"
impact: HIGH
impactDescription: "Avoid incompatible APIs and unsafe mobile integration defaults"
tags: mobile, integration, correctness
---

# Flutter setup and compatible dependencies

Inspect `flutter --version`, `pubspec.yaml`, `pubspec.lock`, and platform deployment targets. Preserve the existing state management and folder layout. For a new app:

```bash
flutter create my_app --org com.yourcompany --platforms ios,android
cd my_app
flutter pub add flutter_riverpod go_router
flutter pub get
flutter analyze
flutter test
```

Add only integrations the app needs. Use the resolver rather than pasting a mixed-major bundle. If using code generation, install mutually compatible `riverpod_annotation`/`riverpod_generator`, or `freezed_annotation`/`freezed` plus `build_runner`; inspect their constraints and commit the application lockfile. Riverpod code generation is optional.

## Manual Riverpod provider

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

final authStateProvider = StreamProvider<AuthState>((ref) =>
  Supabase.instance.client.auth.onAuthStateChange);
```

Wrap the app with `ProviderScope`. Handle loading, signed-out, signed-in, and stream-error states separately. Providers of per-user data must watch identity changes and clear stale data on sign-out.

For Freezed 3 use `abstract class` or `sealed class` as appropriate for generated members. Run generation before analysis; do not pair Freezed 3 with a 2.x annotation pin.

## Initialization and environments

Call `WidgetsFlutterBinding.ensureInitialized`, initialize only the services used, set error handlers, then `runApp`. Firebase initialization precedes FlutterFire calls; Supabase initialization precedes its client use. Configure RevenueCat once and synchronize identity on sign-in/account switching.

`--dart-define` values are compiled into the app and are not secret storage. Use them for public endpoints and client keys. Native flavors configure separate bundle IDs, signing, icons, and service config; `--dart-define` alone does not create native flavors. Flavors are useful when needed, not a store submission requirement.

Start with `lib/features`, shared clients, and routing only if that structure fits the app. Avoid forcing unused layers. See [navigation](navigation.md), [storage](local-storage.md), and [CI](cicd.md).

## Sources

Reviewed 2026-10-20: [Flutter packages](https://docs.flutter.dev/packages-and-plugins/using-packages), [Riverpod code generation](https://riverpod.dev/docs/concepts/about_code_generation), [Freezed](https://pub.dev/packages/freezed).
