---
name: supabase-postgres-best-practices
description: Write, review, and tune Supabase Postgres queries, RLS policies, schemas, migrations, pooling, and database extensions. Use for database work, including slow queries and tenant isolation; not general mobile UI or SDK setup.
metadata:
  version: "1.1.0"
  author: "Eren Öz"
---

# Supabase Postgres Best Practices

Inspect schema, grants, policies, Postgres/extension versions, and query plans first. Read only the rules relevant to the task, typically one or two initially. Impact labels rank applicable issues; they do not require loading every CRITICAL/HIGH file.

| Task | Rules |
|---|---|
| Slow query | [Indexes](rules/query-indexes.md), [RLS performance](rules/query-rls-performance.md), [Diagnostics](rules/monitor-pg-stat.md) |
| Pagination / N+1 / RPC | [Pagination](rules/query-pagination.md), [N+1](rules/query-n-plus-one.md), [Functions](rules/query-functions-rpc.md) |
| Connection errors | [Pooling](rules/conn-pooling.md), [Client configuration](rules/conn-client-config.md) |
| Row security and roles | [Policies](rules/security-rls-patterns.md), [JWT claims](rules/security-auth-uid.md), [Server keys](rules/security-service-key.md) |
| File access | [Storage RLS](rules/security-storage-rls.md) |
| Schema change | [Conventions](rules/schema-conventions.md), [Indexes](rules/schema-indexes.md), [Migrations](rules/schema-migrations.md), [DDL locks](rules/lock-migrations.md) |
| Concurrency | [Advisory locks](rules/lock-advisory.md) |
| Maintenance | [Autovacuum](rules/monitor-autovacuum.md) |
| Vector search | [pgvector](rules/ext-pgvector.md) |
| Scheduled jobs | [pg_cron](rules/ext-pg-cron.md) |
| HTTP from Postgres | [pg_net](rules/ext-pg-net.md) |
| Queues | [pgmq](rules/ext-pgmq.md) |

Verify version-sensitive syntax in official Supabase/PostgreSQL/extension docs before applying it. Preserve the project's conventions and migration process. Test RLS as unauthenticated and authenticated users, including another tenant; owner/service-role queries cannot prove tenant isolation. Check permissions and failure paths of SECURITY DEFINER functions. Treat EXPLAIN ANALYZE as executing the statement, including writes and side effects.

For long work, retain only decisions, files, test results, and next actions in continuation notes. Do not copy the rules into an always-loaded instruction file. Do not deploy or reset a shared database without authorization covering that action.
