---
title: pgvector — vector similarity search for AI features
impact: HIGH
impactDescription: "pgvector enables semantic search, RAG, and recommendation features without a separate vector database; correct index type (hnsw vs ivfflat) is 10x throughput difference"
tags: pgvector, ai, embeddings, vector-search, postgres, extensions
---

# pgvector: vector similarity search

## Enable the extension

```sql
create extension if not exists vector;
```

Supabase enables pgvector by default on all projects.

## Schema: store embeddings alongside your data

```sql
create table documents (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  content     text not null,
  embedding   vector(1536),  -- OpenAI text-embedding-3-small dimension
  created_at  timestamptz not null default now()
);

-- RLS
alter table documents enable row level security;
create policy "users see own documents" on documents
  for select using (user_id = (select auth.uid()));
create policy "users insert own documents" on documents
  for insert with check (user_id = (select auth.uid()));
```

## Embedding dimensions by model

| Model | Dimension |
|---|---|
| OpenAI text-embedding-3-small | 1536 |
| OpenAI text-embedding-3-large | 3072 |
| OpenAI text-embedding-ada-002 (legacy) | 1536 |
| Gemini text-embedding-004 | 768 |
| Gemini text-multilingual-embedding-002 | 768 |

## Generate and store embeddings (Edge Function)

```ts
// Supabase Edge Function
import OpenAI from 'npm:openai@4';

const openai = new OpenAI({ apiKey: Deno.env.get('OPENAI_API_KEY') });

export async function embedText(text: string): Promise<number[]> {
  const res = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  });
  return res.data[0].embedding;
}

// Store
const embedding = await embedText(document.content);
await adminClient.from('documents').insert({
  user_id: userId,
  content: document.content,
  embedding: JSON.stringify(embedding), // pgvector accepts JSON array string
});
```

## Similarity search: three distance operators

```sql
-- Cosine distance (best for text embeddings — magnitude-independent)
embedding <=> '[0.1, 0.2, ...]'::vector

-- L2 (Euclidean) distance
embedding <-> '[0.1, 0.2, ...]'::vector

-- Inner product (for normalized embeddings = same as cosine)
embedding <#> '[0.1, 0.2, ...]'::vector
```

## Search via RPC (respects RLS)

```sql
create or replace function search_documents(
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  p_user_id uuid
)
returns table (id uuid, content text, similarity float)
language sql stable as $$
  select d.id, d.content,
         1 - (d.embedding <=> query_embedding) as similarity
  from documents d
  where d.user_id = p_user_id
    and 1 - (d.embedding <=> query_embedding) > match_threshold
  order by d.embedding <=> query_embedding
  limit match_count;
$$;
```

```ts
const { data } = await supabase.rpc('search_documents', {
  query_embedding: embedding,
  match_threshold: 0.78,
  match_count: 10,
  p_user_id: userId,
});
```

## Indexes: HNSW vs IVFFlat

| | HNSW | IVFFlat |
|---|---|---|
| Query speed | Faster | Slower |
| Build speed | Slower | Faster |
| Memory | More | Less |
| Accuracy | Higher | Lower |
| **Use when** | Production, < 1M rows | > 1M rows or RAM constrained |

```sql
-- HNSW (recommended for most Supabase projects)
create index on documents using hnsw (embedding vector_cosine_ops)
  with (m = 16, ef_construction = 64);

-- IVFFlat (for large datasets)
-- Must have data before building; lists ≈ sqrt(row_count)
create index on documents using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);
```

## Hybrid search (vector + keyword)

```sql
-- Combine vector similarity with full-text search using RRF
create or replace function hybrid_search(
  query_text text,
  query_embedding vector(1536),
  match_count int
)
returns table (id uuid, content text, score float)
language sql stable as $$
  with vector_results as (
    select id, content,
           row_number() over (order by embedding <=> query_embedding) as rank
    from documents
    limit match_count * 2
  ),
  text_results as (
    select id, content,
           row_number() over (order by ts_rank(to_tsvector('english', content),
                                               plainto_tsquery('english', query_text)) desc) as rank
    from documents
    where to_tsvector('english', content) @@ plainto_tsquery('english', query_text)
    limit match_count * 2
  )
  select coalesce(v.id, t.id) as id,
         coalesce(v.content, t.content) as content,
         (coalesce(1.0 / (60 + v.rank), 0) + coalesce(1.0 / (60 + t.rank), 0)) as score
  from vector_results v
  full outer join text_results t using (id)
  order by score desc
  limit match_count;
$$;
```
