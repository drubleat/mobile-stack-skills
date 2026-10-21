---
title: "pgvector retrieval with ownership and budgets"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# pgvector retrieval with ownership and budgets

Enable the vector extension in the intended project. Store an owner/tenant identifier, content, metadata, embedding and embedding-model/version information. Apply RLS and test cross-user access. Model changes can require re-embedding and a dimension/index migration; do not mix embeddings from incompatible spaces.

Choose a currently supported embedding model and explicitly align dimensions with the column and index type. Standard vector/halfvec index limits differ; a 3072-dimensional embedding cannot simply replace a 1536-dimensional vector in the existing index. Verify installed pgvector capabilities.

Embedding ingestion order:

1. Verify the user and resource ownership before any billable provider call.
2. Validate and bound content/metadata and reserve usage quota.
3. Generate embeddings with the configured model/dimensions.
4. Insert `user_id` from the verified identity alongside content/embedding; check errors and support idempotent retries.

Search follows the same auth/quota ordering. Use a SECURITY INVOKER RPC with qualified objects, restricted grants, owner/RLS filtering and a bounded match count. Rank with the matching distance operator and index, using a stable tie-breaker where needed. Approximate indexing plus selective filters can reduce recall; measure results and plans on realistic tenant distributions.

RAG retrieves only authorized chunks, bounds context and marks retrieved content as untrusted data. Prompts do not replace access controls. Preserve source IDs for citations and handle missing/low-confidence retrieval without inventing evidence. Never let a user-supplied tenant ID bypass the authenticated tenant scope.

## Sources

Reviewed 2026-10-20: [Supabase vector](https://supabase.com/docs/guides/database/extensions/pgvector), [pgvector index limits](https://github.com/pgvector/pgvector).
