---
title: "Gemini text generation"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Gemini text generation

Use `@google/genai` on a trusted server. Configure a supported model server-side; inspect the model's capabilities instead of assuming all Gemini versions accept the same thinking and sampling settings.

```ts
import { GoogleGenAI } from 'npm:@google/genai';
const ai = new GoogleGenAI({ apiKey: Deno.env.get('GEMINI_API_KEY') });
const response = await ai.models.generateContent({
  model: Deno.env.get('GEMINI_TEXT_MODEL')!,
  contents: userMessage, // previously validated and bounded
  config: {
    systemInstruction: 'Answer concisely using the supplied information.',
    maxOutputTokens: 1024,
  },
});
if (!response.text) throw new Error('No text returned');
```

Thinking settings belong under `config.thinkingConfig`. Where the selected model supports it, use `thinkingLevel` with the SDK enum; other models use `thinkingBudget`. Do not pass REST-style `thinking_level` at the root of the JavaScript config. Supported levels and sampling behavior are model-specific. Output budgets can include reasoning overhead.

For structured extraction, use `responseMimeType: 'application/json'` plus the supported `responseSchema` or `responseJsonSchema` form. Check missing/blocked/truncated responses before parsing, then validate domain constraints locally. A schema does not establish truth or authorize a write.

`ai.chats.create({model, config, history})` and `chat.sendMessage({message})` retain chat history in memory. Persist only necessary turns under authenticated ownership; bound history and preserve complete model content when tools are involved. See [tools](tools.md).

For streaming, iterate `await ai.models.generateContentStream(...)`, forwarding text only through the application's [stream contract](../streaming.md). Inspect terminal candidate status; a nonempty partial answer does not establish successful completion.

## Sources

Reviewed 2026-10-20: [thinking](https://ai.google.dev/gemini-api/docs/thinking), [text generation](https://ai.google.dev/gemini-api/docs/text-generation).
