---
title: Networking: Dio 5.x
impact: HIGH
impactDescription: "Dio interceptors handle auth token injection and refresh; wrong interceptor order causes race conditions on 401"
tags: flutter, networking, dio, http, interceptors
---

# Networking: dio

Version: `dio: ^5.9.2`

dio is the de-facto HTTP client for Flutter — it supports interceptors, cancellation, multipart uploads, and streaming out of the box. Use it for calls to Supabase Edge Functions and any external APIs your app calls directly.

## Setup

```dart
// lib/core/network/dio_client.dart
import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

Dio createDio({
  required String baseUrl,
  Duration timeout = const Duration(seconds: 30),
}) {
  final dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: timeout,
    sendTimeout: const Duration(seconds: 10),
    headers: {'Content-Type': 'application/json'},
  ));

  dio.interceptors.add(_AuthInterceptor());
  dio.interceptors.add(_RetryInterceptor(dio));

  return dio;
}

// Riverpod provider
final dioProvider = Provider<Dio>((ref) => createDio(
  baseUrl: '${const String.fromEnvironment("SUPABASE_URL")}/functions/v1',
));
```

## Auth interceptor

```dart
class _AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final session = Supabase.instance.client.auth.currentSession;
    if (session != null) {
      options.headers['Authorization'] = 'Bearer ${session.accessToken}';
    }
    options.headers['apikey'] = const String.fromEnvironment('SUPABASE_ANON_KEY');
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      try {
        await Supabase.instance.client.auth.refreshSession();
        // Retry the request with new token
        final newSession = Supabase.instance.client.auth.currentSession;
        if (newSession != null) {
          err.requestOptions.headers['Authorization'] = 'Bearer ${newSession.accessToken}';
          final response = await Dio().fetch(err.requestOptions);
          return handler.resolve(response);
        }
      } catch (_) {}
    }
    handler.next(err);
  }
}
```

## Retry interceptor

```dart
class _RetryInterceptor extends Interceptor {
  final Dio dio;
  _RetryInterceptor(this.dio);

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (_shouldRetry(err) && err.requestOptions.extra['retries'] == null) {
      err.requestOptions.extra['retries'] = 1;
      await Future.delayed(const Duration(seconds: 1));
      try {
        final response = await dio.fetch(err.requestOptions);
        return handler.resolve(response);
      } catch (e) {
        // Fall through to original error
      }
    }
    handler.next(err);
  }

  bool _shouldRetry(DioException err) =>
      err.type == DioExceptionType.connectionTimeout ||
      err.type == DioExceptionType.receiveTimeout ||
      (err.response?.statusCode ?? 0) >= 500;
}
```

## Multipart file upload

```dart
Future<String> uploadImage(String filePath, String userId) async {
  final formData = FormData.fromMap({
    'file': await MultipartFile.fromFile(
      filePath,
      filename: '${userId}_${DateTime.now().millisecondsSinceEpoch}.jpg',
      contentType: DioMediaType('image', 'jpeg'),
    ),
  });

  final response = await dio.post('/upload-image', data: formData);
  return response.data['url'] as String;
}
```

## Cancel requests

```dart
final cancelToken = CancelToken();

// Start request
dio.get('/long-running', cancelToken: cancelToken);

// Cancel (e.g., when widget is disposed)
cancelToken.cancel('Widget disposed');

// Check in catch
} on DioException catch (e) {
  if (CancelToken.isCancel(e)) return;  // Ignore cancellation
  rethrow;
}
```

## Error handling

```dart
class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);
}

T Function(DioException) _dioErrorMapper() => (e) {
  final statusCode = e.response?.statusCode ?? 0;
  final message = e.response?.data?['error'] as String? ?? e.message ?? 'Unknown error';
  throw ApiException(statusCode, message);
};

// Usage
try {
  final response = await dio.post('/ai-proxy', data: body);
  return response.data;
} on DioException catch (e) {
  _dioErrorMapper()(e);
}
```

## JSON deserialization

Dio parses JSON automatically when `Content-Type: application/json` is in the response. Response data is `Map<String, dynamic>` or `List`:

```dart
final response = await dio.get('/profile');
final profile = UserProfile.fromJson(response.data as Map<String, dynamic>);
```

## Logging in development

```dart
if (kDebugMode) {
  dio.interceptors.add(LogInterceptor(
    requestBody: true,
    responseBody: true,
    logPrint: (obj) => debugPrint(obj.toString()),
  ));
}
```

## Gotchas

- Set `receiveTimeout` long for AI requests (streaming can take 30–60s). The default 30s timeout may cut off long AI responses.
- `FormData` for file uploads is NOT JSON — don't set `Content-Type: application/json` for multipart requests; Dio sets the boundary header automatically.
- dio v5 renamed `DioError` to `DioException`. Old code using `DioError` won't compile on v5.
- Cancelling a request with `CancelToken` throws a `DioException` with `type == DioExceptionType.cancel`. Always check for cancellation before rethrowing.
