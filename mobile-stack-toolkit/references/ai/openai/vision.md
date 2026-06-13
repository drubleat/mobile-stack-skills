---
title: OpenAI vision — image understanding
impact: MEDIUM-HIGH
impactDescription: "All GPT-5.x models support vision natively; correct base64 encoding prevents silent failures on mobile uploads"
tags: openai, vision, multimodal, images
---

# OpenAI vision — image understanding

All GPT-5.x models support image input natively. Pass an image alongside text to analyze, describe, extract text, or reason about visual content.

## Passing images in the Responses API

```ts
// URL
const response = await openai.responses.create({
  model: 'gpt-5.4-mini',
  input: [
    { role: 'user', content: [
      { type: 'input_text',  text: 'What meal is this? Estimate the calories.' },
      { type: 'input_image', image_url: 'https://cdn.example.com/meal.jpg', detail: 'high' },
    ]},
  ],
});

// Base64 (for locally picked images in a mobile app)
const response = await openai.responses.create({
  model: 'gpt-5.4-mini',
  input: [
    { role: 'user', content: [
      { type: 'input_text',  text: 'Describe this image.' },
      { type: 'input_image', image_url: `data:image/jpeg;base64,${base64String}` },
    ]},
  ],
});
```

In the **Chat Completions API** the content type is `image_url` (not `input_image`) and it's nested differently — check the migration guide if mixing APIs.

## The `detail` parameter

Controls how much the model "looks" at the image, which affects both accuracy and cost:

| Value | Behavior | When to use |
|---|---|---|
| `"auto"` | Model decides (default) | General use |
| `"low"` | Fast, 512×512 effective resolution | Thumbnails, simple presence detection |
| `"high"` | Full resolution + tiled analysis | Dense text, charts, receipts, fine details |
| `"original"` | Uses the source resolution directly | Spatially sensitive tasks — gpt-5.4+ only |

Most mobile app use cases (food logging, receipt scanning, plant ID) need `"high"`. `"low"` works for "is there a person in this photo?" type checks.

## From a React Native image picker (mobile)

```ts
import * as ImagePicker from 'expo-image-picker';

// Pick and convert to base64
const result = await ImagePicker.launchImageLibraryAsync({ base64: true, quality: 0.7 });
if (result.assets?.[0]?.base64) {
  const text = await callVisionProxy(result.assets[0].base64, result.assets[0].mimeType ?? 'image/jpeg');
}
```

Then in your Edge Function:
```ts
const { base64, mimeType, userPrompt } = await req.json();
const response = await openai.responses.create({
  model: 'gpt-5.4-mini',
  input: [{ role: 'user', content: [
    { type: 'input_text',  text: userPrompt },
    { type: 'input_image', image_url: `data:${mimeType};base64,${base64}` },
  ]}],
});
```

**Resize before sending.** A 12MP photo is 5-10MB. Compress to ≤1MB on the client (`expo-image-manipulator`) — you preserve enough detail for `high` mode while cutting costs and latency significantly.

## Limits

- Up to 1500 images per request; max 512 MB total.
- Supported formats: PNG, JPEG, WEBP, non-animated GIF.
- Minimum image size for `high` detail to be useful: ~512px on the short side.
- Images aren't stored by OpenAI beyond the request (unless you use the Files API).

## Multi-image analysis

```ts
input: [{ role: 'user', content: [
  { type: 'input_text',  text: 'Compare these two receipts.' },
  { type: 'input_image', image_url: `data:image/jpeg;base64,${image1}` },
  { type: 'input_image', image_url: `data:image/jpeg;base64,${image2}` },
]}],
```

## Common gotchas

- **Sending raw URI not base64** → won't work if the URI is a local `file://` path; the API needs a public URL or base64 data.
- **`detail: "low"` on a dense receipt** → model misses fields; use `"high"`.
- **Large base64 inflates request body** → compress first; also consider the Files API (`purpose: "vision"`) to upload once and reuse a File ID.
- **Vision tokens are more expensive** than text tokens — factor this into your rate limit logic.
