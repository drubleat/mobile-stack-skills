---
title: Supabase deployment in CI
impact: HIGH
impactDescription: "Migrations must run before Edge Functions deploy; wrong order causes functions to reference tables that don't exist yet"
tags: cicd, supabase, migrations, edge-functions, deploy
---

# Supabase deployment in CI

Two things need to deploy when you push: **database migrations** and **Edge Functions**. These are separate commands and should run in that order.

## Migration deploy via CLI

```bash
# Authenticate (one-time per machine/CI environment)
supabase login      # interactive; for CI use SUPABASE_ACCESS_TOKEN env var instead

# Push all pending migrations to the linked project
supabase db push \
  --project-ref <YOUR_PROJECT_REF> \
  --password <YOUR_DB_PASSWORD>
```

In CI (GitHub Actions), set `SUPABASE_ACCESS_TOKEN` as an environment variable — the CLI picks it up automatically without needing `supabase login`:

```yaml
- uses: supabase/setup-cli@v1
  with:
    version: latest
- name: Deploy migrations
  run: supabase db push --project-ref ${{ secrets.SUPABASE_PROJECT_REF }} --password ${{ secrets.SUPABASE_DB_PASSWORD }}
  env:
    SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

## Edge Function deploy

```bash
# Deploy all functions
supabase functions deploy --project-ref <YOUR_PROJECT_REF>

# Deploy a single function
supabase functions deploy ai-proxy --project-ref <YOUR_PROJECT_REF>
```

Functions that receive webhook payloads (e.g. RevenueCat webhooks) must be deployed with `--no-verify-jwt`:

```bash
supabase functions deploy revenuecat-webhook \
  --no-verify-jwt \
  --project-ref <YOUR_PROJECT_REF>
```

In GitHub Actions, add after migrations:

```yaml
- name: Deploy Edge Functions
  run: supabase functions deploy --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
  env:
    SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

## Order matters

```
1. supabase db push          # schema changes first
2. supabase functions deploy # functions may depend on new schema
```

Never reverse this order. If a new Edge Function references a column that doesn't exist yet, it will error until migrations run.

## Staging vs production

Maintain two Supabase projects: `myapp-staging` and `myapp-production`. Use separate project refs in each branch:

```yaml
# Deploy to staging on PRs
- name: Deploy to staging
  if: github.event_name == 'pull_request'
  run: supabase db push --project-ref ${{ secrets.STAGING_PROJECT_REF }} ...

# Deploy to production on main
- name: Deploy to production
  if: github.ref == 'refs/heads/main'
  run: supabase db push --project-ref ${{ secrets.PROD_PROJECT_REF }} ...
```

## Migration safety

**Migrations are permanent.** `supabase db push` applies all unapplied migrations in order and records them in the `supabase_migrations.schema_migrations` table. A migration that has been applied cannot be "unapplied" without writing a new reverse migration.

Dangerous patterns to avoid in production migrations:
- `DROP TABLE` or `DROP COLUMN` without confirming the column is unused.
- `ALTER TABLE ... ALTER COLUMN ... TYPE` on a large table without a CONCURRENTLY strategy.
- Adding a `NOT NULL` column without a `DEFAULT` (will fail on tables with existing rows).

Safe patterns:
- Add columns with `DEFAULT` or as nullable first.
- Drop columns in a later migration after confirming nothing references them.
- Use `IF NOT EXISTS` and `IF EXISTS` in migrations to make them idempotent.

## Checking migration status

```bash
# See which migrations have been applied to a project
supabase migration list --project-ref <PROJECT_REF>
```

This lists local migrations and marks each one as `applied` or `pending`. Run this before deploying to confirm what's about to change.

## Secrets for Edge Functions

Secrets are not part of migrations — deploy them separately:

```bash
supabase secrets set OPENAI_API_KEY=sk-... --project-ref <PROJECT_REF>
supabase secrets set REVENUECAT_WEBHOOK_SECRET=... --project-ref <PROJECT_REF>
```

In CI, don't hardcode secrets in the workflow YAML — use GitHub Secrets and reference them:

```yaml
- name: Set Supabase secrets
  run: |
    supabase secrets set \
      OPENAI_API_KEY="${{ secrets.OPENAI_API_KEY }}" \
      REVENUECAT_WEBHOOK_SECRET="${{ secrets.RC_WEBHOOK_SECRET }}" \
      --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
  env:
    SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

Only run this step when secrets have actually changed — avoid re-setting all secrets on every push, as it creates noise in the audit log.
