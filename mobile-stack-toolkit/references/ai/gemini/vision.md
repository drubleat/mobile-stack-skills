---
title: Gemini vision — multimodal image input
impact: MEDIUM-HIGH
impactDescription: "Native multimodal: text, images, video, documents in one request; no separate vision endpoint unlike OpenAI"
tags: gemini, vision, multimodal, images
---

# Gemini vision — multimodal image input

Gemini 3.5 Flash is natively multimodal: text, images, video, documents all go in the same `contents` array. No separate vision endpoint.

## Image input — URL

```ts
const response = await ai.models.generateContent({
  model: 'gemini-3.5-flash',
  contents: [
    {
      role: 'user',
      parts: [
        { text: 'What food is in this image? Estimate the calories.' },
        {
          inlineData: undefined,   // use fileData for URL
          fileData: {
            mimeType: 'image/jpeg',
            fileUri: 'https://cdn.example.com/meal.jpg',
          },
        },
      ],
    },
  ],
});
console.log(response.text);
```

## Image input — base64 (local / picked from device)

```ts
const response = await ai.models.generateContent({
  model: 'gemini-3.5-flash',
  contents: [
    {
      role: 'user',
      parts: [
        { text: 'Describe this image.' },
        {
          inlineData: {
            mimeType: 'image/jpeg',
            data: base64String,   // pure base64, no data:... prefix
          },
        },
      ],
    },
  ],
});
```

**`inlineData.data` is raw base64 — no `data:image/jpeg;base64,` prefix** (opposite of OpenAI). Strip the prefix if you have it: `base64String.replace(/^data:[^;]+;base64,/, '')`.

## From React Native → Edge Function → Gemini

```ts
// Mobile: pick image, send base64 to Edge Function
const result = await ImagePicker.launchImageLibraryAsync({ base64: true, quality: 0.7 });
const { base64, mimeType } = result.assets![0];

await fetch(`${SUPABASE_URL}/functions/v1/vision-proxy`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ base64, mimeType, prompt: 'What is this meal?' }),
});

// Edge Function:
const { base64, mimeType, prompt } = await req.json();
const response = await ai.models.generateContent({
  model: 'gemini-3.5-flash',
  contents: [{
    role: 'user',
    parts: [
      { text: prompt },
      { inlineData: { mimeType, data: base64 } },
    ],
  }],
});
```

## Multi-image input

Multiple images in one turn — Gemini handles this natively:

```ts
parts: [
  { text: 'Compare these two receipts and tell me which total is higher.' },
  { inlineData: { mimeType: 'image/jpeg', data: image1Base64 } },
  { inlineData: { mimeType: 'image/jpeg', data: image2Base64 } },
]
```

## Video input

```ts
parts: [
  { text: 'Summarize what happens in this video.' },
  { fileData: { mimeType: 'video/mp4', fileUri: 'gs://your-bucket/video.mp4' } },
]
```

For video you typically upload to Google Cloud Storage first (or use the Files API) and pass the URI. Inline video as base64 is too large.

## Supported formats

Images: JPEG, PNG, WEBP, HEIC, HEIF. Video: MP4, MOV, AVI, MKV, and others. Documents: PDF (up to ~1000 pages).

## Compress before sending

Sending a 12MP photo as base64 via your Edge Function wastes bandwidth and adds latency with no quality benefit for most vision tasks. Use `expo-image-manipulator` to resize to ~1024px on the long side before upload:

```ts
const compressed = await ImageManipulator.manipulateAsync(
  originalUri,
  [{ resize: { width: 1024 } }],
  { compress: 0.8, format: ImageManipulator.SaveFormat.JPEG, base64: true },
);
// compressed.base64 is ready to send
```

## Common mistakes

- **Sending the `data:image/jpeg;base64,...` prefix** as `inlineData.data` → strip the prefix; Gemini expects raw base64.
- **Using `fileData` for a local file** → `fileData.fileUri` must be a public URL or `gs://` URI. For local/picked images, use `inlineData`.
- **No image resize** → 5MB base64 payload; slow and expensive.
- **Thinking the model "remembers" images between turns** → images must be resent per turn if used in multi-turn context (or stored in the Files API for reuse).
