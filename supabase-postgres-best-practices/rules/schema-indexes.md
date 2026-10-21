---
title: "Index strategy — types, maintenance, and pitfalls"
impact: HIGH
impactDescription: "Wrong index type (btree vs gin vs brin) misses queries entirely; duplicate or unused indexes slow down writes with no read benefit"
tags: indexes, schema, performance, postgres, maintenance
---

# Index strategy: types, maintenance, and pitfalls

## Index type selection

| Use case | Index type | Example |
|---|---|---|
| Equality / range on scalar | `btree` (default) | `created_at`, `user_id`, `status` |
| JSONB keys/values | `gin` | `metadata @> '{"key": "val"}'` |
| Array containment | `gin` | `tags @> ARRAY['flutter']` |
| Full-text search | `gin` on `tsvector` | `to_tsvector('english', body)` |
| Very large append-only tables | `brin` | `log_entries(created_at)` |
| Vector similarity | `hnsw` or `ivfflat` | See [ext-pgvector.md](ext-pgvector.md) |

## Concurrent index creation (zero downtime)

```sql
-- Takes a lock that blocks writes; ordinary reads continue
create index on messages(user_id);

-- Allows ordinary writes, but still takes locks and can wait/fail
create index concurrently on messages(user_id);
```

`CONCURRENTLY` usually reduces write disruption but does not mean lock-free. It cannot run inside a transaction block; check the migration runner. Failed builds may leave invalid indexes that need cleanup.

## Removing unused indexes

```sql
-- Indexes never used in queries
select schemaname, tablename, indexname, idx_scan
from pg_stat_user_indexes
where idx_scan = 0
  and indexname not like '%pkey%'
order by pg_relation_size(indexrelid) desc;
```

Treat zero scans as a candidate for investigation, not permission to drop. Check stats resets, unique/constraint dependencies, replica workloads, and infrequent critical queries.

## Duplicate index detection

```sql
select indrelid::regclass as table,
       array_agg(indexrelid::regclass) as indexes,
       array_agg(indkey) as keys
from pg_index
group by indrelid, indkey
having count(*) > 1;
```

## Index bloat

Dead rows from UPDATEs and DELETEs leave behind index entries. VACUUM removes them, but bloated indexes waste disk and slow scans:

```sql
-- List index sizes (size alone does not measure bloat)
select indexrelid::regclass as index,
       pg_size_pretty(pg_relation_size(indexrelid)) as size
from pg_stat_user_indexes
order by pg_relation_size(indexrelid) desc
limit 20;

-- Rebuild with reduced blocking; concurrent rebuilds still take locks
reindex index concurrently idx_messages_user_id;
```

## Expression indexes

```sql
-- Query: WHERE lower(email) = lower($1)
create index on users(lower(email));

-- Query: WHERE (metadata->>'status') = 'active'
create index on events((metadata->>'status'));
```
