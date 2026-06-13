---
title: pg_stat diagnostics — find slow queries and bottlenecks
impact: MEDIUM-HIGH
impactDescription: "pg_stat_statements identifies the exact queries consuming the most time; without it you're guessing at optimizations"
tags: monitoring, performance, postgres, pg-stat, diagnostics
---

# pg_stat diagnostics: find slow queries and bottlenecks

## Enable pg_stat_statements (Supabase enables this by default)

```sql
-- Verify it's active
select * from pg_extension where extname = 'pg_stat_statements';
```

## Top queries by total time

```sql
select query,
       calls,
       round(total_exec_time::numeric, 2) as total_ms,
       round(mean_exec_time::numeric, 2) as mean_ms,
       round(stddev_exec_time::numeric, 2) as stddev_ms,
       rows
from pg_stat_statements
order by total_exec_time desc
limit 20;
```

## Top queries by mean time (slowest individual calls)

```sql
select query,
       calls,
       round(mean_exec_time::numeric, 2) as mean_ms,
       round(max_exec_time::numeric, 2) as max_ms
from pg_stat_statements
where calls > 10  -- ignore one-offs
order by mean_exec_time desc
limit 20;
```

## Sequential scans on large tables (missing index candidates)

```sql
select relname as table,
       seq_scan,
       seq_tup_read,
       idx_scan,
       n_live_tup as live_rows
from pg_stat_user_tables
where n_live_tup > 10000
  and seq_scan > idx_scan
order by seq_tup_read desc
limit 15;
```

## Table bloat (dead rows from UPDATE/DELETE)

```sql
select relname as table,
       n_dead_tup as dead_rows,
       n_live_tup as live_rows,
       round(100 * n_dead_tup::numeric / nullif(n_live_tup + n_dead_tup, 0), 1) as dead_pct,
       last_autovacuum
from pg_stat_user_tables
where n_dead_tup > 1000
order by dead_pct desc;
```

If `dead_pct` is > 20%, trigger a manual VACUUM:

```sql
vacuum analyze messages;
```

## Active connections and wait events

```sql
select pid, state, wait_event_type, wait_event, query_start,
       now() - query_start as duration, left(query, 80) as query
from pg_stat_activity
where state != 'idle'
order by duration desc;
```

## Reset statistics (after a schema change or index addition)

```sql
select pg_stat_reset();
select pg_stat_statements_reset();
```

Wait at least 1 hour after reset before reading stats — you need representative traffic.

## Supabase Dashboard shortcut

Dashboard → Database → Query Performance shows `pg_stat_statements` data with a UI. Useful for quick checks; use raw SQL for custom filtering.
