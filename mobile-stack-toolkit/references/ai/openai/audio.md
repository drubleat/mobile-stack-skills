---
title: OpenAI audio — STT, TTS, Realtime
impact: MEDIUM-HIGH
impactDescription: "Three distinct audio capabilities with different APIs; picking the wrong one adds unnecessary latency or cost"
tags: openai, audio, stt, tts, whisper, realtime
---

# OpenAI audio — STT, TTS, Realtime

Three distinct capabilities, three different use cases. Pick the right one.

| Task | Model / API | Approach |
|---|---|---|
| Transcribe audio file / recording | `gpt-4o-transcribe` | Request-based (file upload) |
| Convert text to speech | `gpt-4o-mini-tts` | Request-based (streaming supported) |
| Live two-way voice agent | `gpt-realtime-2` | WebSocket / Realtime Sessions API |
| Real-time speech translation | `gpt-realtime-translate` | WebSocket session |

## Speech-to-text (transcription)

Record audio on the device, upload the file, get a transcript. Best for: voice memos, voice-to-note features, voice commands after the recording ends.

```ts
// Edge Function
import { toFile } from 'npm:openai';

const formData = await req.formData();
const audioBlob = formData.get('audio') as File;

const transcription = await openai.audio.transcriptions.create({
  model: 'gpt-4o-transcribe',
  file: audioBlob,
  language: 'tr',          // ISO-639-1; omit for auto-detect
  response_format: 'json', // 'text' | 'json' | 'srt' | 'vtt'
});
console.log(transcription.text);
```

From React Native — record with `expo-audio` (SDK 52+) or `expo-av`, then upload the file as multipart:

```ts
const formData = new FormData();
formData.append('audio', { uri: audioUri, name: 'recording.m4a', type: 'audio/m4a' } as any);
await fetch(`${SUPABASE_URL}/functions/v1/transcribe`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}` },
  body: formData,
});
```

Supported input formats: mp3, mp4, m4a, wav, webm, flac, ogg. Max file size 25 MB.

## Text-to-speech

Synthesize speech from text — for narration, accessibility, or AI voice responses.

```ts
const mp3 = await openai.audio.speech.create({
  model: 'gpt-4o-mini-tts',    // or gpt-4o-tts for higher quality
  voice: 'nova',               // alloy | ash | coral | echo | fable | nova | onyx | sage | shimmer
  input: 'Merhaba, bugün nasılsın?',
  response_format: 'mp3',      // mp3 | opus | aac | flac | wav | pcm
  speed: 1.0,                  // 0.25–4.0
  // Optional: instruct the voice style
  // instructions: 'Speak in a warm, friendly tone.',
});
const buffer = Buffer.from(await mp3.arrayBuffer());
// stream directly or return as base64 to the client
```

TTS supports streaming — stream chunks as they arrive for lower time-to-first-sound.

In React Native, play the returned audio with `expo-audio` or `expo-av`:
```ts
const sound = await Audio.Sound.createAsync({ uri: audioDataUri });
await sound.playAsync();
```

## Realtime voice sessions (WebSocket)

For live, low-latency, bidirectional voice — the model listens and responds in near real-time. Use for: voice assistants, voice tutors, live translation.

Architecture: open a WebSocket to the Realtime API **from your server / Edge Function** (not directly from the mobile client, for the same key-security reason as all other AI calls). The mobile app streams audio to your server; your server relays to the Realtime API.

```ts
// Pseudocode — actual implementation uses the @openai/realtime-api-beta SDK or raw WebSocket
const session = await openai.realtime.sessions.create({
  model: 'gpt-realtime-2',
  voice: 'alloy',
  instructions: 'You are a voice assistant. Be concise.',
  input_audio_format: 'pcm16',
  output_audio_format: 'pcm16',
});
// Use session.client_secret.value to authenticate the client-side WebSocket connection
```

The Realtime API has a different billing model (per minute of session, not per token) — profile usage carefully before shipping at scale.

## Common pitfalls

- **Sending raw file:// URI to OpenAI** → must upload the actual binary, not a local URI string.
- **No `language` param** → auto-detect works but adds latency; specify it if you know the language.
- **Realtime directly from the mobile client** → exposes the API key. Always relay through a server.
- **Audio file too large** → compress or chunk; 25 MB limit.
- **Choosing Realtime for pre-recorded audio** → overkill; use the transcription endpoint instead.
