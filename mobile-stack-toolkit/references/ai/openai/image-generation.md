---
title: OpenAI image generation — GPT Image 2
impact: MEDIUM
impactDescription: "GPT Image 2 supports multi-turn editing and text rendering; DALL-E 3 is deprecated"
tags: openai, image-generation, gpt-image
---

# OpenAI image generation — GPT Image 2

GPT Image 2 is OpenAI's current image generation model (successor to DALL-E 3). It produces high-quality, photorealistic images and supports instruction-following, multi-turn editing, and text rendering.

## Basic generation

```ts
// Edge Function
const result = await openai.images.generate({
  model: 'gpt-image-2',
  prompt: 'A vibrant flat-design illustration of a mobile app dashboard showing nutrition stats, pastel colors, minimal style',
  n: 1,                           // 1–10 images
  size: '1024x1024',              // 1024x1024 | 1536x1024 | 1024x1536 | auto
  quality: 'standard',           // 'standard' | 'hd'
  output_format: 'png',          // 'png' | 'jpeg' | 'webp'
  response_format: 'url',        // 'url' | 'b64_json'
});
const imageUrl = result.data[0].url;
```

Use `'b64_json'` if you need to process the image server-side before sending to the client. `'url'` gives you a temporary CDN link (expires after ~1 hour — download and store if you need it permanently).

## Size options

| Size | Use case |
|---|---|
| `1024x1024` | Square (social media, app UI mock) |
| `1536x1024` | Landscape (banners, cards) |
| `1024x1536` | Portrait (mobile screenshots, story format) |
| `auto` | Model picks based on the prompt |

## Prompt tips for GPT Image 2

- Be specific about style: "flat design illustration", "photorealistic product photo", "watercolor sketch".
- Mention color palette: "pastel blues and greens", "dark mode UI with neon accents".
- For UI/marketing: include context ("shown on an iPhone 16 Pro screen", "on a white background with soft shadow").
- GPT Image 2 handles text in images better than predecessors, but still keep text short.
- Negative prompting isn't a first-class param — phrase what you *do* want rather than what you don't.

## Image editing (inpainting)

```ts
// Edit a region of an existing image with a mask
const result = await openai.images.edit({
  model: 'gpt-image-2',
  image: fs.createReadStream('original.png'),  // PNG, square, RGBA
  mask: fs.createReadStream('mask.png'),        // White = edit zone, black = keep
  prompt: 'Replace the background with a tropical beach',
  n: 1,
  size: '1024x1024',
});
```

## From a mobile workflow

1. User requests an image → mobile sends prompt to Edge Function.
2. Edge Function generates with `gpt-image-2` → gets URL or base64.
3. **Store in Supabase Storage** if the image is user-owned data; don't expose OpenAI's temporary URL to the client. Upload it, return a signed URL or public URL.
4. Display in `<Image source={{ uri }} />`.

```ts
// In Edge Function: generate → upload → return permanent URL
const result = await openai.images.generate({ model: 'gpt-image-2', prompt, ... });
const imageData = await fetch(result.data[0].url).then(r => r.arrayBuffer());
const { data, error } = await supabaseAdmin.storage
  .from('generated-images')
  .upload(`${userId}/${Date.now()}.png`, imageData, { contentType: 'image/png' });
const { data: { publicUrl } } = supabaseAdmin.storage
  .from('generated-images').getPublicUrl(data!.path);
return new Response(JSON.stringify({ url: publicUrl }), { headers: cors });
```

## Cost & moderation notes

- Priced per image (check [openai.com/pricing](https://openai.com/pricing) — varies by size and quality).
- All generations go through OpenAI's safety system; requests for policy-violating content are rejected.
- Rate-limit image generation aggressively in your proxy — it's expensive and slow; users shouldn't be able to trigger it in a tight loop → [../guardrails.md](../guardrails.md).
