---
title: "Dart Edge Function requests"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Dart Edge Function requests

Prefer `supabase.functions.invoke` in apps already using Supabase; it integrates the current auth session. A standalone `FunctionsClient(url, headers)` needs explicit token refresh and disposal. Headers are the second positional argument.

```dart
try {
  final response = await supabase.functions.invoke(
    'ai-proxy', body: {'userMessage': input},
  );
  if (response.status != 200 || response.data is! Map) {
    throw StateError('Invalid function response');
  }
  final text = response.data['text'];
  if (text is! String) throw StateError('Missing response text');
  return text;
} on FunctionException {
  rethrow; // translate expected status codes at the application boundary
}
```

Transport errors may have other types; handle them separately from function HTTP failures. Do not log full responses, tokens or user content. Use bounded deadlines/cancellation and avoid automatic mutation retries without idempotency. The client supports a region option; use the installed API's documented behavior rather than assuming region selection is unavailable.

For SSE, follow the [shared Flutter parser](../flutter/ai-integration.md), which buffers incomplete lines and UTF-8 across chunks. Splitting each network chunk by newline independently corrupts fragmented frames. Own and close the HTTP client and propagate cancellation.

Webhook endpoints may disable gateway JWT checking, but must authenticate provider requests in their handlers. Do not send mobile users directly to privileged webhook/worker endpoints or omit their required Authorization secret.

## Sources

Reviewed 2026-10-20: [FunctionsClient API](https://pub.dev/documentation/functions_client/latest/functions_client/FunctionsClient-class.html).
