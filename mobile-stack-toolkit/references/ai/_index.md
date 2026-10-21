---
title: "AI — domain index"
impact: MEDIUM-HIGH
impactDescription: "Routes to provider files, edge proxy, streaming, structured output, and guardrails"
tags: ai, openai, gemini, index
---

# AI Integration — index

Use a trusted server for provider secrets. Supabase Edge Functions are one host; Firebase AI Logic and short-lived Realtime credentials are supported alternatives. This domain covers the proxy architecture, provider-specific capabilities, prompt craft, streaming, and guardrails.

## Contents
- [Architecture & routing](#architecture--routing)
- [Provider decision](#provider-decision)
- [File map](#file-map)

## Architecture & routing

| Task | File |
|---|---|
| Server secrets and managed client alternatives | [edge-proxy-architecture.md](edge-proxy-architecture.md) |
| Streaming LLM responses to React Native / Flutter | [streaming.md](streaming.md) |
| Prompt engineering (system prompts, few-shot, CoT, structured prompting) | [prompt-engineering.md](prompt-engineering.md) |
| Structured data versus tool choice | [structured-output-tools.md](structured-output-tools.md) |
| Provider-agnostic structured output / JSON Schema | [structured-output.md](structured-output.md) |
| Rate limiting, prompt injection prevention, per-user quotas | [guardrails.md](guardrails.md) |

## Provider decision

| Use case | Go to |
|---|---|
| OpenAI overview, model selection, setup | [openai.md](openai.md) |
| OpenAI text generation (Responses API, multi-turn) | [openai/text-responses-api.md](openai/text-responses-api.md) |
| OpenAI vision (image understanding) | [openai/vision.md](openai/vision.md) |
| OpenAI audio (STT transcription, TTS, Realtime) | [openai/audio.md](openai/audio.md) |
| OpenAI image generation | [openai/image-generation.md](openai/image-generation.md) |
| OpenAI function calling / tool use | [openai/tools.md](openai/tools.md) |
| Gemini overview, model selection, setup | [gemini.md](gemini.md) |
| Gemini text generation (thinking, multi-turn, system instruction) | [gemini/text.md](gemini/text.md) |
| Gemini vision (multimodal input) | [gemini/vision.md](gemini/vision.md) |
| Gemini TTS / audio generation | [gemini/audio-tts.md](gemini/audio-tts.md) |
| Gemini image generation / Imagen migration | [gemini/imagen.md](gemini/imagen.md) |
| Gemini function calling | [gemini/tools.md](gemini/tools.md) |
| ElevenLabs TTS via Edge Function proxy + Conversational AI SDK | [elevenlabs.md](elevenlabs.md) |

## Provider selection

Compare the exact model's modalities, latency, quality, availability, and current price. Follow the provider overview above. Keep a stable application response contract, but expect provider swaps to require adapter work and tests; they are not generally a one-line change.
