---
title: "Flutter image selection and uploads"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Flutter image selection and uploads

Use `image_picker` with platform setup appropriate to the installed package. Add only the camera/photo/microphone usage descriptions needed by the feature. Modern system photo pickers can avoid broad storage permission; do not block selection with an unconditional Permission.storage/Permission.photos precheck.

Handle null/cancelled results, Android activity recreation via lost-data recovery and temporary-file lifetime. Use XFile.readAsBytes for platform-friendly access. Check size and actual type before upload; renaming HEIC/PNG to `.jpg` does not convert it. If normalizing to JPEG, check the compressor's nullable result and use a matching MIME type.

Upload under the authenticated user's path with correct owner RLS. Use a unique object name and insert-only permissions unless overwrite is intentional. For private media return short-lived URLs or authenticated reads; a getPublicUrl call does not turn a private bucket public. Persist object paths, handle metadata-write failures and clean orphan files.

Use cached_network_image or the project's existing image component for display. Cache behavior differs on web; do not promise native disk caching everywhere. Plan private-media cache cleanup on account switch, error/loading placeholders and bounded decode dimensions for large images.

See [Supabase Storage](../supabase/storage.md) for permissions and [Expo image pipeline](../expo/image-pipeline.md) for the equivalent normalized-byte contract.

## Sources

Reviewed 2026-10-20: [image_picker](https://pub.dev/packages/image_picker), [cached_network_image](https://pub.dev/packages/cached_network_image).
