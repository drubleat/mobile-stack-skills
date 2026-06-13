---
title: storage_client 2.5.6 — Supabase Storage Dart client
impact: MEDIUM
impactDescription: "Low-level Supabase Storage client; upload, download, signed URLs, bucket management"
tags: dart, supabase, storage, uploads
---

# storage_client — Supabase Storage Dart client

**Version:** 2.5.6  
**Platforms:** all Dart platforms

```yaml
dependencies:
  storage_client: ^2.5.6
```

`storage_client` is the low-level Dart client for Supabase Storage. Most developers use it through `supabase` or `supabase_flutter` — use this package directly only for CLI scripts, custom SDK wrappers, or non-Flutter Dart environments.

## Direct client (standalone)

```dart
import 'package:storage_client/storage_client.dart';

final client = SupabaseStorageClient(
  'https://your-project.supabase.co/storage/v1',
  {
    'Authorization': 'Bearer $accessToken',
    'apikey': 'sb_publishable_your_key',
  },
);
```

## Upload

### Upload binary data

```dart
import 'dart:typed_data';

final data = Uint8List.fromList('Hello, world!'.codeUnits);

await client.from('my-bucket').uploadBinary(
  'path/to/file.txt',
  data,
  fileOptions: const FileOptions(
    upsert: true,                   // overwrite if exists
    contentType: 'text/plain',
  ),
);
```

### Upload file (io)

```dart
import 'dart:io';

final file = File('/path/to/image.jpg');
await client.from('avatars').upload(
  '$userId/avatar.jpg',
  file,
  fileOptions: const FileOptions(
    upsert: true,
    contentType: 'image/jpeg',
  ),
);
```

## Download

```dart
// Returns Uint8List
final bytes = await client.from('my-bucket').download('path/to/file.txt');
final content = String.fromCharCodes(bytes);
```

## Get URLs

```dart
// Public URL (bucket must be public)
final url = client.from('avatars').getPublicUrl('$userId/avatar.jpg');

// Signed URL (works for private buckets; expires in `expiresIn` seconds)
final signedUrl = await client.from('private').createSignedUrl(
  'documents/report.pdf',
  3600,  // 1 hour
);

// Batch signed URLs
final signedUrls = await client.from('private').createSignedUrls(
  ['file1.jpg', 'file2.jpg'],
  3600,
);
```

## List files

```dart
final List<FileObject> files = await client.from('my-bucket').list(
  path: 'prefix/',
  searchOptions: const SearchOptions(
    limit: 50,
    offset: 0,
    sortBy: SortBy(column: 'created_at', order: 'asc'),
  ),
);

for (final file in files) {
  print(file.name);
  print(file.metadata?.size);
  print(file.createdAt);
}
```

## Delete

```dart
// Delete one or more files
await client.from('avatars').remove(['$userId/avatar.jpg', '$userId/old.jpg']);
```

## Move / copy

```dart
// Move (rename)
await client.from('my-bucket').move(
  'old/path/file.jpg',
  'new/path/file.jpg',
);

// Copy
await client.from('my-bucket').copy(
  'source/file.jpg',
  'destination/file.jpg',
);
```

## Bucket management (admin)

```dart
// List all buckets
final buckets = await client.listBuckets();

// Create bucket
await client.createBucket(
  'new-bucket',
  const BucketOptions(public: true, allowedMimeTypes: ['image/jpeg', 'image/png']),
);

// Update bucket
await client.updateBucket('my-bucket', const BucketOptions(public: false));

// Empty bucket (delete all files)
await client.emptyBucket('my-bucket');

// Delete bucket (must be empty first)
await client.deleteBucket('my-bucket');
```

## FileOptions reference

```dart
const FileOptions(
  upsert: true,           // overwrite existing file (default: false → throws on conflict)
  contentType: 'image/jpeg',
  cacheControl: '3600',   // Cache-Control header in seconds
  duplex: 'half',         // for streaming uploads
)
```

## Gotchas

- Paths must NOT start with `/`. Use `'folder/file.jpg'`, not `'/folder/file.jpg'`.
- File names are case-sensitive. `Avatar.jpg` and `avatar.jpg` are different files.
- `upsert: false` (default) throws a `StorageException` with status 409 if the file already exists. Set `upsert: true` to overwrite.
- The `/storage/v1` suffix in the base URL is required when constructing `SupabaseStorageClient` directly.
- Signed URLs are generated server-side and expire — don't cache them beyond their expiry. Generate them fresh when needed.
