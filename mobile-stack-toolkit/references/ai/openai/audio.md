---
title: "OpenAI transcription, speech, and Realtime"
impact: HIGH
impactDescription: "Use the provider API correctly while preserving server authorization"
tags: ai, mobile, api
---

# OpenAI transcription, speech, and Realtime

Choose the API by interaction: uploaded recording → transcription; text → speech; ongoing two-way conversation → Realtime. Resolve the model and supported formats from current documentation. Keep long-lived provider credentials on the server.

## Uploaded recording

```ts
const form = await req.formData();
const file = form.get('audio');
if (!(file instanceof File) || file.size === 0 || file.size > maxUploadBytes) {
  return new Response('Invalid audio', { status: 400 });
}
const transcript = await openai.audio.transcriptions.create({
  model: transcriptionModel,
  file,
  response_format: 'json',
});
```

Authenticate and enforce request limits before parsing large uploads. Supported response formats differ by model; do not list Whisper-only formats as valid for every transcription model. Match actual file MIME/container; a device `file://` URL is not an upload.

## Speech output

```ts
const speech = await openai.audio.speech.create({
  model: speechModel,
  voice: 'coral',
  input: validatedText,
  response_format: 'mp3',
});
return new Response(speech.body, {
  headers: { ...cors, 'Content-Type': 'audio/mpeg' },
});
```

Use a voice and output format supported by the configured model, and disclose synthesized voices as required by the provider. In Expo use `expo-audio` for new work, with the installed SDK's playback API; `Audio.Sound.createAsync` belongs to legacy `expo-av`, not `expo-audio`. Avoid base64 transport when binary streaming is available.

## Realtime client connections

A server relay is one option. Another is an authenticated server endpoint issuing a short-lived, scoped provider client credential, allowing the device to connect directly over supported WebRTC/WebSocket transport. Never return the server API key. Authorize session creation, set session constraints, rate-limit issuance, and enforce sensitive tool actions on the server.

Use the current Realtime session/client-secret API rather than the deprecated beta session example. Check the installed SDK and chosen model's session schema. React Native also needs an appropriate WebRTC native module and development build when using WebRTC.

Billing depends on model and input/output modalities; it is not universally priced per session minute. Check pricing and measure real traffic. Test interruption, permission denial, reconnect, app backgrounding, device audio routing, and session expiry.

## Sources

Reviewed 2026-10-20: [Audio guide](https://developers.openai.com/api/docs/guides/audio), [Realtime WebRTC](https://developers.openai.com/api/docs/guides/realtime-webrtc).
