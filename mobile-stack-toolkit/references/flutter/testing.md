---
title: Testing: unit, widget, integration
impact: MEDIUM-HIGH
impactDescription: "Widget tests catch layout regressions cheaply; integration tests on device validate real API calls and navigation flows"
tags: flutter, testing, unit-tests, widget-tests, integration
---

# Testing: unit, widget, integration

Flutter has a three-tier testing model: unit tests (fast, no UI), widget tests (single widget), and integration tests (full app on device/emulator).

## Unit tests

Test pure Dart logic — repositories, providers, utilities — with no Flutter dependencies.

```dart
// test/features/auth/auth_repository_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockSupabaseClient extends Mock implements SupabaseClient {}

void main() {
  group('AuthRepository', () {
    late MockSupabaseClient mockClient;
    late AuthRepository repo;

    setUp(() {
      mockClient = MockSupabaseClient();
      repo = AuthRepository(mockClient);
    });

    test('signIn returns user on success', () async {
      when(() => mockClient.auth.signInWithOtp(email: any(named: 'email')))
          .thenAnswer((_) async {});

      expect(() => repo.requestOtp('test@example.com'), returnsNormally);
    });
  });
}
```

```yaml
dev_dependencies:
  mocktail: ^1.0.4
```

Use `mocktail` (not `mockito`) — it works without code generation.

## Widget tests

Test individual widgets or screens in isolation. Faster than integration tests; no real device needed.

```dart
// test/features/home/home_screen_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('HomeScreen shows user name', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          profileProvider.overrideWith((ref) => Future.value({
            'display_name': 'Test User',
          })),
        ],
        child: const MaterialApp(home: HomeScreen()),
      ),
    );

    await tester.pumpAndSettle();  // Wait for async operations

    expect(find.text('Test User'), findsOneWidget);
  });

  testWidgets('Paywall button opens purchase flow', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: PaywallScreen())),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Subscribe'));
    await tester.pumpAndSettle();

    expect(find.byType(PurchaseDialog), findsOneWidget);
  });
}
```

### Riverpod overrides in tests

```dart
ProviderScope(
  overrides: [
    // Override any provider for testing
    hasProProvider.overrideWith((ref) => Future.value(true)),
    authStateProvider.overrideWith((ref) => Stream.value(
      AuthState(event: AuthChangeEvent.signedIn, session: fakeSession),
    )),
  ],
  child: const MaterialApp(home: YourScreen()),
)
```

### Golden tests (screenshot comparison)

```dart
testWidgets('PaywallScreen golden', (tester) async {
  await tester.pumpWidget(...)
  await expectLater(
    find.byType(PaywallScreen),
    matchesGoldenFile('goldens/paywall_screen.png'),
  );
});
```

Run `flutter test --update-goldens` to regenerate golden files.

## Integration tests

Test full app flows on a real device or emulator. Slowest but highest confidence.

```yaml
dev_dependencies:
  integration_test:
    sdk: flutter
```

```dart
// integration_test/auth_flow_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Full sign-in flow', (tester) async {
    app.main();
    await tester.pumpAndSettle(const Duration(seconds: 3));

    // Enter email
    await tester.enterText(find.byKey(const Key('email_field')), 'test@example.com');
    await tester.tap(find.byKey(const Key('send_otp_button')));
    await tester.pumpAndSettle();

    expect(find.text('Check your email'), findsOneWidget);
  });
}
```

Run on device:
```bash
flutter test integration_test/auth_flow_test.dart -d <device_id>
```

## Test organization

```
test/
  features/
    auth/
      auth_repository_test.dart
      auth_screen_test.dart
    paywall/
      entitlement_provider_test.dart
      paywall_screen_test.dart
  shared/
    widgets/
      async_value_widget_test.dart
  goldens/
    paywall_screen.png
integration_test/
  auth_flow_test.dart
  purchase_flow_test.dart
```

## Running tests in CI

```yaml
# .github/workflows (or codemagic.yaml)
- run: flutter test --coverage
- run: flutter test integration_test/ -d emulator-5554
```

Generate coverage report:
```bash
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```

## Gotchas

- Widget tests run on a simulated environment — they don't test real device behavior (native plugins, actual animations). Integration tests cover those.
- `await tester.pumpAndSettle()` waits for all animations and futures to complete. If there's an infinite animation (like a loading spinner), it times out. Use `await tester.pump(const Duration(seconds: 2))` instead.
- Riverpod's `ProviderScope` must wrap the widget in tests — same as in the real app.
- `mocktail` uses `registerFallbackValue()` for custom types. Register them in `setUpAll`:

```dart
setUpAll(() {
  registerFallbackValue(FakeUserProfile());
});
```
