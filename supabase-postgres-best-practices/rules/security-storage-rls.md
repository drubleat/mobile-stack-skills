---
title: Storage bucket RLS — secure file access with the same model as tables
impact: HIGH
impactDescription: "Storage buckets without RLS policies are publicly readable/writable by anyone with the publishable key; every bucket needs explicit policies"
tags: storage, rls, security, supabase, files, buckets
---

# Storage bucket RLS: secure file access

## How Storage RLS works

Storage uses the same RLS engine as the database. Policies are on the `storage.objects` table. The `name` column is the full path within the bucket.

## Create a private bucket with user-scoped access

```sql
-- 1. Create the bucket (or do it in the Dashboard)
insert into storage.buckets (id, name, public)
values ('user-uploads', 'user-uploads', false);  -- false = private (no public URL)

-- 2. Users can upload to their own folder
create policy "user upload own folder" on storage.objects
  for insert
  to authenticated
  with check (
    bucket_id = 'user-uploads'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

-- 3. Users can read their own files
create policy "user read own files" on storage.objects
  for select
  to authenticated
  using (
    bucket_id = 'user-uploads'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

-- 4. Users can delete their own files
create policy "user delete own files" on storage.objects
  for delete
  to authenticated
  using (
    bucket_id = 'user-uploads'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
```

## Folder naming convention: enforce via policy

```
user-uploads/{user_id}/{filename}
```

The policy `(storage.foldername(name))[1] = (select auth.uid())::text` ensures users can only access their own subfolder.

## Public bucket (profile avatars)

```sql
insert into storage.buckets (id, name, public)
values ('avatars', 'avatars', true);  -- public = anyone can download

-- Only authenticated users can upload, and only to their own file
create policy "user upload avatar" on storage.objects
  for insert
  to authenticated
  with check (
    bucket_id = 'avatars'
    and name = (select auth.uid())::text || '.jpg'
  );

create policy "user update avatar" on storage.objects
  for update
  to authenticated
  using (
    bucket_id = 'avatars'
    and name = (select auth.uid())::text || '.jpg'
  );
```

## Signed URLs for private files (time-limited access)

```ts
const { data } = await supabase.storage
  .from('user-uploads')
  .createSignedUrl(`${userId}/report.pdf`, 3600); // 1 hour expiry

// data.signedUrl — share this with the client
```

## Upload from React Native / Flutter

```ts
// React Native — upload from file URI
const fileExt = uri.split('.').pop();
const filePath = `${userId}/${Date.now()}.${fileExt}`;

const response = await fetch(uri);
const blob = await response.blob();

const { error } = await supabase.storage
  .from('user-uploads')
  .upload(filePath, blob, { contentType: `image/${fileExt}` });
```

## File size and type limits (Edge Function validation)

Storage doesn't enforce file type limits natively — validate in your Edge Function or client before upload:

```ts
const MAX_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

if (file.size > MAX_SIZE) throw new Error('File too large');
if (!ALLOWED_TYPES.includes(file.type)) throw new Error('Invalid file type');
```
