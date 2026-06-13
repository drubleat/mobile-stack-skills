---
title: Secrets management & release checklist
impact: CRITICAL
impactDescription: "Secrets in env vars not source code; release checklist prevents submitting with debug keys or missing privacy strings"
tags: cicd, secrets, release, security, checklist
---

# Secrets management & release checklist

## Where to store secrets

Two systems, different scopes:

| Secret type | Store in | Accessed by |
|---|---|---|
| AI API keys (OpenAI, Gemini) | Supabase Edge Function secrets | Edge Function at runtime |
| RevenueCat API key | EAS Secrets (build-time) | app bundle via `EXPO_PUBLIC_RC_*` |
| Supabase URL + publishable key | EAS Secrets | app bundle via `EXPO_PUBLIC_SUPABASE_*` |
| App Store Connect API key | EAS Secrets or GitHub Secrets | EAS Submit / GitHub Actions |
| Supabase service role key | GitHub Secrets only | CI migration jobs (never in app) |
| Database password | GitHub Secrets only | CI `supabase db push` |
| EXPO_TOKEN | GitHub Secrets | GitHub Actions to trigger EAS |

**Rule**: secrets that end up in the app bundle are always `EXPO_PUBLIC_*`. Secrets that must not be in the bundle live in EAS Secrets (build-time env only) or GitHub Secrets (CI only).

## EAS Secrets

```bash
# Set per-project secrets (available in all builds for this project)
eas secret:create --scope project --name EXPO_PUBLIC_SUPABASE_URL --value "https://xxx.supabase.co"
eas secret:create --scope project --name EXPO_PUBLIC_SUPABASE_ANON_KEY --value "sb_publishable_..."

# Set per-environment (only available in specific build profiles)
eas secret:create --scope project --name REVENUE_CAT_IOS_KEY --value "appl_..." --env production

# List all project secrets
eas secret:list

# Delete a secret
eas secret:delete --name OLD_SECRET_NAME
```

EAS Secrets are injected as environment variables at build time. `EXPO_PUBLIC_*` ones are baked into the JS bundle (accessible at runtime). Non-`EXPO_PUBLIC_` ones are only accessible during the build process (for config plugins, native code generation).

## GitHub Secrets

GitHub → repo → Settings → Secrets and variables → Actions.

Use GitHub Secrets for values that CI jobs need but that must never reach the app:
- `SUPABASE_ACCESS_TOKEN` (to run `supabase` CLI commands)
- `SUPABASE_DB_PASSWORD` (for `supabase db push`)
- `EXPO_TOKEN` (to authenticate EAS CLI)

Never put service role keys or DB passwords in EAS Secrets — they'd be accessible in build logs.

## Manual release checklist

Before triggering a production build/submit:

### Code
- [ ] All feature branches merged and PRs closed.
- [ ] Version in `app.config.ts` bumped (semver: `1.2.0` → `1.3.0` for features, `1.2.0` → `1.2.1` for fixes).
- [ ] `CHANGELOG` or release notes drafted (you'll paste this into App Store Connect and Play Console).
- [ ] TypeScript passes: `npx tsc --noEmit`.

### Supabase
- [ ] All new migrations committed and reviewed.
- [ ] Migrations tested on a staging project (`supabase db reset` + `db push` to staging project ref).
- [ ] New Edge Functions deployed to staging and smoke-tested.
- [ ] RLS policies reviewed for any new tables.

### Store assets
- [ ] Screenshots updated if UI changed (especially first screenshot).
- [ ] App description updated if major feature added.
- [ ] What's New text (iOS) written (up to 4000 chars, shown under app listing during update period).

### Pre-build sanity
- [ ] Build runs locally in production profile: `eas build --profile production --platform ios --local` (optional but catches config issues fast).
- [ ] `eas.json` has the correct build profile settings.

### Post-submit
- [ ] Monitor TestFlight processing (5–15 min for iOS).
- [ ] Promote Internal → Closed/External on TestFlight; share with QA testers.
- [ ] Monitor Play Console's Pre-launch report for Android.
- [ ] After approval: roll out at 10–20% (Play) and monitor crash rate before full rollout.

## Rotating secrets

When rotating an API key (e.g. OpenAI key regenerated):
1. Create the new secret in Supabase with the new value: `supabase secrets set OPENAI_API_KEY=sk-new...`
2. Deploy Edge Functions to pick up the new secret: `supabase functions deploy`.
3. Verify the old key is revoked in the provider dashboard.
4. Update the corresponding EAS Secret if it was also stored there: `eas secret:create --name OPENAI_API_KEY --value sk-new...` (this overwrites).
