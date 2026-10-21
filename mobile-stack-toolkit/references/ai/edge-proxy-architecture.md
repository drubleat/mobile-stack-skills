---
title: "Edge Function proxy — why and how"
impact: CRITICAL
impactDescription: "Keep long-lived provider secrets server-side; authorize and bound paid operations"
tags: ai, security, edge-functions, openai, gemini, proxy
---

# Edge Function proxy — why and how

## Keep long-lived provider secrets on the server

Use the project's existing trusted backend. Supabase Edge Functions are the examples here, not a required provider migration. Firebase AI Logic with enforced App Check and short-lived scoped Realtime credentials can support direct client connections without embedding provider secrets.

## Why

**Security.** An API key embedded in a mobile app is a public key. APKs are trivially decompiled; IPAs are extractable. Anyone who finds your key gets your billing account. A leaked OpenAI key can run up thousands of dollars in hours.

**Rate limiting & quotas.** You cannot enforce per-user limits from the client side. The Edge Function checks `usage_counters`, enforces daily quotas, and can apply tier-based limits (free users get 10 calls/day, Pro users get 500).

**Cost control.** Log every request's token count. Set hard limits. Kill a runaway feature from the server without a store release.

**Prompt control.** The system prompt is server-side code, not a string in the app. Do not treat prompt secrecy as a security boundary; enforce authorization in code.

**Provider flexibility.** The mobile app calls `POST /functions/v1/ai-proxy`. If you swap GPT for Gemini next month, you change one Edge Function — every app version, everywhere, immediately.

## The shape

```
Mobile app  →  POST /functions/v1/ai-proxy  →  Supabase Edge Function
                                                      │
                                          verify JWT (is this a real user?)
                                          check quota (usage_counters)
                                          build prompt (system + user input)
                                          call model API (secret key in Deno.env)
                                          log usage
                                                      │
                                              ← response (or stream)
```

## Integration sketch (not a complete request handler)

Add method/content-type checks, bounded body validation before quota reservation, timeouts, provider failure/refusal handling and redacted logging. The snippet omits those HTTP concerns; see [guardrails](guardrails.md).

```ts
// supabase/functions/ai-proxy/index.ts
import { createClient } from 'jsr:@supabase/supabase-js@2';
import OpenAI from 'npm:openai';

const openai = new OpenAI({ apiKey: Deno.env.get('OPENAI_API_KEY') });
const cors = { 'Access-Control-Allow-Origin': '*',
               'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type' };

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });

  // 1. Auth
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_ANON_KEY')!,
    { global: { headers: { Authorization: req.headers.get('Authorization')! } } },
  );
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return new Response('Unauthorized', { status: 401, headers: cors });

  // 2. Server-only client; apply assets/sql/ai-quota.sql first.
  const adminClient = createClient(Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
    { auth: { persistSession: false, autoRefreshToken: false } });
  const { data: quota, error: quotaError } = await adminClient.rpc('increment_ai_usage', {
    p_user_id: user.id, p_limit: 10, // trusted server policy; never from request JSON
  });
  if (quotaError || typeof quota?.over_limit !== 'boolean')
    return new Response('Quota unavailable', { status: 503, headers: cors });
  if (quota.over_limit) return new Response('Rate limit exceeded', { status: 429, headers: cors });

  // 3. Call model
  const { userMessage } = await req.json();
  const response = await openai.responses.create({
    model: Deno.env.get('OPENAI_TEXT_MODEL')!,
    instructions: 'You are a helpful assistant.',
    input: userMessage,
    max_output_tokens: 1024,
  });

  return new Response(JSON.stringify({ text: response.output_text }), {
    headers: { ...cors, 'Content-Type': 'application/json' },
  });
});
```

## Calling from the mobile client

```ts
// lib/ai.ts
export async function askAI(message: string): Promise<string> {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) throw new Error('Sign in required');
  const res = await fetch(`${SUPABASE_URL}/functions/v1/ai-proxy`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ userMessage: message }),
  });
  if (!res.ok) throw new Error(await res.text());
  const { text } = await res.json();
  return text;
}
```

The client has no idea which model is behind it, what the system prompt is, or what API key is used. That's the point.

## When you don't use Supabase

If your backend is Firebase / custom server / another BaaS: same pattern, different host. The proxy can be a Firebase Cloud Function, a Next.js API route, a Cloudflare Worker — anything server-side where you control secrets. For direct client connections, use only a documented managed/ephemeral credential flow. The Supabase examples in [supabase/edge-functions.md](../supabase/edge-functions.md) illustrate the same trust boundary; adapt runtime and credential handling.
