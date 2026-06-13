---
title: AI integration in Flutter via Edge Functions
impact: HIGH
impactDescription: "Same edge proxy pattern as React Native — Supabase Edge Functions are the only place AI keys live"
tags: flutter, ai, edge-functions, supabase, openai, gemini
---

# AI integration in Flutter via Edge Functions

Flutter apps call the same Supabase Edge Function proxy as React Native apps — AI API keys never leave the server. See [../ai/edge-proxy-architecture.md](../ai/edge-proxy-architecture.md) for the Edge Function setup.

## HTTP client: dio

```yaml
dependencies:
  dio: ^5.9.2
```

```dart
// lib/core/network/dio_client.dart
import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

Dio createDio() {
  final dio = Dio(BaseOptions(
    baseUrl: '${const String.fromEnvironment("SUPABASE_URL")}/functions/v1',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 60),  // longer for AI responses
  ));

  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) async {
      final session = Supabase.instance.client.auth.currentSession;
      if (session != null) {
        options.headers['Authorization'] = 'Bearer ${session.accessToken}';
      }
      options.headers['apikey'] = const String.fromEnvironment('SUPABASE_ANON_KEY');
      handler.next(options);
    },
    onError: (error, handler) {
      // Handle auth errors — refresh token and retry
      if (error.response?.statusCode == 401) {
        Supabase.instance.client.auth.refreshSession();
      }
      handler.next(error);
    },
  ));

  return dio;
}
```

## Call AI Edge Function (non-streaming)

```dart
// features/ai/data/ai_repository.dart
class AiRepository {
  final Dio _dio;
  AiRepository(this._dio);

  Future<String> sendMessage(String prompt, List<Map<String, String>> history) async {
    final response = await _dio.post('/ai-proxy', data: {
      'prompt': prompt,
      'history': history,
    });

    return response.data['text'] as String;
  }
}
```

## Streaming responses

Supabase Edge Functions can stream Server-Sent Events (SSE). Dio handles streaming with `ResponseType.stream`:

```dart
Future<Stream<String>> streamMessage(String prompt) async {
  final response = await _dio.post<ResponseBody>(
    '/ai-proxy-stream',
    data: {'prompt': prompt},
    options: Options(responseType: ResponseType.stream),
  );

  return response.data!.stream
      .transform(const Utf8Decoder())
      .transform(const LineSplitter())
      .where((line) => line.startsWith('data: '))
      .map((line) {
        final json = line.substring(6);   // Remove "data: " prefix
        if (json == '[DONE]') return '';
        final decoded = jsonDecode(json) as Map<String, dynamic>;
        return decoded['delta'] as String? ?? '';
      })
      .where((delta) => delta.isNotEmpty);
}

// In widget with StreamBuilder
StreamBuilder<String>(
  stream: streamMessage(prompt),
  builder: (context, snapshot) {
    if (snapshot.hasData) {
      accumulatedText += snapshot.data!;
      return Text(accumulatedText);
    }
    return const CircularProgressIndicator();
  },
)
```

## Riverpod AI state

```dart
// features/ai/providers/chat_provider.dart
@riverpod
class ChatMessages extends _$ChatMessages {
  @override
  List<ChatMessage> build() => [];

  Future<void> sendMessage(String text) async {
    final userMsg = ChatMessage(role: 'user', content: text);
    state = [...state, userMsg];

    final repo = ref.read(aiRepositoryProvider);
    try {
      final response = await repo.sendMessage(text, state.toHistory());
      state = [...state, ChatMessage(role: 'assistant', content: response)];
    } catch (e) {
      // Remove optimistic user message on error
      state = state.where((m) => m != userMsg).toList();
      rethrow;
    }
  }

  void clear() => state = [];
}
```

## Structured output

For AI responses that should return structured data, parse JSON from the Edge Function response:

```dart
Future<RecipeResult> analyzeRecipe(Uint8List imageBytes) async {
  final base64Image = base64Encode(imageBytes);
  final response = await _dio.post('/ai-proxy', data: {
    'task': 'analyze_recipe',
    'image': base64Image,
  });

  return RecipeResult.fromJson(response.data as Map<String, dynamic>);
}
```

The Edge Function uses OpenAI's JSON Schema output or Gemini's `responseMimeType: 'application/json'` to guarantee parseable output. See [../ai/structured-output.md](../ai/structured-output.md).

## Image upload before AI analysis

```dart
import 'package:image_picker/image_picker.dart';

Future<String?> pickAndAnalyzeImage() async {
  final picker = ImagePicker();
  final image = await picker.pickImage(
    source: ImageSource.gallery,
    maxWidth: 1024,
    maxHeight: 1024,
    imageQuality: 85,
  );
  if (image == null) return null;

  final bytes = await image.readAsBytes();
  final result = await aiRepo.analyzeRecipe(bytes);
  return result.description;
}
```

Resize before sending — most Vision models don't benefit from images larger than 1024px, and smaller payloads are faster and cheaper.

## Error handling

```dart
try {
  final result = await aiRepo.sendMessage(prompt, history);
} on DioException catch (e) {
  if (e.response?.statusCode == 429) {
    // Rate limited — show "try again in X seconds"
  } else if (e.response?.statusCode == 402) {
    // Quota exceeded — show upgrade prompt
  } else {
    // Generic error
  }
}
```

The Edge Function returns 429 for quota exceeded and 402 for plan limit hits — let the client surface appropriate UI.
