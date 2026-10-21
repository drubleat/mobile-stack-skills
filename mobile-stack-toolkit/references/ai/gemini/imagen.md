---
title: "Google image generation: migrate from Imagen"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Google image generation: migrate from Imagen

The Gemini API Imagen endpoint is retired. Keep this reference path for migration, but use a supported image-capable Gemini model through `generateContent`. Do not carry Imagen-specific `generateImages` options or response parsing into that request.

```ts
// Server-side integration fragment; model and prompt are validated server inputs.
const response = await ai.models.generateContent({
  model: imageModel,
  contents: prompt,
  config: { responseModalities: ['TEXT', 'IMAGE'] },
});
const parts = response.candidates?.[0]?.content?.parts ?? [];
const images = parts.flatMap(part => part.inlineData?.data ? [part.inlineData] : []);
if (!images.length) throw new Error('No image returned');
```

Check returned MIME types, decoded byte sizes and output count before storage. Store private user output under a server-derived user ID, check upload errors, and return a short-lived URL. Do not label every response PNG or dereference the first candidate unconditionally. Text-only or blocked output is a normal failure case to handle.

Select model-specific aspect ratio, resolution and editing options from the live guide. Test these with the account/backend being deployed; Gemini Developer API and Vertex availability can differ. Apply [guardrails](../guardrails.md) before generation. See [OpenAI images](../openai/image-generation.md) for that provider's distinct request and storage flow.

## Sources

Reviewed 2026-10-20: [Imagen retirement](https://ai.google.dev/gemini-api/docs/imagen), [image generation](https://ai.google.dev/gemini-api/docs/image-generation).
