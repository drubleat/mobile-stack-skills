---
title: Zustand + MMKV — state management & fast persistence
impact: MEDIUM-HIGH
impactDescription: "Zustand replaces Redux with minimal boilerplate; MMKV is ~30x faster than AsyncStorage for persisted state — wrong persist setup causes hydration flickers"
tags: zustand, mmkv, state-management, persistence, expo, react-native
---

# Zustand + MMKV

**Zustand** is a minimal React state management library. No providers, no boilerplate — just a hook. Use it for client-side UI state (auth user, theme, cart, form state). Use TanStack Query for server state.

**MMKV** is a C++ key-value store (~30x faster than AsyncStorage). It's the best persistence layer for Zustand in React Native.

**Zustand version:** 5.0.x | **MMKV version:** 4.x (requires RN 0.76+)

---

## Install

```bash
npx expo install zustand react-native-mmkv react-native-nitro-modules
npx expo prebuild  # required — MMKV has native code
```

MMKV requires a **Dev Build** — does not work in Expo Go.

---

## Basic store (no persistence)

```ts
// store/useCounterStore.ts
import { create } from 'zustand';

interface CounterState {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

export const useCounterStore = create<CounterState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));
```

Use in any component — no Provider needed:

```tsx
import { useCounterStore } from '@/store/useCounterStore';

export function Counter() {
  const { count, increment } = useCounterStore();
  return <Button title={`Count: ${count}`} onPress={increment} />;
}
```

---

## MMKV storage instance

```ts
// lib/storage.ts
import { createMMKV } from 'react-native-mmkv';

export const storage = createMMKV({ id: 'app-storage' });
```

Use directly for non-Zustand persistence (tokens, flags):

```ts
// Write
storage.set('onboarded', true);
storage.set('theme', 'dark');

// Read
const onboarded = storage.getBoolean('onboarded');  // boolean | undefined
const theme = storage.getString('theme');            // string | undefined

// Delete
storage.delete('onboarded');
```

---

## Zustand persist with MMKV

```ts
// store/useUserStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { storage } from '@/lib/storage';

interface UserState {
  userId: string | null;
  displayName: string | null;
  theme: 'light' | 'dark';
  setUser: (id: string, name: string) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  clear: () => void;
}

// Zustand persist storage adapter for MMKV
const mmkvStorage = createJSONStorage(() => ({
  setItem: (key: string, value: string) => storage.set(key, value),
  getItem: (key: string) => storage.getString(key) ?? null,
  removeItem: (key: string) => storage.delete(key),
}));

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      userId: null,
      displayName: null,
      theme: 'light',
      setUser: (id, name) => set({ userId: id, displayName: name }),
      setTheme: (theme) => set({ theme }),
      clear: () => set({ userId: null, displayName: null }),
    }),
    {
      name: 'user-store',   // MMKV key
      storage: mmkvStorage,
      // Only persist selected fields:
      partialize: (state) => ({
        userId: state.userId,
        displayName: state.displayName,
        theme: state.theme,
      }),
    },
  ),
);
```

---

## Handling hydration (avoid flicker)

On app launch, the persisted store rehydrates asynchronously. Check `_hasHydrated` before rendering authenticated content:

```ts
// Add to your store:
interface UserState {
  // ...existing fields
  _hasHydrated: boolean;
  _setHasHydrated: (value: boolean) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      _hasHydrated: false,
      _setHasHydrated: (value) => set({ _hasHydrated: value }),
      // ...rest
    }),
    {
      name: 'user-store',
      storage: mmkvStorage,
      onRehydrateStorage: () => (state) => {
        state?._setHasHydrated(true);
      },
    },
  ),
);
```

```tsx
// app/_layout.tsx
export default function RootLayout() {
  const hasHydrated = useUserStore((s) => s._hasHydrated);
  if (!hasHydrated) return <SplashScreen />;
  return <Stack />;
}
```

---

## Select individual fields (prevent re-renders)

```tsx
// ✅ Only re-renders when theme changes
const theme = useUserStore((state) => state.theme);

// ❌ Re-renders on any state change
const store = useUserStore();
```

---

## Outside React (services, callbacks)

Access the store outside components with `getState`:

```ts
import { useUserStore } from '@/store/useUserStore';

export async function handleAuthCallback(session: Session) {
  useUserStore.getState().setUser(session.user.id, session.user.email ?? '');
}
```

Subscribe to changes outside React:

```ts
const unsubscribe = useUserStore.subscribe(
  (state) => state.userId,
  (userId) => {
    if (!userId) router.replace('/login');
  },
);
// Call unsubscribe() to clean up
```

---

## Multiple stores (recommended pattern)

Keep stores small and focused — one concern per store:

```
store/
  useUserStore.ts      → auth user, display name, theme
  useCartStore.ts      → cart items (persisted with MMKV)
  useUIStore.ts        → modal visibility, loading states (no persistence needed)
  useSettingsStore.ts  → user preferences (persisted)
```

---

## MMKV encryption

For sensitive data (tokens, PII), enable AES encryption:

```ts
import { createMMKV } from 'react-native-mmkv';

export const secureStorage = createMMKV({
  id: 'secure-storage',
  encryptionKey: process.env.EXPO_PUBLIC_MMKV_KEY, // rotate per build via EAS secrets
});
```

Note: For auth tokens, prefer `expo-secure-store` (uses iOS Keychain / Android Keystore) over MMKV — it's more secure for credentials.

---

## Gotchas

- **MMKV requires a Dev Build.** `npx expo prebuild` must be run before using MMKV.
- **MMKV requires RN 0.76+** (Expo SDK 52+). It's a Nitro Module — the old `@rdlabo/react-native-mmkv` pre-Nitro API is different.
- **`partialize` is important.** Persisting action functions is harmless but wasteful — use `partialize` to persist only data fields.
- **Don't use `createJSONStorage(() => AsyncStorage)` for Zustand in new apps** — MMKV is significantly faster and more reliable.
- **Hydration is async even with MMKV.** It's fast but not synchronous — always guard with `_hasHydrated` for auth-gated screens.
