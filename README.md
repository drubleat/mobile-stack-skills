<div align="center">

# mobile-stack-skills

**Claude Code Agent Skills for shipping AI-first mobile apps — fast.**

Production-grade, opinionated playbooks that give Claude deep, current knowledge of the modern mobile stack:
**Expo / React Native · Flutter · Supabase · Firebase · RevenueCat · OpenAI · Gemini.**

![License](https://img.shields.io/badge/license-MIT-blue)
![Skills](https://img.shields.io/badge/skills-2-6366f1)
![Reference files](https://img.shields.io/badge/reference%20files-147-22c55e)
![Stack](https://img.shields.io/badge/Expo%20SDK-56-000020)

</div>

---

## Why this exists

Ask a general-purpose model to "add a paywall to my Expo app" and you get plausible-but-stale advice: deprecated APIs, wrong command order, a leaked API key in the client bundle. This repo fixes that.

It's a set of [Claude Code Agent Skills](https://docs.anthropic.com/claude-code) — structured reference files Claude loads **on demand** while it works. Instead of generic suggestions, Claude pulls the exact file for what you're building and gives you the current SDK version, the correct sequence of commands, and the production pattern that doesn't fall over.

The goal: **go from idea to App Store without Claude having to guess.**

---

## What's inside

| Skill | What it covers | Size |
|---|---|---|
| [`mobile-stack-toolkit`](mobile-stack-toolkit/) | The full mobile stack — Expo/RN + Flutter + Supabase + Firebase + RevenueCat + AI + push + store + CI/CD | 125 files |
| [`supabase-postgres-best-practices`](supabase-postgres-best-practices/) | Deep Postgres rules — indexes, RLS, pooling, migrations, pgvector, pg_cron, pgmq | 22 rules |

The second skill stands alone — it's useful for **any** Supabase project, mobile or web.

---

## How Claude actually uses it (and why it stays fast)

These skills are built on **progressive disclosure**, so the size never bloats your context:

```
SKILL.md  ──►  references/<domain>/_index.md  ──►  references/<domain>/<topic>.md
(the map)        (the router for one domain)         (the deep reference — loaded only when needed)
```

1. Claude reads the lightweight skill **description** at all times.
2. When your task matches, it loads `SKILL.md` (the map).
3. It routes to the relevant domain's `_index.md`, then opens **only the 1–2 leaf files** it needs.

So a "add a paywall" task loads ~3 files — the other 120+ cost **zero tokens** until they're relevant. Depth without drag.

---

## Coverage

**`mobile-stack-toolkit`** — 11 domains:

| Domain | Highlights |
|---|---|
| **Expo / React Native** | SDK 56, EAS Build, OTA, dev builds, **Expo Router** (navigation + `Stack.Protected` auth), **forms** (react-hook-form + zod), **image pipeline** (pick → upload → cache), NativeWind v4, TanStack Query v5, Zustand + MMKV, Sentry, PostHog |
| **Supabase** | Postgres, Auth, Edge Functions, RLS, Realtime, Storage, pgvector, queues, MCP |
| **AI** | OpenAI Responses API (gpt-5.x), Gemini 3.5, ElevenLabs TTS, **edge-proxy architecture**, streaming, structured output, guardrails |
| **Monetization** | RevenueCat v10, Superwall (paywall A/B testing), entitlements, webhooks |
| **Push** | FCM, APNs, Expo Push, handlers across all app states, deep linking |
| **Firebase** | Crashlytics, Analytics, Remote Config, App Check, Firebase AI Logic, Firestore |
| **Flutter** | Riverpod 3.x, go_router 17.x, supabase_flutter, purchases_flutter, dio, testing, CI/CD |
| **App / Play Store** | submission, ASO, permissions, rejection red flags |
| **CI/CD** | EAS Workflows, GitHub Actions, Maestro E2E testing, secrets |
| **Playbooks** | zero-to-store sequence, AI app recipe, cross-cutting gotchas |
| **Packages** | Dart/Flutter package reference library |

**`supabase-postgres-best-practices`** — 7 rule categories: query performance (incl. 100× RLS speedup), connection pooling, RLS/auth security, schema & migrations, locking & concurrency, `pg_stat` diagnostics, and extensions (pgvector / pg_cron / pg_net / pgmq).

---

## Getting started

Claude Code discovers skills from a `skills/` directory — either personal (`~/.claude/skills/`, available in every project) or per-project (`<project>/.claude/skills/`). Each skill is a folder containing a `SKILL.md`. So installing means putting these two skill folders into one of those locations.

### 1. Clone

```bash
git clone https://github.com/drubleat/mobile-stack-skills.git
cd mobile-stack-skills
```

### 2. Install the skills

**Option A — personal (recommended, available across all your projects):**

```bash
mkdir -p ~/.claude/skills
cp -R mobile-stack-toolkit ~/.claude/skills/
cp -R supabase-postgres-best-practices ~/.claude/skills/
```

**Option B — single project only:**

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R mobile-stack-toolkit /path/to/your-project/.claude/skills/
cp -R supabase-postgres-best-practices /path/to/your-project/.claude/skills/
```

> If `~/.claude/skills/` didn't exist before, restart Claude Code once so it starts watching the new directory. After that, edits and additions are picked up live.
>
> Prefer to keep this repo as the single source of truth? Symlink instead of copying (`ln -s "$(pwd)/mobile-stack-toolkit" ~/.claude/skills/mobile-stack-toolkit`). Note that symlinks pointing outside your project may trigger per-file read permission prompts — copying avoids them.

### 3. Verify

Open Claude Code and type `/` — you should see `mobile-stack-toolkit` and `supabase-postgres-best-practices` in the skill list.

### 4. Just build

Ask naturally — Claude loads the right reference automatically, no file paths needed:

> *"Set up an Expo + Supabase app with email auth and a RevenueCat paywall."*
> *"Add a vector search over my documents table."*
> *"Why are my Firestore security rules letting updates through?"*

---

## Goal

Build the most comprehensive, accurate, and up-to-date Claude Code skill set for mobile development — covering every tool in the modern AI-first stack with enough depth that Claude can take you from idea to launch without looking anything up.

This is a **living document**. SDKs change, APIs break, new tools emerge. Community contributions are what keep it current.

---

## Contributing — this repo gets better with you

This is a community project, and the whole point is that no single person can keep an entire mobile stack current. **If you've ever hit a wrong command, a deprecated API, or a missing tool while building — you already know something worth contributing.** Big or small, it's welcome.

You don't need to be an expert or write a whole new domain. Some of the most useful contributions are tiny:

- 🔧 **Spotted something stale?** A bumped SDK version, a renamed method, a model that no longer exists — fix the one line.
- 🪲 **A code example didn't work for you?** Open an issue (or a PR) — that's a real bug and others will hit it too.
- 🧭 **Missing a tool you use every day?** Add a reference file for it. If it helped you, it'll help someone else.
- 📦 **Know a package well?** Add it under `mobile-stack-toolkit/references/packages/`.
- 💡 **Just have an idea?** Open an issue and let's talk it through — proposals are contributions too.

No contribution is too small. A single corrected version number genuinely keeps the skill useful for everyone who clones it after you.

### How to contribute

1. **Fork** the repo (your fork shows up as your own copy — go wild)
2. Create a branch for your change:
   ```bash
   git checkout -b fix/expo-sdk-57-updates
   ```
3. Make your edit. For new reference files, follow [`mobile-stack-toolkit/_template.md`](mobile-stack-toolkit/_template.md) and add the frontmatter (`title`, `impact`, `impactDescription`, `tags`).
4. If you added a file, add it to that domain's `_index.md` router table so Claude can find it.
5. **Open a Pull Request** describing what changed and why.

That's it — your PR lands in the review queue, we go over it together, and once it looks good it gets merged in. First-time PR? Even better — open it and we'll help you polish it.

> **One house rule:** don't write from memory. Every SDK version, command, and API in this repo is verified against official docs at write time. If you're unsure, check the source first — accuracy is the entire value of this project.

### Frontmatter

Every reference file starts with:

```yaml
---
title: Short, action-oriented title
impact: CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM|LOW
impactDescription: "One sentence: the quantified benefit or the risk prevented"
tags: comma, separated, lowercase, tags
---
```

`impact` is how Claude prioritizes which files to load — get it right.

---

## Stack versions (as of v1.0.0)

| Technology | Version |
|---|---|
| Expo SDK | 56 (React Native 0.85) |
| react-native-purchases (RevenueCat) | v10.x |
| @react-native-firebase | v21.x |
| react-hook-form / zod | v7.79 / v4.x |
| flutter_riverpod / go_router | 3.3.2 / 17.3.0 |
| supabase_flutter / purchases_flutter | 2.14.2 / 10.2.3 |
| OpenAI API | Responses API (gpt-5.x) |
| Gemini API | 3.5 (gemini-3.5-flash) |

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

## Author

**Eren Öz** — [eren@qoodly.com](mailto:eren@qoodly.com)

*Contributions and feedback welcome via GitHub Issues and Pull Requests.*
