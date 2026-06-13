---
title: Firebase Auth: when to use vs Supabase Auth
impact: MEDIUM-HIGH
impactDescription: "Use Firebase Auth when already Firebase-standalone; Supabase Auth is simpler for Supabase-primary stacks"
tags: firebase, auth, oauth, google, apple
---

# Firebase Auth

## When to use Firebase Auth vs Supabase Auth

- **Firebase-standalone**: use Firebase Auth for all authentication — email/password, Google, Apple.
- **Supabase + Firebase hybrid**: use Supabase Auth. Only add Firebase Auth if you already have an existing Firebase user base to migrate from. Don't run two auth systems in parallel.

## Email / password (standalone)

```ts
import auth from '@react-native-firebase/auth';

// Sign up
const { user } = await auth().createUserWithEmailAndPassword(email, password);

// Sign in
const { user } = await auth().signInWithEmailAndPassword(email, password);

// Sign out
await auth().signOut();

// Listen for auth state changes
const unsubscribe = auth().onAuthStateChanged((user) => {
  if (user) {
    // user is signed in
  } else {
    // user is signed out
  }
});
// Call unsubscribe() on component unmount
```

## Google Sign-In

```bash
npx expo install @react-native-google-signin/google-signin
```

```ts
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import auth from '@react-native-firebase/auth';

GoogleSignin.configure({
  webClientId: 'YOUR_WEB_CLIENT_ID',  // from google-services.json oauth_client
});

async function signInWithGoogle() {
  await GoogleSignin.hasPlayServices();
  const { idToken } = await GoogleSignin.signIn();
  const credential = auth.GoogleAuthProvider.credential(idToken);
  return auth().signInWithCredential(credential);
}
```

## Apple Sign-In

```bash
npx expo install expo-apple-authentication
```

```ts
import * as AppleAuthentication from 'expo-apple-authentication';
import auth from '@react-native-firebase/auth';

async function signInWithApple() {
  const credential = await AppleAuthentication.signInAsync({
    requestedScopes: [
      AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
      AppleAuthentication.AppleAuthenticationScope.EMAIL,
    ],
  });
  const { identityToken } = credential;
  const appleCredential = auth.AppleAuthProvider.credential(identityToken);
  return auth().signInWithCredential(appleCredential);
}
```

Enable Apple Sign-In in Firebase Console → Authentication → Sign-in method → Apple.

## Get the current user's ID token (for backend calls)

```ts
const user = auth().currentUser;
if (user) {
  const token = await user.getIdToken();  // JWT, expires every hour
  // Send as Authorization: Bearer <token> header to your backend
}
```

## Auto-create user profile on first sign-in

```ts
auth().onAuthStateChanged(async (user) => {
  if (!user) return;
  
  // Check if Firestore profile exists; create if not
  const profileRef = firestore().collection('profiles').doc(user.uid);
  const doc = await profileRef.get();
  if (!doc.exists) {
    await profileRef.set({
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      createdAt: firestore.FieldValue.serverTimestamp(),
    });
  }
});
```

## Flutter — google_sign_in 7.x (breaking changes)

`google_sign_in 7.x` introduced breaking changes from 6.x. The patterns below are correct for **7.2.0+**.

```dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

final auth = FirebaseAuth.instance;

// Listen for auth state
auth.authStateChanges().listen((User? user) {
  if (user == null) print('signed out');
  else print('signed in: ${user.uid}');
});

// Email sign-in
final credential = await auth.signInWithEmailAndPassword(
  email: email,
  password: password,
);

// Google Sign-In — 7.x pattern
class AuthService {
  AuthService() {
    // REQUIRED in 7.x: must call initialize() before any sign-in
    // On web: skip — use signInWithPopup instead (web hangs if initialize() called without clientId)
    if (!kIsWeb) {
      GoogleSignIn.instance.initialize();
    }
  }

  Future<UserCredential?> signInWithGoogle() async {
    if (kIsWeb) {
      // Web: use Firebase Auth popup directly
      return await auth.signInWithPopup(GoogleAuthProvider());
    }

    // Mobile: 7.x uses authenticate() not signIn()
    final googleUser = await GoogleSignIn.instance.authenticate();
    if (googleUser == null) return null; // user cancelled

    final googleAuth = await googleUser.authentication;
    // 7.x: idToken only on initial auth; accessToken requires separate request
    final credential = GoogleAuthProvider.credential(idToken: googleAuth.idToken);
    return await auth.signInWithCredential(credential);
  }

  Future<void> signOut() async {
    // Web: skip GoogleSignIn.signOut() — it's not initialized on web
    if (!kIsWeb) {
      await GoogleSignIn.instance.signOut();
    }
    await auth.signOut();
  }
}
```

**Key 7.x changes vs 6.x:**
- `signIn()` → `authenticate()` (signIn is deprecated/removed)
- `initialize()` is now **required** before first use (do it in constructor or main())
- On web without `clientId` in `initialize()`, the app hangs with a blank screen
- `accessToken` is not included in initial auth — call `GoogleSignIn.instance.requestScopes()` separately if you need Google API access

## Gotchas

- `onAuthStateChanged` / `authStateChanges()` fires with `null` on app start while Firebase checks persistence. Show a loading state until the first emission.
- ID tokens expire after 1 hour. Always call `getIdToken()` (auto-refreshes) rather than caching the raw token.
- Apple Sign-In only returns `email` and `displayName` on the **first** authorization. Store them in Firestore on first sign-in; subsequent sign-ins won't include them.
- **google_sign_in 7.x**: `initialize()` must be called before any `authenticate()` call. Forgetting this causes a `PlatformException` at runtime, not compile time.
