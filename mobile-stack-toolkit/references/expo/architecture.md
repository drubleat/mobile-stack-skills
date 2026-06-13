---
title: App architecture: state, navigation, auth gating
impact: HIGH
impactDescription: "Auth gate pattern prevents authenticated screens flashing before redirect; Zustand + React Query is the minimal correct stack"
tags: expo, architecture, state, navigation, auth
---

# App architecture: state, navigation, auth gating

Patterns for structuring an Expo app so it stays sane as it grows. None of this assumes Supabase specifically — swap in any auth/backend; the shapes hold.

## State management — split by *kind* of state

The single most common mistake is using one tool for everything. Split it:

| State kind | Tool | Examples |
|---|---|---|
| **Server state** (lives in your backend, cached on client) | **TanStack Query** (`@tanstack/react-query`) | user's items, remote config, AI results |
| **Client/UI state** (ephemeral, local) | **Zustand** (or React context for tiny cases) | theme, modal open, draft form, wizard step |

- **TanStack Query** handles fetching, caching, retries, background refetch, and invalidation. Stop hand-rolling `useEffect` + `useState` fetch logic. Mutations + `queryClient.invalidateQueries` keep the UI fresh after writes.
- **Zustand** is a tiny global store with no provider boilerplate — ideal for app-wide UI state and cross-screen flags. Prefer it over Redux for new apps unless you have a specific reason.
- Avoid putting server data in Zustand; you'll reinvent caching badly. Avoid Context for frequently-changing values (re-render storms).

## Singletons in `lib/`

Initialize clients **once** and import them everywhere:

```ts
// lib/supabase.ts (or your backend client)
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const supabase = createClient(
  process.env.EXPO_PUBLIC_SUPABASE_URL!,
  process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!,
  { auth: { storage: AsyncStorage, persistSession: true, autoRefreshToken: true } },
);
```

Do the same for RevenueCat (`lib/revenuecat.ts`) and your AI client (`lib/ai.ts`, which only ever calls your Edge Function).

## Navigation & auth gating with expo-router

Use route groups and a **single gate in the root layout** rather than scattering auth checks across screens.

```tsx
// app/_layout.tsx
export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>          {/* exposes { session, loading } */}
        <RootNavigator />
      </AuthProvider>
    </QueryClientProvider>
  );
}

function RootNavigator() {
  const { session, loading } = useAuth();
  if (loading) return <SplashScreen />;
  return (
    <Stack>
      <Stack.Protected guard={!!session}>
        <Stack.Screen name="(tabs)" />
      </Stack.Protected>
      <Stack.Protected guard={!session}>
        <Stack.Screen name="(auth)" />
      </Stack.Protected>
    </Stack>
  );
}
```

The pattern: keep `(auth)/` and `(tabs)/` (or `(app)/`) as separate route groups, render one or the other based on session. expo-router's `Stack.Protected` guards (or an imperative `redirect` in a layout effect on older setups) prevent authenticated routes from mounting for logged-out users. Don't gate inside each screen — it's leaky and flickers.

## Auth flow specifics

- Drive UI off an `onAuthStateChange`-style subscription, not a one-time fetch, so login/logout reflects instantly.
- Persist the session in `AsyncStorage` (above) so users stay logged in across launches.
- Store *secrets the client legitimately needs* (rare) in `expo-secure-store`, not AsyncStorage.
- Deep links into protected screens should resolve *after* the gate — handle the redirect target post-auth. Push notification deep links follow the same rule → [../push/deep-linking.md](../push/deep-linking.md).

## Where entitlements fit

Gate **features** on RevenueCat entitlements, but gate **server actions** on the server (Edge Function checks the `subscriptions` table). Client-side entitlement state is for UX only; never trust it for anything that costs you money → [../monetization/entitlement-checks.md](../monetization/entitlement-checks.md).

## Folder reminder

Routes in `app/`, reusable UI in `components/`, data hooks (`useItems`, `useEntitlement`) in `hooks/`, clients in `lib/`. Keep screens thin: they compose hooks + components, they don't fetch directly.
