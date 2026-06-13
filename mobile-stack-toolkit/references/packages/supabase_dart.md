---
title: supabase 2.12.2 — Dart client (no Flutter dependency)
impact: MEDIUM-HIGH
impactDescription: "Use in non-Flutter Dart projects or server-side Dart; shares API shape with supabase_flutter"
tags: dart, supabase, backend, non-flutter
---

# supabase — Dart client (no Flutter dependency)

**Version:** 2.12.2  
**Platforms:** all Dart platforms (server, CLI, Flutter via supabase_flutter)

```yaml
dependencies:
  supabase: ^2.12.2
```

Use this package when writing **pure Dart** code (CLI tools, Dart scripts, server-side Dart, tests without Flutter). For Flutter apps, use `supabase_flutter` instead — it adds session persistence and Flutter-specific wiring on top of this package.

## Initialize

```dart
import 'package:supabase/supabase.dart';

final supabase = SupabaseClient(
  'https://your-project.supabase.co',
  'sb_publishable_your_key',
);
```

No `await` needed — the client is synchronous to create.

## Auth

```dart
// Sign in
final response = await supabase.auth.signInWithPassword(
  email: email,
  password: password,
);
final user = response.user;
final session = response.session;
final accessToken = session?.accessToken;

// Sign up
await supabase.auth.signUp(email: email, password: password);

// Sign out
await supabase.auth.signOut();

// Current user / session
supabase.auth.currentUser
supabase.auth.currentSession

// Auth as admin (server-side — requires service role key)
final adminClient = SupabaseClient(url, serviceRoleKey);
await adminClient.auth.admin.getUserById(userId);
await adminClient.auth.admin.createUser(AdminUserAttributes(email: email));
await adminClient.auth.admin.deleteUser(userId);
```

## Database

Same PostgREST API as `supabase_flutter`:

```dart
// Queries
final data = await supabase.from('users').select().eq('active', true);

// Typed usage with fromJson
final List<Map<String, dynamic>> rows = await supabase
    .from('profiles')
    .select()
    .eq('plan', 'pro');

final profiles = rows.map(UserProfile.fromJson).toList();

// RPC
final result = await supabase.rpc('my_function', params: {'arg': value});
```

## Storage

```dart
import 'dart:typed_data';

// Upload bytes
final bytes = Uint8List.fromList(fileBytes);
await supabase.storage.from('my-bucket').uploadBinary(
  'path/file.jpg',
  bytes,
  fileOptions: const FileOptions(upsert: true),
);

// Get public URL
final url = supabase.storage.from('my-bucket').getPublicUrl('path/file.jpg');

// Create signed URL (private buckets)
final signedUrl = await supabase.storage
    .from('private')
    .createSignedUrl('file.pdf', 3600);

// Download
final Uint8List fileData = await supabase.storage
    .from('my-bucket')
    .download('path/file.jpg');
```

## Edge Functions

```dart
final response = await supabase.functions.invoke(
  'my-function',
  body: {'key': 'value'},
);
```

## Realtime

```dart
final channel = supabase.channel('changes')
    .onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'messages',
      callback: (payload) => print(payload.newRecord),
    )
    .subscribe();

// Clean up
await supabase.removeChannel(channel);
```

## Use as server-side client (Dart scripts, CLI)

```dart
// scripts/seed.dart
import 'package:supabase/supabase.dart';

void main() async {
  final supabase = SupabaseClient(
    const String.fromEnvironment('SUPABASE_URL'),
    const String.fromEnvironment('SUPABASE_SERVICE_ROLE_KEY'),
  );

  await supabase.from('products').insert([
    {'name': 'Pro Plan', 'price': 999},
    {'name': 'Basic Plan', 'price': 499},
  ]);

  print('Seeded successfully');
}
```

Run: `dart run --define=SUPABASE_URL=... --define=SUPABASE_SERVICE_ROLE_KEY=... scripts/seed.dart`

## Gotchas

- `supabase` (Dart) does NOT persist auth sessions — sessions are in-memory only. Use `supabase_flutter` if you need persistent auth on Flutter.
- For server-side admin operations (creating users, bypassing RLS), initialize `SupabaseClient` with the `service_role` key (`sb_secret_...`). Never expose this key client-side.
- `SupabaseClient` does not need to be disposed for short-lived scripts. For long-running Dart servers, call `supabase.dispose()` on shutdown to close WebSocket connections.
