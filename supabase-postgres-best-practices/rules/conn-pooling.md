---
title: "Connection pooling and transaction scope"
impact: HIGH
impactDescription: "Match database guarantees to the operation and verify with real roles"
tags: postgres, supabase, correctness
---

# Connection pooling and transaction scope

The Supabase HTTP client uses the Data API; each request is not a new direct database connection owned by the mobile app. Pool sizing applies when a server uses a direct Postgres driver. Never put database credentials in a mobile client.

Choose the Dashboard-provided connection string for the network/runtime: direct or session pooling for session-dependent work, transaction pooling for short serverless transactions. Check IPv4/IPv6 reachability and the project's actual limits instead of assuming fixed connection counts.

```ts
// Server-side postgres.js example, for a transaction-pooler connection.
const db = postgres(connectionString, {
  prepare: false,
  max: 2,
  idle_timeout: 20,
  connect_timeout: 10,
});
```

Set the pool size from aggregate process/instance concurrency. A module singleton reuses a pool within one instance; hundreds of instances still multiply connections. Close short-lived script clients and bound query timeouts.

Transaction pooling does not preserve session state across transactions. Use `SET LOCAL` and transaction-scoped advisory locks inside one explicit transaction. Session advisory locks and LISTEN require a persistent session; NOTIFY can be issued transactionally but delivery/listening has separate semantics. Driver prepared-statement support must match the configured pooler; for postgres.js against Supavisor transaction mode disable automatic preparation rather than changing SQL to `?` placeholders.

Use [advisory-lock guidance](lock-advisory.md) for scope. A lock taken in one RPC does not cover an HTTP call made after that RPC returns.

## Sources

Reviewed 2026-10-20: [Supabase connections](https://supabase.com/docs/guides/database/connecting-to-postgres), [postgres.js](https://github.com/porsager/postgres).
