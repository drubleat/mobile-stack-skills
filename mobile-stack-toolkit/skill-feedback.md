---
title: "Skill feedback & known issues"
impact: LOW
impactDescription: "Tracks outdated information, missing coverage, and improvement suggestions for this skill"
tags: meta, feedback, issues
---

# Skill feedback

Found something outdated, wrong, or missing? Add it here.

## How to report

Open an issue or PR on the repository, or add an entry below with the date.

## Maintenance policy

Check installed versions and official sources before changing a reference. Do not duplicate a live version table here. See the repository audit notes for this maintenance pass.

## Candidate follow-up topics (not implemented in this pass)

- Offline synchronization and conflict resolution.
- Account deletion, data export, and third-party cleanup.
- Mobile accessibility and localization review.
- SDK upgrade planning with native compatibility checks.
- Subscription reconciliation test fixtures and operational monitoring.

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
