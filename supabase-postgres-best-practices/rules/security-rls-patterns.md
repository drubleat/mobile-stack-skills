---
title: "RLS policies: existing rows and new values"
impact: CRITICAL
impactDescription: "Prevent unauthorized access and incorrect state transitions"
tags: security, correctness
---

# RLS policies: existing rows and new values

RLS must be enabled and SQL privileges must permit the operation. With RLS enabled and no applicable policy, ordinary roles are denied. Superusers, BYPASSRLS roles, and normally the table owner bypass it.

`USING` checks existing rows for SELECT, UPDATE, and DELETE. `WITH CHECK` checks new values for INSERT and UPDATE. For `FOR ALL` and `FOR UPDATE`, omitting `WITH CHECK` reuses `USING`; it does **not** silently permit arbitrary inserts. Explicit clauses make intent easier to review.

```sql
alter table public.messages enable row level security;
create policy "read own" on public.messages for select to authenticated
  using (user_id = (select auth.uid()));
create policy "insert own" on public.messages for insert to authenticated
  with check (user_id = (select auth.uid()));
create policy "update own" on public.messages for update to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));
create policy "delete own" on public.messages for delete to authenticated
  using (user_id = (select auth.uid()));
```

For business roles use server-controlled claims such as `app_metadata.role`, not the top-level JWT `role` used by PostgREST and never user-editable `user_metadata`. Claims can be stale until the JWT refreshes; immediate revocation requires a database lookup or another server check. Multiple permissive policies combine with OR, so inspect all policies and grants.

Membership subqueries can be appropriate; use a narrowly scoped private SECURITY DEFINER helper only when necessary to avoid recursion or expensive checks. Lock its search path and grants. See [JWT claims](security-auth-uid.md) and [function security](query-functions-rpc.md).

## Verify as actual application roles

Use real fixture UUIDs inside an explicit transaction:

```sql
begin;
set local role authenticated;
select set_config('request.jwt.claims',
  '{"sub":"00000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
select * from public.messages;
rollback;
```

Test own-row access, other-user access, owner-changing updates, forged role claims, missing JWT, and no-policy denial. Expected write errors need savepoints or independent transactions. Tests run as the owner/service role do not validate RLS.

## Sources

Reviewed 2026-10-20: [PostgreSQL CREATE POLICY](https://www.postgresql.org/docs/current/sql-createpolicy.html), [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security).
