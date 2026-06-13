---
title: Migration discipline — schema as code, safe changes
impact: HIGH
impactDescription: "Dashboard click-ops drift from the migration history; irreversible migrations without fallback plans cause outages"
tags: migrations, schema, postgres, supabase-cli, ci
---

# Migration discipline: schema as code

## The workflow

```bash
# 1. Make changes locally
supabase db diff --schema public -f add_messages_table

# 2. Review the generated migration
cat supabase/migrations/20260613120000_add_messages_table.sql

# 3. Apply locally
supabase db reset  # or supabase migration up

# 4. Commit and push — CI deploys via supabase db push
git add supabase/migrations/
git commit -m "feat: add messages table"
```

**Never** make schema changes in the Supabase Studio dashboard that aren't captured in a migration. The dashboard is read-only for schema purposes.

## Safe migration patterns

### Adding a nullable column (safe, no lock)

```sql
alter table messages add column read_at timestamptz;
```

### Adding a NOT NULL column (safe with default)

```sql
-- Two-step: add nullable, backfill, add constraint
alter table messages add column priority int;
update messages set priority = 0 where priority is null;
alter table messages alter column priority set not null;
alter table messages alter column priority set default 0;
```

One-step `ADD COLUMN ... NOT NULL DEFAULT ...` on Postgres 11+ is safe (the default is stored in catalog, not per-row) but avoid it on huge tables to be safe.

### Renaming a column (zero-downtime)

```sql
-- Step 1 (deploy A): add new column, sync with trigger
alter table users add column full_name text;
create trigger sync_full_name before insert or update on users
  for each row execute function sync_full_name_trigger();

-- Step 2 (deploy B): migrate reads to new column, remove old column
alter table users drop column name;
```

### Adding an index without downtime

```sql
create index concurrently idx_messages_user_created
  on messages(user_id, created_at desc);
```

### Dropping a column safely

```sql
-- Step 1: deploy code that no longer reads the column
-- Step 2 (separate migration): drop
alter table messages drop column legacy_field;
```

## Irreversible migrations checklist

Before any `DROP TABLE`, `DROP COLUMN`, or `TRUNCATE`:
- [ ] Application code no longer references the column/table
- [ ] Backup verified (Supabase PITR or pg_dump)
- [ ] Tested on staging
- [ ] Maintenance window or blue/green deploy in place
