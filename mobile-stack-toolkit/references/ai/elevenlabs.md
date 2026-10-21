---
title: "ElevenLabs speech and voice agents"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# ElevenLabs speech and voice agents

Use a trusted backend for TTS requests requiring a long-lived ElevenLabs key. Authenticate the user, reserve quota, bound text/output and set a timeout before calling the provider. Choose a currently available voice/model from the account; fixed voice lists, free-tier quotas and latency numbers age quickly.

For streamed TTS, call the documented text-to-speech stream endpoint and check HTTP status/content type. Return audio bytes or store them and return a signed URL—choose one explicit client contract. `supabase.functions.invoke` returning bytes does not turn them into a URI for an audio player. Do not manually set hop-by-hop Transfer-Encoding headers.

For Expo use the supported `expo-audio` player and current file APIs. If downloading bytes, write an actual matching audio format to a unique cache file, clean up files, and release the player on disposal. For Flutter use a compatible player and an explicit byte-download/file contract; do not assume every `audio/*` response is a `List<int>` in every functions SDK.

For real-time agents, `@elevenlabs/react-native` has a separate native/session lifecycle. Follow its provider/dependency setup, microphone permissions and supported authenticated session flow. Mint short-lived scoped credentials on a trusted server for private agents; never bundle the REST key. End sessions on cancel/disposal and handle reconnects with bounded spend.

See [guardrails](guardrails.md) and [audio alternatives](openai/audio.md). Test denial, interrupted playback, backgrounding, concurrent requests and provider failures.

## Sources

Reviewed 2026-10-20: [ElevenLabs TTS streaming](https://elevenlabs.io/docs/api-reference/text-to-speech/stream), [React Native SDK](https://elevenlabs.io/docs/agents-platform/libraries/react-native).
