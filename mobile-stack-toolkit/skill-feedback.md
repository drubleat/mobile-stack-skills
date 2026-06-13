---
title: Skill feedback & known issues
impact: LOW
impactDescription: "Tracks outdated information, missing coverage, and improvement suggestions for this skill"
tags: meta, feedback, issues
---

# Skill feedback

Found something outdated, wrong, or missing? Add it here.

## How to report

Open an issue or PR on the repository, or add an entry below with the date.

## Versioning

This skill targets:
- **Expo SDK 56** (React Native 0.85, React 19.2)
- **Supabase JS v2** (`@supabase/supabase-js@2.x`)
- **react-native-purchases v10** (RevenueCat)
- **Flutter SDK 3.x** with `flutter_riverpod 3.3.2`, `go_router 17.3.0`
- **OpenAI Responses API** (gpt-5.4, gpt-5.4-mini, gpt-5.5)
- **Gemini 3.5** (gemini-3.5-flash, gemini-3.5-flash-lite)

When a major version ships and these files need updating, that's the right time for a PR.

## Known gaps / wishlist

- [ ] Supabase Auth v2 hook — custom access token hook with org/team claims
- [ ] RevenueCat Billing (web checkout) — new in 2025
- [ ] Flutter 4.x — when released, update package versions
- [ ] Stripe mobile SDK — alternative to RevenueCat for one-time purchases
- [ ] Superwall Flutter — RevenueCat PurchaseController full test coverage
- [ ] PostHog session replay setup — requires additional config beyond capture

## Changelog

### v1.0.0 (2026-06-13) — Initial public release

**125 reference files across 11 domains**, plus the `supabase-postgres-best-practices` companion skill (22 Postgres rules).

- **Expo / React Native** — SDK 56, EAS Build, OTA, dev builds, troubleshooting; Expo Router (routes, params, modals, typed routes, deep linking, `Stack.Protected` auth gating); forms (react-hook-form + zod, Controller pattern); image pipeline (pick → ArrayBuffer upload → cache); NativeWind v4; TanStack Query v5; Zustand + MMKV; Sentry; PostHog
- **Supabase** — Postgres, Auth, Edge Functions, RLS, Realtime, Storage, pgvector, pg_cron, pg_net, queues, MCP
- **AI** — OpenAI Responses API + Gemini 3.5, ElevenLabs TTS, edge-proxy architecture, streaming, structured output, guardrails
- **Monetization** — RevenueCat v10, Superwall (RN + Flutter)
- **Push** — FCM, APNs, Expo Push, handlers, deep linking
- **Firebase** — Crashlytics, Analytics, Remote Config, App Check, Firebase AI Logic, Firestore
- **Flutter** — Riverpod 3.x, go_router 17.x, supabase_flutter, purchases_flutter, dio, testing, CI/CD
- **Store / CI/CD / Playbooks / Packages** — submission, EAS Workflows, GitHub Actions, Maestro E2E, zero-to-store recipes, Dart/Flutter package reference
- Full frontmatter on all files (`impact`, `impactDescription`, `tags`)
- Meta files: `_sections.md`, `_template.md`, `skill-feedback.md`
