---
title: functions_client 2.6.2 — Supabase Edge Functions Dart client
impact: MEDIUM
impactDescription: "Invoke Edge Functions from Dart; handles auth headers and JSON serialization"
tags: dart, supabase, edge-functions
---

# functions_client — Supabase Edge Functions Dart client

**Version:** 2.6.2  
**Platforms:** all Dart platforms

```yaml
dependencies:
  functions_client: ^2.6.2
```

`functions_client` is the low-level Dart client for invoking Supabase Edge Functions. Most developers use it through `supabase` or `supabase_flutter`. Use this package directly only for non-Flutter Dart environments.

## Direct client

```dart
import 'package:functions_client/functions_client.dart';

final client = FunctionsClient(
  'https://your-project.supabase.co/functions/v1',
  {
    'Authorization': 'Bearer $userJwt',
    'apikey': 'sb_publishable_your_key',
  },
);
```

## Invoke a function

```dart
// Basic invocation
final response = await client.invoke('my-function', body: {'key': 'value'});
// response.data is Map<String, dynamic> or List

// With custom headers
final response = await client.invoke(
  'my-function',
  body: {'prompt': 'Hello'},
  headers: {'X-Custom-Header': 'value'},
  method: HttpMethod.post,  // default is POST
);
```

## Response handling

```dart
try {
  final response = await client.invoke('ai-proxy', body: {'prompt': input});

  // Check HTTP status
  if (response.status != 200) {
    final error = response.data?['error'] as String?;
    throw Exception('Function failed: $error');
  }

  final text = response.data?['text'] as String?;
  return text ?? '';
} on FunctionsException catch (e) {
  // FunctionsException wraps HTTP errors from the function
  print('Status: ${e.status}');
  print('Details: ${e.details}');
  rethrow;
}
```

## Streaming response (SSE)

For streaming AI responses, use the raw HTTP client instead:

```dart
import 'package:http/http.dart' as http;

final request = http.Request(
  'POST',
  Uri.parse('https://your-project.supabase.co/functions/v1/ai-stream'),
);
request.headers['Authorization'] = 'Bearer $jwt';
request.headers['apikey'] = anonKey;
request.headers['Content-Type'] = 'application/json';
request.body = jsonEncode({'prompt': input});

final streamedResponse = await http.Client().send(request);

await for (final chunk in streamedResponse.stream.transform(utf8.decoder)) {
  // Process SSE chunks
  for (final line in chunk.split('\n')) {
    if (line.startsWith('data: ')) {
      final data = line.substring(6);
      if (data == '[DONE]') return;
      final decoded = jsonDecode(data);
      yield decoded['delta'] as String? ?? '';
    }
  }
}
```

The `functions_client` package doesn't support streaming — use `http` directly for SSE.

## Via supabase / supabase_flutter (recommended)

```dart
// supabase_flutter (Flutter apps)
final response = await Supabase.instance.client.functions.invoke(
  'my-function',
  body: {'key': 'value'},
);

// supabase (Dart)
final response = await supabase.functions.invoke(
  'my-function',
  body: {'key': 'value'},
);
```

This is identical to using `functions_client` directly — `supabase`/`supabase_flutter` wires up the auth headers automatically.

## HttpMethod options

```dart
HttpMethod.get
HttpMethod.post     // default
HttpMethod.put
HttpMethod.patch
HttpMethod.delete
HttpMethod.head
```

```dart
// GET request to an Edge Function
final response = await client.invoke(
  'health-check',
  method: HttpMethod.get,
);
```

## Gotchas

- Edge Functions that accept webhook payloads (RevenueCat, Stripe) are deployed with `--no-verify-jwt` — they don't require an `Authorization` header. Omit it or it may cause validation issues.
- `FunctionsException` is thrown for non-2xx responses from the function itself, and for network errors. Always handle it.
- The function must return a valid response. If it throws an unhandled error in Deno, the client receives a 500 with `{ "error": "Internal Server Error" }`.
- Regional invocations aren't supported by this package — the default region is used. For latency optimization, deploy Edge Functions to the same region as your Supabase project.
