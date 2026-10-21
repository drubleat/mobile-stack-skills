---
title: "Gemini models and SDK selection"
impact: HIGH
impactDescription: "Use the provider API correctly while preserving server authorization"
tags: ai, mobile, api
---

# Gemini models and SDK selection

Use `@google/genai` for new JS/TS integrations. Preserve a working existing SDK until a scoped migration is requested. Configure the model on the server and check current availability, modalities, regional access, quotas, and deprecations.

```ts
import { GoogleGenAI } from 'npm:@google/genai'; // pin/lock in the project
const ai = new GoogleGenAI({ apiKey: Deno.env.get('GEMINI_API_KEY') });
const model = Deno.env.get('GEMINI_MODEL');
if (!model) throw new Error('GEMINI_MODEL is required');
```

Do not infer capabilities from a generation name. Thinking controls, sampling settings, function-call IDs, and supported output schemas depend on the specific model and SDK version. JS configuration uses the SDK's camelCase fields; REST examples may use different casing. Use current migration guidance when upgrading instead of a universal “all old parameters were removed” table.

| Capability | Reference |
|---|---|
| Text, thinking, conversations | [Text](gemini/text.md) |
| Image input | [Vision](gemini/vision.md) |
| Speech generation | [Audio/TTS](gemini/audio-tts.md) |
| Imagen generation | [Imagen](gemini/imagen.md) |
| Function calling | [Tools](gemini/tools.md) |

Keep the provider API key on the server. For Firebase-native apps, [Firebase AI Logic](../firebase/ai-logic.md) can provide a managed client path with App Check; it is a different integration/security model. Provider pricing and context limits are intentionally linked rather than duplicated in this router.

## Sources

Reviewed 2026-10-20: [Gemini models](https://ai.google.dev/gemini-api/docs/models), [Google Gen AI SDK](https://ai.google.dev/gemini-api/docs/libraries), [pricing](https://ai.google.dev/gemini-api/docs/pricing).
