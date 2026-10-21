---
title: "OpenAI models and SDK selection"
impact: HIGH
impactDescription: "Use the provider API correctly while preserving server authorization"
tags: ai, mobile, api
---

# OpenAI models and SDK selection

Use the installed SDK and current [model catalog](https://developers.openai.com/api/docs/models) to select a model for the required modality, quality, latency, context length, and budget. Preserve an explicitly requested model. Check availability, deprecations, and [API pricing](https://developers.openai.com/api/docs/pricing); this skill does not carry a live price list.

```ts
// Deno: pin/lock the version selected for your project.
import OpenAI from 'npm:openai';
const openai = new OpenAI({ apiKey: Deno.env.get('OPENAI_API_KEY') });
const model = Deno.env.get('OPENAI_MODEL');
if (!model) throw new Error('OPENAI_MODEL is required');
```

In Node use `import OpenAI from 'openai'`. Keep provider configuration server-side; clients must not choose arbitrary expensive models. Use a dated snapshot when reproducibility requires one and the model supports it. An alias can change behavior; it is not a guarantee of compatibility.

For new integrations, use Responses when it meets requirements. Existing Chat Completions integrations can remain; migration is a separate scoped change. Do not promise cache savings or a deprecation date without a source.

| Capability | Reference |
|---|---|
| Text and conversation state | [Text](openai/text-responses-api.md) |
| Image input | [Vision](openai/vision.md) |
| Transcription, speech, Realtime | [Audio](openai/audio.md) |
| Image generation and edits | [Images](openai/image-generation.md) |
| Function calling | [Tools](openai/tools.md) |

Keep API keys server-side, enforce [quotas](guardrails.md), and set provider billing alerts. Alerts do not replace application spending controls.

## Sources

Reviewed 2026-10-20: [Responses](https://developers.openai.com/api/docs/guides/text), [model catalog](https://developers.openai.com/api/docs/models).
