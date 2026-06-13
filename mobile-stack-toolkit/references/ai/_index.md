---
title: AI — domain index
impact: MEDIUM-HIGH
impactDescription: "Routes to provider files, edge proxy, streaming, structured output, and guardrails"
tags: ai, openai, gemini, index
---

# AI Integration — index

All AI features in this toolkit flow through a **Supabase Edge Function proxy** — never directly from the client. This domain covers the proxy architecture, provider-specific capabilities, prompt craft, streaming, and guardrails.

## Contents
- [Architecture & routing](#architecture--routing)
- [Provider decision](#provider-decision)
- [File map](#file-map)

## Architecture & routing

| Task | File |
|---|---|
| Why every AI call goes through an Edge Function | [edge-proxy-architecture.md](edge-proxy-architecture.md) |
| Streaming LLM responses to React Native / Flutter | [streaming.md](streaming.md) |
| Prompt engineering (system prompts, few-shot, CoT, structured prompting) | [prompt-engineering.md](prompt-engineering.md) |
| Provider-agnostic structured output / JSON Schema | [structured-output.md](structured-output.md) |
| Rate limiting, prompt injection prevention, per-user quotas | [guardrails.md](guardrails.md) |

## Provider decision

| Use case | Go to |
|---|---|
| OpenAI overview, model selection, setup | [openai.md](openai.md) |
| OpenAI text generation (Responses API, multi-turn) | [openai/text-responses-api.md](openai/text-responses-api.md) |
| OpenAI vision (image understanding) | [openai/vision.md](openai/vision.md) |
| OpenAI audio (STT transcription, TTS, Realtime) | [openai/audio.md](openai/audio.md) |
| OpenAI image generation (GPT Image 2) | [openai/image-generation.md](openai/image-generation.md) |
| OpenAI function calling / tool use | [openai/tools.md](openai/tools.md) |
| Gemini overview, model selection, setup | [gemini.md](gemini.md) |
| Gemini text generation (thinking, multi-turn, system instruction) | [gemini/text.md](gemini/text.md) |
| Gemini vision (multimodal input) | [gemini/vision.md](gemini/vision.md) |
| Gemini TTS / audio generation (30 voices, Turkish) | [gemini/audio-tts.md](gemini/audio-tts.md) |
| Gemini image generation (Imagen 4) | [gemini/imagen.md](gemini/imagen.md) |
| Gemini function calling | [gemini/tools.md](gemini/tools.md) |
| ElevenLabs TTS via Edge Function proxy + Conversational AI SDK | [elevenlabs.md](elevenlabs.md) |

## Provider decision — quick pick

```
Need text/reasoning?
  ├─ GPT-5.5 for complex/professional/coding work ($5/$30 per MTok)
  ├─ GPT-5.4-mini for high-volume or latency-sensitive ($0.75/$4.50)
  ├─ gemini-3.5-flash for agentic/coding tasks with thinking ($1.50/$9)
  └─ gemini-2.5-flash-lite for cheapest inference ($0.10/$0.40)

Need vision (image understanding)?  → Either works; see openai/vision.md or gemini/vision.md
Need STT / speech-to-text?         → OpenAI gpt-4o-transcribe (strong multilingual)
Need TTS / text-to-speech?         → Gemini 3.1 Flash TTS (controllable, Turkish ✓)
Need image generation?             → GPT Image 2 (photorealistic) or Imagen 4 (configurable)
Need function calling?             → Both support it; see provider-specific tools.md
```

The choice of provider usually comes down to: cost tier for your traffic, which modality you need, and whether you already have credits with one provider. Architecturally, since everything goes through your Edge Function, **swapping providers is a one-line change** in the function — the mobile client never needs updating.
