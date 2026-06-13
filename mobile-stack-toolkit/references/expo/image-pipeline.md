---
title: Image pipeline — pick, compress, upload to Supabase Storage
impact: HIGH
impactDescription: "Avatar/photo upload is in ~90% of real apps; the RN upload pattern is non-obvious (blob doesn't work — needs ArrayBuffer) and gets it 0-byte files if done wrong"
tags: image, expo-image, image-picker, supabase-storage, upload, expo, react-native
---

# Image Pipeline — Pick → Upload → Display

The full client-side image flow: pick from library/camera → upload to Supabase Storage → render with caching. The upload step has a well-known RN trap (Supabase doesn't accept a `Blob` in React Native — you must pass an `ArrayBuffer`), which silently produces **0-byte files** if done wrong.

**Packages:** `expo-image-picker`, `expo-image`, `expo-file-system`, `base64-arraybuffer`, `@supabase/supabase-js`

---

## Install

```bash
npx expo install expo-image-picker expo-image expo-file-system
npm install base64-arraybuffer
```

For Storage uploads you also need `react-native-url-polyfill` imported once at app entry (see [../supabase/_index.md](../supabase/_index.md)).

---

## Step 1 — Pick an image

```tsx
import * as ImagePicker from 'expo-image-picker';

async function pickImage() {
  // Request permission first
  const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
  if (!perm.granted) {
    Alert.alert('Permission required', 'We need access to your photos.');
    return null;
  }

  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ['images'],     // new API — array of strings (NOT MediaTypeOptions.Images)
    allowsEditing: true,
    aspect: [1, 1],             // square crop for avatars
    quality: 0.7,               // compress to 70% — smaller upload, good enough quality
  });

  if (result.canceled) return null;
  return result.assets[0];      // { uri, width, height, mimeType, fileSize, ... }
}
```

### From the camera instead

```tsx
const perm = await ImagePicker.requestCameraPermissionsAsync();
if (!perm.granted) return;

const result = await ImagePicker.launchCameraAsync({
  mediaTypes: ['images'],
  quality: 0.7,
});
```

---

## Step 2 — Upload to Supabase Storage

Supabase Storage in React Native does **not** accept a `Blob` or `File` — pass a decoded `ArrayBuffer`. Read the file as base64, then decode.

```tsx
import { File } from 'expo-file-system';   // SDK 54+ new API
import { decode } from 'base64-arraybuffer';
import { supabase } from '@/lib/supabase';

async function uploadImage(uri: string, userId: string): Promise<string> {
  // Read file as base64 (new File API)
  const file = new File(uri);
  const base64 = await file.base64();

  // Decode to ArrayBuffer — what Supabase actually accepts
  const arrayBuffer = decode(base64);

  // Build a unique path; foldering by userId works with RLS storage policies
  const ext = uri.split('.').pop()?.toLowerCase() ?? 'jpg';
  const contentType = ext === 'png' ? 'image/png' : 'image/jpeg';
  const path = `${userId}/${Date.now()}.${ext}`;

  const { data, error } = await supabase.storage
    .from('avatars')
    .upload(path, arrayBuffer, {
      contentType,        // REQUIRED — without it the file may be stored as octet-stream
      upsert: true,       // overwrite if same path
    });

  if (error) throw error;
  return data.path;
}
```

### Legacy SDK (< 54) file read

If you're on an older Expo SDK, `readAsStringAsync` lives in the legacy module:

```tsx
import * as FileSystem from 'expo-file-system/legacy';

const base64 = await FileSystem.readAsStringAsync(uri, {
  encoding: FileSystem.EncodingType.Base64,
});
const arrayBuffer = decode(base64);
```

### Alternative — fetch + arrayBuffer (no base64 lib)

```tsx
const response = await fetch(uri);
const arrayBuffer = await response.arrayBuffer();
await supabase.storage.from('avatars').upload(path, arrayBuffer, { contentType });
```

This avoids `base64-arraybuffer` but can be less reliable for large files on some RN versions — the base64 + decode path is the battle-tested one.

---

## Step 3 — Storage bucket + RLS policy

Create the bucket and lock it down so users can only write to their own folder:

```sql
-- Create a private bucket (do this in the dashboard or via SQL)
insert into storage.buckets (id, name, public)
values ('avatars', 'avatars', false);

-- Users can upload to a folder named after their own uid
create policy "Users upload own avatar"
on storage.objects for insert
to authenticated
with check (
  bucket_id = 'avatars'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);

-- Users can read their own files
create policy "Users read own avatar"
on storage.objects for select
to authenticated
using (
  bucket_id = 'avatars'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);
```

The `${userId}/...` path convention in Step 2 is what makes `(storage.foldername(name))[1] = auth.uid()` work. See [../supabase/storage.md](../supabase/storage.md) for deeper Storage RLS.

---

## Step 4 — Get a displayable URL

### Private bucket → signed URL

```tsx
async function getAvatarUrl(path: string): Promise<string> {
  const { data, error } = await supabase.storage
    .from('avatars')
    .createSignedUrl(path, 60 * 60); // valid 1 hour
  if (error) throw error;
  return data.signedUrl;
}
```

### Public bucket → public URL

```tsx
const { data } = supabase.storage.from('avatars').getPublicUrl(path);
const url = data.publicUrl;  // no expiry, no auth — only for non-sensitive images
```

---

## Step 5 — Render with expo-image

Use `expo-image` (not RN `Image`) for disk caching, blurhash placeholders, and smooth transitions:

```tsx
import { Image } from 'expo-image';

<Image
  source={avatarUrl}
  placeholder={{ blurhash: 'L6PZfSi_.AyE_3t7t7R**0o#DgR4' }}
  contentFit="cover"
  transition={300}
  cachePolicy="memory-disk"     // cache across launches
  style={{ width: 96, height: 96, borderRadius: 48 }}
/>
```

In a `FlashList`/`FlatList`, pass `recyclingKey` so recycled rows don't flash the previous image:

```tsx
<Image source={item.url} recyclingKey={item.id} cachePolicy="memory-disk" />
```

---

## Full end-to-end avatar uploader

```tsx
import { useState } from 'react';
import { Pressable } from 'react-native';
import { Image } from 'expo-image';
import * as ImagePicker from 'expo-image-picker';
import { File } from 'expo-file-system';
import { decode } from 'base64-arraybuffer';
import { supabase } from '@/lib/supabase';

export function AvatarUploader({ userId }: { userId: string }) {
  const [url, setUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  async function handlePress() {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) return;

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.7,
    });
    if (result.canceled) return;

    try {
      setUploading(true);
      const uri = result.assets[0].uri;
      const base64 = await new File(uri).base64();
      const path = `${userId}/${Date.now()}.jpg`;

      const { error } = await supabase.storage
        .from('avatars')
        .upload(path, decode(base64), { contentType: 'image/jpeg', upsert: true });
      if (error) throw error;

      const { data } = await supabase.storage
        .from('avatars')
        .createSignedUrl(path, 3600);
      setUrl(data?.signedUrl ?? null);

      // Persist the path on the profile row
      await supabase.from('profiles').update({ avatar_path: path }).eq('id', userId);
    } finally {
      setUploading(false);
    }
  }

  return (
    <Pressable onPress={handlePress} disabled={uploading}>
      <Image
        source={url}
        placeholder={{ blurhash: 'L6PZfSi_.AyE_3t7t7R**0o#DgR4' }}
        contentFit="cover"
        cachePolicy="memory-disk"
        style={{ width: 96, height: 96, borderRadius: 48 }}
      />
    </Pressable>
  );
}
```

---

## Gotchas

- **The 0-byte file bug:** uploading `result.assets[0]` directly, or a `Blob`/`File` object, produces a 0-byte file in RN. You MUST decode to an `ArrayBuffer`. This is the #1 Supabase Storage RN issue.
- **`mediaTypes: ['images']`** — the array-of-strings form. `ImagePicker.MediaTypeOptions.Images` is deprecated.
- **Always set `contentType`** on `upload()` — otherwise the file is stored as `application/octet-stream` and won't render in `<img>`/`expo-image`.
- **`expo-file-system` API changed in SDK 54** — use `new File(uri).base64()`. On older SDKs, `readAsStringAsync` from `expo-file-system/legacy`.
- **Store the path, not the signed URL, in your DB.** Signed URLs expire. Save `avatar_path` and generate a fresh signed URL on read.
- **Compress with `quality: 0.7`** at pick time. A raw phone photo is 3–6 MB; uploading full-res burns user bandwidth and your storage. For heavier resizing, add `expo-image-manipulator`.
- **Foldername convention drives RLS** — the `${userId}/file` path is what lets the storage policy check `foldername(name)[1] = auth.uid()`. Break the convention and uploads get rejected (or worse, allowed for everyone).
