---
title: speech_to_text 7.4.0 — on-device speech recognition
impact: MEDIUM
impactDescription: "On-device STT; microphone permission required on both platforms; locale handling for multilingual apps"
tags: flutter, speech, stt, microphone, ai
---

# speech_to_text — on-device speech recognition

**Version:** 7.4.0  
**Platforms:** Android, iOS, macOS, Web, Windows

```yaml
dependencies:
  speech_to_text: ^7.4.0
```

## iOS permissions

```xml
<!-- ios/Runner/Info.plist -->
<key>NSMicrophoneUsageDescription</key>
<string>We use the microphone to convert your speech to text.</string>
<key>NSSpeechRecognitionUsageDescription</key>
<string>We use speech recognition to transcribe your voice input.</string>
```

## Android permissions

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.INTERNET"/>
```

## Initialize (once per app lifecycle)

```dart
import 'package:speech_to_text/speech_to_text.dart';

final SpeechToText _speech = SpeechToText();
bool _speechEnabled = false;

Future<void> initSpeech() async {
  _speechEnabled = await _speech.initialize(
    onError: (error) => print('STT error: ${error.errorMsg}'),
    onStatus: (status) => print('STT status: $status'),
  );
}
```

`initialize()` returns `false` if the device doesn't support speech recognition or the user denies the microphone permission. Always check before calling `listen()`.

## Start / stop listening

```dart
import 'package:speech_to_text/speech_recognition_result.dart';

// Start
await _speech.listen(
  onResult: (SpeechRecognitionResult result) {
    setState(() {
      _recognizedText = result.recognizedWords;
      _isFinal = result.finalResult;
    });
  },
  listenOptions: SpeechListenOptions(
    listenFor: const Duration(seconds: 30),  // max listening duration
    pauseFor: const Duration(seconds: 3),    // silence before auto-stop (iOS only)
    localeId: 'tr-TR',                       // locale — Turkish example
    cancelOnError: true,
    partialResults: true,                    // get words as they come in
  ),
  onSoundLevelChange: (level) => setState(() => _soundLevel = level),
);

// Stop gracefully (returns final result)
await _speech.stop();

// Cancel immediately (no final result)
await _speech.cancel();
```

## Check state

```dart
_speech.isListening   // bool — currently recording
_speech.isAvailable   // bool — device supports STT
_speech.isNotListening
```

## Available locales

```dart
final locales = await _speech.locales();
for (final locale in locales) {
  print('${locale.localeId} — ${locale.name}');
}
// 'tr-TR' — Turkish available on Android and iOS
```

## Riverpod integration

```dart
@riverpod
class SpeechState extends _$SpeechState {
  final _speech = SpeechToText();

  @override
  ({bool listening, String text}) build() => (listening: false, text: '');

  Future<void> start() async {
    final enabled = await _speech.initialize();
    if (!enabled) return;

    await _speech.listen(
      onResult: (result) {
        state = (listening: _speech.isListening, text: result.recognizedWords);
      },
      listenOptions: SpeechListenOptions(partialResults: true),
    );
    state = (listening: true, text: state.text);
  }

  Future<void> stop() async {
    await _speech.stop();
    state = (listening: false, text: state.text);
  }
}
```

## Combine with AI

```dart
// Common pattern: STT → Edge Function AI → response
final result = await ref.read(speechStateProvider.notifier).stopAndGetText();
if (result.isNotEmpty) {
  final aiResponse = await supabase.functions.invoke('ai-proxy', body: {'prompt': result});
  // Display response
}
```

See [../flutter/ai-integration.md](../flutter/ai-integration.md) for the Edge Function proxy pattern.

## Gotchas

- `initialize()` must be called before every `listen()` session after a cold start. Safe to call once in `initState`.
- **Android ignores `pauseFor`** — auto-stop timing on Android is system-controlled.
- Partial results (`partialResults: true`) deliver words as they're recognized — the final `result.finalResult == true` event gives the complete transcription.
- On iOS, speech recognition is done server-side by Apple; requires internet. On Android, it can be on-device (Pixel devices) or server-side depending on the device.
- `localeId` format: BCP-47 (`'tr-TR'`, `'en-US'`, `'de-DE'`).
