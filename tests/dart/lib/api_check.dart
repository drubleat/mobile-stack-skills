import 'package:supabase/supabase.dart';
Future<void> checkApiShapes(SupabaseClient client) async {
  final response = await client.from('posts').select('*')
      .inFilter('status', ['active']).isFilter('deleted_at', null)
      .count(CountOption.exact);
  print(response.count);
  final functions = FunctionsClient('https://example.com', {'apikey': 'placeholder'});
  try { await functions.invoke('test', region: 'eu-west-1'); }
  on FunctionException { rethrow; }
  finally { await functions.dispose(); }
  final storage = SupabaseStorageClient('https://example.com', {'apikey': 'placeholder'});
  for (final file in await storage.from('test').list()) { print(file.metadata?['size']); }
}
