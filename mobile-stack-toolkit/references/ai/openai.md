---
title: OpenAI — overview and model selection
impact: HIGH
impactDescription: "Correct model choice (gpt-5.5 vs gpt-5.4-mini) drives 10–40x cost difference with minimal quality tradeoff"
tags: openai, models, pricing, responses-api
---

# OpenAI — overview & model selection

## SDK install & init (in an Edge Function)

```bash
# In Deno (Edge Function) — use npm: import
# In Node.js / local tooling
npm install openai
```

```ts
// Deno Edge Function
import OpenAI from 'npm:openai';
const openai = new OpenAI({ apiKey: Deno.env.get('OPENAI_API_KEY') });

// Node.js
import OpenAI from 'openai';
const openai = new OpenAI(); // reads OPENAI_API_KEY from env automatically
```

## Current models (June 2026)

| Model | ID | Best for | Input / Output per MTok |
|---|---|---|---|
| **GPT-5.5** | `gpt-5.5` | Complex professional work, coding, agentic tasks | $5 / $30 |
| **GPT-5.4** | `gpt-5.4` | Strong general purpose | $2.50 / $15 |
| **GPT-5.4 mini** | `gpt-5.4-mini` | High-volume, latency-sensitive | $0.75 / $4.50 |
| GPT-4o Transcribe | `gpt-4o-transcribe` | Speech-to-text | per minute |
| GPT Image 2 | `gpt-image-2` | Image generation | per image |
| GPT Realtime 2 | `gpt-realtime-2` | Live voice agents (websocket) | per session |

All frontier models (`gpt-5.x`) support text and image input (vision), multilingual, and function calling. Context: 1M tokens (gpt-5.5/5.4), 400K (gpt-5.4-mini).

> **Re-check model IDs before pinning** — OpenAI releases new snapshots frequently. Use `gpt-5.4-mini` (not `gpt-5.4-mini-YYYY-MM-DD`) to always get the latest stable snapshot, or pin a dated snapshot for stability.

## Responses API vs Chat Completions

**Use the Responses API for all new projects.** It's OpenAI's current recommended API with better performance, built-in state management, and native tool support.

| | Chat Completions | Responses API |
|---|---|---|
| Endpoint | `/chat/completions` | `/responses` |
| Input param | `messages` array | `input` (string or Items) |
| System prompt | `{ role: "system", content: "..." }` | top-level `instructions` param |
| Output access | `choices[0].message.content` | `response.output_text` |
| Multi-turn state | manual transcript | `previous_response_id` |

Chat Completions still works and isn't going away, but the Responses API gives you better cache utilization (40-80% improvement per OpenAI) and a cleaner API for agentic workflows.

## Capability map → files

| Capability | File |
|---|---|
| Text generation, multi-turn, Responses API | [openai/text-responses-api.md](openai/text-responses-api.md) |
| Vision / image understanding | [openai/vision.md](openai/vision.md) |
| STT, TTS, Realtime voice | [openai/audio.md](openai/audio.md) |
| Image generation (GPT Image 2) | [openai/image-generation.md](openai/image-generation.md) |
| Function calling / tool use | [openai/tools.md](openai/tools.md) |

## Security checklist (always)

- `OPENAI_API_KEY` lives only in `supabase secrets set` / Edge Function env. Never in the mobile bundle.
- Set a **spending limit** in the OpenAI dashboard — a runaway function or a leaked key won't bleed indefinitely.
- Add per-user rate limiting in your proxy → [guardrails.md](guardrails.md).
