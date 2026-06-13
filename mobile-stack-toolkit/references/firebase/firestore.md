---
title: Cloud Firestore: data model, rules, queries
impact: MEDIUM-HIGH
impactDescription: "Document/collection model differs fundamentally from Postgres; security rules must mirror RLS discipline"
tags: firebase, firestore, nosql, rules, queries
---

# Cloud Firestore: data model, rules, queries

## Data model

Firestore is a document-oriented NoSQL database: **Collection → Document → Fields**. Documents can have subcollections.

```
/users/{uid}               → user profile document
/users/{uid}/posts/{id}    → subcollection of posts per user
/chats/{chatId}            → top-level chat document
/chats/{chatId}/messages/{id}  → subcollection of messages
```

Design rules:
- Keep documents small (< 1MB; aim for < 10KB). Large documents are slow to read.
- Queries can only filter/sort on fields within a single collection (no JOINs).
- Use subcollections for one-to-many relationships.
- Use top-level collections for cross-user queries (e.g. a global activity feed).

## Basic CRUD

```ts
import firestore from '@react-native-firebase/firestore';

// Create / set document
await firestore().collection('users').doc(uid).set({
  email: 'user@example.com',
  plan: 'free',
  createdAt: firestore.FieldValue.serverTimestamp(),
});

// Read document (one-time)
const doc = await firestore().collection('users').doc(uid).get();
if (doc.exists) console.log(doc.data());

// Update (merge — doesn't overwrite whole document)
await firestore().collection('users').doc(uid).update({
  plan: 'pro',
  updatedAt: firestore.FieldValue.serverTimestamp(),
});

// Delete
await firestore().collection('users').doc(uid).delete();
```

## Real-time listener

```ts
const unsubscribe = firestore()
  .collection('posts')
  .where('authorId', '==', uid)
  .orderBy('createdAt', 'desc')
  .limit(20)
  .onSnapshot((snapshot) => {
    const posts = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
    setPosts(posts);
  });

// Cleanup on unmount
useEffect(() => {
  return unsubscribe;
}, []);
```

## Queries and indexes

Firestore supports equality filters on multiple fields. Compound queries (multiple `where` clauses or `orderBy` + `where`) require a **composite index**. The Firebase console error message will include a link to create the missing index.

```ts
// This requires a composite index on (category, createdAt):
firestore()
  .collection('posts')
  .where('category', '==', 'recipes')
  .orderBy('createdAt', 'desc')
  .get()
```

## Batch writes and transactions

```ts
// Batch: multiple writes in one atomic operation (no reads)
const batch = firestore().batch();
batch.set(firestore().collection('posts').doc(), { title: 'Post A' });
batch.update(firestore().collection('users').doc(uid), { postCount: firestore.FieldValue.increment(1) });
await batch.commit();

// Transaction: read + write atomically
await firestore().runTransaction(async (tx) => {
  const userDoc = await tx.get(firestore().collection('users').doc(uid));
  const currentCount = userDoc.data()?.postCount ?? 0;
  tx.update(firestore().collection('users').doc(uid), { postCount: currentCount + 1 });
});
```

## Security rules

Firestore rules live in `firestore.rules`. Deploy with:

```bash
npx -y firebase-tools@latest deploy --only firestore:rules
```

### Core principles (from Firebase's security-rules-auditor)

1. **Default deny** — start with denying everything, allow only what's needed
2. **Validate on BOTH create AND update** — the most common bypass is validating only on create
3. **Never trust user-provided role/ownership fields** — always derive from `request.auth.uid`
4. **Type-check fields** — use `is string`, `is int`, `is timestamp`
5. **Size limits** — add string length and array size constraints to prevent DoS

### Validator function pattern (required for production)

```firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // ── USERS ──────────────────────────────────────────────────────────
    function isValidUserData(data) {
      return data.keys().hasOnly(['email', 'displayName', 'plan', 'createdAt', 'updatedAt'])
        && data.email is string && data.email.size() < 256
        && data.displayName is string && data.displayName.size() < 100
        && data.plan in ['free', 'pro', 'enterprise'];
    }

    match /users/{uid} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow create: if request.auth != null
                    && request.auth.uid == uid
                    && isValidUserData(request.resource.data);
      // CRITICAL: validate on update too — users can't change their own uid/plan via client
      allow update: if request.auth != null
                    && request.auth.uid == uid
                    && isValidUserData(request.resource.data)
                    && request.resource.data.plan == resource.data.plan;  // plan only via server
      allow delete: if false;  // never allow client-side profile deletion
    }

    // ── POSTS ──────────────────────────────────────────────────────────
    function isValidPost(data) {
      return data.keys().hasOnly(['title', 'content', 'authorId', 'createdAt', 'updatedAt'])
        && data.title is string && data.title.size() > 0 && data.title.size() < 200
        && data.content is string && data.content.size() < 50000
        && data.authorId == request.auth.uid;  // enforce ownership in data
    }

    match /posts/{postId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null && isValidPost(request.resource.data);
      allow update: if request.auth != null
                    && resource.data.authorId == request.auth.uid  // owner check
                    && isValidPost(request.resource.data);
      allow delete: if request.auth != null && resource.data.authorId == request.auth.uid;
    }

    // ── USER SUBCOLLECTIONS ─────────────────────────────────────────────
    match /users/{uid}/messages/{msgId} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

### The update bypass (most common security hole)

```firestore
// ❌ WRONG — user can create with valid data, then update to set role='admin'
match /users/{uid} {
  allow create: if isValidUserData(request.resource.data);
  allow update: if request.auth.uid == uid;  // no data validation on update!
}

// ✅ CORRECT — same validator runs on both create and update
match /users/{uid} {
  allow create: if request.auth.uid == uid && isValidUserData(request.resource.data);
  allow update: if request.auth.uid == uid && isValidUserData(request.resource.data);
}
```

### Deploy and verify

```bash
# Deploy rules
npx -y firebase-tools@latest deploy --only firestore:rules

# Test rules locally with emulator
npx -y firebase-tools@latest emulators:start --only firestore
```

## Firestore editions (Standard vs Enterprise)

Supabase is not relevant here but Firestore has two editions:
- **Standard** — default, basic NoSQL
- **Enterprise** — native mode, higher throughput limits, collection group queries, better for large apps

Check which you have:
```bash
npx -y firebase-tools@latest firestore:databases:get '(default)'
```

New projects default to Standard. Migrate to Enterprise via `firestore:databases:create --edition=enterprise` if you need collection group queries or > 1M writes/day.

## Offline support

Firestore caches documents locally automatically. Reads from cache when offline, writes queue and sync when reconnected. No configuration needed — this is on by default in the RN SDK.

## Flutter

```dart
import 'package:cloud_firestore/cloud_firestore.dart';

final db = FirebaseFirestore.instance;

// Write
await db.collection('users').doc(uid).set({
  'email': email,
  'createdAt': FieldValue.serverTimestamp(),
});

// Real-time stream
StreamBuilder<DocumentSnapshot>(
  stream: db.collection('users').doc(uid).snapshots(),
  builder: (context, snapshot) {
    if (!snapshot.hasData) return const CircularProgressIndicator();
    final data = snapshot.data!.data() as Map<String, dynamic>?;
    return Text(data?['email'] ?? '');
  },
)
```

## Gotchas

- `serverTimestamp()` fields appear as `null` in the snapshot immediately after a write (before the server acknowledges). Store local timestamps separately if you need to display them immediately.
- Queries are shallow — they only return documents in the matched collection, not subcollections.
- `limit()` applies after `orderBy`, so always combine them for pagination.
- Missing composite index → the query silently returns 0 results (or throws a permission-denied-like error). Check the console.
