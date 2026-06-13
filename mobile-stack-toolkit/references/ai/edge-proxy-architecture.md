---
title: Edge Function proxy — why and how
impact: CRITICAL
impactDescription: "Calling AI APIs directly from the client exposes secret keys; this pattern is non-negotiable for production"
tags: ai, security, edge-functions, openai, gemini, proxy
---

# Edge Function proxy — why and how

## The rule: no AI API call ever leaves directly from the mobile client

This is non-negotiable. Every call to OpenAI, Gemini, or any model API goes through a **Supabase Edge Function** that you own. The mobile app calls your function; your function calls the model.

## Why

**Security.** An API key embedded in a mobile app is a public key. APKs are trivially decompiled; IPAs are extractable. Anyone who finds your key gets your billing account. A leaked OpenAI key can run up thousands of dollars in hours.

**Rate limiting & quotas.** You cannot enforce per-user limits from the client side. The Edge Function checks `usage_counters`, enforces daily quotas, and can apply tier-based limits (free users get 10 calls/day, Pro users get 500).

**Cost control.** Log every request's token count. Set hard limits. Kill a runaway feature from the server without a store release.

**Prompt control.** The system prompt is server-side code, not a string in the app. Users can't inspect or override it.

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

## Minimal Edge Function skeleton

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

  // 2. Quota check (see guardrails.md)
  const overLimit = await checkAndIncrementQuota(supabase, user.id);
  if (overLimit) return new Response('Rate limit exceeded', { status: 429, headers: cors });

  // 3. Call model
  const { userMessage } = await req.json();
  const response = await openai.responses.create({
    model: 'gpt-5.4-mini',
    instructions: 'You are a helpful assistant.',
    input: userMessage,
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
  const res = await fetch(`${SUPABASE_URL}/functions/v1/ai-proxy`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${session!.access_token}`,
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

If your backend is Firebase / custom server / another BaaS: same pattern, different host. The proxy can be a Firebase Cloud Function, a Next.js API route, a Cloudflare Worker — anything server-side where you control secrets. The mobile client still only talks to your own endpoint, never directly to OpenAI/Gemini. The Supabase examples in [supabase/edge-functions.md](../supabase/edge-functions.md) apply 1:1.
