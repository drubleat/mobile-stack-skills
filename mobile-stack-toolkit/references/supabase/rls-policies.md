---
title: Row Level Security: recipes & performance
impact: CRITICAL
impactDescription: "Correct RLS is the difference between a secure app and a world-readable database; wrong patterns cause data breaches"
tags: supabase, rls, security, postgres, auth
---

# Row Level Security: recipes & performance

RLS is the difference between a secure app and a public database. Get these patterns right and most of your security is done.

## The mental model

- Enable RLS on **every** table in `public`. With RLS on and no policy, the table is **deny-all** (safe default). You then add policies that *grant* access.
- Policies are filters, per operation: **SELECT**, **INSERT**, **UPDATE**, **DELETE**.
- `USING` decides which existing rows are visible/affected (SELECT/UPDATE/DELETE). `WITH CHECK` validates the new row's values (INSERT/UPDATE).
- The publishable key + a user JWT runs *as that user*. The secret key (Edge Functions) **bypasses RLS entirely** — which is exactly why secret-key code must do its own authorization.

## The owner-based recipe (covers ~90% of tables)

```sql
alter table public.items enable row level security;

create policy "select own"
  on public.items for select
  using ( (select auth.uid()) = user_id );

create policy "insert own"
  on public.items for insert
  with check ( (select auth.uid()) = user_id );

create policy "update own"
  on public.items for update
  using ( (select auth.uid()) = user_id )
  with check ( (select auth.uid()) = user_id );

create policy "delete own"
  on public.items for delete
  using ( (select auth.uid()) = user_id );
```

## Performance: wrap `auth.uid()` in a subselect

Write `(select auth.uid())`, not bare `auth.uid()`. Wrapping it lets Postgres evaluate the function **once per query** (an initplan) instead of **once per row**. On large tables this is a massive difference. Same for any `auth.jwt()` call.

Also: **keep an index on `user_id`** and still pass an explicit `.eq('user_id', uid)` filter from the client where you can — don't make RLS do all the filtering work.

## Public-read, owner-write

```sql
create policy "anyone can read" on public.posts for select using ( true );
create policy "owner can write" on public.posts for insert
  with check ( (select auth.uid()) = user_id );
```

## Role / membership checks — use a SECURITY DEFINER function

Don't put multi-table joins inside a policy (slow, and recursive if the joined table also has RLS). Extract the check into a function:

```sql
create function public.is_org_member(org uuid) returns boolean
language sql security definer set search_path = '' stable as $$
  select exists (
    select 1 from public.memberships
    where org_id = org and user_id = (select auth.uid())
  );
$$;

create policy "members read org rows" on public.documents for select
  using ( public.is_org_member(org_id) );
```

`stable` + `security definer` + locked `search_path` is the safe, fast pattern. Put helper functions a client shouldn't call directly in a **private schema**.

## Common mistakes (the ones that cause incidents)

- **Forgot to enable RLS.** Table is wide open to anyone with the publishable key. Add `enable row level security` in the *same* migration as `create table`.
- **RLS enabled, no policies, "nothing works."** That's deny-all working as intended — you still need to add grant policies.
- **INSERT without `WITH CHECK`** → users can insert rows owned by *other* users. Owner inserts always need `with check (uid = user_id)`.
- **Bare `auth.uid()`** on big tables → per-row evaluation, slow queries. Wrap it.
- **Trusting RLS for paid gating.** RLS controls row access, not business rules like "is this user subscribed." Do entitlement checks in the Edge Function against `subscriptions` → [../monetization/entitlement-checks.md](../monetization/entitlement-checks.md).
- **Service key in the client.** It bypasses every policy above. It lives only in Edge Functions → [edge-functions.md](edge-functions.md).

## Verifying policies

Test as a real user from the client (or `set role` + `request.jwt.claims` in SQL). After writing policies, try to read/write another user's row and confirm it fails — a passing "negative test" is the proof RLS works.
