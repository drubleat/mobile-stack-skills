---
title: "Dio requests, refresh, and retry boundaries"
impact: HIGH
impactDescription: "Avoid incompatible APIs and unsafe mobile integration defaults"
tags: mobile, integration, correctness
---

# Dio requests, refresh, and retry boundaries

Configure timeouts, cancellation, and a trusted base URL. Inject user tokens only for your backend origin; an absolute URL must not receive credentials just because it uses the same Dio instance.

```dart
final dio = Dio(BaseOptions(
  baseUrl: backendUrl,
  connectTimeout: const Duration(seconds: 10),
  receiveTimeout: const Duration(seconds: 30),
));
dio.interceptors.add(InterceptorsWrapper(onRequest: (options, handler) {
  if (options.uri.origin != Uri.parse(backendUrl).origin) {
    return handler.reject(DioException(requestOptions: options,
      error: 'Unexpected authenticated request origin'));
  }
  final session = Supabase.instance.client.auth.currentSession;
  if (session != null) options.headers['Authorization'] = 'Bearer ${session.accessToken}';
  handler.next(options);
}));
```

Prefer the auth SDK's refresh behavior. If an explicit 401 recovery is required, serialize refresh with a shared future, retry at most once, preserve the original request/client configuration, and stop on a second 401. Do not create an unconfigured `Dio()` to retry a request, or start an unawaited refresh and assume the failed request succeeded.

Retry only replay-safe operations. GET/HEAD can often retry transient failures with bounded exponential backoff and jitter. A timeout after POST may mean the server completed the action; use a server-enforced idempotency key before retrying purchases, AI jobs, or uploads. Recreate consumed streams/FormData for retries. Honor cancellation and `Retry-After` where applicable.

Use `CancelToken` when requests belong to a disposed screen. Map errors after checking whether the response body is a map, string, or empty; do not blindly index arbitrary bodies. Treat cancellation separately from failure.

Dio constructs multipart boundaries for FormData. Set content type from the actual file format. Use `ResponseType.stream` for streaming and parse frames across network chunk boundaries; see [AI integration](ai-integration.md).

Avoid request-header/body logging for authenticated traffic. Redact authorization, cookies, API keys, personal content, and signed URLs even in development shared logs.

## Sources

Reviewed 2026-10-20: [Dio documentation](https://pub.dev/packages/dio).
