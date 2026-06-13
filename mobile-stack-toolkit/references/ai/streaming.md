---
title: Streaming AI responses to React Native
impact: HIGH
impactDescription: "Streaming drops perceived latency from 5–10s to ~300ms first token; non-streamed AI UIs feel broken by comparison"
tags: ai, streaming, openai, gemini, react-native, ux
---

# Streaming AI responses to React Native

Streaming gets the first token to the user in ~300ms instead of waiting 5–10s for the full response. For any text-generation feature visible in the UI, stream.

## Architecture

```
Mobile app  →  POST /functions/v1/ai-stream
              ← Server-Sent Events (text/event-stream)
                 chunk … chunk … chunk … [DONE]
```

The Edge Function calls the model with `stream: true` (OpenAI) or `generateContentStream` (Gemini) and pipes chunks to the client as SSE.

## Edge Function — OpenAI streaming

```ts
// supabase/functions/ai-stream/index.ts
Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  // ... auth + quota check ...

  const { userMessage } = await req.json();
  const stream = await openai.responses.create({
    model: 'gpt-5.4-mini',
    instructions: 'You are a helpful assistant.',
    input: userMessage,
    stream: true,
  });

  const readable = new ReadableStream({
    async start(controller) {
      for await (const event of stream) {
        const text = event.delta ?? '';     // delta contains the new text chunk
        if (text) {
          controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ text })}\n\n`));
        }
      }
      controller.enqueue(new TextEncoder().encode('data: [DONE]\n\n'));
      controller.close();
    },
  });

  return new Response(readable, {
    headers: { ...cors, 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
  });
});
```

## Edge Function — Gemini streaming

```ts
const stream = await ai.models.generateContentStream({
  model: 'gemini-3.5-flash',
  contents: [{ role: 'user', parts: [{ text: userMessage }] }],
});

const readable = new ReadableStream({
  async start(controller) {
    for await (const chunk of stream) {
      const text = chunk.text ?? '';
      if (text) {
        controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ text })}\n\n`));
      }
    }
    controller.enqueue(new TextEncoder().encode('data: [DONE]\n\n'));
    controller.close();
  },
});
return new Response(readable, {
  headers: { ...cors, 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
});
```

## React Native client — consuming SSE

React Native's `fetch` doesn't support `EventSource`. Use a manual reader loop instead:

```ts
// lib/ai.ts
export async function streamAI(message: string, onChunk: (text: string) => void) {
  const { data: { session } } = await supabase.auth.getSession();

  const response = await fetch(`${SUPABASE_URL}/functions/v1/ai-stream`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${session!.access_token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ userMessage: message }),
  });

  if (!response.ok || !response.body) throw new Error('Stream failed');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';    // keep incomplete line in buffer

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim();
        if (data === '[DONE]') return;
        try {
          const { text } = JSON.parse(data);
          if (text) onChunk(text);
        } catch {}
      }
    }
  }
}
```

## Rendering streamed text in a component

```tsx
const [response, setResponse] = useState('');

const handleSend = async () => {
  setResponse('');
  await streamAI(userInput, (chunk) => {
    setResponse(prev => prev + chunk);
  });
};

// In JSX:
<Text>{response}</Text>
// Or for a typing-cursor effect: <Text>{response}{loading ? '▍' : ''}</Text>
```

## Hermes / JSC compatibility note

React Native's Hermes engine supports `ReadableStream` from RN 0.73+. If you're on an older version, you may need a polyfill or use the `react-native-fetch-api` package. SDK 55+ with Hermes works without polyfills.

## When NOT to stream

- Short responses (≤2 sentences): the latency overhead of setting up a stream isn't worth it; just use a regular request and show a loading indicator.
- Structured JSON output: stream gives you partial JSON, which you can't parse until `[DONE]`. Use a regular request and display a skeleton loader instead.
- Image/audio generation: these APIs don't meaningfully support streaming to the client.
