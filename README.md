# Mobile Stack Skills

On-demand mobile development references for **Codex and Claude Code**: Expo/React Native, Flutter, Supabase, Firebase, RevenueCat, AI integration, notifications, testing, and releases.

| Skill | Scope |
|---|---|
| [mobile-stack-toolkit](mobile-stack-toolkit/SKILL.md) | Mobile implementation and integration across 11 domains |
| [supabase-postgres-best-practices](supabase-postgres-best-practices/SKILL.md) | Standalone Postgres queries, RLS, migrations, pooling, and extensions |

Each skill works independently. The toolkit can suggest the Postgres companion when installed, but does not require sibling files.

## Context-efficient use

```text
name + description → SKILL.md → relevant domain index → needed topic
```

Only the descriptions are needed for discovery. Once selected, the short entrypoint routes to the task's references. Start with one or two relevant leaves, and load more when needed; skip the index if the exact leaf is known. Do not include the entire skill or all references in AGENTS.md/CLAUDE.md.

`impact` labels help prioritize relevant issues; agents do not automatically interpret them as a requirement to load files. Unopened reference bodies are not loaded by this workflow, but actual token use depends on the agent and tools. There is no fixed percentage or “zero overhead” guarantee.

## Install

```bash
git clone https://github.com/drubleat/mobile-stack-skills.git
cd mobile-stack-skills
```

Choose a target explicitly. The installer uses Python 3.10+ with no third-party dependencies, copies both skills by default, and refuses to overwrite any existing skill.

**Codex — per project:**

```bash
python3 scripts/install_skills.py --target /path/to/project/.agents/skills
```

**Codex — personal:**

```bash
python3 scripts/install_skills.py --target ~/.agents/skills
```

For environments that use the legacy `~/.codex/skills` location, use that location as `--target` instead. Avoid duplicate installations in multiple discovery roots. See [official Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

**Claude Code:**

```bash
python3 scripts/install_skills.py --target ~/.claude/skills
# Or: --target /path/to/project/.claude/skills
```

Install only one skill by adding `--skill mobile-stack-toolkit` or `--skill supabase-postgres-best-practices`. To update, review changes and move the old installed directory to a backup outside the agent's discovery paths, then install the replacement. Local edits are never silently overwritten.

Start a new session if the skill list does not refresh. In Codex explicitly invoke `$mobile-stack-toolkit` or `$supabase-postgres-best-practices`, or ask a relevant question naturally. In Claude Code use the skill picker/slash invocation supported by your version.

Example requests:

- “Use $mobile-stack-toolkit to add a RevenueCat paywall to this existing Expo app.”
- “Review this Flutter auth and notification flow.”
- “Use $supabase-postgres-best-practices to verify tenant isolation in these policies.”

Installation does not configure accounts, connect MCP servers, deploy functions, or grant permission to publish an app.

## Coverage

| Domain | Topics |
|---|---|
| Expo / React Native | Setup, builds, OTA, routing, forms, media, styling, state, diagnostics |
| Flutter | Setup, routing, networking, storage, UI, integrations, tests, CI |
| Supabase | Auth, RLS, schema, functions, storage, realtime, extensions |
| Firebase | Auth, Firestore, Storage, App Check, AI Logic, FCM, diagnostics |
| Monetization | RevenueCat, entitlements, webhook reconciliation, Superwall |
| AI | Provider adapters, text, images, audio, tools, streaming, quotas |
| Push | Expo Push, FCM, APNs, routing, device tokens, server delivery |
| Stores | Submission, privacy, metadata, review preparation |
| CI/CD | EAS, GitHub Actions, migrations, secrets, Maestro |
| Playbooks | New-app sequence and cross-component troubleshooting |
| Dart packages | Focused package API references |

## Version and evidence policy

Examples target API families, not an automatically maintained “latest stack.” Existing version pins are historical examples unless a specific review says otherwise. Inspect the application's lockfile and official migration guides before using them. Do not upgrade a project merely to match this repository.

Model IDs, pricing, store rules, and platform requirements change. Check the linked official source at implementation time. Updated references distinguish workflow sketches from runnable assets. A successful structural check does not prove an SDK sample works on a physical device or a live service.

The [audit notes](AUDIT.md) record corrections and validation limits. New skill proposals are kept separate from this maintenance pass.

## Contribute and validate

Keep shared instructions short; put conditional details in linked references. Use [the reference template](mobile-stack-toolkit/_template.md), add a domain index link, and cite an official source with the review date. Avoid unsourced numerical performance claims and absolute rules that override the user's stack or scope.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_skills.py
.venv/bin/python -m unittest discover -s tests -v
```

Validation checks YAML, metadata, local links, independent installation paths, reference reachability, and entrypoint context budgets. CI also exercises the quota asset against a disposable PostgreSQL cluster. To run that integration locally, put a complete PostgreSQL installation on PATH and set `RUN_POSTGRES_TESTS=1` when running unittest. No existing database is used. With Dart 3.12.2 available, run `python3 scripts/check_dart_snippets.py`. It extracts the documented SSE parser, resolves the committed fixture lockfile, analyzes selected SDK calls, and runs five loopback HTTP tests; it does not call a paid provider. CI runs the same checks. Use meaningful platform/runtime checks for other changed examples and state what was not run.

## License

[MIT](LICENSE). Author: **Eren Öz** — [eren@qoodly.com](mailto:eren@qoodly.com).
