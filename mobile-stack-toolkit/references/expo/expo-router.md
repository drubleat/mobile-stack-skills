---
title: Expo Router — file-based navigation deep dive
impact: HIGH
impactDescription: "Navigation is the skeleton of every RN app; wrong route group / auth guard structure causes flicker, leaks protected screens, or breaks deep links"
tags: expo-router, navigation, routing, expo, react-native, auth, deep-linking
---

# Expo Router — Navigation Deep Dive

Expo Router is file-based routing for React Native (built on React Navigation). Every file in `app/` becomes a route; the file tree IS the navigation tree. This file is the complete reference; for the high-level state/auth-gating philosophy see [architecture.md](architecture.md).

**Requires:** Expo SDK 53+ for `Stack.Protected` (older SDKs use imperative redirects).

---

## The seven rules

1. **`app/` defines all routes.** A file at `app/settings.tsx` → route `/settings`.
2. **`app/index.tsx` is the entry route** (`/`).
3. **`app/_layout.tsx` replaces `App.tsx`** — root setup (providers, fonts, splash) goes here.
4. **`_layout.tsx` files define navigators** (Stack, Tabs) and persist UI across child routes.
5. **Non-route code lives outside `app/`** — put components/hooks in `components/`, `hooks/`, `lib/` or Expo Router treats them as routes.
6. **Route groups `(name)`** organize without affecting the URL.
7. **Every route is a deep link** automatically — `/user/42` works as a URL and an app link.

---

## File → route mapping

```
app/
├── _layout.tsx           → root navigator (Stack)
├── index.tsx             → /
├── settings.tsx          → /settings
├── (tabs)/               → route group (no URL segment)
│   ├── _layout.tsx       → Tabs navigator
│   ├── index.tsx         → /          (home tab)
│   ├── search.tsx        → /search
│   └── profile.tsx       → /profile
├── post/
│   ├── [id].tsx          → /post/:id  (dynamic)
│   └── [...rest].tsx     → /post/*    (catch-all)
└── +not-found.tsx        → 404 fallback
```

| Pattern | Meaning |
|---|---|
| `(group)` | Route group — organizes files, **not** in the URL |
| `[param]` | Dynamic segment — `app/post/[id].tsx` → `/post/123` |
| `[...rest]` | Catch-all — matches any remaining segments |
| `_layout.tsx` | Defines a navigator + shared UI for that directory |
| `+not-found.tsx` | Unmatched route fallback |
| `+html.tsx` | Web-only root HTML (web target) |

---

## Navigating — declarative (`Link`)

```tsx
import { Link } from 'expo-router';

// Static
<Link href="/settings">Settings</Link>

// Dynamic route with typed params (preferred — type-safe)
<Link href={{ pathname: '/post/[id]', params: { id: post.id } }}>
  {post.title}
</Link>

// Query params
<Link href={{ pathname: '/search', params: { q: 'coffee' } }}>Search</Link>

// Wrap a custom component
<Link href="/profile" asChild>
  <Pressable>
    <Text>Profile</Text>
  </Pressable>
</Link>

// Relative
<Link href="./details">Details</Link>
```

---

## Navigating — imperative (`router`)

```tsx
import { useRouter } from 'expo-router';

function MyComponent() {
  const router = useRouter();

  router.push('/post/123');        // push onto the stack (back button returns)
  router.replace('/login');        // replace — no back (use after logout)
  router.navigate('/profile');     // navigate or unwind if already in stack
  router.back();                   // pop
  router.dismiss();                // dismiss a modal / stack group
  router.setParams({ q: 'tea' });  // update query params without navigating

  // With params object
  router.push({ pathname: '/post/[id]', params: { id: '123' } });
}
```

`replace` vs `push`: use **`replace`** for auth transitions (login → home, logout → login) so the back button doesn't return to a stale screen. Use **`push`** for normal forward navigation.

---

## Reading params

```tsx
// app/post/[id].tsx
import { useLocalSearchParams } from 'expo-router';

export default function Post() {
  const { id, q } = useLocalSearchParams<{ id: string; q?: string }>();
  // id from the [id] segment, q from a query param
}
```

`useLocalSearchParams` = params for **this** screen. `useGlobalSearchParams` = params from the URL globally (re-renders on any param change anywhere — use sparingly).

---

## Stack navigator

```tsx
// app/_layout.tsx
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack screenOptions={{ headerShown: true }}>
      <Stack.Screen name="index" options={{ title: 'Home' }} />
      <Stack.Screen name="post/[id]" options={{ title: 'Post' }} />
      <Stack.Screen
        name="modal"
        options={{ presentation: 'modal' }}
      />
    </Stack>
  );
}
```

---

## Tabs navigator

```tsx
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#6366f1' }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" color={color} size={size} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person" color={color} size={size} />
          ),
        }}
      />
    </Tabs>
  );
}
```

---

## Modals

A modal is just a screen with `presentation: 'modal'`.

```tsx
// app/_layout.tsx
<Stack>
  <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
  <Stack.Screen name="compose" options={{ presentation: 'modal' }} />
</Stack>
```

```tsx
// app/compose.tsx — dismiss pattern
import { router } from 'expo-router';

export default function Compose() {
  return (
    <View>
      <Button title="Cancel" onPress={() => router.back()} />
      {/* iOS: swipe down also dismisses. Android: back button. */}
    </View>
  );
}
```

Other presentations: `'modal'`, `'transparentModal'`, `'fullScreenModal'` (iOS), `'formSheet'`.

---

## Auth gating — the canonical pattern (SDK 53+)

Use `Stack.Protected` with a `guard` boolean. Protected routes can't be reached by client-side navigation when the guard is false — no per-screen checks, no flicker.

### 1. Session provider

```tsx
// lib/auth-context.tsx
import { createContext, useContext, type PropsWithChildren } from 'react';
import { useStorageState } from './useStorageState'; // expo-secure-store wrapper

const AuthContext = createContext<{
  signIn: (token: string) => void;
  signOut: () => void;
  session?: string | null;
  isLoading: boolean;
} | null>(null);

export function useSession() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useSession must be used within SessionProvider');
  return value;
}

export function SessionProvider({ children }: PropsWithChildren) {
  const [[isLoading, session], setSession] = useStorageState('session');

  return (
    <AuthContext.Provider
      value={{
        signIn: (token) => setSession(token),
        signOut: () => setSession(null),
        session,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
```

### 2. Root layout with protected routes

```tsx
// app/_layout.tsx
import { Stack } from 'expo-router';
import { SessionProvider, useSession } from '@/lib/auth-context';
import * as SplashScreen from 'expo-splash-screen';

SplashScreen.preventAutoHideAsync();

function RootNavigator() {
  const { session, isLoading } = useSession();

  // Keep splash up while restoring the session — avoids login flash
  useEffect(() => {
    if (!isLoading) SplashScreen.hideAsync();
  }, [isLoading]);

  if (isLoading) return null;

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Protected guard={!!session}>
        <Stack.Screen name="(app)" />
      </Stack.Protected>

      <Stack.Protected guard={!session}>
        <Stack.Screen name="sign-in" />
      </Stack.Protected>
    </Stack>
  );
}

export default function Root() {
  return (
    <SessionProvider>
      <RootNavigator />
    </SessionProvider>
  );
}
```

### File structure for this pattern

```
app/
├── _layout.tsx          → SessionProvider + protected Stack
├── sign-in.tsx          → public
└── (app)/               → protected group
    ├── _layout.tsx      → Tabs (or Stack)
    ├── index.tsx
    └── profile.tsx
```

**Why this beats per-screen guards:** logged-out users never mount `(app)` routes — no data fetch, no flicker, no leak. The guard is evaluated once at the navigator level.

### With Supabase auth

Replace `useStorageState` with the Supabase session listener:

```tsx
useEffect(() => {
  supabase.auth.getSession().then(({ data }) => setSession(data.session));
  const { data: sub } = supabase.auth.onAuthStateChange((_e, s) => setSession(s));
  return () => sub.subscription.unsubscribe();
}, []);
```

See [../supabase/auth.md](../supabase/auth.md) for the full Supabase session flow.

---

## Typed routes

Enable in `app.json` for autocomplete + compile-time checks on `href`:

```json
{
  "expo": {
    "experiments": {
      "typedRoutes": true
    }
  }
}
```

After this, `<Link href="/psot/123">` (typo) becomes a TypeScript error. Run `npx expo customize` / restart the type server to regenerate.

---

## Deep linking

Routes map to URLs automatically. Configure the scheme in `app.json`:

```json
{
  "expo": {
    "scheme": "myapp"
  }
}
```

Now `myapp://post/123` opens `app/post/[id].tsx` with `id=123`. For universal/app links (https), add `associatedDomains` (iOS) and `intentFilters` (Android) — see [../push/deep-linking.md](../push/deep-linking.md) if push deep links are involved.

---

## Gotchas

- **`Stack.Protected` needs SDK 53+.** On older versions, gate with an imperative `<Redirect href="/sign-in" />` in the layout — but upgrade if you can; the imperative pattern flickers.
- **Don't gate inside each screen.** It's leaky (screen mounts before redirect) and flickers. Gate at the navigator with `Stack.Protected` or route groups.
- **`useLocalSearchParams` returns strings.** A `[id]` param is always a string — `Number(id)` if you need a number.
- **Components in `app/` become routes.** A `app/components/Button.tsx` will be treated as a route `/components/Button`. Keep non-routes outside `app/`.
- **Route groups don't nest URLs** — `(tabs)/index.tsx` is `/`, not `/tabs`. Use them purely for organization and shared layouts.
- **Splash screen timing** — hide splash only AFTER the session is restored, or users see a login flash before being sent to the app.
- **`router.replace` after auth** — never `push` after login/logout, or the back button returns to a screen the user shouldn't see.
