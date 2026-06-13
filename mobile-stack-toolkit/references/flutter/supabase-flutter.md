---
title: supabase_flutter: auth + database
impact: HIGH
impactDescription: "supabase_flutter 2.14.x initializes in main(); auth state stream drives route guards"
tags: flutter, supabase, auth, database, realtime
---

# supabase_flutter: auth + database

Version: `supabase_flutter: ^2.14.2`

## Initialization

```dart
await Supabase.initialize(
  url: const String.fromEnvironment('SUPABASE_URL'),
  anonKey: const String.fromEnvironment('SUPABASE_ANON_KEY'),
);

// Shorthand accessor used throughout the app
final supabase = Supabase.instance.client;
```

## Authentication

### Email OTP (passwordless)

```dart
// Send OTP
await supabase.auth.signInWithOtp(email: email);

// Verify OTP
await supabase.auth.verifyOTP(type: OtpType.email, token: otpCode, email: email);
```

### Google Sign-In

```dart
import 'package:google_sign_in/google_sign_in.dart';

final googleUser = await GoogleSignIn(serverClientId: 'YOUR_WEB_CLIENT_ID').signIn();
final googleAuth = await googleUser!.authentication;

await supabase.auth.signInWithIdToken(
  provider: OAuthProvider.google,
  idToken: googleAuth.idToken!,
  accessToken: googleAuth.accessToken,
);
```

### Apple Sign-In

```dart
import 'package:sign_in_with_apple/sign_in_with_apple.dart';

final credential = await SignInWithApple.getAppleIDCredential(
  scopes: [AppleIDAuthorizationScopes.email, AppleIDAuthorizationScopes.fullName],
);

await supabase.auth.signInWithIdToken(
  provider: OAuthProvider.apple,
  idToken: credential.identityToken!,
);
```

`signInWithIdToken` is the correct method for native mobile sign-in on both platforms — avoids web OAuth redirects.

### Auth state listener

```dart
// In a Riverpod provider or initState
supabase.auth.onAuthStateChange.listen((data) {
  final session = data.session;
  if (session != null) {
    // Signed in
  } else {
    // Signed out — redirect to login
  }
});
```

### Sign out

```dart
await supabase.auth.signOut();
```

## Database (PostgREST)

### Read

```dart
// Single row
final data = await supabase
    .from('profiles')
    .select()
    .eq('id', supabase.auth.currentUser!.id)
    .single();

// Multiple rows with filter
final posts = await supabase
    .from('posts')
    .select('id, title, created_at')
    .eq('author_id', userId)
    .order('created_at', ascending: false)
    .limit(20);
```

### Insert / Upsert

```dart
await supabase.from('profiles').upsert({
  'id': supabase.auth.currentUser!.id,
  'display_name': name,
  'updated_at': DateTime.now().toIso8601String(),
});
```

### Real-time subscription

```dart
final channel = supabase.channel('subscriptions_channel')
    .onPostgresChanges(
      event: PostgresChangeEvent.update,
      schema: 'public',
      table: 'subscriptions',
      filter: PostgresChangeFilter(
        type: PostgresChangeFilterType.eq,
        column: 'user_id',
        value: supabase.auth.currentUser!.id,
      ),
      callback: (payload) {
        // Refresh subscription state
        ref.invalidate(subscriptionProvider);
      },
    )
    .subscribe();

// Dispose in widget
@override
void dispose() {
  supabase.removeChannel(channel);
  super.dispose();
}
```

## Riverpod integration pattern

```dart
// shared/providers/supabase_providers.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'supabase_providers.g.dart';

@riverpod
SupabaseClient supabase(Ref ref) => Supabase.instance.client;

@riverpod
Stream<AuthState> authState(Ref ref) =>
    ref.watch(supabaseProvider).auth.onAuthStateChange;

@riverpod
Future<Map<String, dynamic>?> profile(Ref ref) async {
  final client = ref.watch(supabaseProvider);
  final user = client.auth.currentUser;
  if (user == null) return null;

  return await client.from('profiles').select().eq('id', user.id).single();
}
```

## Edge Functions

```dart
final response = await supabase.functions.invoke(
  'ai-proxy',
  body: {'prompt': userMessage},
  headers: {'Content-Type': 'application/json'},
);

if (response.status != 200) {
  throw Exception('Edge Function failed: ${response.data}');
}
final result = response.data as Map<String, dynamic>;
```

## Type generation

```bash
# Generate Dart types from Supabase schema
npx supabase gen types dart --project-id <ref> > lib/core/types/supabase_types.dart
```

Note: Dart type generation from Supabase is newer than TypeScript; the output may need manual cleanup for complex schemas.

## Gotchas

- The `supabase_flutter` package handles auth token refresh and persistence automatically (uses `SharedPreferences` internally). Don't implement your own token refresh.
- Always check `supabase.auth.currentUser` before making authenticated requests — it's `null` if not signed in.
- `signInWithIdToken` requires the Supabase project to have Google/Apple enabled in Authentication → Providers.
- Real-time channels leak if you don't call `removeChannel()` when the widget is disposed.
