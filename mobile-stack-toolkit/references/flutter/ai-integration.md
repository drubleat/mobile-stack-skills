---
title: "Flutter AI proxy and SSE consumption"
impact: HIGH
impactDescription: "Avoid incompatible APIs and unsafe mobile integration defaults"
tags: mobile, integration, correctness
---

# Flutter AI proxy and SSE consumption

Use the same request/response contract as the server: `POST /ai-stream`, JSON `{ "userMessage": "..." }`, SSE `data: {"text":"..."}` frames, terminal `data: [DONE]`, and `data: {"error":"..."}` for stream failures. See [proxy](../ai/edge-proxy-architecture.md) and [streaming](../ai/streaming.md).

## Dart HTTP streaming

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Stream<String> streamAI(Uri endpoint, String jwt, String prompt) async* {
  final client = http.Client();
  try {
    final request = http.Request('POST', endpoint)
      ..headers.addAll({'Authorization': 'Bearer $jwt', 'Content-Type': 'application/json'})
      ..body = jsonEncode({'userMessage': prompt});
    final response = await client.send(request);
    if (response.statusCode != 200) throw Exception('Stream request failed');
    final frame = <String>[];
    var accumulated = '';
    await for (final line in response.stream.transform(utf8.decoder).transform(const LineSplitter())) {
      if (line.isEmpty) {
        if (frame.isEmpty) continue;
        final payload = frame.join('\n');
        frame.clear();
        if (payload == '[DONE]') return;
        final data = jsonDecode(payload) as Map<String, dynamic>;
        if (data['error'] != null) throw Exception('Generation failed');
        final delta = data['text'];
        if (delta is! String) throw const FormatException('Invalid text frame');
        accumulated += delta;
        yield accumulated;
      } else if (line.startsWith('data:')) {
        final value = line.substring(5);
        frame.add(value.startsWith(' ') ? value.substring(1) : value);
      }
    }
    throw const FormatException('Stream ended without completion');
  } finally {
    client.close();
  }
}
```

The decoder and LineSplitter retain partial UTF-8/line chunks. The frame buffer supports multi-line SSE data. This parser targets the application contract above; it is not a general reconnecting EventSource client. Bound accumulated output and frame sizes for your app.

Create and retain the stream in a controller or widget lifecycle callback; do not recreate it in every `build`. `StreamBuilder<String>` receives a `Stream<String>`, not `Future<Stream<String>>`. Render the cumulative snapshot directly; appending in the builder duplicates text on rebuilds. Tie disposal/cancel actions to the HTTP request so stalled connections close promptly, and do not transparently retry a charged request without idempotency.

For non-streaming requests, invoke the proxy with `userMessage` and check response type/status. Handle 401, 403, 429, and retryable service failures. Structured responses still require local shape/domain validation. Keep conversation ownership and paid-action authorization on the server.

## Sources

Reviewed 2026-10-20: [Dart HTTP](https://pub.dev/packages/http), [Dart LineSplitter](https://api.dart.dev/dart-convert/LineSplitter-class.html).
