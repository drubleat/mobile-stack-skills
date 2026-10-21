# Maintenance audit — 2026-10-21

This maintenance pass covers both skill entrypoints, the reference graph and version-sensitive/security-sensitive examples. It preserves the two installable skills and adds no new skill triggers.

## Changes

- Short routing entrypoints, supported metadata and Codex UI descriptors; independent installation and progressive disclosure.
- YAML/link/reachability/context-budget validation, a no-overwrite installer and CI.
- Atomic server-only quota asset; RLS, function grants, lock scope, pooling, queues and HTTP-extension corrections.
- Provider model selection and retired API migration; bounded tool loops, complete Gemini parts, explicit streaming contracts.
- Modular Firebase, native identity, per-installation push, webhook reconciliation, store/release and build-secret corrections.
- Replaced misleading complete-looking snippets with explicit integration contracts when an app-specific implementation is required. Retained historical package baselines are labelled, not advertised as current.

## Verification scope

Static checks validate metadata, local paths, independent reference graphs and entry budgets. Tooling tests exercise installation collisions/rollback and malformed reference metadata. SQL integration tests use a disposable local PostgreSQL cluster and synthetic roles/users; no existing database or live service is modified.

Native applications, store submissions, paid AI requests and live subscription/push integrations are not exercised by this library audit. Each consuming app must resolve its SDK dependencies and validate device behavior and account configuration. Official sources are linked in revised references; a source-review date is not a claim that every snippet was executed.

## Measured results

| Check | Result |
|---|---|
| Skill entrypoints | Both pass the Codex skill-creator validator |
| Reference graph | 121 mobile reference files + 22 Postgres rules; all reachable and locally linked |
| Mobile entry size | 8,846 → 3,821 UTF-8 bytes (56.8% smaller); 481 body words |
| Postgres entry size | 2,571 → 2,467 UTF-8 bytes; 231 body words |
| Tooling regression tests | 10 passed: isolated installs, collisions, rollback, invalid YAML, links and budgets |
| PostgreSQL integration tests | 5 passed on PostgreSQL 18, in a disposable socket-only cluster |
| Concurrent quota check | 48 requests against a limit of 10: exactly 10 admitted, stored count 10 |
| Dart analyzer | No issues for the extracted SSE parser and selected Supabase API calls |
| Dart runtime tests | 5 passed: fragmented UTF-8/CRLF, truncated stream, error frame, invalid payload, HTTP failure |

Entrypoint byte savings are not a measured token reduction for whole sessions. The principal context rule is to load only the index and leaves needed for the current task. The SQL entrypoint no longer mandates preloading every critical/high rule.

Tests are committed and wired into GitHub Actions. The Dart fixture lockfile pins the checked dependency graph; updating it requires rerunning analysis and runtime tests. TypeScript snippets are not comprehensively compiled, and no complete Expo or Flutter app was built in this audit.
