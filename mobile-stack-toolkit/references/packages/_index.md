---
title: "Flutter package reference library — index"
impact: MEDIUM
impactDescription: "Community-extensible flat reference; one file per Dart/Flutter package"
tags: flutter, packages, dart, index
---

# Package Reference Library

A flat, community-extensible reference for Dart/Flutter packages. Each file covers one package: version scope, install, core API with examples, gotchas.

**Format:** one file per package, named `<package_name>.md`.  
**Contributing:** fork → add `references/packages/<your_package>.md` → PR. No category decisions needed.

---

## Index

### Audio / Speech
| Package | Purpose |
|---|---|
| [speech_to_text](speech_to_text.md) | Platform speech recognition (STT) |

### Internationalization
| Package | Purpose |
|---|---|
| [intl](intl.md) | Date/number formatting, i18n messages |

### Platform / Device
| Package | Purpose |
|---|---|
| [url_launcher](url_launcher.md) | Open URLs, tel:, email:, sms: |
| [connectivity_plus](connectivity_plus.md) | Network type detection + change stream |

### State Management
| Package | Purpose |
|---|---|
| [provider](provider.md) | InheritedWidget wrapper, ChangeNotifier |

### Firebase (Flutter)
| Package | Purpose |
|---|---|
| [firebase_auth](firebase_auth.md) | Firebase authentication (email, Google, Apple) |
| [firebase_storage](firebase_storage.md) | Firebase file storage |
| [firebase_messaging](firebase_messaging.md) | FCM push notifications |

### Supabase (Dart/Flutter)
| Package | Purpose |
|---|---|
| [supabase_flutter](supabase_flutter.md) | Flutter wrapper for Supabase |
| [supabase_dart](supabase_dart.md) | Core Dart client (no Flutter dep) |
| [postgrest_dart](postgrest_dart.md) | PostgREST query builder |
| [storage_client](storage_client.md) | Supabase Storage Dart client |
| [functions_client](functions_client.md) | Supabase Edge Functions Dart client |

---

> For architectural patterns (how packages fit together), see the domain files:  
> [flutter/](../flutter/_index.md) · [firebase/](../firebase/_index.md) · [supabase/](../supabase/_index.md)
