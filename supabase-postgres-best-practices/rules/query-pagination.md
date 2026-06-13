---
title: Pagination — keyset over offset for large tables
impact: HIGH
impactDescription: "OFFSET N scans and discards N rows on every page; keyset pagination is O(1) regardless of page depth"
tags: pagination, performance, postgres, postgrest, queries
---

# Pagination: keyset over offset

## Why offset pagination degrades

```sql
-- Page 100 of 20 rows: Postgres scans and discards 2000 rows
SELECT * FROM messages ORDER BY created_at DESC LIMIT 20 OFFSET 2000;
```

At page 500, you're throwing away 10,000 rows per request.

## Keyset (cursor) pagination

```sql
-- First page
SELECT id, content, created_at
FROM messages
WHERE user_id = $1
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Next page — pass last row's (created_at, id) as cursor
SELECT id, content, created_at
FROM messages
WHERE user_id = $1
  AND (created_at, id) < ($last_created_at, $last_id)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

The compound `(created_at, id)` cursor breaks ties when multiple rows share the same timestamp.

## Supabase client keyset pattern

```ts
// First page
const { data } = await supabase
  .from('messages')
  .select('id, content, created_at')
  .eq('user_id', userId)
  .order('created_at', { ascending: false })
  .order('id', { ascending: false })
  .limit(20);

const cursor = data?.at(-1); // { id, created_at }

// Next page
const { data: nextPage } = await supabase
  .from('messages')
  .select('id, content, created_at')
  .eq('user_id', userId)
  .or(`created_at.lt.${cursor.created_at},and(created_at.eq.${cursor.created_at},id.lt.${cursor.id})`)
  .order('created_at', { ascending: false })
  .order('id', { ascending: false })
  .limit(20);
```

## When offset is acceptable

- **Admin dashboards** with small tables (< 10k rows)
- **Page number UI** where users jump to page 50 and performance isn't critical
- **Supabase `.range(from, to)`** maps to LIMIT/OFFSET — fine for these cases

## Required index

```sql
-- Composite index matching the ORDER BY
create index on messages(user_id, created_at desc, id desc);
```
