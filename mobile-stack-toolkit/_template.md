---
title: Reference file template
impact: LOW
impactDescription: "Template for adding new reference files; ensures consistent frontmatter and structure across all domains"
tags: meta, template, contributing
---

# Reference file template

Copy this template when adding a new reference file.

## File naming

- Use `kebab-case.md`
- Place in the appropriate domain directory under `references/`
- If adding a new package to `packages/`, name it `{package_name}.md` (use underscores to match the Dart package name)

## Frontmatter template

```yaml
---
title: Short, action-oriented title (what does this cover?)
impact: CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM|LOW
impactDescription: "One sentence: quantified benefit or risk prevented. Examples: '100x faster queries', 'missing this causes App Store rejection', 'eliminates 80% of push notification debugging'"
tags: comma, separated, tags, lowercase
---
```

## Impact level guide

| Level | When to use |
|---|---|
| **CRITICAL** | Security issue, data loss, or App Store rejection if wrong |
| **HIGH** | Core workflow, must-get-right for the feature to work |
| **MEDIUM-HIGH** | Important optimization or common integration pattern |
| **MEDIUM** | Useful reference, standard patterns |
| **LOW-MEDIUM** | Supplementary detail, rarely the first thing needed |
| **LOW** | Meta files, routers, rarely loaded directly |

## Content structure

```markdown
# Title

One-sentence description of what this file covers and why it matters.

## Section heading

Code example first, explanation second. Show the correct pattern before
explaining why it's correct.

## Common mistakes / gotchas

List the 2-3 most common errors and their fixes. This is often the most
valuable section.

## Related files

Cross-reference with relative links:
- [auth.md](auth.md) — for session handling
- [../ai/edge-proxy-architecture.md](../ai/edge-proxy-architecture.md)
```

## Package reference template

For files in `packages/`:

```markdown
---
title: {package_name} {version} — one-line description
impact: HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM
impactDescription: "..."
tags: flutter, dart, {relevant-tags}
---

# {package_name} — description

**Version:** {x.y.z}
**Pub.dev:** https://pub.dev/packages/{package_name}

## Install

\`\`\`yaml
# pubspec.yaml
dependencies:
  {package_name}: ^{x.y.z}
\`\`\`

## Core API

[Most common usage with code example]

## Gotchas

[2-3 common mistakes]
```

## After adding a file

1. Add a row to the domain's `_index.md` router table
2. Add a row to `_sections.md` if it changes the file count
3. Check if `SKILL.md` should route to it directly
