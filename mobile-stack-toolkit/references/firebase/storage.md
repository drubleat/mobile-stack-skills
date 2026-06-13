---
title: Firebase Storage: GCS-backed file storage
impact: MEDIUM
impactDescription: "Prefer Supabase Storage in hybrid stacks; Firebase Storage is the right choice in Firebase-standalone setups"
tags: firebase, storage, uploads, gcs
---

# Firebase Storage

Firebase Storage is an alternative to Supabase Storage backed by Google Cloud Storage. Use it if you're in a Firebase-standalone setup. In a Supabase + Firebase hybrid, prefer Supabase Storage — it's simpler to secure with RLS and avoids mixing access control systems.

## When to use Firebase Storage vs Supabase Storage

| Use Firebase Storage | Use Supabase Storage |
|---|---|
| Firebase-standalone project | Supabase + Firebase hybrid |
| Already invested in Firebase ecosystem | User auth is in Supabase |
| Need CDN via Firebase Hosting integration | Need RLS-controlled private files |
| Large file storage (video, audio at scale) | Simple bucket + folder path model |

## Setup

```bash
npx expo install @react-native-firebase/storage
```

No additional plugin config needed beyond `@react-native-firebase/app`.

## Upload a file

```ts
import storage from '@react-native-firebase/storage';
import * as ImagePicker from 'expo-image-picker';

async function uploadAvatar(userId: string) {
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
    quality: 0.8,
  });
  if (result.canceled) return;

  const uri = result.assets[0].uri;
  const ref = storage().ref(`avatars/${userId}/avatar.jpg`);

  const task = ref.putFile(uri);

  task.on('state_changed', (snapshot) => {
    const progress = snapshot.bytesTransferred / snapshot.totalBytes;
    setUploadProgress(progress);
  });

  await task;

  const downloadUrl = await ref.getDownloadURL();
  return downloadUrl;
}
```

`putFile` takes a local file path (the `uri` from image picker). It handles chunking and retries internally.

## Upload from bytes / blob

```ts
const bytes = await fetch(imageUri).then((r) => r.arrayBuffer());
const ref = storage().ref(`images/${userId}/${Date.now()}.jpg`);
await ref.put(bytes, { contentType: 'image/jpeg' });
const url = await ref.getDownloadURL();
```

## Download URL

Download URLs from Firebase Storage are permanent, publicly accessible URLs (if the bucket/file is public) or signed URLs (for private files). Unlike Supabase, Firebase Storage uses Firebase Security Rules rather than RLS.

## Security rules

Rules live in `storage.rules`. Deploy with `firebase deploy --only storage`.

```firestore
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // User can only read/write their own directory
    match /avatars/{userId}/{allPaths=**} {
      allow read: if request.auth != null;                         // any authenticated user can read avatars
      allow write: if request.auth != null && request.auth.uid == userId;  // only own files
    }

    match /private/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## Delete a file

```ts
await storage().ref(`avatars/${userId}/avatar.jpg`).delete();
```

## List files in a directory

```ts
const listResult = await storage().ref(`avatars/${userId}`).list({ maxResults: 20 });
const urls = await Promise.all(
  listResult.items.map((item) => item.getDownloadURL())
);
```

## Flutter

```dart
import 'package:firebase_storage/firebase_storage.dart';

final storageRef = FirebaseStorage.instance.ref();
final avatarRef = storageRef.child('avatars/$userId/avatar.jpg');

// Upload from file
final file = File(localPath);
final task = avatarRef.putFile(file);

task.snapshotEvents.listen((snapshot) {
  final progress = snapshot.bytesTransferred / snapshot.totalBytes;
  print('Upload progress: $progress');
});

await task;
final downloadUrl = await avatarRef.getDownloadURL();

// Upload from bytes
final bytes = await imageFile.readAsBytes();
await avatarRef.putData(bytes, SettableMetadata(contentType: 'image/jpeg'));
```

## Gotchas

- **Large file uploads on mobile**: `putFile` handles chunking automatically, but the upload can fail if the device loses connectivity mid-upload. Firebase Storage resumes uploads automatically if the same task object is still in scope; completed chunks don't need to be re-uploaded.
- **Download URLs expire**: URLs returned by `getDownloadURL()` are long-lived but can be invalidated if security rules change or the file is deleted. Don't cache them forever.
- **Firebase Storage vs Supabase Storage URLs**: Firebase Storage URLs are direct Google CDN URLs. Supabase Storage URLs are proxied through Supabase's own CDN. Both work fine for images in mobile apps.
