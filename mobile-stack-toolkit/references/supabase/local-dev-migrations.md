---
title: Local dev & migrations workflow
impact: HIGH
impactDescription: "Schema-as-code prevents dashboard drift; missing this step breaks CI and teammates"
tags: supabase, migrations, local-dev, cli, postgres
---

# Local dev & migrations

Treat your database schema as **code in `supabase/migrations/`**. The dashboard is for inspection, not for making schema changes you care about.

## Local stack

```bash
npm i -g supabase          # or use `npx supabase` everywhere
supabase init              # creates supabase/ (config.toml, functions/, migrations/)
supabase start             # boots the full stack in Docker (db, auth, storage, studio, ...)
supabase status            # prints local URLs + keys
supabase stop              # stop (use `--no-backup` to also wipe local data)
```

`supabase start` needs Docker running. It gives you a complete local Supabase (Postgres + Auth + Storage + Edge Runtime + Studio at `localhost:54323`) so you can develop offline and test against real Postgres, not a mock.

## Migration workflow

The reliable loop:

```bash
# 1. Create an empty migration and write SQL by hand (preferred — explicit & reviewable)
supabase migration new create_profiles

# 2. Apply migrations to the local DB
supabase db reset          # drops local DB, re-runs ALL migrations + seed.sql (clean slate)

# 3. When happy, push to the remote project
supabase link --project-ref <ref>
supabase db push           # applies pending migrations to the linked remote DB
```

- **`supabase db reset`** is your friend locally: it guarantees the migrations actually reproduce the schema from scratch (catches "works because I clicked it in Studio" bugs).
- **`supabase migration new <name>`** then editing the SQL file is more predictable than auto-diffing. If you *did* change things in Studio, capture them with `supabase db diff -f <name>` to generate a migration from the difference.
- Keep a `supabase/seed.sql` for local test data; it runs on every `db reset`.

## Generating TypeScript types

Keep client types in sync with the schema:

```bash
supabase gen types typescript --local > lib/database.types.ts
# or from remote:
supabase gen types typescript --project-id <ref> > lib/database.types.ts
```

Then type the client: `createClient<Database>(...)`. Now `supabase.from('profiles')` is fully typed and a schema change that breaks the app shows up at compile time.

## Migration hygiene

- **One logical change per migration**, named descriptively (`add_streak_to_profiles`).
- **Never edit a migration that's already been pushed** to remote/shared — write a new one. Editing applied migrations desyncs environments.
- Migrations are timestamp-ordered by filename; don't reorder them.
- Commit migrations with the feature PR so reviewers see schema + code together.

## Common pitfalls

- **"It works locally but not in prod"** → you made a change in the remote Studio that isn't in a migration. Reconcile with `supabase db diff`.
- **`db push` fails on conflict** → remote has drift; pull/inspect before forcing. Don't `--force` blindly on a shared DB.
- **RLS forgotten in a migration** → every `create table` migration should also `alter table ... enable row level security;` and add policies in the same migration → [rls-policies.md](rls-policies.md).

CI auto-deploy of migrations → [../cicd/supabase-deploy.md](../cicd/supabase-deploy.md).
