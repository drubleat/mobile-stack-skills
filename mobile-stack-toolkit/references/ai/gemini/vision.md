---
title: "Gemini image and document input"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Gemini image and document input

For small validated images, use `inlineData: { mimeType, data }` in `contents[].parts`; `data` is base64 without the data-URL prefix. For larger media, use the documented Files API and its returned URI. Do not assume any HTTPS URL or a `gs://` URI is accepted by every Gemini backend.

```ts
const response = await ai.models.generateContent({
  model: visionModel,
  contents: [{ role: 'user', parts: [
    { text: prompt },
    { inlineData: { mimeType: validatedMimeType, data: validatedBase64 } },
  ] }],
  config: { maxOutputTokens: 1024 },
});
if (!response.text) throw new Error('No vision result');
```

This is the provider call only. Authenticate and reserve quota first, check decoded byte limits and actual format, and restrict any server-side URL fetching against SSRF. Treat text in documents/images as untrusted content. Check authorization before reading private uploads; clean up temporary provider files when no longer needed.

On mobile, handle picker cancellation and missing assets. Resize according to the task: OCR and small objects can need more detail than a thumbnail. Preserve aspect ratio, normalize orientation and send a MIME type matching the bytes. See [image pipeline](../../expo/image-pipeline.md).

For video/PDF input, check the selected API's current MIME, duration, size and page limits; do not copy image assumptions. Preserve required media references across chat turns and handle expired files. A vision estimate, including food calories, is approximate rather than a measurement.

## Sources

Reviewed 2026-10-20: [image understanding](https://ai.google.dev/gemini-api/docs/image-understanding), [Files API](https://ai.google.dev/gemini-api/docs/files).
