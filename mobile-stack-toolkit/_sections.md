---
title: Skill structure & section map
impact: LOW
impactDescription: "Navigation map of all domains and files in this skill — for contributors and for Claude when asked 'what does this skill cover?'"
tags: meta, index, structure
---

# Skill structure

## Domain overview

```
mobile-stack-toolkit/
├── SKILL.md                   ← entry point (load this first)
├── references/
│   ├── expo/                  ← React Native / Expo (SDK 56)
│   ├── supabase/              ← Postgres, Auth, Edge Functions, Realtime, Storage, pgvector, queues
│   ├── ai/                    ← OpenAI (Responses API), Gemini 3.5, edge proxy, streaming
│   ├── monetization/          ← RevenueCat v10, paywalls, webhooks
│   ├── push/                  ← FCM, APNs, Expo Push, deep linking
│   ├── firebase/              ← Crashlytics, Analytics, Remote Config, Firestore, hybrid patterns
│   ├── flutter/               ← Flutter + Riverpod + go_router + supabase_flutter
│   ├── store/                 ← App Store Connect, Play Console, ASO, privacy, rejections
│   ├── cicd/                  ← EAS Workflows, GitHub Actions, secrets, Supabase deploy
│   ├── playbooks/             ← zero-to-store, AI app recipe, cross-cutting gotchas
│   └── packages/              ← Dart/Flutter package reference library
└── _sections.md               ← this file
```

## File count by domain

| Domain | Files | Notes |
|---|---|---|
| expo/ | 15 | SDK 56, EAS, OTA, expo-router, forms (RHF+zod), image pipeline, NativeWind, TanStack Query, Zustand+MMKV, Sentry, PostHog |
| supabase/ | 13 | Core + pgvector, pg_cron, pg_net, queues, MCP |
| ai/ | 20 | OpenAI + Gemini subdirs, streaming, structured output, guardrails, ElevenLabs |
| monetization/ | 9 | RevenueCat v10, Superwall (RN + Flutter) |
| push/ | 7 | FCM, APNs, Expo Push, handlers, deep linking |
| firebase/ | 12 | Full Firebase coverage + App Check + AI Logic |
| flutter/ | 15 | Full Flutter stack |
| store/ | 6 | iOS + Android submission |
| cicd/ | 5 | EAS + GitHub Actions + Maestro E2E testing |
| playbooks/ | 3 | End-to-end recipes |
| packages/ | 14 | Dart/Flutter package reference |

**Total: ~125 files, 11 domains**

## Impact level distribution

| Impact | Files | Examples |
|---|---|---|
| CRITICAL | 9 | rls-policies, edge-proxy-architecture, guardrails, entitlement-checks |
| HIGH | 45 | Most core setup and integration files |
| MEDIUM-HIGH | 22 | Paywalls, OTA, deep linking, Flutter CI/CD |
| MEDIUM | 20 | Package refs, animations, analytics |
| LOW-MEDIUM | 4 | intl, url_launcher |

## Companion skill

**[supabase-postgres-best-practices](../../supabase-postgres-best-practices/SKILL.md)** — 22 deep Postgres rules (query perf, connection pooling, RLS patterns, schema design, locking, pg_stat diagnostics, pgvector, pg_cron, pg_net, pgmq). Load when the task involves SQL, indexes, migrations, or Postgres internals.
