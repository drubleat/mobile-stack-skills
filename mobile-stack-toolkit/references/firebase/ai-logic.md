---
title: Firebase AI Logic — call Gemini directly from mobile with App Check security
impact: HIGH
impactDescription: "Firebase AI Logic lets Flutter/RN apps call Gemini with App Check token authentication — a legitimate alternative to Supabase Edge proxy for Firebase-native stacks"
tags: firebase, ai, gemini, flutter, react-native, app-check, firebase-ai
---

# Firebase AI Logic (firebase_ai / firebase-ai)

Firebase AI Logic (previously Vertex AI for Firebase) lets you call Gemini models directly from your mobile app. Firebase App Check handles security — requests without a valid attestation token are rejected server-side, so you don't need your own backend proxy.

## When to use Firebase AI Logic vs Supabase Edge proxy

| | Firebase AI Logic | Supabase Edge proxy |
|---|---|---|
| **Security model** | App Check token (platform attestation) | Server-side JWT + your own auth |
| **Backend required** | No — Firebase handles it | Yes — Edge Function needed |
| **Stack fit** | Firebase-standalone or Firebase-primary | Supabase-primary stack |
| **Cost visibility** | Firebase console / Google Cloud billing | OpenAI/Gemini billing direct |
| **Custom logic** | Limited (client-side only) | Full control (server-side) |
| **Secret API keys** | Managed by Google | Your Edge Function secrets |
| **Use when** | Firebase-native app, rapid prototype | Production Supabase stack |

For Supabase-primary stacks, prefer the edge proxy → [ai/edge-proxy-architecture.md](../ai/edge-proxy-architecture.md). Firebase AI Logic is the right choice when you're already Firebase-standalone and don't want to add a Supabase backend just for AI.

## Setup — Flutter

```yaml
# pubspec.yaml
dependencies:
  firebase_core: ^4.0.0
  firebase_auth: ^6.0.0
  firebase_app_check: ^0.3.2+2
  firebase_ai: ^3.0.0  # replaces firebase_vertexai
```

**CRITICAL**: Run CLI provisioning first (does NOT happen via `flutterfire configure`):

```bash
npx -y firebase-tools@latest init ailogic
```

```dart
// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  
  // App Check must be initialized before AI Logic
  await FirebaseAppCheck.instance.activate(
    androidProvider: kDebugMode ? AndroidProvider.debug : AndroidProvider.playIntegrity,
    appleProvider: kDebugMode ? AppleProvider.debug : AppleProvider.appAttest,
  );

  // Sign in (anonymous is fine for AI-only apps)
  await FirebaseAuth.instance.signInAnonymously();
  
  runApp(const MyApp());
}
```

### Text generation

```dart
import 'package:firebase_ai/firebase_ai.dart';

class AIService {
  late final GenerativeModel _model;

  AIService() {
    // Use GoogleAI (Gemini Developer API) — free tier + pay-as-you-go
    // Switch to FirebaseAI.vertexAI() for enterprise scale (requires Blaze plan)
    _model = FirebaseAI.googleAI().generativeModel(
      model: 'gemini-2.5-flash',  // check firebase.google.com/docs/ai-logic/models for latest
    );
  }

  Future<String> generateText(String prompt) async {
    final response = await _model.generateContent([Content.text(prompt)]);
    return response.text ?? '';
  }

  // Streaming
  Stream<String> generateStream(String prompt) async* {
    final stream = _model.generateContentStream([Content.text(prompt)]);
    await for (final chunk in stream) {
      yield chunk.text ?? '';
    }
  }
}
```

### Multi-turn chat

```dart
final chat = _model.startChat(history: []);

Future<String> sendMessage(String message) async {
  final response = await chat.sendMessage(Content.text(message));
  return response.text ?? '';
}
```

### Vision (image + text)

```dart
Future<String> analyzeImage(Uint8List imageBytes, String prompt) async {
  final response = await _model.generateContent([
    Content.multi([
      DataPart('image/jpeg', imageBytes),
      TextPart(prompt),
    ]),
  ]);
  return response.text ?? '';
}
```

### Structured output (JSON schema)

```dart
final model = FirebaseAI.googleAI().generativeModel(
  model: 'gemini-2.5-flash',
  generationConfig: GenerationConfig(
    responseMimeType: 'application/json',
    responseSchema: Schema.object(properties: {
      'sentiment': Schema.enumString(enumValues: ['positive', 'negative', 'neutral']),
      'confidence': Schema.number(),
      'summary': Schema.string(),
    }),
  ),
);
```

## Setup — React Native

```bash
npx expo install @react-native-firebase/firebase-ai
```

```ts
import firebaseAI from '@react-native-firebase/firebase-ai';
import appCheck from '@react-native-firebase/app-check';

// After App Check init (see app-check.md)
const ai = firebaseAI();
const model = ai.generativeModel({ model: 'gemini-2.5-flash' });

// Text generation
const { response } = await model.generateContent('What is Flutter?');
console.log(response.text());

// Streaming
const stream = model.generateContentStream('Explain React Native in 3 sentences');
for await (const chunk of stream.stream) {
  process.stdout.write(chunk.text());
}
```

## Model selection (always verify current models)

Firebase AI Logic model names change — don't hardcode stale ones:

```bash
# Check current supported models
npx -y firebase-tools@latest ai:models:list
```

Use **Remote Config** to store the model name so you can update it without a release:

```dart
// In Firebase Remote Config: key = "ai_model_name", value = "gemini-2.5-flash"
final remoteConfig = FirebaseRemoteConfig.instance;
await remoteConfig.fetchAndActivate();
final modelName = remoteConfig.getString('ai_model_name');

final model = FirebaseAI.googleAI().generativeModel(model: modelName);
```

## Pricing tiers

| Provider | Free tier | Pay-as-you-go |
|---|---|---|
| Gemini Developer API (`googleAI`) | Yes (rate limited) | Yes |
| Vertex AI Gemini API (`vertexAI`) | No (Blaze plan required) | Yes — enterprise SLAs |

Default to `googleAI()`. Switch to `vertexAI()` only if you need > 1M RPM or enterprise data residency guarantees.

## App Check enforcement (required for production)

Enable enforcement in Firebase Console → App Check → AI Logic → Enable enforcement. Without enforcement, App Check is monitoring-only and doesn't block unauthorized calls.

See [app-check.md](app-check.md) for full App Check setup.
