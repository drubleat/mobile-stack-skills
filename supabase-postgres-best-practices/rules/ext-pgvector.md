---
title: "pgvector search, dimensions and RLS"
impact: HIGH
impactDescription: "Align embedding dimensions, index operators and tenant authorization"
tags: postgres, pgvector, rag, security
---

# pgvector search, dimensions and RLS

Enable the extension in the intended database; do not assume every project already has it. Choose a supported embedding model and track model/version/dimension with stored data. Changing the model may require re-embedding rather than just changing a model string.

Standard vector indexes support different dimension limits from halfvec indexes (commonly 2000 and 4000 respectively); verify the installed extension. Match the operator class to the distance metric. `<#>` returns negative inner product, so ordering semantics differ from a raw positive similarity value.

## Owned document search

This fragment assumes public.documents has id, user_id, content and a vector(1536) embedding, with RLS and suitable grants. Place the vector extension in the schema expected by the migration and qualify extension types/operators if using a different search_path.

```sql
create or replace function public.search_documents(
  query_embedding vector(1536), match_count integer default 10
) returns table(id uuid, content text, distance double precision)
language sql stable security invoker as $$
  select d.id, d.content, d.embedding <=> query_embedding
  from public.documents d
  where d.user_id = (select auth.uid())
  order by d.embedding <=> query_embedding
  limit least(greatest(coalesce(match_count, 10), 1), 50);
$$;
revoke all on function public.search_documents(vector, integer) from public, anon;
grant execute on function public.search_documents(vector, integer) to authenticated;
```

Authenticate and reserve quota before billable embedding generation. Validate content, returned dimensions and insert errors; derive user_id from verified identity. A service-role caller bypasses RLS, so authorization must still be explicit there.

Compare HNSW/IVFFlat using recall, latency, build time and memory on representative filtered queries. There is no universal one-million-row cutoff or 10x guarantee. Inspect plans, and account for approximate indexes returning too few rows under selective tenant filters.

For hybrid retrieval, explicitly ORDER BY the relevant score before each candidate LIMIT, rank those candidates, merge by document ID and order the final score with a stable tie-breaker. Window ranking alone does not guarantee the row order consumed by LIMIT. Apply the same tenant visibility to both keyword and vector candidate sets.

Reviewed 2026-10-21: [pgvector](https://github.com/pgvector/pgvector), [Supabase vector](https://supabase.com/docs/guides/database/extensions/pgvector).
