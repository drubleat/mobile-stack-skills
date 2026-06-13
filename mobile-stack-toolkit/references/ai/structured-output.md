---
title: Structured output — provider-agnostic guide
impact: HIGH
impactDescription: "API-enforced JSON schemas eliminate parse errors and retry loops; prompt-only JSON is unreliable at scale"
tags: ai, structured-output, json, openai, gemini
---

# Structured output — provider-agnostic guide

Getting JSON back from an LLM reliably enough for production use requires both prompt design and API-level enforcement.

## The three tiers (weakest to strongest)

**1. Prompt-only:** "Respond with JSON." Unreliable — the model may add prose, wrap in markdown, or hallucinate fields. Don't use in production.

**2. JSON mode:** Tell the API to return valid JSON (but no schema). The model won't add markdown fences, but it can still return any shape.

**3. JSON Schema / Structured Output:** Provide a schema; the API guarantees the response matches it. Use this. Both OpenAI and Gemini support it.

## OpenAI — JSON Schema (Responses API)

```ts
const response = await openai.responses.create({
  model: 'gpt-5.4-mini',
  input: `Extract from: "${userMessage}"`,
  text: {
    format: {
      type: 'json_schema',
      name: 'meal_entry',
      schema: {
        type: 'object',
        properties: {
          food_name:  { type: 'string' },
          calories:   { type: 'number' },
          meal_type:  { type: 'string', enum: ['breakfast','lunch','dinner','snack'] },
          confidence: { type: 'number', description: '0-1, how confident the model is' },
        },
        required: ['food_name', 'calories', 'meal_type', 'confidence'],
        additionalProperties: false,
      },
      strict: true,
    },
  },
});
const meal = JSON.parse(response.output_text);
```

`strict: true` + `additionalProperties: false` = the model either matches the schema exactly or refuses. Handles missing fields with nulls if the field isn't `required`.

## Gemini — responseSchema

```ts
import { Type } from 'npm:@google/genai';

const response = await ai.models.generateContent({
  model: 'gemini-3.5-flash',
  config: {
    responseMimeType: 'application/json',
    responseSchema: {
      type: Type.OBJECT,
      properties: {
        food_name:  { type: Type.STRING },
        calories:   { type: Type.NUMBER },
        meal_type:  { type: Type.STRING, enum: ['breakfast','lunch','dinner','snack'] },
        confidence: { type: Type.NUMBER },
      },
      required: ['food_name', 'calories', 'meal_type', 'confidence'],
    },
  },
  contents: `Extract meal data from: "${userMessage}"`,
});
const meal = JSON.parse(response.text);
```

## Schema design tips

- **`required` everything you'll actually use.** Optional fields that the model omits cause `undefined` errors downstream.
- **Use `enum` for categorical fields.** It constrains the model and eliminates free-form strings you'd have to normalize anyway.
- **`additionalProperties: false` (OpenAI).** Prevents spurious fields the model invents.
- **Add a `confidence` or `extracted: boolean` field.** Lets the model signal low certainty, which you can surface in the UI ("Are you sure this is a banana?").
- **Avoid deep nesting in schemas.** Flat is faster to parse and cheaper (fewer tokens in the schema description).
- **Numbers for numbers.** Don't ask for `"calories: '200'"` — ask for `calories: number`. Type coercion at parse time is a footgun.

## Handling refusals & parse errors

Even with schema enforcement, validate on your end:

```ts
try {
  const data = JSON.parse(response.output_text ?? response.text);
  // Zod or manual validation
  if (typeof data.calories !== 'number') throw new Error('Invalid schema');
  return data;
} catch (e) {
  // Return a structured error to the client — don't crash
  return { error: 'Could not extract meal data. Please try rephrasing.' };
}
```

## Structured output vs function calling

Use structured output when you **just want typed data** from the model. Use function calling when the model needs to **call external APIs or trigger actions** to complete its answer. Don't use function calling as a structured-output workaround — it's heavier and introduces a loop → see [openai/tools.md](openai/tools.md) and [gemini/tools.md](gemini/tools.md).
