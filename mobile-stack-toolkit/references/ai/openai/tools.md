---
title: "OpenAI function calling"
impact: HIGH
impactDescription: "Use the provider API correctly while preserving server authorization"
tags: ai, mobile, api
---

# OpenAI function calling

The model requests actions; your server validates and authorizes their execution. A schema is not authorization. Use an allowlist, authenticated user context, idempotency for writes, and bounded tool rounds.

## Strict schema

```ts
const tools = [{
  type: 'function' as const,
  name: 'get_nutrition_data',
  description: 'Look up nutritional information for a named food and serving size.',
  strict: true,
  parameters: {
    type: 'object',
    properties: {
      food_name: { type: 'string' },
      serving_g: { type: ['number', 'null'] },
    },
    required: ['food_name', 'serving_g'],
    additionalProperties: false,
  },
}];
```

Strict function schemas require all properties in `required`; represent an optional value with a nullable type. Validate positive ranges and application semantics again on the server.

## Bounded response loop

```ts
const instructions = 'Help users log meals using available nutrition data.';
let response = await openai.responses.create({ model, instructions, input: userMessage, tools });
for (let round = 0; round < 5; round++) {
  const calls = response.output.filter(item => item.type === 'function_call');
  if (calls.length === 0) {
    if (response.status !== 'completed') throw new Error('Incomplete response');
    return response.output_text;
  }
  const outputs = [];
  for (const call of calls) {
    // Application-owned function: validate name/args, check user permissions,
    // and enforce idempotency/approval before any consequential side effect.
    const result = await executeAuthorizedTool(user, call.name, JSON.parse(call.arguments));
    outputs.push({ type: 'function_call_output' as const, call_id: call.call_id,
      output: JSON.stringify(result) });
  }
  response = await openai.responses.create({
    model, instructions, tools,
    previous_response_id: response.id,
    input: outputs,
  });
}
throw new Error('Tool round limit exceeded');
```

This excerpt uses stored response chaining. Re-send instructions on each request. For stateless/manual chaining, retain the relevant complete output items, including reasoning items required by the model, plus tool results. Do not let a client attach another user's response ID.

Parallelize independent read-only calls when helpful; dependent writes must preserve ordering. A follow-up can request more tools, so one follow-up is not necessarily the final answer. Handle refusals, incomplete responses, argument parse errors, and provider failures explicitly.

Provider-hosted tools such as web/file search execute within the API; your custom functions execute in your application. For typed data without actions use [structured output](../structured-output.md).

## Sources

Reviewed 2026-10-20: [Function calling](https://developers.openai.com/api/docs/guides/function-calling).
