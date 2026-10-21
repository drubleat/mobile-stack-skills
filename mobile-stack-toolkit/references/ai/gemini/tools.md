---
title: "Gemini tool loops"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Gemini tool loops

Declare functions under `config.tools[].functionDeclarations`. Keep the tool allowlist small; validate arguments, authenticate the actor and authorize each resource in application code. Tool descriptions are not an access-control layer.

Integration fragment: `tools`, `config`, `model`, `userMessage` and `executeAuthorizedTool` are application-owned values. The executor must reject unknown tools and invalid arguments and enforce permissions independently of model output.

```ts
import type { Content, Part } from 'npm:@google/genai';
const contents: Content[] = [{ role: 'user', parts: [{ text: userMessage }] }];
for (let round = 0; round < 4; round++) {
  const response = await ai.models.generateContent({ model, config, contents });
  const content = response.candidates?.[0]?.content;
  if (!content) throw new Error('No model content');
  const calls = (content.parts ?? []).flatMap(p => p.functionCall ? [p.functionCall] : []);
  if (!calls.length) {
    if (!response.text) throw new Error('No final text');
    return response.text;
  }
  if (calls.length > 8) throw new Error('Tool call budget exceeded');
  contents.push(content); // preserve all parts, including thought signatures
  const parts: Part[] = [];
  for (const call of calls) {
    if (!call.name) throw new Error('Missing tool name');
    const result = await executeAuthorizedTool(call.name, call.args ?? {});
    parts.push({ functionResponse: {
      name: call.name,
      ...(call.id ? { id: call.id } : {}),
      response: { result },
    } });
  }
  contents.push({ role: 'user', parts });
}
throw new Error('Tool round budget exceeded');
```

Preserve identifiers when supplied and return every call's result. Do not reconstruct a single model part and discard signatures. Parallelize only independent reads; order mutations and provide idempotency keys for retries. Bound execution time and response sizes as well as round count. Persist conversation state with user ownership checks.

Built-in search/code execution have different lifecycle and billing behavior; enable only features supported by the model. For typed data without execution, use [structured output](../structured-output.md).

## Sources

Reviewed 2026-10-20: [function calling](https://ai.google.dev/gemini-api/docs/function-calling), [thought signatures](https://ai.google.dev/gemini-api/docs/thought-signatures).
