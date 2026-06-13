---
title: Storage: S3-style uploads with RLS
impact: MEDIUM
impactDescription: "RLS on storage buckets matches database RLS model; signed URLs prevent direct bucket exposure"
tags: supabase, storage, uploads, rls, signed-urls
---

# Storage

S3-style object storage with the same RLS model as the database. Use it for avatars, user uploads, AI input/output images, etc.

## Buckets: public vs private

- **Public bucket** → objects are reachable via a permanent public URL. Fine for non-sensitive assets (app images). Anyone with the URL can read.
- **Private bucket** → access controlled by **Storage RLS policies**; reads need a **signed URL**. Use this for anything user-owned or sensitive. **Default to private.**

Create buckets in a migration or the dashboard; set `public` accordingly and constrain file size / MIME types at the bucket level.

## Upload from React Native

RN doesn't have `File`; upload from a URI via `ArrayBuffer` (don't send a base64 string — it bloats and is slow):

```ts
import { decode } from 'base64-arraybuffer';
// pick with expo-image-picker (base64:true) OR fetch the uri -> arrayBuffer
const path = `${userId}/${Date.now()}.jpg`;
const { error } = await supabase.storage
  .from('avatars')
  .upload(path, decode(base64), { contentType: 'image/jpeg', upsert: true });
```

**Path convention = security.** Prefix every object with the owner's id (`${userId}/...`). Your Storage RLS policy then checks that the first path segment equals the caller's uid.

## Storage RLS

Storage objects live in `storage.objects`; write policies against it. Owner-folder pattern:

```sql
create policy "users manage own folder"
on storage.objects for all
using (
  bucket_id = 'avatars'
  and (select auth.uid())::text = (storage.foldername(name))[1]
)
with check (
  bucket_id = 'avatars'
  and (select auth.uid())::text = (storage.foldername(name))[1]
);
```

`storage.foldername(name)[1]` extracts the first path segment — combined with the `${userId}/` convention, users can only touch their own files. Same `(select auth.uid())` performance rule as table RLS → [rls-policies.md](rls-policies.md).

## Reading: signed URLs for private buckets

```ts
const { data } = await supabase.storage
  .from('avatars')
  .createSignedUrl(path, 60 * 60);   // valid 1 hour
// data.signedUrl -> pass to <Image source={{ uri }} />
```

For public buckets use `getPublicUrl(path)` (no expiry). Generate signed URLs **on demand**, short-lived; don't store them.

## Validation (do it on both ends)

- **Client**: cap dimensions/size before upload (resize/compress with `expo-image-manipulator`) to save bandwidth and cost.
- **Bucket**: set allowed MIME types and a max file size — this is the enforcement that actually matters, since the client can be bypassed.
- **Server (if needed)**: for anything requiring real validation/moderation (e.g. AI-generated or user images that must be screened), upload through an **Edge Function** that checks content before storing → [../ai/guardrails.md](../ai/guardrails.md).

## Resumable / large uploads

For large files (video) use resumable uploads (TUS protocol) rather than a single `upload` call, so a dropped mobile connection doesn't restart from zero.

## Pitfalls

- **base64 string straight to `upload`** → use `ArrayBuffer`; base64 is ~33% larger and slow.
- **Private bucket, image won't load** → you used `getPublicUrl` instead of `createSignedUrl`, or the Storage RLS policy denies the read.
- **No owner prefix in the path** → your folder-based RLS can't isolate users; everyone shares one namespace.
- **Signed URL expired** → generate it right before use with a sensible TTL; don't cache it in the DB.
- **Forgot bucket-level limits** → a user uploads a 2 GB file; set max size + MIME allowlist on the bucket.
