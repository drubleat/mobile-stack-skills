---
title: ElevenLabs — TTS and Conversational AI in React Native
impact: MEDIUM
impactDescription: "ElevenLabs has two separate SDKs for two different use cases — using the wrong one for TTS costs time and produces no audio"
tags: elevenlabs, tts, text-to-speech, conversational-ai, ai, expo, react-native, audio
---

# ElevenLabs — React Native

ElevenLabs has **two completely separate SDKs** for two different things. Choose the right one:

| SDK | Package | Use case |
|---|---|---|
| **Conversational AI** | `@elevenlabs/react-native` | Real-time voice agent (WebRTC + LiveKit) — the user *talks to* an AI |
| **TTS (text-to-speech)** | ❌ No dedicated RN SDK | Stream audio from the REST API via an Edge Function proxy |

Most apps want TTS (read text aloud). That uses the REST API, not the `@elevenlabs/react-native` package.

---

## TTS via Edge Function proxy (recommended)

Never call the ElevenLabs REST API directly from the client — your API key would be exposed. Proxy through a Supabase Edge Function.

### Edge Function

```ts
// supabase/functions/tts/index.ts
import { serve } from 'https://deno.land/std@0.177.0/http/server.ts';

const ELEVENLABS_API_KEY = Deno.env.get('ELEVENLABS_API_KEY')!;
const VOICE_ID = 'EXAVITQu4vr4xnSDxMaL'; // "Sarah" — swap for your voice

serve(async (req) => {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  const { text } = await req.json();
  if (!text || typeof text !== 'string') {
    return new Response('text is required', { status: 400 });
  }

  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}/stream`,
    {
      method: 'POST',
      headers: {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json',
        Accept: 'audio/mpeg',
      },
      body: JSON.stringify({
        text,
        model_id: 'eleven_multilingual_v2',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
        },
      }),
    },
  );

  if (!response.ok) {
    const err = await response.text();
    return new Response(err, { status: response.status });
  }

  return new Response(response.body, {
    headers: {
      'Content-Type': 'audio/mpeg',
      'Transfer-Encoding': 'chunked',
    },
  });
});
```

Deploy:
```bash
supabase secrets set ELEVENLABS_API_KEY=sk_xxx
supabase functions deploy tts
```

### React Native client (expo-av)

```bash
npx expo install expo-av
```

```ts
// lib/tts.ts
import { Audio } from 'expo-av';
import { supabase } from './supabase';

export async function speak(text: string): Promise<void> {
  // Get a short-lived signed URL or call the Edge Function directly
  const { data, error } = await supabase.functions.invoke('tts', {
    body: { text },
    // responseType tells the client to return raw bytes
  });

  if (error) throw error;

  // The Edge Function returns audio/mpeg — write it to a temp file
  // then load with expo-av
  const { sound } = await Audio.Sound.createAsync(
    { uri: data },   // if your client returns a URL
    { shouldPlay: true },
  );

  await sound.playAsync();
  // Unload when done to free memory
  sound.setOnPlaybackStatusUpdate((status) => {
    if (status.isLoaded && status.didJustFinish) {
      sound.unloadAsync();
    }
  });
}
```

**Alternative — fetch as blob and play:**

```ts
import * as FileSystem from 'expo-file-system';
import { Audio } from 'expo-av';

export async function speakText(text: string) {
  const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL!;
  const anonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!;

  const res = await fetch(`${supabaseUrl}/functions/v1/tts`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${anonKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) throw new Error(`TTS failed: ${res.status}`);

  // Write the audio stream to a local file
  const tmpPath = FileSystem.cacheDirectory + 'tts_output.mp3';
  const buffer = await res.arrayBuffer();
  await FileSystem.writeAsStringAsync(
    tmpPath,
    Buffer.from(buffer).toString('base64'),
    { encoding: FileSystem.EncodingType.Base64 },
  );

  await Audio.setAudioModeAsync({ playsInSilentModeIOS: true });
  const { sound } = await Audio.Sound.createAsync(
    { uri: tmpPath },
    { shouldPlay: true },
  );
  sound.setOnPlaybackStatusUpdate((status) => {
    if (status.isLoaded && status.didJustFinish) sound.unloadAsync();
  });
}
```

---

## Available voices

Find voice IDs in the [ElevenLabs voice library](https://elevenlabs.io/voice-library) or via API:

```bash
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/voices
```

Common preset voices:
- `EXAVITQu4vr4xnSDxMaL` — Sarah
- `21m00Tcm4TlvDq8ikWAM` — Rachel
- `AZnzlk1XvdvUeBnXmlld` — Domi
- `pNInz6obpgDQGcFmaJgB` — Adam

---

## Models

| Model | Use case | Latency |
|---|---|---|
| `eleven_multilingual_v2` | Best quality, 29 languages | ~1–2s |
| `eleven_turbo_v2_5` | Low latency, English + 32 langs | ~300ms |
| `eleven_flash_v2_5` | Ultra-low latency (streaming) | ~75ms |

For mobile read-aloud where latency matters, use `eleven_turbo_v2_5`.

---

## Conversational AI SDK (voice agents)

Use `@elevenlabs/react-native` only when you want a **real-time voice agent** — user speaks, AI responds with voice.

```bash
npm install @elevenlabs/react-native
```

This package uses **LiveKit / WebRTC** under the hood. It requires a Conversational AI agent configured in the ElevenLabs dashboard.

```tsx
import { useConversation } from '@elevenlabs/react-native';

export function VoiceAgent({ agentId }: { agentId: string }) {
  const conversation = useConversation();

  async function startSession() {
    await conversation.startSession({ agentId });
  }

  async function endSession() {
    await conversation.endSession();
  }

  return (
    <View>
      <Text>Status: {conversation.status}</Text>
      <Button title="Start" onPress={startSession} />
      <Button title="End" onPress={endSession} />
    </View>
  );
}
```

---

## Flutter — TTS

Same pattern: Edge Function proxy → fetch audio bytes → play with `just_audio` or `audioplayers`:

```dart
import 'package:just_audio/just_audio.dart';

final player = AudioPlayer();

Future<void> speak(String text) async {
  final res = await supabase.functions.invoke('tts', body: {'text': text});
  // Supabase Flutter SDK returns data as bytes when Content-Type is audio/*
  // Write to temp file and load
  final tmpFile = File('${Directory.systemTemp.path}/tts.mp3');
  await tmpFile.writeAsBytes(res.data as List<int>);
  await player.setFilePath(tmpFile.path);
  await player.play();
}
```

---

## Gotchas

- **`@elevenlabs/react-native` is NOT for TTS** — it's only for real-time voice agents. Using it to play static text audio won't work.
- **Audio session on iOS** — call `Audio.setAudioModeAsync({ playsInSilentModeIOS: true })` before playback or audio is muted on silent mode.
- **API key in the Edge Function** — never hardcode the key client-side. ElevenLabs keys can be set to specific voices/limits but they still must stay server-side.
- **Character limits** — free tier is 10k characters/month. Track usage if you're calling TTS on user-generated content.
- **Turbo model for UX** — `eleven_multilingual_v2` introduces 1–2s latency before first audio byte. Use `eleven_turbo_v2_5` for better perceived responsiveness.
