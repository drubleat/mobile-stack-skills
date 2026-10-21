---
title: "RLS ownership, grants and negative tests"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# RLS ownership, grants and negative tests

Enable RLS on exposed application tables and grant only the necessary operations. RLS with no applicable policy denies ordinary roles; table owners and BYPASSRLS roles have different behavior. Test as actual anon/authenticated roles, not only the database owner.

```sql
alter table public.items enable row level security;
create policy own_items on public.items for all to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));
```

This assumes ordinary users may create/update/delete all mutable columns of their own item. Separate policies/grants for read-only or privileged fields. A row-owner check does not protect a server-managed `plan` column from its owner; use column grants, separate tables or carefully designed trusted mutations.

USING filters existing rows; WITH CHECK validates new row values. For ALL/UPDATE policies that omit WITH CHECK, PostgreSQL can reuse USING. Do not claim that omission universally grants ownership changes. Permissive policies combine with OR; a broad extra policy can defeat a restrictive-looking one. Review all policies and SQL grants together.

Wrapping row-independent `auth.uid()`/`auth.jwt()` in a scalar subquery can produce an initplan. Verify with EXPLAIN on realistic data. Index relevant owner/filter columns and pass query filters as well; no syntax guarantees an index scan for every workload.

Membership joins may be fine with suitable indexes. Use a SECURITY DEFINER helper only when necessary to avoid recursion or implement an intentional privilege boundary. Put it in a non-exposed schema, qualify names/fix search_path, validate caller/resource scope and restrict EXECUTE grants. STABLE alone does not make a function safe or fast.

Test own and other-user SELECT/INSERT/UPDATE/DELETE, ownership changes, unauthenticated calls, revoked memberships and forged user_metadata. Use trusted app_metadata/normalized tables for authorization, accounting for JWT freshness. RLS can express business access rules, but paid external actions also need server-side entitlement/quota checks. See [entitlements](../monetization/entitlement-checks.md).

## Sources

Reviewed 2026-10-20: [PostgreSQL policies](https://www.postgresql.org/docs/current/sql-createpolicy.html), [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security).
