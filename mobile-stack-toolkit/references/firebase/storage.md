---
title: "Firebase Storage: upload and access boundaries"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Firebase Storage: upload and access boundaries

Use modular RN Firebase APIs (`getStorage`, `ref`, `putFile`, `getDownloadURL`) or Flutter's `FirebaseStorage.instance.ref`. Check picker cancellation, actual MIME/size and upload completion/errors. A local path is not automatically supported on every platform; follow the native SDK's file/byte contract.

A Firebase download URL contains a bearer download token. It is not a short-lived signed URL and can remain usable by anyone holding it independently of later rules changes. Use authenticated SDK reads for private content or a deliberately designed short-lived serving endpoint. Rotate/revoke tokens or delete objects when invalidating shared links.

Rules example for owner-managed images (adapt size/type policy):

```text
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{uid}/{path=**} {
      function owner() { return request.auth != null && request.auth.uid == uid; }
      allow read, delete: if owner();
      allow create, update: if owner()
        && request.resource.size <= 5 * 1024 * 1024
        && request.resource.contentType.matches('image/(jpeg|png|webp)');
    }
  }
}
```

Delete has no incoming resource, so keep its rule separate from upload validation. MIME metadata is not malware/content verification; validate actual bytes in a trusted pipeline when required. Test unauthenticated access, cross-user access, oversize/invalid uploads, overwrite and deletion with the Rules emulator.

Use resumable transfers/cancellation when the SDK supports them, clean abandoned uploads, and track metadata writes independently so partial failures can be repaired. Never store service-account credentials in a mobile app.

## Sources

Reviewed 2026-10-20: [RN Storage](https://rnfirebase.io/storage/usage), [Storage Rules](https://firebase.google.com/docs/storage/security).
