---
title: Connection pooling — Supavisor modes and limits
impact: CRITICAL
impactDescription: "Each serverless function invocation opens a new Postgres connection; without pooling, 100 concurrent Edge Functions exhaust the connection limit and crash the database"
tags: connections, pooling, supavisor, edge-functions, performance
---

# Connection pooling: Supavisor modes and limits

## Why pooling is mandatory for serverless

Postgres has a hard connection limit (25–500 depending on plan). Each Supabase Edge Function invocation, Next.js serverless function, or mobile client using the service key opens a **new** connection. Without pooling, 100 concurrent requests hit the connection ceiling and subsequent requests fail with `FATAL: remaining connection slots are reserved`.

## Supabase connection strings

Supabase provides two connection strings per project:

| String | Port | Mode | Use case |
|---|---|---|---|
| Direct | 5432 | None | Migrations, long-running scripts, pg_dump |
| Pooler (Transaction) | 6543 | Transaction | Edge Functions, serverless, high-concurrency |
| Pooler (Session) | 5432 on pooler host | Session | Prepared statements, `SET LOCAL`, advisory locks |

```
# Direct (migrations only)
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# Transaction pooler (Edge Functions / serverless)
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Session pooler (prepared statements)
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

## Edge Functions: always use transaction pooler

```ts
// In Edge Function — use pooler URL from env
const db = postgres(Deno.env.get('DATABASE_URL_POOLER')!);
```

## Transaction mode limitations

Transaction mode does **not** support:
- `SET` (session-level settings are reset after each transaction)
- Prepared statements (use `?` placeholders, not named prepared statements)
- `LISTEN` / `NOTIFY` (use Realtime instead)
- Advisory locks held across statements

## Monitoring connections

```sql
-- Current connection count by application
select application_name, count(*) 
from pg_stat_activity 
group by application_name 
order by count desc;

-- Approaching limit alert threshold
select count(*) as active,
       (select setting::int from pg_settings where name = 'max_connections') as max_conn
from pg_stat_activity;
```

## Client-side pool sizing (Drizzle/Prisma/postgres.js)

```ts
// postgres.js — keep pool small in serverless; each function instance has its own pool
const db = postgres(connectionString, {
  max: 5,          // max connections per instance
  idle_timeout: 20, // close idle connections quickly
  connect_timeout: 10,
});
```
