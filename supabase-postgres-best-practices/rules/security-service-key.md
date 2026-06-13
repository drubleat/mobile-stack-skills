---
title: Service key discipline — never expose sb_secret_ outside the server
impact: CRITICAL
impactDescription: "The service key bypasses all RLS; a single leaked key gives full read/write access to every table for everyone"
tags: security, keys, service-role, edge-functions, secrets
---

# Service key discipline: `sb_secret_` stays on the server

## The rule

```
sb_publishable_...  → client (Expo app, browser, public env vars)
sb_secret_...       → server only (Edge Functions, CI, migration scripts)
```

The `sb_secret_` (formerly `service_role`) key **bypasses all Row Level Security**. Anyone who holds this key can read, write, and delete every row in every table.

## Where it must NOT appear

```
❌ process.env.EXPO_PUBLIC_*   — bundled into the app binary
❌ app.config.js extra.*       — bundled into app.json
❌ Client-side JS/TS           — shipped to device
❌ GitHub repository (even private) — git history is forever
❌ Supabase Dashboard env vars marked "public"
```

## Where it belongs

```
✅ Supabase Edge Function secrets (SUPABASE_SERVICE_ROLE_KEY auto-injected)
✅ GitHub Actions secrets
✅ EAS Build secrets (server-side builds only, not EXPO_PUBLIC_*)
✅ Local .env files (in .gitignore)
```

## Edge Function: prefer user context over service key

```ts
// ✅ Better — user's own RLS context applies
const userClient = createClient(url, publishableKey, {
  global: { headers: { Authorization: req.headers.get('Authorization')! } },
});

// Use service key only when you genuinely need to bypass RLS
// (e.g., creating a profile for a new user, webhook processing)
const adminClient = createClient(url, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);
```

## Rotation procedure if leaked

1. Go to Supabase Dashboard → Settings → API
2. Click **Reveal** on the service role key → **Reset**
3. Update all Edge Function secrets and CI secrets immediately
4. Audit `pg_stat_activity` and recent auth logs for unauthorized access
5. If data may have been exfiltrated, notify affected users per your privacy policy

## Detection: audit for key exposure

```bash
# Check if service key appears anywhere in source
grep -r "service_role\|sb_secret_" --include="*.ts" --include="*.js" --include="*.env*" .
# Any hit outside of .env.local / Edge Function files is a problem
```
