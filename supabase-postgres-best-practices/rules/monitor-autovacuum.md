---
title: Autovacuum tuning — prevent table bloat and stat staleness
impact: MEDIUM
impactDescription: "Default autovacuum settings are tuned for small tables; high-write tables accumulate bloat and stale planner stats that cause query regressions"
tags: monitoring, postgres, autovacuum, performance, maintenance
---

# Autovacuum tuning for high-write tables

## Why autovacuum matters

Every `UPDATE` in Postgres writes a new row version and marks the old one dead. `DELETE` marks rows dead. Autovacuum reclaims dead space and updates query planner statistics. If it can't keep up:

- Table bloat → wasted storage, slower sequential scans
- Stale stats → query planner picks wrong index or plan
- Table age → transaction ID wraparound (catastrophic if ignored)

## Default thresholds (often too conservative)

```sql
-- Trigger VACUUM when: dead_rows > 50 + 0.2 * live_rows
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.2  -- 20% of the table

-- Trigger ANALYZE when: changed_rows > 50 + 0.1 * live_rows  
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1
```

For a 10M-row table, vacuum only triggers after 2,000,050 dead rows. That's too late.

## Per-table overrides for high-write tables

```sql
-- More aggressive autovacuum for tables with heavy inserts/updates
alter table messages set (
  autovacuum_vacuum_scale_factor = 0.01,   -- trigger at 1% dead rows
  autovacuum_analyze_scale_factor = 0.01,
  autovacuum_vacuum_cost_delay = 2          -- less throttling
);

-- For append-only tables (logs, events), disable scale factor bloat trigger
alter table audit_logs set (
  autovacuum_vacuum_scale_factor = 0.001
);
```

## Check autovacuum activity

```sql
select relname, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze,
       n_dead_tup, n_live_tup,
       autovacuum_count, autoanalyze_count
from pg_stat_user_tables
order by n_dead_tup desc
limit 20;
```

## Manual vacuum when needed

```sql
-- Full table cleanup (does NOT lock with regular VACUUM)
vacuum analyze messages;

-- Reclaim disk space (locks table — maintenance window only)
vacuum full messages;
```

## Transaction ID wraparound — the failsafe

```sql
-- Tables approaching wraparound (danger zone > 1.5 billion)
select relname, age(relfrozenxid) as xid_age
from pg_class
where relkind = 'r'
order by xid_age desc
limit 10;
```

Supabase auto-vacuums aggressively before wraparound, but monitor this on high-volume projects. Supabase Dashboard → Database → Vacuum shows visual indicators.
