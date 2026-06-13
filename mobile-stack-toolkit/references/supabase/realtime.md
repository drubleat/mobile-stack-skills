---
title: Realtime: Postgres change subscriptions
impact: MEDIUM
impactDescription: "Eliminates polling for live UI; understanding channel lifecycle prevents memory leaks"
tags: supabase, realtime, websocket, postgres
---

# Realtime

Push Postgres changes (and ephemeral events) to clients over a websocket. Use it when the UI must reflect server state without polling.

## Three Realtime features

1. **Postgres Changes** — subscribe to INSERT/UPDATE/DELETE on a table. The obvious "live list" use case.
2. **Broadcast** — low-latency, ephemeral messages between clients (typing indicators, cursors, live reactions). Not persisted.
3. **Presence** — who's online / shared state (online users, "X is viewing").

Most apps start with Postgres Changes.

## Live list (Postgres Changes)

```ts
const channel = supabase
  .channel('items-feed')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'items', filter: `user_id=eq.${userId}` },
    (payload) => {
      // payload.eventType: INSERT | UPDATE | DELETE; payload.new / payload.old
      applyChange(payload);
    },
  )
  .subscribe();

// cleanup
return () => { supabase.removeChannel(channel); };
```

In React, create the channel in a `useEffect` and remove it in the cleanup — **leaking channels** on every re-render is the most common Realtime bug.

## Two prerequisites people forget

1. **Enable Realtime for the table** (add it to the `supabase_realtime` publication):
   ```sql
   alter publication supabase_realtime add table public.items;
   ```
2. **RLS still applies to Realtime.** A client only receives change events for rows its SELECT policy allows. If events don't arrive, check the RLS SELECT policy first → [rls-policies.md](rls-policies.md). The server-side `filter` narrows further but does not replace RLS.

## With TanStack Query

Don't manage a parallel list in state. Let Realtime **invalidate** the query and refetch (or patch the cache):

```ts
.on('postgres_changes', { event: '*', schema: 'public', table: 'items' }, () => {
  queryClient.invalidateQueries({ queryKey: ['items'] });
})
```

This keeps a single source of truth and avoids "two lists drifting" bugs. For high-frequency updates, patch the cache directly with `setQueryData` instead of refetching.

## Broadcast & Presence (quick shape)

```ts
const room = supabase.channel('room-1', { config: { presence: { key: userId } } });
room
  .on('broadcast', { event: 'typing' }, ({ payload }) => showTyping(payload))
  .on('presence', { event: 'sync' }, () => setOnline(room.presenceState()))
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') await room.track({ online_at: Date.now() });
  });
room.send({ type: 'broadcast', event: 'typing', payload: { userId } });
```

## When NOT to use Realtime

- **One-shot data** → just fetch with TanStack Query; a websocket is overkill.
- **Massive fan-out / very hot tables** → Postgres Changes has overhead per subscriber; consider Broadcast or a purpose-built channel, and always use the `filter` to limit scope.
- **Background delivery / notifications when the app is closed** → that's push, not Realtime → [../push/_index.md](../push/_index.md).

## Pitfalls

- **No events** → table not in the `supabase_realtime` publication, or RLS SELECT policy blocks the rows.
- **Duplicate handlers / memory growth** → channel not removed on unmount; always `removeChannel` in cleanup.
- **Connection drops on background** → expected on mobile; re-subscribe on app foreground, and treat Realtime as a freshness optimization, not a guaranteed delivery channel.
