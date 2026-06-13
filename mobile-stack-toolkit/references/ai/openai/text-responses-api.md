---
title: OpenAI text generation — Responses API
impact: HIGH
impactDescription: "Responses API replaces Chat Completions; using old `messages`/`system` params returns errors on new models"
tags: openai, responses-api, text-generation, streaming
---

# OpenAI text generation — Responses API

The Responses API is OpenAI's current recommended API for text generation. All examples use it.

## Basic request

```ts
const response = await openai.responses.create({
  model: 'gpt-5.4-mini',          // or gpt-5.5 for complex tasks
  instructions: 'You are a concise assistant. Reply in the same language the user writes.',
  input: userMessage,
});
console.log(response.output_text);  // convenience helper — aggregates all text output
```

`instructions` is a top-level param, not a message role. It maps to the highest-priority system context. Put your static persona/rules here.

## Key parameters

| Param | Type | Notes |
|---|---|---|
| `model` | string | `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini` |
| `instructions` | string | System-level behavior, static content only |
| `input` | string \| array | Simple string, or an Items array for multimodal / multi-turn |
| `temperature` | 0–2 | 0 for deterministic/structured, 0.7 for creative, default 1 |
| `max_output_tokens` | int | Cap output length; important for cost control |
| `previous_response_id` | string | Chain responses for multi-turn (see below) |
| `reasoning` | object | `{ effort: "low"|"medium"|"high" }` — for reasoning-capable models |
| `stream` | boolean | Enable streaming (see streaming.md) |

## Multi-turn conversations

Two approaches. Pick one per use case:

**Option A — `previous_response_id` (server manages state):**
```ts
// First turn
const r1 = await openai.responses.create({ model, instructions, input: 'Hello' });
// Second turn — OpenAI remembers r1's context
const r2 = await openai.responses.create({
  model, instructions,
  input: 'What did I just say?',
  previous_response_id: r1.id,
});
```
Pros: no transcript management, better caching. Con: state lives on OpenAI's servers (consider privacy).

**Option B — manual Items array (you own the transcript):**
```ts
const messages = [
  { role: 'user', content: [{ type: 'input_text', text: 'Hello' }] },
  { role: 'assistant', content: [{ type: 'output_text', text: 'Hi there!' }] },
  { role: 'user', content: [{ type: 'input_text', text: 'What did I just say?' }] },
];
const response = await openai.responses.create({ model, instructions, input: messages });
```
Pros: full control, works with other context (images, files) in the same array.

## Structured output (guaranteed JSON)

```ts
const response = await openai.responses.create({
  model: 'gpt-5.4-mini',
  instructions: 'Extract meal data from the user message.',
  input: userMessage,
  text: {
    format: {
      type: 'json_schema',
      name: 'meal',
      schema: {
        type: 'object',
        properties: {
          food_name: { type: 'string' },
          calories:  { type: 'number' },
          meal_type: { type: 'string', enum: ['breakfast','lunch','dinner','snack'] },
        },
        required: ['food_name', 'calories', 'meal_type'],
        additionalProperties: false,
      },
      strict: true,
    },
  },
});
const meal = JSON.parse(response.output_text);
```

`strict: true` enforces the schema; the model will refuse rather than produce invalid JSON. Use `additionalProperties: false` to prevent extra fields.

## Reasoning models

For GPT-5.5 and other reasoning-capable models, control thinking effort:

```ts
const response = await openai.responses.create({
  model: 'gpt-5.5',
  instructions: 'Analyze this business problem thoroughly.',
  input: complexProblem,
  reasoning: { effort: 'high' },   // low | medium | high
});
```

Use `high` for complex analysis/coding, `low` for simple tasks where you pay reasoning token costs. Reasoning tokens are billed separately.

## Response output shape

```json
{
  "id": "resp_...",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [{ "type": "output_text", "text": "..." }]
    }
  ],
  "output_text": "..."  // aggregated shortcut
}
```

For streaming responses the shape arrives in chunks — see [../streaming.md](../streaming.md).

## Migrating from Chat Completions

```ts
// Before (Chat Completions)
const r = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [{ role: 'system', content: 'You are...' }, { role: 'user', content: msg }],
});
const text = r.choices[0].message.content;

// After (Responses API)
const r = await openai.responses.create({
  model: 'gpt-5.4-mini',
  instructions: 'You are...',
  input: msg,
});
const text = r.output_text;
```

Chat Completions still works and isn't going away — migrate at your own pace.
