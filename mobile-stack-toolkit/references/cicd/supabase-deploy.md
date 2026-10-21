---
title: "Supabase deployment in CI"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Supabase deployment in CI

Use a reviewed CLI version and a protected release job with `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD` and the selected project ref provided via the CI secret/variable environment. Link before commands that operate on the linked database:

```bash
supabase link --project-ref "$SUPABASE_PROJECT_REF"
supabase migration list
supabase db push --dry-run
# After checks and the release gate:
supabase db push
supabase functions deploy --project-ref "$SUPABASE_PROJECT_REF"
```

`db push` and `migration list` do not take the function deployment `--project-ref` flag. Avoid inserting secret expressions into shell source; pass environment variables and quote expansions. Serialize deployments to each environment. PR checks use local/test databases without production credentials.

Use expand/migrate/contract: deploy backward-compatible additions, then new consumers, then remove old fields only after old mobile binaries stop depending on them. Database-first is useful for additions, but there is no universally safe fixed ordering for destructive changes. A failed multi-step release needs an explicit forward-fix or rollback plan.

`ALTER COLUMN TYPE` has no generic `CONCURRENTLY` option. Review lock duration, table size and rewrite behavior. Use validated backfills and staged constraints. `IF NOT EXISTS` is not a substitute for checking the expected existing schema.

A third-party webhook may need gateway JWT verification disabled; authenticate its documented secret/signature in the handler before reading or writing data. This does not make every function public. See [webhooks](../monetization/webhooks-supabase.md).

Set function secrets separately using the CLI's environment-file support or the dashboard. Keep temporary files out of Git and logs. Never embed provider keys in mobile build variables. Validate staging with real RLS roles and monitor after release.

## Sources

Reviewed 2026-10-20: [CLI reference](https://supabase.com/docs/reference/cli/introduction), [migrations](https://supabase.com/docs/guides/deployment/database-migrations).
