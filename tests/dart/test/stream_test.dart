import 'dart:convert';
import 'dart:io';
import 'package:test/test.dart';
import 'package:skill_snippet_check/stream.dart';
void main() {
  late HttpServer server;
  late Uri endpoint;
  setUp(() async {
    server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    endpoint = Uri.parse('http://127.0.0.1:${server.port}/ai-stream');
  });
  tearDown(() async { await server.close(force: true); });
  void serve(String body, {int status = 200}) {
    server.listen((request) async {
      await request.drain<void>();
      request.response.statusCode = status;
      request.response.headers.contentType = ContentType('text', 'event-stream');
      for (final byte in utf8.encode(body)) {
        request.response.add([byte]);
        await request.response.flush();
      }
      await request.response.close();
    });
  }
  test('fragmented UTF-8, CRLF and multi-line data', () async {
    serve('data: {"text":"İ"}\r\n\r\ndata: {\ndata: "text":"ğ"}\n\ndata: [DONE]\n\n');
    expect(await streamAI(endpoint, 'test-token', 'hello').toList(), ['İ', 'İğ']);
  });
  test('truncated response fails', () async {
    serve('data: {"text":"partial"}\n\n');
    await expectLater(streamAI(endpoint, 'token', 'hello').drain<void>(), throwsFormatException);
  });
  test('error frame fails', () async {
    serve('data: {"error":"provider_failed"}\n\n');
    await expectLater(streamAI(endpoint, 'token', 'hello').drain<void>(), throwsException);
  });
  test('invalid text shape fails', () async {
    serve('data: {"text":42}\n\n');
    await expectLater(streamAI(endpoint, 'token', 'hello').drain<void>(), throwsFormatException);
  });
  test('HTTP error fails', () async {
    serve('unauthorized', status: 401);
    await expectLater(streamAI(endpoint, 'token', 'hello').drain<void>(), throwsException);
  });
}
