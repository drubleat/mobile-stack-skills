---
title: GitHub Actions: PR checks + production pipeline
impact: HIGH
impactDescription: "Type check + test + Supabase migration in one pipeline; concurrency groups prevent parallel deploys stomping each other"
tags: cicd, github-actions, testing, supabase, pipeline
---

# GitHub Actions: PR checks + production pipeline

Use GitHub Actions for the parts EAS Workflows can't handle: type checking, tests, Supabase migration deploys, and custom orchestration. Pair it with EAS Workflows for native builds.

## Required secrets (GitHub → Settings → Secrets)

```
EXPO_TOKEN              # from expo.dev → account settings → access tokens
SUPABASE_ACCESS_TOKEN   # from supabase.com → account → access tokens
SUPABASE_PROJECT_REF    # your project reference (from dashboard URL)
SUPABASE_DB_PASSWORD    # project database password
```

## PR check: type check + OTA preview

```yaml
# .github/workflows/pr.yml
name: PR check

on:
  pull_request:
    branches: [main]

jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npx tsc --noEmit

  preview-update:
    runs-on: ubuntu-latest
    needs: typecheck
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - name: Deploy preview update
        run: |
          eas update \
            --branch pr-${{ github.event.pull_request.number }} \
            --message "PR #${{ github.event.pull_request.number }}: ${{ github.event.pull_request.title }}" \
            --non-interactive
```

## Production pipeline: migrate → build → submit

```yaml
# .github/workflows/production.yml
name: Production deploy

on:
  push:
    branches: [main]

jobs:
  migrate-supabase:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: supabase/setup-cli@v1
        with:
          version: latest
      - name: Apply migrations
        run: |
          supabase db push \
            --project-ref ${{ secrets.SUPABASE_PROJECT_REF }} \
            --password ${{ secrets.SUPABASE_DB_PASSWORD }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

  build-ios:
    runs-on: ubuntu-latest
    needs: migrate-supabase
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas build --platform ios --profile production --non-interactive

  build-android:
    runs-on: ubuntu-latest
    needs: migrate-supabase
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas build --platform android --profile production --non-interactive

  submit:
    runs-on: ubuntu-latest
    needs: [build-ios, build-android]
    steps:
      - uses: actions/checkout@v4
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas submit --platform all --profile production --non-interactive
```

## Key patterns

**Always use `--non-interactive`** for any EAS command in CI. Without it, the command may hang waiting for input.

**`needs:` for ordering**: migrations must finish before builds start; builds must finish before submit. GitHub Actions runs jobs in parallel by default unless `needs:` is specified.

**Node version pinned**: use `node-version: '22'` (Node 22 LTS). Don't use `latest` in CI — a Node major version bump can break builds unexpectedly.

**`npm ci` not `npm install`**: `npm ci` uses the lockfile exactly and fails if package-lock.json is out of sync. Faster and reproducible.

## Caching

Add node_modules caching to speed up jobs that install the same dependencies:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

The `actions/setup-node@v4` `cache: 'npm'` shorthand handles this automatically.

## EAS Workflows vs GitHub Actions

| Task | Use |
|---|---|
| Trigger EAS Build | Either (EAS Workflows simpler) |
| Type check / tests | GitHub Actions |
| Supabase migration | GitHub Actions (EAS Workflows can't run `supabase` CLI) |
| PR status checks on GitHub UI | GitHub Actions |
| Slack/custom notifications | GitHub Actions |
