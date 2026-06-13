---
title: Gemini text generation
impact: HIGH
impactDescription: "thinking_level string enum replaces numeric thinking_budget; temperature/top_p/top_k removed in 3.5"
tags: gemini, text-generation, thinking, streaming
---

# Gemini text generation

## Basic request

```ts
import { GoogleGenAI } from 'npm:@google/genai';
const ai = new GoogleGenAI({ apiKey: Deno.env.get('GEMINI_API_KEY') });

const response = await ai.models.generateContent({
  model: 'gemini-3.5-flash',
  contents: 'Explain how neural networks work in 2 sentences.',
});
console.log(response.text);   // convenience shorthand
```

## System instruction

```ts
const response = await ai.models.generateContent({
  model: 'gemini-3.5-flash',
  config: {
    systemInstruction: 'You are a nutrition coach. Reply concisely in the same language the user writes.',
  },
  contents: userMessage,
});
```

The `config.systemInstruction` is Gemini's equivalent of the OpenAI `instructions` param — static, high-priority guidance that stays out of the user turn.

## Multi-turn conversations

Use the stateful `chat` helper:

```ts
const chat = ai.chats.create({
  model: 'gemini-3.5-flash',
  config: { systemInstruction: 'You are a helpful assistant.' },
  history: [],   // inject prior turns here to resume a saved session
});

const r1 = await chat.sendMessage({ message: 'Hello' });
const r2 = await chat.sendMessage({ message: 'What did I just say?' });
console.log(r2.text);
```

The chat object accumulates history internally. To persist across app sessions, serialize `chat.getHistory()` to your DB and pass it back in `history` on next init.

## Key config parameters

```ts
config: {
  systemInstruction: string,
  maxOutputTokens: 1024,        // cap output; critical for cost control
  thinking_level: 'medium',     // Gemini 3.5 only — 'minimal'|'low'|'medium'|'high'
  // temperature / top_p / top_k — REMOVED in Gemini 3.5, don't use
}
```

### Thinking (Gemini 3.5 Flash specific)

Gemini 3.5 has an internal reasoning step before answering. Control the depth:

```ts
config: { thinking_level: 'minimal' }   // quick, cheap
config: { thinking_level: 'high' }      // deep, expensive
```

`thinking_level` is a **string enum** (not a numeric budget like in Gemini 2.5). Setting `thinking_budget` here will be ignored or error — remove it if migrating.

Thinking costs extra tokens. Use `'minimal'` or `'low'` for simple tasks (classification, extraction); `'medium'`/`'high'` for complex analysis or coding. For tasks where you're using structured output or function calling, the model often performs better with some thinking enabled.

## Structured output (JSON)

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
      },
      required: ['food_name', 'calories', 'meal_type'],
    },
  },
  contents: `Extract meal data from: "${userMessage}"`,
});
const meal = JSON.parse(response.text);
```

`responseMimeType: 'application/json'` + `responseSchema` gives you guaranteed JSON output. Gemini 3.5 is strict about schema conformance.

## Streaming

```ts
const stream = await ai.models.generateContentStream({
  model: 'gemini-3.5-flash',
  contents: userMessage,
});
for await (const chunk of stream) {
  process.stdout.write(chunk.text ?? '');
}
```

For streaming from an Edge Function to React Native → [../streaming.md](../streaming.md).

## Common mistakes

- **Using `temperature` with Gemini 3.5** → parameter is deprecated and no longer has effect. Remove it.
- **Numeric `thinking_budget`** → was Gemini 2.5 API. Replace with `thinking_level` string.
- **`candidate_count > 1`** → unsupported in Gemini 3.5; always returns one candidate.
- **Not setting `maxOutputTokens`** → the model may run up costs on open-ended prompts.
