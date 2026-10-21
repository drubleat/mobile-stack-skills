---
title: "OpenAI text generation — Responses API"
impact: HIGH
impactDescription: "Responses and Chat Completions have different request shapes; choose the API deliberately"
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
| `temperature` | 0–2 | Model-dependent; omit unless supported by the selected model/reasoning setting |
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
This avoids resending the transcript in application code. Prior context still counts toward input usage; caching and retention depend on the request and service settings.

**Option B — manual Items array (you own the transcript):**
```ts
const firstInput = [{ role: 'user' as const, content: 'Hello' }];
const first = await openai.responses.create({ model, instructions, input: firstInput, store: false });
const response = await openai.responses.create({
  model, instructions, store: false,
  input: [
    ...firstInput,
    ...first.output, // preserve all output items, not only assistant text
    { role: 'user', content: 'What did I just say?' },
  ],
});
```
Pros: full control, works with other context (images, files) in the same array.

## Schema-constrained structured output

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
if (response.status !== 'completed') throw new Error('Incomplete response');
const refused = response.output.some(item => item.type === 'message' &&
  item.content.some(part => part.type === 'refusal'));
if (refused || !response.output_text) throw new Error('No structured result');
const meal = JSON.parse(response.output_text); // validate domain constraints next
```

`strict: true` constrains successful structured responses; check refusals and incomplete status before parsing. Use `additionalProperties: false` to prevent extra fields.

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

Use `high` for complex analysis/coding, `low` for simple tasks where you pay reasoning token costs. Reasoning tokens count toward output usage and applicable output-token billing.

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

Check the current API/model lifecycle before migrating; do not change an existing integration solely because this example uses Responses.

## State and privacy boundaries

Map conversation/response IDs to the authenticated user on the server. Do not trust a client-supplied `previous_response_id`. Re-send instructions on each chained call. Manual transcripts do not disable provider storage automatically; configure `store: false` and review applicable retention controls when needed. Handle `incomplete` status, refusals, timeouts, and output limits before parsing structured data.

Reviewed 2026-10-21: [conversation state](https://developers.openai.com/api/docs/guides/conversation-state). Model literals are historical examples; select a supported model from the current catalog.
