---
title: "RLS query performance — cache row-independent auth helpers"
impact: CRITICAL
impactDescription: "A scalar subquery can avoid repeated row-independent auth evaluation; verify the actual query plan"
tags: rls, performance, postgres, auth, query
---

# RLS query performance: wrap auth functions in `select`

## The rule

```sql
-- Baseline — may repeatedly evaluate the auth helper
create policy "owner access" on messages
  for select using (user_id = auth.uid());

-- Candidate optimization — check for InitPlan in EXPLAIN
create policy "owner access" on messages
  for select using (user_id = (select auth.uid()));
```

The uncorrelated `(select auth.uid())` subquery allows PostgreSQL to use an InitPlan for a row-independent value. This can reduce repeated helper work. Measure the plan and timing under the real application role; there is no universal speedup. Do not apply this caching pattern to a helper whose result depends on the current row.

## Apply to all auth functions

```sql
-- All of these should be wrapped:
(select auth.uid())
(select auth.jwt() ->> 'role')
(select auth.jwt() -> 'app_metadata' ->> 'org_id')
```

## Verify with EXPLAIN

```sql
explain analyze
select * from messages where user_id = (select auth.uid());
```

Look for `InitPlan` in the plan — this confirms the subquery is evaluated once. Do not infer a specific plan node from the SQL alone; compare actual plans and timings under an application role.

## Index alignment

Wrap isn't enough if the column lacks an index:

```sql
-- Index must exist on the filtered column
create index on messages(user_id);
```

With the wrapped `(select auth.uid())` and this index, Postgres can choose an index scan for the authenticated user's rows rather than a sequential scan of the whole table.

Reviewed 2026-10-21 against [Supabase RLS performance guidance](https://supabase.com/docs/guides/database/postgres/row-level-security).
