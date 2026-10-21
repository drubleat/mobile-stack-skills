---
title: "Gemini speech generation"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Gemini speech generation

Select a currently supported speech model separately from the text model. Server-side `generateContent` requests can use `config.responseModalities: ['AUDIO']` and `speechConfig.voiceConfig.prebuiltVoiceConfig`. Check the model guide for supported voices, languages, streaming and multi-speaker behavior; do not inherit these from a different model family.

```ts
const response = await ai.models.generateContent({
  model: speechModel,
  contents: [{ role: 'user', parts: [{ text: boundedText }] }],
  config: {
    responseModalities: ['AUDIO'],
    speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } } },
  },
});
const audio = response.candidates?.[0]?.content?.parts?.find(p => p.inlineData)?.inlineData;
if (!audio?.data) throw new Error('No audio returned');
const bytes = Uint8Array.from(atob(audio.data), char => char.charCodeAt(0));
```

Inspect `audio.mimeType` and the selected model's output specification. Raw PCM is not an MP3/WAV file: wrap it with a matching WAV header or encode it before playback. Match sample rate, bit depth and channels; do not rename raw bytes `.wav`. Check storage failures and return signed URLs for private speech. Use `expo-audio` or the project's existing maintained player and release its resources on disposal.

Cache only where appropriate, keying by model, voice, text and settings. User text/audio may contain personal information; use bounded retention and authorization. For interactive speech, evaluate the Live API's separate session/authentication contract. For audio transcription alternatives see [OpenAI audio](../openai/audio.md).

## Sources

Reviewed 2026-10-20: [speech generation](https://ai.google.dev/gemini-api/docs/speech-generation).
