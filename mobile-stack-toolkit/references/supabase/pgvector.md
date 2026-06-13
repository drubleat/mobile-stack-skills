---
title: pgvector — semantic search & RAG in Supabase
impact: HIGH
impactDescription: "pgvector eliminates a separate vector database for AI apps; semantic search and RAG features can be built entirely within Supabase with RLS applied to embeddings"
tags: pgvector, ai, embeddings, vector-search, supabase, rag
---

# pgvector: semantic search & RAG in Supabase

pgvector is enabled by default on all Supabase projects. It lets you store and search vector embeddings in Postgres — same RLS, same client, no separate vector DB.

## Schema: embeddings table

```sql
create extension if not exists vector;

create table documents (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  content     text not null,
  embedding   vector(1536),  -- OpenAI text-embedding-3-small
  metadata    jsonb not null default '{}',
  created_at  timestamptz not null default now()
);

alter table documents enable row level security;
create policy "user owns docs" on documents
  for all using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

create index on documents using hnsw (embedding vector_cosine_ops)
  with (m = 16, ef_construction = 64);
```

## Embedding dimensions

| Model | Dimension |
|---|---|
| OpenAI `text-embedding-3-small` | 1536 |
| OpenAI `text-embedding-3-large` | 3072 |
| Gemini `text-embedding-004` | 768 |

## Edge Function: embed and store

```ts
// supabase/functions/embed-document/index.ts
import OpenAI from 'npm:openai@4';

const openai = new OpenAI({ apiKey: Deno.env.get('OPENAI_API_KEY') });

Deno.serve(async (req) => {
  const { content, metadata } = await req.json();
  const authHeader = req.headers.get('Authorization')!;

  const { data: [{ embedding }] } = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: content,
  });

  const userClient = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_ANON_KEY')!,
    { global: { headers: { Authorization: authHeader } } }
  );

  const { data, error } = await userClient.from('documents').insert({
    content,
    embedding: JSON.stringify(embedding),
    metadata: metadata ?? {},
  }).select('id').single();

  if (error) return Response.json({ error: error.message }, { status: 500 });
  return Response.json({ id: data.id });
});
```

## Edge Function: semantic search via RPC

```sql
-- Create the search function in a migration
create or replace function search_documents(
  query_embedding vector(1536),
  match_threshold float default 0.75,
  match_count int default 10
)
returns table (id uuid, content text, metadata jsonb, similarity float)
language sql stable security invoker as $$
  select d.id, d.content, d.metadata,
         1 - (d.embedding <=> query_embedding) as similarity
  from documents d
  where d.user_id = (select auth.uid())
    and 1 - (d.embedding <=> query_embedding) > match_threshold
  order by d.embedding <=> query_embedding
  limit match_count;
$$;
```

```ts
// Search Edge Function
Deno.serve(async (req) => {
  const { query } = await req.json();

  // 1. Embed the query
  const { data: [{ embedding }] } = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: query,
  });

  // 2. Search via RPC (RLS applied — user sees own docs only)
  const { data: results } = await userClient.rpc('search_documents', {
    query_embedding: embedding,
    match_threshold: 0.75,
    match_count: 5,
  });

  return Response.json({ results });
});
```

## Mobile client: call search

```ts
// React Native
const search = async (query: string) => {
  const { data } = await supabase.functions.invoke('search-documents', {
    body: { query },
  });
  return data.results;
};
```

## RAG pattern (search → prompt)

```ts
// In Edge Function: retrieve context, build prompt, call LLM
const results = await searchDocuments(queryEmbedding);
const context = results.map(r => r.content).join('\n\n');

const response = await openai.responses.create({
  model: 'gpt-5.4-mini',
  instructions: 'Answer using only the provided context.',
  input: `Context:\n${context}\n\nQuestion: ${query}`,
});
```

## Deep reference

For SQL-level detail on HNSW vs IVFFlat indexes, hybrid search (vector + keyword), and dimension choices → [supabase-postgres-best-practices: ext-pgvector](../../supabase-postgres-best-practices/rules/ext-pgvector.md).
