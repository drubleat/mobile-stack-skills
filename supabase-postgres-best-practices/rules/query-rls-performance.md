---
title: RLS query performance — always wrap auth functions in select
impact: CRITICAL
impactDescription: "Bare auth.uid() in RLS policies is re-evaluated per row; (select auth.uid()) evaluates once — can be 100x faster on large tables"
tags: rls, performance, postgres, auth, query
---

# RLS query performance: wrap auth functions in `select`

## The rule

```sql
-- ❌ WRONG — re-evaluated for every row scanned
create policy "owner access" on messages
  for select using (user_id = auth.uid());

-- ✅ CORRECT — evaluated once per query, cached
create policy "owner access" on messages
  for select using (user_id = (select auth.uid()));
```

The parenthesized `(select auth.uid())` is a scalar subquery. Postgres evaluates it **once** and treats the result as a constant throughout the query. Without it, `auth.uid()` is called as a volatile function per row — on a 100k-row table this can mean a 100x performance difference.

## Apply to all auth functions

```sql
-- All of these should be wrapped:
(select auth.uid())
(select auth.jwt() ->> 'role')
(select auth.jwt() -> 'user_metadata' ->> 'org_id')
```

## Verify with EXPLAIN

```sql
explain analyze
select * from messages where user_id = (select auth.uid());
```

Look for `InitPlan` in the plan — this confirms the subquery is evaluated once. A bare `auth.uid()` shows as a `FunctionScan` inline with each row.

## Index alignment

Wrap isn't enough if the column lacks an index:

```sql
-- Index must exist on the filtered column
create index on messages(user_id);
```

With the wrapped `(select auth.uid())` and this index, Postgres does an index scan for the authenticated user's rows rather than a sequential scan of the whole table.
