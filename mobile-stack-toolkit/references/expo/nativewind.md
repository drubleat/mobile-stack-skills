---
title: NativeWind v4 — Tailwind CSS for React Native
impact: MEDIUM
impactDescription: "NativeWind lets you use Tailwind utility classes in React Native; wrong metro/babel config silently breaks className support"
tags: nativewind, tailwind, styling, expo, react-native, ui
---

# NativeWind v4

NativeWind v4 is a Tailwind CSS implementation for React Native. It uses the Tailwind compiler at build time and ships a CSS-in-JS runtime for native targets.

**Note:** v4 is a complete rewrite from v2. If you're migrating from v2, the setup is different.

---

## Install

```bash
npm install nativewind react-native-reanimated react-native-safe-area-context
npm install --save-dev tailwindcss@^3.4.17 prettier-plugin-tailwindcss@^0.5.11 babel-preset-expo
```

---

## Configure

### 1. `tailwind.config.js`

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,jsx,ts,tsx}', './components/**/*.{js,jsx,ts,tsx}'],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

### 2. `global.css`

Create at the root of your project:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 3. `babel.config.js`

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ['babel-preset-expo', { jsxImportSource: 'nativewind' }],
    ],
    plugins: ['nativewind/babel'],
  };
};
```

### 4. `metro.config.js`

```js
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: './global.css' });
```

### 5. TypeScript support

Create `nativewind-env.d.ts` in the project root:

```ts
/// <reference types="nativewind/types" />
```

### 6. Import `global.css` in your root layout

```tsx
// app/_layout.tsx
import '../global.css';
```

---

## Usage

Use `className` just like Tailwind on the web. All React Native core components are supported.

```tsx
import { View, Text, Pressable } from 'react-native';

export function Card({ title, onPress }: { title: string; onPress: () => void }) {
  return (
    <View className="bg-white rounded-2xl p-4 shadow-sm mb-3">
      <Text className="text-lg font-semibold text-gray-900">{title}</Text>
      <Pressable
        className="mt-3 bg-indigo-600 rounded-xl py-2 px-4 active:opacity-70"
        onPress={onPress}
      >
        <Text className="text-white font-medium text-center">Open</Text>
      </Pressable>
    </View>
  );
}
```

---

## Dark mode

NativeWind reads the system color scheme via `useColorScheme`:

```tsx
import { useColorScheme } from 'nativewind';

export function ThemeToggle() {
  const { colorScheme, toggleColorScheme } = useColorScheme();
  return (
    <Pressable onPress={toggleColorScheme}>
      <Text className="text-gray-900 dark:text-white">
        {colorScheme === 'dark' ? 'Light mode' : 'Dark mode'}
      </Text>
    </Pressable>
  );
}
```

Use `dark:` prefix in classNames:

```tsx
<View className="bg-white dark:bg-gray-900 p-4">
  <Text className="text-black dark:text-white">Hello</Text>
</View>
```

---

## Conditional classes

Use a utility like `clsx` or plain template strings:

```tsx
import clsx from 'clsx';

<View className={clsx('p-4 rounded-xl', isActive ? 'bg-indigo-600' : 'bg-gray-100')} />
```

---

## Custom theme values

Add custom colors, spacing, fonts in `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      brand: '#6366f1',
      surface: '#f9fafb',
    },
    fontFamily: {
      sans: ['Inter-Regular', 'sans-serif'],
      bold: ['Inter-Bold', 'sans-serif'],
    },
  },
},
```

Then use as `bg-brand`, `font-bold`, etc.

---

## Gotchas

- **`className` not working?** Check that `nativewind/babel` is in `plugins` AND `jsxImportSource: 'nativewind'` is in the babel preset options. Both are required.
- **Clear Metro cache** after any config change: `npx expo start --clear`.
- **Tailwind v4 is NOT supported** — NativeWind v4 requires Tailwind v3 (`^3.4.17`). Don't upgrade to Tailwind v4 until NativeWind explicitly supports it.
- **Web support** requires `react-dom` and `@expo/webpack-config` or the Expo web metro config. The className prop works natively on web targets.
- **`prettier-plugin-tailwindcss`** sorts class names automatically in your editor — not required at runtime, but recommended for team consistency.
- `react-native-reanimated` must be installed because NativeWind's animation utilities depend on it, even if you don't use animations directly.
