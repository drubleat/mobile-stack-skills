---
title: RLS policy patterns — USING vs WITH CHECK, multi-role
impact: CRITICAL
impactDescription: "Confusing USING and WITH CHECK leaves insert/update rows unprotected; missing policies on all operations silently allow writes"
tags: rls, security, postgres, policies, auth
---

# RLS policy patterns: USING vs WITH CHECK

## The distinction

| Clause | When evaluated | Controls |
|---|---|---|
| `USING` | On **read** (SELECT, DELETE) | Which existing rows are visible / deletable |
| `WITH CHECK` | On **write** (INSERT, UPDATE) | Which new/modified rows are allowed |

```sql
-- ❌ Common mistake: USING-only policy doesn't protect inserts
create policy "user owns row" on messages
  for all using (user_id = (select auth.uid()));

-- A user can insert a message with user_id = someone_else_id
-- because WITH CHECK defaults to the USING expression for UPDATE
-- but for INSERT it defaults to TRUE if no WITH CHECK is specified
-- on a FOR ALL policy... actually this depends on Postgres version.

-- ✅ Explicit is always safer
create policy "select own messages" on messages
  for select using (user_id = (select auth.uid()));

create policy "insert own messages" on messages
  for insert with check (user_id = (select auth.uid()));

create policy "update own messages" on messages
  for update using (user_id = (select auth.uid()))
             with check (user_id = (select auth.uid()));

create policy "delete own messages" on messages
  for delete using (user_id = (select auth.uid()));
```

## Enabling RLS — never forget this

```sql
alter table messages enable row level security;
-- Without this line, no policies take effect at all
```

## Multi-role patterns

### Admin bypass via JWT claim

```sql
create policy "admins see everything" on messages
  for select using (
    (select auth.jwt() ->> 'role') = 'admin'
    or user_id = (select auth.uid())
  );
```

### Team / org membership

```sql
create policy "team members see project" on project_files
  for select using (
    project_id in (
      select project_id from project_members
      where user_id = (select auth.uid())
    )
  );
```

### Public read, owner write

```sql
create policy "public read" on posts
  for select using (published = true or user_id = (select auth.uid()));

create policy "owner insert" on posts
  for insert with check (user_id = (select auth.uid()));

create policy "owner update" on posts
  for update using (user_id = (select auth.uid()))
             with check (user_id = (select auth.uid()));
```

## Test policies with SET ROLE

```sql
-- Simulate a specific user
set local role authenticated;
set local "request.jwt.claims" to '{"sub": "user-uuid-here", "role": "authenticated"}';
select * from messages; -- should only return that user's rows
```

## Checklist

- [ ] `enable row level security` on every public table
- [ ] All four operations (SELECT / INSERT / UPDATE / DELETE) have explicit policies or are intentionally blocked
- [ ] `auth.uid()` is always wrapped in `(select auth.uid())`
- [ ] No `service_role` key usage from the client
