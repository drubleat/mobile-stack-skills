---
title: postgrest 2.7.1 — PostgREST Dart client
impact: MEDIUM-HIGH
impactDescription: "Low-level PostgREST client used by supabase_flutter; useful for custom query builder patterns"
tags: dart, supabase, postgrest, queries
---

# postgrest — PostgREST Dart query builder

**Version:** 2.7.1  
**Platforms:** all Dart platforms

```yaml
dependencies:
  postgrest: ^2.7.1
```

`postgrest` is the low-level Dart client for the PostgREST REST API. Most Flutter developers use it indirectly through `supabase` or `supabase_flutter`. Use this package directly only if you're building a custom Supabase SDK wrapper, a CLI tool, or targeting a self-hosted PostgREST instance without Supabase.

## Direct usage (without supabase package)

```dart
import 'package:postgrest/postgrest.dart';

final client = PostgrestClient(
  'https://your-project.supabase.co/rest/v1',
  headers: {
    'apikey': 'sb_publishable_your_key',
    'Authorization': 'Bearer YOUR_JWT',
  },
  schema: 'public',
);

// Select
final data = await client.from('profiles').select();

// Filters
final row = await client
    .from('profiles')
    .select('id, email, plan')
    .eq('id', userId)
    .single();
```

## Filter methods

```dart
// Equality
.eq('column', value)
.neq('column', value)

// Comparison
.gt('count', 0)
.gte('price', 100)
.lt('age', 18)
.lte('score', 100)

// String
.like('name', 'John%')         // case-sensitive LIKE
.ilike('email', '%@gmail.com') // case-insensitive LIKE

// Set membership
.in_('status', ['active', 'pending'])

// Null checks
.is_('deleted_at', null)
.not('deleted_at', 'is', null)

// Range
.filter('price', 'gte', '100')

// Full text search
.textSearch('body', 'flutter dart')
```

## Ordering and pagination

```dart
// Order
.order('created_at', ascending: false)
.order('name', ascending: true, nullsFirst: false)

// Pagination
.limit(20)
.range(0, 19)    // rows 0-19 (first 20)
.range(20, 39)   // rows 20-39 (second page)
```

## Response count

```dart
// Get total count alongside data
final response = await client.from('posts')
    .select('*', const FetchOptions(count: CountOption.exact))
    .limit(20);

print(response.count);  // total matching rows (ignores .limit)
print(response.data);   // List<Map<String, dynamic>>
```

## Joins (foreign key relationships)

```dart
// One-to-many: posts with their author profile
final posts = await client.from('posts')
    .select('*, profiles!author_id(display_name, avatar_url)');

// Many-to-many (via junction table)
final data = await client.from('users')
    .select('*, users_roles(roles(name))');
```

## Error handling

```dart
try {
  final data = await client.from('profiles').select().single();
} on PostgrestException catch (e) {
  print(e.code);     // PostgreSQL error code (e.g. 'PGRST116', '23505')
  print(e.message);  // Human-readable message
  print(e.details);  // Technical details
  print(e.hint);     // Suggested fix
}
```

Common codes:
| Code | Meaning |
|---|---|
| `PGRST116` | `single()` returned 0 or 2+ rows |
| `23505` | Unique constraint violation |
| `42501` | RLS policy denied access |
| `PGRST204` | No content (success, no body) |

## Schema selection

```dart
// Switch to a different Postgres schema
final client = PostgrestClient(
  url,
  headers: {'apikey': key},
  schema: 'private',  // default is 'public'
);

// Or per-query
await client.schema('audit').from('logs').select();
```

## Gotchas

- `single()` throws `PostgrestException` (PGRST116) if 0 or more than 1 row matches. Use `maybeSingle()` when the row might not exist — returns null instead of throwing.
- PostgREST returns JSON arrays even for single-row queries when using `select()` without `single()`/`maybeSingle()`. The response is always `List<Map<String, dynamic>>`.
- JWT tokens must be set in the `Authorization` header for authenticated (non-public) requests. The `supabase` package handles this automatically.
- RLS errors return `42501` code but the `message` may be a generic "new row violates row-level security policy" — not very descriptive for debugging. Enable `pgrst.db-anon-role` logs in Supabase dashboard for more detail.
