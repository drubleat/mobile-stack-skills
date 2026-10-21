---
title: "AI quotas and authorization"
impact: CRITICAL
impactDescription: "Prevent unauthorized access and incorrect state transitions"
tags: security, correctness
---

# AI quotas and authorization

Authenticate the caller before spending money. Derive the user ID and tier on the server. Do not accept a user ID, daily date, quota limit, model name, or provider URL from untrusted input without validation.

## Atomic daily quota

Use [the quota migration](../../assets/sql/ai-quota.sql) as a starting point. It caps increments atomically, uses a server-derived UTC day, enables RLS, fixes the function search path, and revokes client execution. Review existing schema/policies before applying it; `CREATE TABLE IF NOT EXISTS` does not repair a different existing schema. Remove any obsolete three-argument quota RPC after migrating its callers so it cannot remain an authorization bypass.

Call it using a separate server-only admin client **after** user authentication:

```ts
const { data, error } = await adminClient.rpc('increment_ai_usage', {
  p_user_id: user.id,
  p_limit: serverVerifiedLimit,
});
if (error || typeof data?.over_limit !== 'boolean') {
  return new Response('Quota unavailable', { status: 503 });
}
if (data.over_limit) {
  return new Response('Quota exceeded', { status: 429 });
}
```

The quota counts admitted attempts, including provider failures. If billing should count only successful work, use an idempotent reservation/settlement design. A daily count alone does not cap tokens, concurrent requests, or image/audio spend: add per-request output limits, request size bounds, deadlines, and concurrency controls. Provider budget alerts are monitoring, not guaranteed hard spending caps.

## Prompt and tool boundaries

Keep instructions and untrusted content separate. Do not put credentials or confidential secrets in prompts; a hidden system prompt is not an authorization boundary. Validate tool names and arguments, authorize every action against the authenticated user, and require the applicable approval for consequential writes. Treat retrieved content and tool outputs as data. Limit tool rounds and retries.

Validate the complete request before calling the provider; reject malformed JSON and unexpected types. Bound encoded uploads and inspect content where necessary. Apply output schemas and rendering-context escaping; schema correctness does not imply factual correctness. Log request IDs, usage, latency, and errors without logging credentials or raw personal content by default.

Test concurrent admission at the quota boundary, database failure, invalid JWTs, client RPC denial, and account switching. If authorization/quota state is unavailable, do not call the paid provider.

## Sources

Reviewed 2026-10-20: [Supabase function security](https://supabase.com/docs/guides/database/functions), [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security).
