---
title: Edge Functions: server-side TypeScript on Deno
impact: HIGH
impactDescription: "Every secret, AI call, and privileged action lives here; wrong patterns expose keys or bypass RLS"
tags: supabase, edge-functions, deno, secrets, ai-proxy
---

# Edge Functions

Server-side TypeScript on a Deno-based runtime, deployed globally. This is where every secret lives and every privileged action happens: AI proxying, the RevenueCat webhook, sending push, anything the client can't be trusted with.

## Anatomy

```ts
// supabase/functions/ai-proxy/index.ts
import { createClient } from 'jsr:@supabase/supabase-js@2';

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });

  // Identify the caller from their JWT (anon/publishable client passes it through)
  const authHeader = req.headers.get('Authorization')!;
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_ANON_KEY')!,             // acts AS the user → RLS applies
    { global: { headers: { Authorization: authHeader } } },
  );
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return new Response('Unauthorized', { status: 401, headers: cors });

  // ... do privileged work, call OpenAI with a SECRET key from env ...
  return new Response(JSON.stringify({ ok: true }), {
    headers: { ...cors, 'Content-Type': 'application/json' },
  });
});
```

Two client patterns inside a function:
- **As the user** (anon/publishable key + forwarded `Authorization`) → RLS still protects data. Use this for normal reads/writes on the user's behalf.
- **As admin** (`SUPABASE_SERVICE_ROLE_KEY` / `sb_secret_...`) → bypasses RLS. Use only for trusted writes like the subscriptions upsert in the webhook, and authorize manually.

## Local dev

```bash
supabase functions new ai-proxy
supabase functions serve ai-proxy --env-file ./supabase/.env   # hot reload
# call it: POST http://localhost:54321/functions/v1/ai-proxy
```

## Secrets

```bash
supabase secrets set OPENAI_API_KEY=sk-... GEMINI_API_KEY=...
supabase secrets set --env-file ./supabase/.env     # bulk
supabase secrets list
```

- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` are **auto-injected** — don't set them yourself.
- Secrets are available immediately, **no redeploy needed**.
- Never commit `supabase/.env`; gitignore it.

## Deploy

```bash
supabase functions deploy ai-proxy                 # one function
supabase functions deploy                          # all
supabase functions deploy webhook --no-verify-jwt  # for public webhooks (RevenueCat)
```

`--no-verify-jwt` (or `verify_jwt = false` in `config.toml`) is required for endpoints called by external services that don't carry a Supabase JWT — e.g. the RevenueCat webhook, which you instead authenticate with a shared secret header → [../monetization/webhooks-supabase.md](../monetization/webhooks-supabase.md).

## CORS (always needed for app calls)

```ts
const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};
```

Handle the `OPTIONS` preflight explicitly (as above) or every fetch from the app fails mysteriously.

## Background tasks & streaming

- Long work after responding: `EdgeRuntime.waitUntil(promise)` keeps the task alive after you return a response (e.g. fire-and-forget logging, follow-up writes).
- Streaming LLM tokens back to the app: return a `ReadableStream` (SSE). Details + RN consumption: [../ai/streaming.md](../ai/streaming.md).

## Pitfalls

- **Imports**: use `jsr:` / `npm:` / `https:` URL imports (Deno), not bare node `require`. Pin versions.
- **`Deno.env.get` returns undefined** → secret not set for that project, or you're testing locally without `--env-file`.
- **CORS/preflight failures** → missing `OPTIONS` handler.
- **Webhook 401** → you left JWT verification on; deploy with `--no-verify-jwt` and check your own shared-secret header instead.
- **Putting the service key in the app** → catastrophic; it only ever belongs here.

Deploying functions in CI → [../cicd/supabase-deploy.md](../cicd/supabase-deploy.md).
