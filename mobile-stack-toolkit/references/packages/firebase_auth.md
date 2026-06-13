---
title: firebase_auth 6.5.2 — Firebase authentication
impact: HIGH
impactDescription: "Google/Apple sign-in, email/password, anonymous auth; auth state stream drives route guards"
tags: flutter, firebase, auth, google, apple
---

# firebase_auth — Firebase authentication

**Version:** 6.5.2  
**Platforms:** Android, iOS, macOS, Web, Windows

```yaml
dependencies:
  firebase_core: ^4.10.0
  firebase_auth: ^6.5.2
```

> For architectural patterns (Google/Apple native sign-in, Riverpod integration), see [../firebase/auth.md](../firebase/auth.md).

## Initialize

```dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';

// Firebase auto-initializes from google-services.json / GoogleService-Info.plist.
// Access the instance directly:
final auth = FirebaseAuth.instance;

// Or bind to a specific Firebase app:
final auth = FirebaseAuth.instanceFor(app: Firebase.app());
```

## Auth state stream

```dart
// Fires on: sign-in, sign-out, token refresh
auth.authStateChanges().listen((User? user) {
  if (user == null) {
    print('Signed out');
  } else {
    print('Signed in: ${user.uid}');
  }
});

// Current user (synchronous, null if not signed in)
final user = auth.currentUser;
```

## Email + password

```dart
// Sign up
try {
  final credential = await auth.createUserWithEmailAndPassword(
    email: email,
    password: password,
  );
  final user = credential.user!;
  await user.sendEmailVerification();
} on FirebaseAuthException catch (e) {
  if (e.code == 'email-already-in-use') { /* ... */ }
  if (e.code == 'weak-password') { /* ... */ }
}

// Sign in
final credential = await auth.signInWithEmailAndPassword(
  email: email,
  password: password,
);

// Password reset
await auth.sendPasswordResetEmail(email: email);

// Update password (requires recent sign-in)
await auth.currentUser!.updatePassword(newPassword);
```

## Google Sign-In

```dart
import 'package:google_sign_in/google_sign_in.dart';

Future<UserCredential> signInWithGoogle() async {
  final googleUser = await GoogleSignIn().signIn();
  final googleAuth = await googleUser!.authentication;

  final credential = GoogleAuthProvider.credential(
    accessToken: googleAuth.accessToken,
    idToken: googleAuth.idToken,
  );

  return auth.signInWithCredential(credential);
}
```

## Apple Sign-In

```dart
import 'package:sign_in_with_apple/sign_in_with_apple.dart';

Future<UserCredential> signInWithApple() async {
  final appleCredential = await SignInWithApple.getAppleIDCredential(
    scopes: [
      AppleIDAuthorizationScopes.email,
      AppleIDAuthorizationScopes.fullName,
    ],
  );

  final oauthCredential = OAuthProvider('apple.com').credential(
    idToken: appleCredential.identityToken,
    accessToken: appleCredential.authorizationCode,
  );

  return auth.signInWithCredential(oauthCredential);
}
```

## Phone authentication

```dart
await auth.verifyPhoneNumber(
  phoneNumber: '+905551234567',
  verificationCompleted: (credential) async {
    // Auto-verification on Android (SMS read)
    await auth.signInWithCredential(credential);
  },
  verificationFailed: (e) => print('Failed: ${e.message}'),
  codeSent: (verificationId, resendToken) {
    // Show OTP input field; store verificationId
    _verificationId = verificationId;
  },
  codeAutoRetrievalTimeout: (verificationId) {},
);

// After user enters OTP:
final credential = PhoneAuthProvider.credential(
  verificationId: _verificationId,
  smsCode: otpCode,
);
await auth.signInWithCredential(credential);
```

## User profile

```dart
final user = auth.currentUser!;

// Update display name and photo
await user.updateDisplayName('John Doe');
await user.updatePhotoURL('https://...');

// Read
print(user.uid);
print(user.email);
print(user.displayName);
print(user.emailVerified);
print(user.phoneNumber);

// Get fresh ID token (for backend calls)
final token = await user.getIdToken();        // refreshes if expired
final token = await user.getIdToken(true);    // force refresh
```

## Sign out

```dart
await auth.signOut();
// Also sign out of Google if using Google sign-in:
await GoogleSignIn().signOut();
```

## FirebaseAuthException codes

| Code | Meaning |
|---|---|
| `user-not-found` | No user with that email |
| `wrong-password` | Incorrect password |
| `email-already-in-use` | Email already registered |
| `weak-password` | Password too short |
| `invalid-email` | Email format invalid |
| `too-many-requests` | Rate limited — try again later |
| `network-request-failed` | No internet |

## Gotchas

- `authStateChanges()` fires on app start with the persisted session — show a loading state until first emission (it can be null briefly).
- ID tokens expire after **1 hour**. Call `getIdToken()` (which auto-refreshes) before every backend request; never cache raw tokens.
- Apple only returns `email` and `fullName` on the **first authorization**. Store them to Firestore/Supabase on first sign-in — they're null on subsequent sign-ins.
- Windows desktop Google Sign-In requires registering a client ID at [cloud.google.com](https://cloud.google.com) — the Google Sign-In Flutter plugin handles this differently on desktop vs mobile.
- Email verification is not enforced by Firebase by default — check `user.emailVerified` in your app if you want to require it.
