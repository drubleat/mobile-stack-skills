---
name: supabase-postgres-best-practices
version: "1.0.0"
author: Eren Öz <eren@qoodly.com>
description: >-
  Production Postgres best practices for Supabase projects. Use this whenever
  the task involves writing or reviewing SQL, PostgREST queries, RLS policies,
  database schema, indexes, migrations, connection handling, or pg_* extensions
  (pgvector, pg_cron, pg_net, pgmq). Triggers on phrases like "write a query",
  "create an index", "RLS policy", "slow query", "connection pool", "vector
  search", "scheduled job", "database security", or any mention of Supabase
  Postgres internals. Covers query performance, connection management, security,
  schema design, concurrency, and observability — 20+ rules with code examples.
metadata:
  version: "1.0.0"
  author: "mobile-stack-toolkit"
---

# Supabase Postgres Best Practices

20+ production rules organized by category. Each rule file has an `impact` rating — load CRITICAL and HIGH rules first for any task, then drill into specifics.

## Rule categories

| Prefix | Category | Load when… |
|---|---|---|
| `query-*` | Query performance | Writing or reviewing SQL queries |
| `conn-*` | Connection management | Configuring clients or seeing connection errors |
| `security-*` | RLS + auth security | Writing RLS policies or auth logic |
| `schema-*` | Table & index design | Designing or altering tables |
| `lock-*` | Concurrency & locking | Seeing deadlocks or migration issues |
| `monitor-*` | pg_stat diagnostics | Investigating slow queries or high load |
| `ext-*` | Extensions (pgvector, pg_cron, pg_net, pgmq) | Using Postgres extensions |

## Quick routing

- **Slow query** → [query-indexes.md](rules/query-indexes.md), [query-rls-performance.md](rules/query-rls-performance.md), [monitor-pg-stat.md](rules/monitor-pg-stat.md)
- **Connection errors / pooling** → [conn-pooling.md](rules/conn-pooling.md), [conn-client-config.md](rules/conn-client-config.md)
- **RLS / security** → [security-rls-patterns.md](rules/security-rls-patterns.md), [security-auth-uid.md](rules/security-auth-uid.md), [security-service-key.md](rules/security-service-key.md)
- **Schema / migrations** → [schema-conventions.md](rules/schema-conventions.md), [schema-indexes.md](rules/schema-indexes.md), [lock-migrations.md](rules/lock-migrations.md)
- **Vector search** → [ext-pgvector.md](rules/ext-pgvector.md)
- **Scheduled jobs** → [ext-pg-cron.md](rules/ext-pg-cron.md)
- **HTTP from Postgres** → [ext-pg-net.md](rules/ext-pg-net.md)
- **Message queues** → [ext-pgmq.md](rules/ext-pgmq.md)
