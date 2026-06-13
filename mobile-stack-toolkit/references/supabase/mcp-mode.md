---
title: Supabase MCP — connect Claude directly to your Supabase project
impact: MEDIUM-HIGH
impactDescription: "Supabase MCP lets Claude read your schema, write migrations, and query data directly — eliminates copy-paste workflow for AI-assisted database development"
tags: supabase, mcp, claude, ai-dev, migrations, schema
---

# Supabase MCP: connect Claude to your project

The Supabase CLI ships an MCP server that lets Claude (and other MCP clients) interact directly with your Supabase project: read schema, generate migrations, run queries, and inspect Edge Functions.

## Start the MCP server

```bash
# Requires Supabase CLI ≥ 2.x and a linked project
supabase mcp start
```

This starts a local MCP server on a Unix socket. Connect Claude Code to it via the MCP config.

## Configure in Claude Code

Add to your project's `.claude/settings.json` (or `~/.claude/settings.json` for global):

```json
{
  "mcpServers": {
    "supabase": {
      "command": "supabase",
      "args": ["mcp", "start"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "<your-personal-access-token>"
      }
    }
  }
}
```

Get your access token from: [supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens)

## What Claude can do via Supabase MCP

| Capability | Example prompt |
|---|---|
| Read schema | "What tables exist in the public schema? Show me the columns for `profiles`." |
| Write migrations | "Add a `bio` column to `profiles` and write a migration file." |
| Execute SQL | "How many users signed up in the last 7 days?" |
| Inspect RLS policies | "List all RLS policies on the `messages` table." |
| Create Edge Functions | "Create an Edge Function that sends a welcome email on user signup." |
| Read Edge Function logs | "Show me errors in the `embed-document` function from the last hour." |

## Local development workflow

```bash
# 1. Start local Supabase stack
supabase start

# 2. Start MCP server (in another terminal or let Claude Code spawn it)
supabase mcp start

# 3. In Claude Code — Claude now has direct access to your local DB
# "Create a migration that adds pgvector support and an embeddings table"
# Claude writes supabase/migrations/..._add_embeddings.sql
# "Apply the migration"
# Claude runs: supabase db reset (or supabase migration up)
```

## Safety: MCP operates on local DB by default

When running `supabase mcp start` without `--linked`, it connects to the **local Docker database**, not your production project. To connect to a remote project:

```bash
supabase mcp start --project-ref <your-project-ref>
```

Only use the linked/remote mode for read-only schema inspection. Run migrations through CI, not through MCP directly connected to production.

## Useful MCP prompts for this stack

```
"Using the Supabase MCP, show me all tables without RLS enabled"

"Generate a migration to add an index on messages(user_id, created_at DESC)"

"Write an RPC function for semantic search using pgvector on the documents table"

"Show me the 5 slowest queries from pg_stat_statements"

"Create a pg_cron job that deletes soft-deleted posts older than 30 days"
```

## Supabase MCP vs Dashboard

| | MCP (Claude) | Dashboard |
|---|---|---|
| Write migrations | ✅ Version-controlled | ❌ Click-ops, no history |
| Schema inspection | ✅ Conversational | ✅ Visual |
| Query data | ✅ Natural language | ✅ SQL editor |
| RLS testing | ✅ Can `SET ROLE` | Limited |
| Edge Function logs | ✅ | ✅ |
