---
title: OpenAI function calling & tool use
impact: HIGH
impactDescription: "Structured tool use with `strict: true` eliminates hallucinated argument shapes and enables reliable agentic flows"
tags: openai, function-calling, tools, structured-output
---

# OpenAI function calling & tool use

Function calling lets the model invoke your application's functions in a structured way — it decides when to call, what args to pass, and you execute the function and feed the result back. The result is reliable, typed integrations between the model and real-world actions.

## Define a tool

```ts
const tools = [
  {
    type: 'function' as const,
    name: 'get_nutrition_data',
    description: 'Look up calorie and macro data for a food item by name.',
    parameters: {
      type: 'object',
      properties: {
        food_name:  { type: 'string', description: 'The name of the food, e.g. "apple" or "grilled chicken breast"' },
        serving_g:  { type: 'number', description: 'Serving size in grams. Default 100 if not specified.' },
      },
      required: ['food_name'],
      additionalProperties: false,
    },
    strict: true,  // model must match schema exactly
  },
];
```

**`strict: true`** forces the model to match the schema — no extra fields, no missing required params. Use it for production. Without it, the model may add fields or omit required ones, causing parse errors.

## The tool-use loop

```ts
// 1. Initial request with tools
const response = await openai.responses.create({
  model: 'gpt-5.4-mini',
  instructions: 'Help users log meals. Use get_nutrition_data to look up food information.',
  input: userMessage,
  tools,
});

// 2. Check if the model wants to call a tool
const toolCalls = response.output.filter(o => o.type === 'function_call');

if (toolCalls.length > 0) {
  // 3. Execute each tool call
  const toolResults = await Promise.all(toolCalls.map(async (call) => {
    const args = JSON.parse(call.arguments);
    const result = await executeTool(call.name, args);  // your function
    return {
      type: 'function_call_output' as const,
      call_id: call.call_id,
      output: JSON.stringify(result),
    };
  }));

  // 4. Send results back — model produces final answer
  const finalResponse = await openai.responses.create({
    model: 'gpt-5.4-mini',
    instructions: 'Help users log meals.',
    input: [
      .../* original messages */,
      ...response.output,          // includes the function_call items
      ...toolResults,              // function_call_output items
    ],
    tools,
  });
  return finalResponse.output_text;
}

return response.output_text;
```

## Parallel tool calls

The model can call multiple tools in one turn. `toolCalls` may contain several items — run them in `Promise.all` (as above) and return all results in a single follow-up request. Don't loop: one round-trip per model turn.

## Built-in tools (no execution loop needed)

OpenAI's Responses API has first-party tools the API executes internally:

```ts
tools: [
  { type: 'web_search' },          // model searches the web
  { type: 'file_search', vector_store_ids: ['vs_...'] },  // semantic search over your files
]
```

For these, you don't handle a tool-call loop — the API completes the search and folds the result into the response automatically.

## Controlling tool invocation

```ts
tool_choice: 'auto'         // model decides (default)
tool_choice: 'required'     // must use at least one tool
tool_choice: 'none'         // text only, ignore tools
tool_choice: { type: 'function', name: 'get_nutrition_data' }  // force a specific tool
```

Use `tool_choice: 'required'` when the tool is the point — e.g. a "analyze this receipt" flow where you always want structured extraction, not a conversational fallback.

## Common mistakes

- **Missing `call_id` in the response.** The `function_call_output` item must include the exact `call_id` from the `function_call` item. Mismatch = API error.
- **Not running tools in parallel.** The model may request 3 lookups at once; running them sequentially triples latency.
- **Tool descriptions that are too vague.** The model picks tools based on description + param names. "Do something with food" is worse than "Look up calorie and macro data for a food item by name."
- **Exposing internal APIs as tools without auth.** If a tool calls an internal service, your Edge Function is the auth layer — the model doesn't handle that.
- **Schema without `additionalProperties: false`.** Without it the model may pass extra params, breaking typed arg parsing.

## Structured output vs function calling

| | Structured output | Function calling |
|---|---|---|
| Use for | Getting typed data from the model | Triggering side effects or lookups |
| Execution | None (model produces the value) | You run the function |
| Response shape | `output_text` → `JSON.parse()` | `function_call` → execute → `function_call_output` |

Use structured output when you just want the model to return typed data. Use function calling when the model needs external information to complete its answer, or needs to trigger an action.
