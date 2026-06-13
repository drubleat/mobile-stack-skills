---
title: TanStack Query v5 — data fetching for React Native
impact: MEDIUM-HIGH
impactDescription: "TanStack Query eliminates manual loading/error/cache state; React Native requires explicit online and app-focus wiring or stale data and ghost refetches appear"
tags: tanstack-query, react-query, expo, react-native, data-fetching, caching
---

# TanStack Query v5 — React Native

TanStack Query (formerly React Query) handles server-state: fetching, caching, deduplication, background refetching, and pagination. It is NOT a global state manager — use it for async data from APIs/Supabase, and Zustand for local UI state.

**Package:** `@tanstack/react-query`  
**Version:** 5.x (v5.76+ as of June 2026)

---

## Install

```bash
npx expo install @tanstack/react-query
# Optional: devtools (web/macOS only)
npm install --save-dev @tanstack/react-query-devtools
```

---

## Setup

```tsx
// app/_layout.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,  // 5 minutes
      retry: 2,
    },
  },
});

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <Stack />
    </QueryClientProvider>
  );
}
```

---

## React Native–specific wiring (required)

React Native doesn't automatically tell TanStack Query about network status or app focus. Wire these up once at the root level.

```tsx
// hooks/useReactQuerySetup.ts
import { useEffect } from 'react';
import { AppState, AppStateStatus, Platform } from 'react-native';
import NetInfo from '@react-native-community/netinfo';
import { focusManager, onlineManager } from '@tanstack/react-query';

export function useReactQuerySetup() {
  useEffect(() => {
    // 1. Network status — refetch when connection restores
    const unsubscribeNetInfo = NetInfo.addEventListener((state) => {
      onlineManager.setOnline(!!state.isConnected);
    });

    // 2. App focus — refetch stale queries when app comes to foreground
    function onAppStateChange(status: AppStateStatus) {
      if (Platform.OS !== 'web') {
        focusManager.setFocused(status === 'active');
      }
    }
    const subscription = AppState.addEventListener('change', onAppStateChange);

    return () => {
      unsubscribeNetInfo();
      subscription.remove();
    };
  }, []);
}
```

Call in your root layout:

```tsx
// app/_layout.tsx
export default function RootLayout() {
  useReactQuerySetup();
  return (
    <QueryClientProvider client={queryClient}>
      <Stack />
    </QueryClientProvider>
  );
}
```

Requires `@react-native-community/netinfo`:
```bash
npx expo install @react-native-community/netinfo
```

---

## useQuery — read data

```tsx
import { useQuery } from '@tanstack/react-query';
import { supabase } from '@/lib/supabase';

async function fetchProfile(userId: string) {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single();
  if (error) throw error;
  return data;
}

export function ProfileScreen({ userId }: { userId: string }) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['profile', userId],
    queryFn: () => fetchProfile(userId),
    enabled: !!userId,   // skip if no userId
  });

  if (isLoading) return <ActivityIndicator />;
  if (error) return <Text>Error: {error.message}</Text>;

  return <Text>{data?.full_name}</Text>;
}
```

---

## useMutation — write data

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function UpdateProfileButton({ userId }: { userId: string }) {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: async (name: string) => {
      const { error } = await supabase
        .from('profiles')
        .update({ full_name: name })
        .eq('id', userId);
      if (error) throw error;
    },
    onSuccess: () => {
      // Invalidate so the profile refetches
      queryClient.invalidateQueries({ queryKey: ['profile', userId] });
    },
  });

  return (
    <Button
      title={isPending ? 'Saving...' : 'Save'}
      onPress={() => mutate('New Name')}
      disabled={isPending}
    />
  );
}
```

---

## Screen-level refetch on focus

When navigating back to a screen, refetch stale data using `useFocusEffect` (Expo Router / React Navigation):

```tsx
import { useFocusEffect } from 'expo-router';
import { useCallback } from 'react';

export function FeedScreen() {
  const { data, refetch } = useQuery({
    queryKey: ['feed'],
    queryFn: fetchFeed,
  });

  useFocusEffect(
    useCallback(() => {
      refetch();
    }, [refetch]),
  );

  return <FeedList data={data} />;
}
```

Or disable a query when the screen is not focused (prevents background polling on unfocused tabs):

```tsx
import { useIsFocused } from '@react-navigation/native';

const isFocused = useIsFocused();
const { data } = useQuery({
  queryKey: ['feed'],
  queryFn: fetchFeed,
  subscribed: isFocused,  // v5: replaces `enabled` for this pattern
});
```

---

## Pagination (infinite queries)

```tsx
import { useInfiniteQuery } from '@tanstack/react-query';

const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
  queryKey: ['messages'],
  queryFn: ({ pageParam = 0 }) =>
    supabase
      .from('messages')
      .select('*')
      .order('created_at', { ascending: false })
      .range(pageParam, pageParam + 19)
      .then(({ data }) => data ?? []),
  getNextPageParam: (lastPage, allPages) =>
    lastPage.length === 20 ? allPages.flat().length : undefined,
  initialPageParam: 0,
});
```

---

## Persistence across app restarts

Use `@tanstack/query-async-storage-persister` to persist the query cache to AsyncStorage:

```bash
npx expo install @tanstack/react-query-persist-client @tanstack/query-async-storage-persister @react-native-async-storage/async-storage
```

```tsx
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';
import AsyncStorage from '@react-native-async-storage/async-storage';

const persister = createAsyncStoragePersister({
  storage: AsyncStorage,
  throttleTime: 1000,
});

export default function RootLayout() {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister }}
    >
      <Stack />
    </PersistQueryClientProvider>
  );
}
```

---

## Key defaults to know

| Default | Value | Why it matters |
|---|---|---|
| `staleTime` | 0 | Data is immediately considered stale; refetches on every mount |
| `gcTime` | 5 min | Cache lives 5 min after last observer unmounts |
| `retry` | 3 | Failed requests retry 3 times with exponential backoff |
| `refetchOnWindowFocus` | true | Triggers on web focus; **no effect on native** without `focusManager` wiring |

Set `staleTime` to something reasonable (e.g. `1000 * 60 * 5`) to avoid waterfalling refetches on navigation.

---

## Gotchas

- **`refetchOnWindowFocus` does nothing on native** — you must wire `AppState` to `focusManager` yourself (shown above).
- **`onlineManager` also doesn't auto-wire** — without `NetInfo`, query thinks the device is always online.
- **Query keys must be serializable.** Objects and arrays are fine; functions or class instances in query keys cause bugs.
- **Don't mix with SWR or Axios's own cache** — use one caching layer. TanStack Query is the cache; fetch/axios/supabase-js are the transport.
