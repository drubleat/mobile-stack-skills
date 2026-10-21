---
title: "OpenAI image generation and edits"
impact: HIGH
impactDescription: "Use the provider API correctly while preserving server authorization"
tags: ai, mobile, api
---

# OpenAI image generation and edits

Choose an available GPT Image model from the model catalog; set `OPENAI_IMAGE_MODEL` on the server. Do not mix DALL-E parameters with GPT Image parameters. Model-specific sizes, quality, edit support, and transparency constraints must be checked before use.

```ts
const result = await openai.images.generate({
  model: imageModel, // validated server configuration
  prompt,
  n: 1,
  size: '1024x1024',
  quality: 'medium',
  output_format: 'png',
});
const encoded = result.data?.[0]?.b64_json;
if (!encoded) throw new Error('No image returned');
const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
const path = `${user.id}/${crypto.randomUUID()}.png`;
const { error: uploadError } = await userClient.storage
  .from('generated-images').upload(path, bytes, { contentType: 'image/png' });
if (uploadError) throw uploadError;
const { data, error: signingError } = await userClient.storage
  .from('generated-images').createSignedUrl(path, 300);
if (signingError || !data) throw signingError ?? new Error('Signing failed');
return new Response(JSON.stringify({ url: data.signedUrl }), {
  headers: { ...cors, 'Content-Type': 'application/json' },
});
```

This excerpt assumes validated auth, prompt limits, a private bucket with owner-folder policies, quota checks, and configured clients. GPT Image responses use base64 data; do not request `response_format: 'url'` or read a nonexistent URL. Handle provider rejection, timeout, upload failure, and retry idempotency without generating twice accidentally.

For edits, upload valid input files. A PNG mask's **transparent alpha regions** identify the edit region; black/white RGB alone is not the mask contract. Check that the chosen model supports the requested masking/transparency behavior and required dimensions. Never assume all input images must be square.

Use a job/status flow when generation can outlast the server request deadline. Bound concurrency and image count. For streaming/partial images, use the selected model's documented API; a text SSE parser is not an image protocol.

## Sources

Reviewed 2026-10-20: [Image generation](https://developers.openai.com/api/docs/guides/image-generation), [model catalog](https://developers.openai.com/api/docs/models).
