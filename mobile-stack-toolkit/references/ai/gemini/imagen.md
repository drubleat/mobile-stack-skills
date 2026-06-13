---
title: Gemini Imagen 4 — image generation
impact: MEDIUM
impactDescription: "Imagen 4 via Gemini API; aspect ratio config and safety filter tuning differ from OpenAI image gen"
tags: gemini, imagen, image-generation, google
---

# Gemini Imagen 4 — image generation

Imagen 4 is Google's current image generation model family, available via the Gemini API. High-quality photorealistic and artistic image generation with configurable aspect ratios.

## Models

| Model ID | Notes |
|---|---|
| `imagen-4.0-generate-001` | Standard — best quality/cost balance |
| `imagen-4.0-ultra-generate-001` | Ultra — highest quality, slowest, most expensive |
| `imagen-4.0-fast-generate-001` | Fast — lower quality, fast turnaround |

## Basic generation

```ts
import { GoogleGenAI } from 'npm:@google/genai';
const ai = new GoogleGenAI({ apiKey: Deno.env.get('GEMINI_API_KEY') });

const response = await ai.models.generateImages({
  model: 'imagen-4.0-generate-001',
  prompt: 'A flat design illustration of a mobile app showing a fitness dashboard with circular progress rings, vibrant colors on a dark background',
  config: {
    numberOfImages: 1,           // 1–4
    aspectRatio: '9:16',         // 1:1 | 3:4 | 4:3 | 9:16 | 16:9
    imageSize: '1K',             // '1K' | '2K' (standard/ultra only)
    personGeneration: 'DONT_ALLOW',  // 'DONT_ALLOW' | 'ALLOW_ADULT'
  },
});

// Output: array of base64-encoded PNG images
const imageBase64 = response.generatedImages![0].image!.imageBytes;
const imageBuffer = Buffer.from(imageBase64, 'base64');
```

## Configuration options

| Param | Values | Notes |
|---|---|---|
| `numberOfImages` | 1–4 | Default 4; usually use 1 for production to control cost |
| `aspectRatio` | `1:1`, `3:4`, `4:3`, `9:16`, `16:9` | Pick based on where the image is displayed |
| `imageSize` | `1K`, `2K` | `2K` only on standard/ultra; not on fast |
| `personGeneration` | `DONT_ALLOW`, `ALLOW_ADULT` | `ALLOW_ALL` blocked in EU/UK/MENA regions |

## Prompt tips for Imagen

- **English only** — Imagen 4 supports English prompts only. Max 480 tokens.
- Be descriptive about style: "watercolor illustration", "photorealistic product render", "flat design icon".
- Keep in-image text short (≤25 chars) for best text rendering results.
- Mention composition: "centered on white background", "bird's eye view", "close-up detail".
- Imagen handles photorealistic people well at `ALLOW_ADULT` — specify age/demographic explicitly.

## Storing and serving images

Images come as raw base64 bytes. Always store them — don't serve raw base64 to the client:

```ts
// Edge Function: generate → upload to Supabase Storage → return URL
const imageBytes = response.generatedImages![0].image!.imageBytes;
const imageBuffer = Buffer.from(imageBytes, 'base64');
const path = `${userId}/generated/${Date.now()}.png`;

await supabaseAdmin.storage
  .from('generated-images')
  .upload(path, imageBuffer, { contentType: 'image/png' });

const { data: { publicUrl } } = supabaseAdmin.storage
  .from('generated-images')
  .getPublicUrl(path);

return new Response(JSON.stringify({ url: publicUrl }), { headers: cors });
```

## Safety & limitations

- All outputs include a **SynthID watermark** (invisible, machine-readable).
- Requests violating Google's content policy are rejected.
- `ALLOW_ALL` (permits children in images) is **blocked in EU, UK, Switzerland, and MENA** — use `ALLOW_ADULT` as the safe default.
- No negative prompting param — phrase positively.
- No image editing / inpainting API (unlike OpenAI) — generation only.

## When to use Imagen vs GPT Image 2

| | Imagen 4 | GPT Image 2 |
|---|---|---|
| Style control | Strong | Strong |
| Instruction following | Very good | Excellent |
| Text in images | Limited (≤25 chars) | Better |
| Image editing (inpainting) | ❌ Not supported | ✅ Yes |
| Aspect ratios | 5 presets | More flexible |
| English-only | ✅ Yes | No restriction |
| SynthID watermark | ✅ Auto | Optional |

Imagen is a strong default if you're already in the Gemini ecosystem. Use GPT Image 2 if you need in-image editing or better text rendering.
