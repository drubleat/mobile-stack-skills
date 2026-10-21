---
title: "Firebase authentication: modular clients and native identity"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Firebase authentication: modular clients and native identity

Initialize the native app using [setup](setup-cli.md). React Native Firebase uses modular imports:

```ts
import { getAuth, onAuthStateChanged, signInWithEmailAndPassword } from '@react-native-firebase/auth';
const auth = getAuth();
const unsubscribe = onAuthStateChanged(auth, user => setUser(user));
// Dispose unsubscribe with the screen/provider lifecycle.
await signInWithEmailAndPassword(auth, email, password);
```

Show a loading state until initial restoration resolves. Catch sign-in failures and cancellation; do not log credentials. Use token-change listeners if backend requests must react to refreshed claims. Firebase Security Rules/server verification enforce access; a route guard is only UI.

For React Native Google sign-in, configure native client IDs and signing fingerprints, call `GoogleSignin.signIn()`, check its success result and read the ID token from the result shape documented by the installed package (modern releases use `result.data.idToken`). Convert it with `GoogleAuthProvider.credential` and call modular `signInWithCredential`.

For Apple native sign-in, generate a cryptographically random raw nonce, send its SHA-256 hash to Apple's authorization request and pass the raw nonce with the ID token to Firebase's Apple credential. Do not use the authorization code as an OAuth access token. Handle first-authorization-only profile fields and persist them without overwriting existing values with null.

## Flutter with google_sign_in 7

Initialize Firebase explicitly before accessing FirebaseAuth. Initialize the Google singleton once and await it before interactive authentication:

```dart
final google = GoogleSignIn.instance;
await google.initialize(serverClientId: webClientId);
// On a supported native platform, from the user's sign-in action:
final account = await google.authenticate();
final idToken = account.authentication.idToken;
if (idToken == null) throw StateError('Missing Google ID token');
await FirebaseAuth.instance.signInWithCredential(
  GoogleAuthProvider.credential(idToken: idToken),
);
```

This requires firebase_auth/google_sign_in imports and configured platform IDs. Authentication and API scope authorization are separate in v7; request extra scopes through `account.authorizationClient` only when needed. Web uses the documented Google sign-in button flow, not an assumed native `authenticate()` implementation. Handle `GoogleSignInException`, including cancellation.

For Flutter Apple use Firebase's supported provider flow or the documented nonce-based native credential flow. See the official platform example before implementing account linking/re-authentication. Enforce email verification in Rules/server code when required, and implement account deletion including provider revocation where applicable.

## Sources

Reviewed 2026-10-20: [RN social auth](https://rnfirebase.io/auth/social-auth), [Flutter federated auth](https://firebase.google.com/docs/auth/flutter/federated-auth), [google_sign_in](https://pub.dev/packages/google_sign_in).
