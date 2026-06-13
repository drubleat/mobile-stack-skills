---
title: supabase_flutter 2.14.2 — Flutter Supabase client
impact: HIGH
impactDescription: "Official Supabase Flutter SDK; covers init, auth state, typed queries, realtime, and storage"
tags: flutter, supabase, dart, auth, database
---

# supabase_flutter — Flutter Supabase client

**Version:** 2.14.2  
**Platforms:** Android, iOS, macOS, Web, Windows, Linux

```yaml
dependencies:
  supabase_flutter: ^2.14.2
```

> For architectural patterns (Riverpod integration, realtime, storage), see [../flutter/supabase-flutter.md](../flutter/supabase-flutter.md).

## Initialize

```dart
import 'package:supabase_flutter/supabase_flutter.dart';

await Supabase.initialize(
  url: const String.fromEnvironment('SUPABASE_URL'),
  anonKey: const String.fromEnvironment('SUPABASE_PUBLISHABLE_KEY'),
);

// Shorthand used everywhere else
final supabase = Supabase.instance.client;
```

Uses `sb_publishable_` key prefix (new format replacing `anon`). See [../supabase/_index.md](../supabase/_index.md) for key naming.

## Auth

```dart
// OTP (email magic link / code)
await supabase.auth.signInWithOtp(email: email);
await supabase.auth.verifyOTP(type: OtpType.email, token: code, email: email);

// Native Google/Apple sign-in
await supabase.auth.signInWithIdToken(
  provider: OAuthProvider.google,
  idToken: googleIdToken,
  accessToken: googleAccessToken,
);

// Sign out
await supabase.auth.signOut();

// Current user
final user = supabase.auth.currentUser;
final session = supabase.auth.currentSession;

// Auth state stream
supabase.auth.onAuthStateChange.listen((data) {
  final event = data.event;
  final session = data.session;
});
```

`AuthChangeEvent` values: `signedIn`, `signedOut`, `tokenRefreshed`, `userUpdated`, `passwordRecovery`.

## Database (PostgREST)

```dart
// Select
final data = await supabase.from('profiles').select();
final single = await supabase.from('profiles').select().eq('id', userId).single();

// Select with joins
final posts = await supabase.from('posts')
    .select('*, profiles(display_name, avatar_url)')
    .order('created_at', ascending: false)
    .limit(20);

// Insert
await supabase.from('profiles').insert({'id': userId, 'email': email});

// Upsert
await supabase.from('profiles').upsert({'id': userId, 'plan': 'pro'});

// Update
await supabase.from('profiles').update({'plan': 'pro'}).eq('id', userId);

// Delete
await supabase.from('posts').delete().eq('id', postId);

// Filters
.eq('column', value)
.neq('column', value)
.gt('count', 0)
.gte('created_at', isoDate)
.in_('status', ['active', 'pending'])
.ilike('name', '%search%')   // case-insensitive LIKE
.is_('deleted_at', null)
```

## PostgREST error handling

```dart
try {
  final data = await supabase.from('posts').select().single();
} on PostgrestException catch (e) {
  print('Code: ${e.code}');      // e.g. 'PGRST116' (row not found)
  print('Message: ${e.message}');
  print('Details: ${e.details}');
}
```

## Realtime

```dart
final channel = supabase.channel('my_channel')
    .onPostgresChanges(
      event: PostgresChangeEvent.all,
      schema: 'public',
      table: 'messages',
      callback: (payload) {
        print('Change: ${payload.eventType} ${payload.newRecord}');
      },
    )
    .subscribe();

// Clean up
supabase.removeChannel(channel);
```

## Storage

```dart
// Upload
final bytes = await imageFile.readAsBytes();
await supabase.storage.from('avatars').uploadBinary(
  '$userId/avatar.jpg',
  bytes,
  fileOptions: const FileOptions(upsert: true, contentType: 'image/jpeg'),
);

// Get public URL
final url = supabase.storage.from('avatars').getPublicUrl('$userId/avatar.jpg');

// Signed URL (private buckets)
final signedUrl = await supabase.storage.from('private-files')
    .createSignedUrl('$userId/document.pdf', 3600);  // 1 hour expiry
```

## Edge Functions

```dart
final response = await supabase.functions.invoke(
  'ai-proxy',
  body: {'prompt': 'Hello'},
  headers: {'Content-Type': 'application/json'},
);
if (response.status != 200) throw Exception('Function error');
final result = response.data as Map<String, dynamic>;
```

## RPC (Postgres functions)

```dart
final result = await supabase.rpc('increment_ai_usage', params: {
  'p_user_id': userId,
  'p_limit': 5,
});
```

## Gotchas

- `supabase_flutter` handles token refresh and session persistence automatically via `SharedPreferences`. Don't implement your own token refresh.
- `onAuthStateChange` fires an initial `signedIn` event if there's a persisted session — check for null session before acting on the event type.
- Network errors in `onAuthStateChange` appear as stream errors, not emitted events. Add `.handleError()` to the listen call.
- `single()` throws `PostgrestException` (code `PGRST116`) if 0 or 2+ rows match. Use `maybeSingle()` if the row might not exist — returns null instead of throwing.
- Realtime channels must be removed on widget dispose. Leaked channels consume server connections.
