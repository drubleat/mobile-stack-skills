---
title: Flutter project setup: structure, build flavors, Riverpod
impact: HIGH
impactDescription: "flutter_riverpod 3.x requires ConsumerWidget; build flavors are required before the first store submission"
tags: flutter, setup, riverpod, project-structure, flavors
---

# Flutter project setup: structure, build flavors, Riverpod

## Create and structure the project

```bash
flutter create my_app --org com.yourcompany --platforms ios,android
cd my_app
```

Recommended folder structure:

```
lib/
  main.dart              # entry point
  app.dart               # MaterialApp / CupertinoApp + router
  core/
    theme/               # colors, typography, ThemeData
    utils/               # helpers, extensions
    constants/           # app-wide constants
  features/
    auth/
      data/              # repositories, data sources
      domain/            # entities, use cases
      presentation/      # screens, widgets, providers
    home/
    paywall/
    ai/
  shared/
    providers/           # global Riverpod providers
    widgets/             # shared UI components
    models/              # shared data models (freezed)
```

Feature-first structure scales better than layer-first (`data/`, `domain/`, `presentation/` at top level) — features stay cohesive and can be deleted cleanly.

## pubspec.yaml baseline

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^3.3.2
  riverpod_annotation: ^2.6.1
  go_router: ^17.3.0
  dio: ^5.9.2
  supabase_flutter: ^2.14.2
  purchases_flutter: ^10.2.3
  firebase_core: ^4.10.0
  firebase_messaging: ^16.3.0
  firebase_crashlytics: ^5.2.3
  firebase_analytics: ^11.4.2
  freezed_annotation: ^2.4.4
  json_annotation: ^4.9.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.13
  freezed: ^3.2.5
  riverpod_generator: ^2.6.2
  riverpod_lint: ^2.6.2
  json_serializable: ^6.9.4
  flutter_lints: ^5.0.0
```

## State management: Riverpod 3.x

Riverpod 3.x uses code generation (`@riverpod` annotation). Always use `riverpod_annotation` with `build_runner`.

```dart
// features/auth/presentation/providers/auth_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

part 'auth_provider.g.dart';

@riverpod
Stream<AuthState> authState(Ref ref) {
  return Supabase.instance.client.auth.onAuthStateChange;
}

@riverpod
class UserProfile extends _$UserProfile {
  @override
  Future<Map<String, dynamic>?> build() async {
    final user = Supabase.instance.client.auth.currentUser;
    if (user == null) return null;
    final data = await Supabase.instance.client
        .from('profiles')
        .select()
        .eq('id', user.id)
        .single();
    return data;
  }

  Future<void> refresh() async {
    ref.invalidateSelf();
    await future;
  }
}
```

Generate code: `dart run build_runner watch -d`

## Immutable models with freezed

```dart
// shared/models/user_profile.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_profile.freezed.dart';
part 'user_profile.g.dart';

@freezed
class UserProfile with _$UserProfile {
  const factory UserProfile({
    required String id,
    required String email,
    String? displayName,
    @Default('free') String plan,
  }) = _UserProfile;

  factory UserProfile.fromJson(Map<String, dynamic> json) =>
      _$UserProfileFromJson(json);
}
```

## Build flavors (dev / staging / production)

Use `--dart-define` to inject environment variables per flavor. Access them at runtime:

```dart
const supabaseUrl = String.fromEnvironment('SUPABASE_URL');
const supabaseAnonKey = String.fromEnvironment('SUPABASE_ANON_KEY');
```

```bash
# Dev
flutter run --dart-define=SUPABASE_URL=https://dev.supabase.co \
            --dart-define=SUPABASE_ANON_KEY=sb_publishable_dev_...

# Production
flutter build ipa --dart-define=SUPABASE_URL=https://prod.supabase.co \
                  --dart-define=SUPABASE_ANON_KEY=sb_publishable_prod_...
```

For more complex flavor setups (separate bundle IDs, app icons, Firebase configs per flavor), use the `flutter_flavorizr` package.

## main.dart initialization order

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Firebase first
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;
  PlatformDispatcher.instance.onError = (error, stack) {
    FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
    return true;
  };

  // Supabase
  await Supabase.initialize(
    url: const String.fromEnvironment('SUPABASE_URL'),
    anonKey: const String.fromEnvironment('SUPABASE_ANON_KEY'),
  );

  // RevenueCat
  await Purchases.setLogLevel(LogLevel.debug);
  await Purchases.configure(
    PurchasesConfiguration(Platform.isIOS ? 'appl_...' : 'goog_...'),
  );

  runApp(const ProviderScope(child: MyApp()));
}
```

`ProviderScope` must wrap the entire app for Riverpod to work. Firebase and Supabase must be initialized before `runApp`.
