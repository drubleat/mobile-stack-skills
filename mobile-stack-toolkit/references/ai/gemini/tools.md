---
title: Gemini function calling & tool use
impact: HIGH
impactDescription: "Gemini 3.5 requires strict id+name matching in function responses — a breaking change that silently breaks tool loops"
tags: gemini, function-calling, tools, structured-output
---

# Gemini function calling & tool use

Gemini 3.5 supports function calling with strict `id` + `name` matching (a breaking change from 2.5). The pattern is similar to OpenAI but the API shape differs.

## Define tools

```ts
import { Type } from 'npm:@google/genai';

const tools = [{
  functionDeclarations: [
    {
      name: 'get_nutrition_data',
      description: 'Look up calorie and macro data for a food item.',
      parameters: {
        type: Type.OBJECT,
        properties: {
          food_name: {
            type: Type.STRING,
            description: 'The name of the food item, e.g. "apple" or "grilled chicken"',
          },
          serving_g: {
            type: Type.NUMBER,
            description: 'Serving size in grams. Default 100.',
          },
        },
        required: ['food_name'],
      },
    },
  ],
}];
```

All function declarations go under `functionDeclarations` inside a single tool object. Don't put each function in its own top-level tools entry.

## The tool-use loop

```ts
const response = await ai.models.generateContent({
  model: 'gemini-3.5-flash',
  config: {
    systemInstruction: 'Help users log meals. Use get_nutrition_data to look up food info.',
    tools,
  },
  contents: [{ role: 'user', parts: [{ text: userMessage }] }],
});

// Check for function calls
const part = response.candidates?.[0].content.parts?.[0];
if (part?.functionCall) {
  const { name, id, args } = part.functionCall;

  // Execute the function
  const result = await executeTool(name, args);

  // Return result — Gemini 3.5 requires matching id AND name
  const followUp = await ai.models.generateContent({
    model: 'gemini-3.5-flash',
    config: { systemInstruction: '...', tools },
    contents: [
      { role: 'user',  parts: [{ text: userMessage }] },
      { role: 'model', parts: [{ functionCall: { name, id, args } }] },
      {
        role: 'user',
        parts: [{
          functionResponse: {
            id,       // ← Gemini 3.5: REQUIRED — must match functionCall.id
            name,     // ← Gemini 3.5: REQUIRED — must match functionCall.name
            response: { result: JSON.stringify(result) },
          },
        }],
      },
    ],
  });
  return followUp.text;
}

return response.text;
```

### Gemini 3.5 strict requirement

In **Gemini 2.5**, `id` in the function response was optional. In **Gemini 3.5**, both `id` and `name` are required and must exactly match the `functionCall` fields. Omitting `id` causes an error.

## Parallel tool calls

If the model calls multiple functions in one turn, `response.candidates[0].content.parts` will contain multiple `functionCall` parts:

```ts
const functionCallParts = response.candidates![0].content.parts!
  .filter(p => p.functionCall);

const results = await Promise.all(functionCallParts.map(async (p) => {
  const { name, id, args } = p.functionCall!;
  const result = await executeTool(name, args);
  return { role: 'user' as const, parts: [{ functionResponse: { id, name, response: { result } } }] };
}));
// Send all results back in one request
```

## Built-in Google tools

```ts
config: {
  tools: [{ googleSearch: {} }],     // model can search the web
  // or
  tools: [{ codeExecution: {} }],    // model runs Python code internally
}
```

For `googleSearch` and `codeExecution`, no execution loop — the API handles it and returns grounded answers.

## Tool choice control

```ts
config: {
  toolConfig: {
    functionCallingConfig: {
      mode: 'AUTO',       // model decides — default
      // mode: 'ANY'      // must call a function
      // mode: 'NONE'     // no function calls
      // allowedFunctionNames: ['get_nutrition_data']  // restrict to specific functions
    },
  },
}
```

## Common pitfalls

- **Missing `id` in `functionResponse`** → error in Gemini 3.5; copy `functionCall.id` exactly.
- **`functionDeclarations` at the wrong level** → must be inside a tool object `[{ functionDeclarations: [...] }]`, not `[{ name: '...' }]` directly.
- **Not parallel-processing multiple calls** → degrades latency when the model requests several functions at once.
- **Relying on function calling for guaranteed structure** when you just want typed output → use `responseMimeType: 'application/json'` + `responseSchema` instead (simpler, no execution loop) → [../structured-output.md](../structured-output.md).
