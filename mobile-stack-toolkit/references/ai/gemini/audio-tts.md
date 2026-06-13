---
title: Gemini audio & TTS
impact: MEDIUM
impactDescription: "Gemini TTS models are separate from multimodal models; STT is better handled by OpenAI Whisper"
tags: gemini, audio, tts, speech
---

# Gemini audio & TTS

Gemini offers **controllable text-to-speech** via dedicated TTS models. This is distinct from audio *understanding* (which is handled by the main multimodal models). Currently, TTS is the primary audio generation use case; STT is best handled by OpenAI Whisper → [../openai/audio.md](../openai/audio.md).

## TTS models (June 2026)

| Model | Notes |
|---|---|
| `gemini-3.1-flash-tts-preview` | Best balance of quality and speed; recommended |
| `gemini-2.5-flash-preview-tts` | Good quality |
| `gemini-2.5-pro-preview-tts` | Highest quality |

Note: these are preview models — check [ai.google.dev](https://ai.google.dev) for GA releases.

**Streaming is not supported** for TTS. The full audio is returned as a single response.

## Single-speaker TTS

```ts
import { GoogleGenAI } from 'npm:@google/genai';

const ai = new GoogleGenAI({ apiKey: Deno.env.get('GEMINI_API_KEY') });

const response = await ai.models.generateContent({
  model: 'gemini-3.1-flash-tts-preview',
  contents: [{ parts: [{ text: 'Merhaba, bugün nasılsın? Sana nasıl yardımcı olabilirim?' }] }],
  config: {
    responseModalities: ['AUDIO'],
    speechConfig: {
      voiceConfig: {
        prebuiltVoiceConfig: { voiceName: 'Kore' },
      },
    },
  },
});

// Output is base64-encoded PCM audio (24kHz, mono, 16-bit)
const audioData = response.candidates![0].content.parts![0].inlineData!.data;
const audioBuffer = Buffer.from(audioData, 'base64');
// Write to file or stream to client
```

## Available voices (30 total — selection)

| Voice | Style |
|---|---|
| `Kore` | Firm |
| `Puck` | Upbeat |
| `Charon` | Informative |
| `Fenrir` | Excitable |
| `Aoede` | Breezy |
| `Zephyr` | Bright |
| `Enceladus` | Breathy |
| `Leda` | Youthful |

You can control style beyond the preset via the prompt text itself — write naturally ("say this warmly", "speak slowly and clearly") and the model adapts. The voice style is guided by natural language, not just voice selection.

## Multi-speaker TTS

For dialogue or podcast-style audio:

```ts
config: {
  responseModalities: ['AUDIO'],
  speechConfig: {
    multiSpeakerVoiceConfig: {
      speakerVoiceConfigs: [
        { speaker: 'Host', voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } } },
        { speaker: 'Guest', voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Puck' } } },
      ],
    },
  },
},
contents: [{
  parts: [{
    text: `Host: Welcome to the show.\nGuest: Thanks for having me!`,
  }],
}],
```

The model splits the text on speaker names and generates interleaved audio.

## Turkish language support

Turkish (`tr`) is explicitly supported in 90+ languages Gemini TTS understands. **No special configuration needed** — just write the text in Turkish and the model speaks it in Turkish using the selected voice:

```ts
contents: [{ parts: [{ text: 'Bu uygulamayı kullandığınız için teşekkür ederiz.' }] }]
```

The model auto-detects language from text; you don't set a language code for TTS.

## Returning audio to the mobile client

The audio output is raw PCM (24kHz, 16-bit mono). Your Edge Function options:

**A) Return base64 to client, play from memory:**
```ts
// Edge Function returns:
return new Response(JSON.stringify({ audio: audioData /* base64 */ }), { headers: cors });

// React Native: decode and play
import { Audio } from 'expo-av';
// Convert PCM → wav header + play, or use a PCM player
```

**B) Encode to WAV in the Edge Function first** (simpler to play client-side):
```ts
// Write a WAV header around the raw PCM bytes
const wavBuffer = pcmToWav(audioBuffer, { sampleRate: 24000, channels: 1, bitDepth: 16 });
// Return as binary or base64
```

**C) Upload to Supabase Storage, return URL** — best for longer audio or caching:
```ts
await supabaseAdmin.storage.from('tts-cache').upload(`${userId}/${hash}.wav`, wavBuffer);
```

## Common pitfalls

- **Expecting streaming** → TTS returns the full audio in one shot; no chunks.
- **Playing raw PCM directly** → needs a WAV header or a PCM-capable audio player. Encode to WAV/MP3 server-side.
- **Long text** → TTS works best on paragraph-length text. Split very long content into chunks and concatenate.
- **Not caching repeat phrases** → UI phrases like "Are you sure?" don't need regeneration. Cache the audio by hash of the input text in Supabase Storage.
