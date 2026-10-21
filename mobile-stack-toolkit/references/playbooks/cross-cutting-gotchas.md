---
title: "Cross-domain failure checklist"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Cross-domain failure checklist

Use this checklist to choose the next reference; avoid loading every domain.

| Symptom | Check | Reference |
|---|---|---|
| Paid access missing or wrong user | Identity aliases, restore/transfer policy, verified expiry, event ordering | [webhooks](../monetization/webhooks-supabase.md) |
| AI spend exceeds intended cap | Server-only atomic admission, failure handling, paid-user budgets | [guardrails](../ai/guardrails.md) |
| Native module missing | Installed binary includes the module; rebuild after native config changes | [native builds](../expo/native-dev-builds.md) |
| Slow or unauthorized query | Correct policies, real-role tests and query plans; no universal index guarantee | [RLS](../supabase/rls-policies.md) |
| Gemini options rejected | SDK camelCase, model-specific thinking settings | [Gemini text](../ai/gemini/text.md) |
| Webhook blocked or spoofed | Gateway JWT setting plus verified provider authentication | [webhooks](../monetization/webhooks-supabase.md) |
| Push reaches wrong device/account | Per-installation token records, logout detach and environment | [FCM](../push/fcm-setup.md) |
| Release affects old binaries | Expand/contract schema and runtime-compatible OTA | [deploy](../cicd/supabase-deploy.md) |

Provider secrets belong on trusted servers; publishable mobile configuration is not secret. Supabase publishable/secret API keys differ from legacy JWT anon/service-role keys: do not substitute an opaque secret key for a Bearer JWT. Verify the endpoint's auth contract and actual migration notices instead of inventing a deprecation deadline.

For stuck emulators/build caches, inspect the specific process and preserve local source/native changes before cleanup. Do not delete all lockfiles or shut down unrelated user devices as the first troubleshooting step.

## Sources

Reviewed 2026-10-20: [Supabase API keys](https://supabase.com/docs/guides/api/api-keys).
