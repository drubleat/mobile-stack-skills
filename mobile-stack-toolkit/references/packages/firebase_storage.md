---
title: firebase_storage 13.4.2 — Firebase Storage client
impact: MEDIUM
impactDescription: "Upload task monitoring, download URLs, and security rules integration"
tags: flutter, firebase, storage, uploads
---

# firebase_storage — Firebase file storage

**Version:** 13.4.2  
**Platforms:** Android, iOS, macOS, Web, Windows

```yaml
dependencies:
  firebase_core: ^4.10.0
  firebase_storage: ^13.4.2
```

> For architectural patterns and when to use Firebase Storage vs Supabase Storage, see [../firebase/storage.md](../firebase/storage.md).

## Get a reference

```dart
import 'package:firebase_storage/firebase_storage.dart';

final storage = FirebaseStorage.instance;

// Path-based reference
final ref = storage.ref('avatars/$userId/profile.jpg');

// Or chained
final ref = storage.ref().child('avatars').child(userId).child('profile.jpg');
```

## Upload

### Upload local file

```dart
import 'dart:io';

final file = File(localPath);
final ref = storage.ref('uploads/$userId/${file.path.split('/').last}');

final UploadTask task = ref.putFile(
  file,
  SettableMetadata(contentType: 'image/jpeg'),
);

// Wait for completion
final snapshot = await task;
final downloadUrl = await snapshot.ref.getDownloadURL();
```

### Upload bytes (from image_picker or camera)

```dart
import 'dart:typed_data';

final Uint8List bytes = await imageFile.readAsBytes();
final ref = storage.ref('images/$userId/${DateTime.now().millisecondsSinceEpoch}.jpg');

final task = ref.putData(
  bytes,
  SettableMetadata(contentType: 'image/jpeg'),
);
await task;
final url = await ref.getDownloadURL();
```

### Upload string

```dart
await ref.putString(
  'Hello, world!',
  metadata: SettableMetadata(contentLanguage: 'en', contentType: 'text/plain'),
);

// Base64 string
await ref.putString(base64EncodedData, format: PutStringFormat.base64);
```

## Track upload progress

```dart
final task = ref.putFile(file);

task.snapshotEvents.listen((TaskSnapshot snapshot) {
  final progress = snapshot.bytesTransferred / snapshot.totalBytes;
  setState(() => _uploadProgress = progress);

  switch (snapshot.state) {
    case TaskState.running: break;
    case TaskState.success: print('Upload complete'); break;
    case TaskState.canceled: print('Cancelled'); break;
    case TaskState.error: print('Error'); break;
    case TaskState.paused: break;
  }
});

await task;
```

## Pause / resume / cancel

```dart
final task = ref.putFile(file);

task.pause();
task.resume();
task.cancel();
```

## Download URL

```dart
// Permanent URL (public bucket)
final url = await ref.getDownloadURL();

// Use in CachedNetworkImage or Image.network
CachedNetworkImage(imageUrl: url)
```

## Download to bytes

```dart
// Max 10MB
final Uint8List? bytes = await ref.getData(10 * 1024 * 1024);
```

## Metadata

```dart
// Get metadata
final metadata = await ref.getMetadata();
print(metadata.contentType);
print(metadata.size);
print(metadata.timeCreated);

// Update metadata
await ref.updateMetadata(SettableMetadata(
  contentType: 'image/jpeg',
  customMetadata: {'uploadedBy': userId},
));
```

## List files

```dart
final ListResult result = await storage.ref('avatars/$userId').list(
  const ListOptions(maxResults: 20),
);

for (final item in result.items) {
  final url = await item.getDownloadURL();
  print(url);
}

// Paginate with nextPageToken
if (result.nextPageToken != null) {
  final nextPage = await storage.ref('avatars/$userId').list(
    ListOptions(maxResults: 20, pageToken: result.nextPageToken),
  );
}
```

## Delete

```dart
await storage.ref('avatars/$userId/profile.jpg').delete();
```

## Development: use emulator

```dart
// Before runApp
await FirebaseStorage.instance.useStorageEmulator('localhost', 9199);
```

## Firebase Storage Security Rules

```firestore
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /avatars/{userId}/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId
                   && request.resource.size < 5 * 1024 * 1024;  // 5MB limit
    }
  }
}
```

## Gotchas

- Upload tasks survive widget rebuilds — a cancelled widget doesn't cancel the upload. Store the `UploadTask` reference outside the widget if you need to cancel on dispose.
- `getDownloadURL()` returns a long-lived token URL. If Storage security rules change, previously generated URLs may be invalidated.
- Download URLs are **not signed URLs** — they're permanent, publicly-accessible tokens tied to the file. To restrict access, use Firebase Storage Security Rules to make the bucket private, then use `ref.getData()` (authenticated) or short-lived signed URLs.
- Web platform: CORS must be configured on the Firebase Storage bucket for browser uploads.
