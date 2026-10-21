---
title: "Image selection, normalized uploads and private display"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Image selection, normalized uploads and private display

Use the system picker without demanding broad library access when the platform/API does not require it. Camera capture requires camera permission. Handle cancellation, missing assets and limited access. Request only permissions needed by the feature.

Normalize image bytes before assigning a file extension/MIME type; HEIC/PNG bytes do not become JPEG by renaming them. Preserve orientation/aspect ratio and choose resolution appropriate to the task. Enforce byte/type limits on the server/bucket as well as the client.

```ts
import * as ImagePicker from 'expo-image-picker';
import * as ImageManipulator from 'expo-image-manipulator';
import { decode } from 'base64-arraybuffer';
const picked = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'] });
if (picked.canceled || !picked.assets?.[0]) return;
// manipulateAsync is a compatibility API; use the contextual API when migrating SDKs.
const image = await ImageManipulator.manipulateAsync(picked.assets[0].uri, [], {
  format: ImageManipulator.SaveFormat.JPEG, compress: 0.8, base64: true,
});
if (!image.base64) throw new Error('Image conversion failed');
const bytes = decode(image.base64);
if (bytes.byteLength > 5 * 1024 * 1024) throw new Error('Image too large');
const path = `${userId}/${uniqueUploadId}.jpg`; // authenticated user; fresh random ID
const { error } = await supabase.storage.from('avatars').upload(path, bytes, {
  contentType: 'image/jpeg', upsert: false,
});
if (error) throw error;
```

This is an integration fragment: supply the authenticated client and a random upload ID. Supabase's documented RN upload path uses ArrayBuffer, avoiding unreliable Blob/FormData behavior. Insert-only uploads do not require overwrite policies; `upsert: true` additionally requires the relevant select/update permissions.

Create the bucket with size/MIME limits and owner-folder RLS; see [Storage](../supabase/storage.md). For private images, save an object path in a schema column such as `avatar_path`, then generate a signed URL on read. Add that column through a migration before writing it. Check profile-update and URL-generation errors; clean orphan uploads if persistence fails. Do not persist expiring signed URLs as permanent profile data.

Render with `expo-image` or the project's existing image component. Consider disk-cache privacy on logout/account switch and refresh expired signed URLs. A public bucket is appropriate only for deliberately public content. Disable duplicate uploads and restore UI state after all failures.

## Sources

Reviewed 2026-10-20: [Expo picker](https://docs.expo.dev/versions/latest/sdk/imagepicker/), [image manipulation](https://docs.expo.dev/versions/latest/sdk/imagemanipulator/), [Supabase upload](https://supabase.com/docs/guides/storage/uploads/standard-uploads).
