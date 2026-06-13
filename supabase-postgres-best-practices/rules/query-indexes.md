---
title: Index design for Supabase / PostgREST queries
impact: CRITICAL
impactDescription: "Missing indexes on filter/sort columns cause sequential scans; a single missing index on a 1M-row table turns a 2ms query into a 2s query"
tags: indexes, performance, postgres, query, schema
---

# Index design for Supabase / PostgREST queries

## Always index FK columns

Every foreign key column should have an index. Postgres does **not** auto-create indexes on FK columns (unlike primary keys).

```sql
-- profiles.user_id references auth.users(id)
create index on profiles(user_id);

-- messages.conversation_id references conversations(id)
create index on messages(conversation_id);
```

## Composite indexes: column order matters

Put the most selective column first. For range + equality queries, put the equality column first:

```sql
-- Query: WHERE user_id = $1 AND created_at > $2 ORDER BY created_at DESC
create index on messages(user_id, created_at desc);
```

## Partial indexes for soft-delete or status filters

```sql
-- Only index active records — index stays small as deleted rows accumulate
create index on subscriptions(user_id) where status = 'active';
create index on posts(created_at) where deleted_at is null;
```

## GIN indexes for JSONB and full-text search

```sql
-- JSONB column queries
create index on events using gin(metadata);

-- Full-text search
create index on products using gin(to_tsvector('english', name || ' ' || description));
```

## Covering indexes (INCLUDE) to avoid heap fetches

```sql
-- Include all columns the query needs — avoids heap fetch entirely
create index on messages(user_id, created_at desc)
  include (content, read_at);
```

## What to avoid

- **Over-indexing**: every write pays index maintenance. Keep unused indexes dropped.
- **Indexing low-cardinality columns alone**: `CREATE INDEX ON users(is_active)` is useless if 99% of rows are `true`.
- **Ignoring VACUUM**: dead tuples bloat indexes; ensure autovacuum is running.

## Detect missing indexes

```sql
-- Top sequential scans on large tables — candidates for indexing
select relname, seq_scan, seq_tup_read, idx_scan
from pg_stat_user_tables
where seq_scan > 100
order by seq_tup_read desc
limit 20;
```
