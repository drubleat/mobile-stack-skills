---
title: "Postgres RPC security and transactions"
impact: CRITICAL
impactDescription: "Prevent unauthorized access and incorrect state transitions"
tags: security, correctness
---

# Postgres RPC security and transactions

Use an invoker function for ordinary queries and atomic database operations. SECURITY DEFINER executes with its owner's permissions and can bypass RLS; it is not required just because a function writes data.

```sql
create or replace function public.get_user_stats()
returns jsonb language sql stable security invoker set search_path = '' as $$
  select jsonb_build_object('message_count', count(*))
  from public.messages where user_id = (select auth.uid());
$$;
revoke all on function public.get_user_stats() from public, anon;
grant execute on function public.get_user_stats() to authenticated;
```

RLS on the underlying table still applies, and callers need the corresponding table privileges. New functions normally grant EXECUTE to PUBLIC; revoking only from `anon` leaves inherited PUBLIC access intact.

For privileged functions, fix `search_path = ''`, qualify table/function names, derive caller identity, validate all inputs, and grant execution only to intended roles. Put internal helpers in an unexposed schema. Test unauthorized calls.

## Transactions and concurrency

Each PostgREST RPC call is its own transaction. A transaction-scoped advisory lock is released when the RPC returns; it cannot protect later HTTP calls from an Edge Function. Put all protected database work in the same function, or use an explicit lease/job queue for external work.

A transfer example must validate a positive amount, authorize the source account, lock both accounts in deterministic order, ensure sufficient balance and recipient existence, and enforce idempotency. Merely subtracting then adding inside a SECURITY DEFINER function allows unauthorized debits and negative transfers. Do not expose a simplified transfer snippet as production code.

Functions returning `SETOF` a table can be filtered with PostgREST. Preserve RLS and stable pagination; cap expensive queries. An exception rolls back database writes in that transaction, but cannot undo external API side effects.

## Sources

Reviewed 2026-10-20: [Supabase database functions](https://supabase.com/docs/guides/database/functions), [PostgREST transactions](https://docs.postgrest.org/en/stable/references/transactions.html).
