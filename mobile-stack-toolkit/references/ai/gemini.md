---
title: Gemini — overview and model selection
impact: HIGH
impactDescription: "Gemini 3.5 has breaking API changes from 2.5; using old params (thinking_budget, temp) causes silent degradation"
tags: gemini, models, pricing, google
---

# Gemini — overview & model selection

## SDK install & init

```bash
npm install @google/genai          # JS/TS SDK (latest — not the older @google/generative-ai)
```

```ts
// Edge Function (Deno) or Node.js
import { GoogleGenAI } from 'npm:@google/genai';   // Deno
// import { GoogleGenAI } from '@google/genai';    // Node.js

const ai = new GoogleGenAI({ apiKey: Deno.env.get('GEMINI_API_KEY') });
```

> **Package name changed.** The current SDK is `@google/genai` (with `GoogleGenAI` class). The older `@google/generative-ai` (with `GoogleGenerativeAI`) is legacy — don't use it in new projects.

## Current models (June 2026)

| Model | ID | Best for | Input / Output per MTok |
|---|---|---|---|
| **Gemini 3.5 Flash** | `gemini-3.5-flash` | Agentic tasks, coding, complex reasoning with thinking | $1.50 / $9 |
| **Gemini 3.1 Flash-Lite** | `gemini-3.1-flash-lite` | Speed + scale | — |
| **Gemini 2.5 Flash-Lite** | `gemini-2.5-flash-lite` | Cheapest inference | $0.10 / $0.40 |
| Gemini 3.1 Flash TTS | `gemini-3.1-flash-tts-preview` | Text-to-speech | per character |
| Imagen 4 | `imagen-4.0-generate-001` | Image generation | per image |

> **Gemini 2.0 Flash was shut down June 1, 2026.** If you're migrating, move to `gemini-2.5-flash-lite` (cheapest) or `gemini-3.5-flash` (best).

## Gemini 3.5 — breaking changes from 2.5

If you're upgrading from Gemini 2.5, these **will break** your code:

| Param | Gemini 2.5 | Gemini 3.5 |
|---|---|---|
| Thinking control | `thinking_budget: 1024` (int) | `thinking_level: "medium"` (string enum) |
| Sampling | `temperature`, `top_p`, `top_k` work | Removed — "no longer recommended" |
| Function calling | Flexible | Now requires strict `id` + `name` matching |
| Image segmentation | Supported | Removed |
| `candidate_count` | Supported | Unsupported |

## Capability map → files

| Capability | File |
|---|---|
| Text generation, thinking, multi-turn, system instruction | [gemini/text.md](gemini/text.md) |
| Vision / multimodal image input | [gemini/vision.md](gemini/vision.md) |
| Text-to-speech (30 voices, Turkish ✓) | [gemini/audio-tts.md](gemini/audio-tts.md) |
| Image generation (Imagen 4) | [gemini/imagen.md](gemini/imagen.md) |
| Function calling / tool use | [gemini/tools.md](gemini/tools.md) |

## Context windows

- Gemini 3.5 Flash: **1M token input**, 65K max output.
- Long-context is a genuine Gemini differentiator. For tasks requiring the entire codebase or a full document in context, Gemini often wins on price vs GPT-5.x at 1M context.

## Security checklist

- `GEMINI_API_KEY` lives only in Edge Function secrets — never the mobile bundle.
- Set quota limits in Google AI Studio / Google Cloud console.
- Add per-user rate limiting in your proxy → [guardrails.md](guardrails.md).
