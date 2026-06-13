---
title: Avoid N+1 queries with PostgREST resource embedding
impact: HIGH
impactDescription: "N+1 patterns send hundreds of round-trips for paginated lists; PostgREST embedding collapses these into one query"
tags: performance, postgrest, queries, embedding, joins
---

# Avoid N+1 queries with PostgREST resource embedding

## The problem

```ts
// ❌ N+1 — one query per post to fetch the author
const { data: posts } = await supabase.from('posts').select('*');
for (const post of posts) {
  const { data: author } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', post.user_id)
    .single();
}
```

100 posts = 101 database round-trips.

## Solution: PostgREST resource embedding

```ts
// ✅ One query — PostgREST generates a JOIN
const { data } = await supabase
  .from('posts')
  .select(`
    id, content, created_at,
    profiles ( id, username, avatar_url )
  `);
```

PostgREST follows the FK relationship (`posts.user_id → profiles.id`) and generates a single SQL query with a JOIN.

## Nested embedding

```ts
const { data } = await supabase
  .from('conversations')
  .select(`
    id, title,
    messages (
      id, content, created_at,
      profiles ( username, avatar_url )
    )
  `)
  .order('created_at', { referencedTable: 'messages', ascending: false })
  .limit(20, { referencedTable: 'messages' });
```

## Many-to-many via junction table

```ts
// posts ← post_tags → tags
const { data } = await supabase
  .from('posts')
  .select(`
    id, title,
    post_tags ( tags ( id, name ) )
  `);
```

## Aggregate columns (avoid fetching all rows)

```ts
// Count messages per conversation without fetching message content
const { data } = await supabase
  .from('conversations')
  .select('id, title, messages(count)');
```

## When embedding isn't enough

For complex aggregations or cross-table analytics, create a Postgres view or function and expose it via PostgREST:

```sql
create view conversation_summaries as
  select c.id, c.title, count(m.id) as message_count,
         max(m.created_at) as last_message_at
  from conversations c
  left join messages m on m.conversation_id = c.id
  group by c.id, c.title;
```

```ts
const { data } = await supabase.from('conversation_summaries').select('*');
```
