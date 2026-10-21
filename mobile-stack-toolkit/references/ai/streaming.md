---
title: "AI streaming contract and lifecycle"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# AI streaming contract and lifecycle

Streaming improves time to first visible output when the provider and network permit it; it does not guarantee a fixed latency. Keep a small application protocol independent of provider SDK events:

- `data: {"text":"delta"}` followed by a blank line adds text.
- `data: [DONE]` followed by a blank line confirms completion.
- `data: {"error":"generation_failed"}` followed by a blank line marks failure.

Authenticate, validate inputs and reserve quota before opening the stream. Limit request duration, frame size and total output. Before headers, use normal HTTP errors; afterward emit an error frame and close. Never send `[DONE]` merely because the upstream iterator ended after an incomplete or failed response.

For OpenAI Responses, narrow by `event.type === 'response.output_text.delta'` before reading `event.delta`. Track `response.completed`, `response.failed` and `response.incomplete`; handle refusal separately. For Gemini, forward `chunk.text` when present and inspect terminal status. Do not forward arbitrary provider events or internal reasoning.

## Expo client transport

Use `import { fetch } from 'expo/fetch'` for the documented streaming transport, with `AbortController`. Do not infer streaming fetch support from the Hermes or React Native version alone. Check HTTP status and `response.body` before obtaining a reader. Bare React Native projects must select and test a compatible transport.

A parser must retain partial UTF-8 bytes and incomplete lines across chunks, accept CRLF, join consecutive `data:` lines within one frame, and dispatch at the blank line. Ignore SSE comments and non-data fields according to the protocol. Validate JSON shapes; never swallow malformed/error frames. EOF without `[DONE]` is failure. Release/cancel the reader and abort upstream work when navigation or cancellation ends the request.

The [Flutter implementation](../flutter/ai-integration.md) shows the same framing contract. For a JavaScript parser, test split UTF-8 characters, multiple frames per chunk, fragmented terminators, server errors, truncated streams, output limits and user cancellation before shipping.

Accumulate deltas in one state/controller, throttle rendering for large output, and avoid appending the same cumulative snapshot twice. A retry may repeat paid work or mutations; use a server request ID and an explicit retry policy. Image/audio streaming depends on the endpoint; inspect its documented output format instead of applying this text parser.

## Sources

Reviewed 2026-10-20: [Expo fetch](https://docs.expo.dev/versions/latest/sdk/expo/), [OpenAI streaming](https://developers.openai.com/api/docs/guides/streaming-responses).
