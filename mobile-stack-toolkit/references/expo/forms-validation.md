---
title: Forms & validation — react-hook-form + zod
impact: HIGH
impactDescription: "Every app has forms (login, signup, profile, checkout); the Controller + zod pattern prevents re-render storms and gives type-safe validation in one place"
tags: forms, react-hook-form, zod, validation, expo, react-native, typescript
---

# Forms & Validation — react-hook-form + zod

The standard React Native form stack: **react-hook-form** for state (uncontrolled, minimal re-renders) + **zod** for schema validation + **@hookform/resolvers** to bridge them. One schema gives you both runtime validation and a TypeScript type.

**Versions (June 2026):** `react-hook-form` v7.79.x, `zod` v4.4.x, `@hookform/resolvers` v5.x

---

## Install

```bash
npx expo install react-hook-form zod @hookform/resolvers
```

---

## Why `Controller` (not `register`) in React Native

`register` works by attaching to DOM refs — that's web-only. React Native `TextInput` is a controlled component, so you wrap each field in `<Controller>`, which connects `value`/`onChangeText` to the form state.

---

## Basic form

```tsx
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { View, TextInput, Text, Button } from 'react-native';

// 1. Schema — single source of truth
const loginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'At least 8 characters'),
});

// 2. Type inferred from the schema
type LoginForm = z.infer<typeof loginSchema>;

export function LoginScreen() {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  async function onSubmit(data: LoginForm) {
    // data is fully typed and validated here
    await supabase.auth.signInWithPassword(data);
  }

  return (
    <View>
      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            placeholder="Email"
            autoCapitalize="none"
            keyboardType="email-address"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
          />
        )}
      />
      {errors.email && <Text style={{ color: 'red' }}>{errors.email.message}</Text>}

      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            placeholder="Password"
            secureTextEntry
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
          />
        )}
      />
      {errors.password && (
        <Text style={{ color: 'red' }}>{errors.password.message}</Text>
      )}

      <Button
        title={isSubmitting ? 'Signing in...' : 'Sign In'}
        onPress={handleSubmit(onSubmit)}
        disabled={isSubmitting}
      />
    </View>
  );
}
```

---

## Reusable input component (recommended)

Repeating the full `Controller` block per field gets noisy. Extract a typed wrapper:

```tsx
// components/FormField.tsx
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { TextInput, Text, View, TextInputProps } from 'react-native';

type Props<T extends FieldValues> = {
  control: Control<T>;
  name: Path<T>;
  label?: string;
  error?: string;
} & TextInputProps;

export function FormField<T extends FieldValues>({
  control,
  name,
  label,
  error,
  ...inputProps
}: Props<T>) {
  return (
    <View className="mb-3">
      {label && <Text className="mb-1 text-gray-700">{label}</Text>}
      <Controller
        control={control}
        name={name}
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            className="border border-gray-300 rounded-lg px-3 py-2"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            {...inputProps}
          />
        )}
      />
      {error && <Text className="mt-1 text-red-500 text-sm">{error}</Text>}
    </View>
  );
}
```

Usage collapses to:

```tsx
<FormField
  control={control}
  name="email"
  label="Email"
  error={errors.email?.message}
  keyboardType="email-address"
  autoCapitalize="none"
/>
```

---

## Common zod patterns

```ts
const signupSchema = z
  .object({
    name: z.string().min(2, 'Name is too short'),
    email: z.string().email(),
    age: z.coerce.number().min(18, 'Must be 18+'),  // coerce: string input → number
    password: z.string().min(8),
    confirmPassword: z.string(),
    acceptTerms: z.boolean().refine((v) => v === true, 'You must accept the terms'),
    role: z.enum(['user', 'admin']),
    bio: z.string().max(160).optional(),
    website: z.string().url().or(z.literal('')),  // optional URL
  })
  // Cross-field validation
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],  // attach the error to this field
  });
```

`z.coerce.number()` is important for RN — `TextInput` always returns a string, so coerce it.

---

## Programmatic control

```tsx
const { setValue, getValues, reset, watch, trigger, setError } = useForm<LoginForm>({
  resolver: zodResolver(loginSchema),
});

setValue('email', 'prefilled@example.com');   // set a field
const email = getValues('email');             // read without subscribing
reset();                                       // clear form
reset({ email: 'x@y.com', password: '' });     // reset to specific values
const subscription = watch('email');           // subscribe to a field (re-renders)
await trigger('email');                        // manually validate a field
setError('email', { message: 'Already taken' }); // server-side error
```

### Surfacing server errors

When the backend rejects (e.g. "email already registered"), map it back to the field:

```tsx
async function onSubmit(data: SignupForm) {
  const { error } = await supabase.auth.signUp(data);
  if (error?.message.includes('already registered')) {
    setError('email', { message: 'This email is already in use' });
    return;
  }
}
```

---

## Keyboard handling

Wrap forms so the keyboard doesn't cover inputs:

```tsx
import { KeyboardAvoidingView, Platform, ScrollView } from 'react-native';

<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  style={{ flex: 1 }}
>
  <ScrollView keyboardShouldPersistTaps="handled">
    {/* form fields */}
  </ScrollView>
</KeyboardAvoidingView>
```

`keyboardShouldPersistTaps="handled"` lets a "Submit" tap register without first dismissing the keyboard.

---

## Validation timing

```tsx
useForm({
  resolver: zodResolver(schema),
  mode: 'onBlur',        // validate when field loses focus (good default for mobile)
  // 'onChange' — validate on every keystroke (can feel aggressive)
  // 'onSubmit' — validate only on submit (default)
  reValidateMode: 'onChange',  // after first error, re-check on each change
});
```

For mobile, `mode: 'onBlur'` is usually the best UX — errors appear after the user leaves a field, not while typing.

---

## Gotchas

- **Use `Controller`, never `register`, in React Native.** `register` is web/DOM-only and silently does nothing with `TextInput`.
- **zod v4 + older resolvers bug:** with `@hookform/resolvers` below v4, RN can throw `"expected a Zod schema"` and silently skip `onSubmit`. Fix: upgrade `@hookform/resolvers` to v5+, or as a fallback import `import * as z from 'zod/v3'`.
- **`z.coerce.number()` for numeric inputs** — `TextInput` returns strings; without coercion, number validations always fail.
- **`handleSubmit(onSubmit)` not `onSubmit`** — pass the wrapped handler to `onPress`, or validation never runs.
- **`defaultValues` should be set** — uncontrolled inputs without defaults can start as `undefined` and trigger React's controlled/uncontrolled warning.
- **Don't `watch()` everything** — `watch()` with no args subscribes to all fields and re-renders on every keystroke, defeating react-hook-form's performance advantage. Watch specific fields only.
