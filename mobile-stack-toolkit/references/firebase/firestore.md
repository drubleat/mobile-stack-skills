---
title: "Firestore data and field authorization"
impact: HIGH
impactDescription: "Avoid incompatible APIs and unsafe mobile integration defaults"
tags: mobile, integration, correctness
---

# Firestore data and field authorization

Model collections around access/query patterns. Security Rules are not filters: queries must be compatible with the rule. Admin SDKs bypass client rules and require their own authorization. Standard Firestore supports collection-group queries; they do not require an Enterprise migration.

Use modular React Native Firebase APIs for modern versions:

```ts
import { getFirestore, doc, setDoc, updateDoc, serverTimestamp } from '@react-native-firebase/firestore';
const db = getFirestore();
await setDoc(doc(db, 'users', uid), {
  displayName: 'New user', plan: 'free', createdAt: serverTimestamp(),
});
await updateDoc(doc(db, 'users', uid), { displayName: 'Updated name' });
```

## Server-owned paid plan

```firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function owns(uid) {
      return request.auth != null && request.auth.uid == uid;
    }
    function validProfile(data) {
      return data.keys().hasAll(['displayName', 'plan', 'createdAt'])
        && data.keys().hasOnly(['displayName', 'plan', 'createdAt'])
        && data.displayName is string && data.displayName.size() <= 100
        && data.plan in ['free', 'pro', 'enterprise']
        && data.createdAt is timestamp;
    }
    match /users/{uid} {
      allow read: if owns(uid);
      allow create: if owns(uid) && validProfile(request.resource.data)
        && request.resource.data.plan == 'free'
        && request.resource.data.createdAt == request.time;
      allow update: if owns(uid) && validProfile(request.resource.data)
        && request.resource.data.diff(resource.data).affectedKeys().hasOnly(['displayName']);
      allow delete: if false; // account deletion is a separate authenticated server workflow
    }
  }
}
```

Restrict protected fields on **create and update**. Merely allowing `plan` values from an enum lets a new client choose `pro`. The server can reconcile billing state with the Admin SDK. Keep private and public fields in separate documents when readers differ; reads cannot hide selected fields.

## Query and lifecycle checks

- Use an appropriate composite index when the query requires it. Missing-index errors are failures with creation guidance, not empty successful result sets. Commit index configuration.
- Bound queries and paginate with a stable cursor. Collection reads do not recursively fetch subcollections.
- Unsubscribe snapshot listeners on disposal; surface listener errors. Transactions may rerun, so keep external side effects outside their callback.
- Native SDK offline persistence can retain personal data across account changes; define cache/sign-out behavior and test it.
- Emulator tests should reject creating a paid plan, changing it later, adding an unauthorized field, accessing another user, and unauthenticated access, while permitting valid profile edits.

For Flutter use `Firebase.initializeApp` before `FirebaseFirestore.instance`; `cloud_firestore` exposes `doc`, `set`, `update`, snapshots, transactions, and batches.

## Sources

Reviewed 2026-10-20: [Firestore field rules](https://firebase.google.com/docs/firestore/security/rules-fields), [RN Firebase migration](https://rnfirebase.io/migrating-to-v22).
