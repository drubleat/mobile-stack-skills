---
title: Flutter package reference library — index
impact: MEDIUM
impactDescription: "Community-extensible flat reference; one file per Dart/Flutter package"
tags: flutter, packages, dart, index
---

# Package Reference Library

A flat, community-extensible reference for Dart/Flutter packages. Each file covers one package: version, install, core API with examples, gotchas.

**Format:** one file per package, named `<package_name>.md`.  
**Contributing:** fork → add `references/packages/<your_package>.md` → PR. No category decisions needed.

---

## Index

### Audio / Speech
| Package | Version | Purpose |
|---|---|---|
| [speech_to_text](speech_to_text.md) | 7.4.0 | On-device speech recognition (STT) |

### Internationalization
| Package | Version | Purpose |
|---|---|---|
| [intl](intl.md) | 0.20.2 | Date/number formatting, i18n messages |

### Platform / Device
| Package | Version | Purpose |
|---|---|---|
| [url_launcher](url_launcher.md) | 6.3.2 | Open URLs, tel:, email:, sms: |
| [connectivity_plus](connectivity_plus.md) | 7.1.1 | Network type detection + change stream |

### State Management
| Package | Version | Purpose |
|---|---|---|
| [provider](provider.md) | 6.1.5+1 | InheritedWidget wrapper, ChangeNotifier |

### Firebase (Flutter)
| Package | Version | Purpose |
|---|---|---|
| [firebase_auth](firebase_auth.md) | 6.5.2 | Firebase authentication (email, Google, Apple) |
| [firebase_storage](firebase_storage.md) | 13.4.2 | Firebase file storage |
| [firebase_messaging](firebase_messaging.md) | 16.3.0 | FCM push notifications |

### Supabase (Dart/Flutter)
| Package | Version | Purpose |
|---|---|---|
| [supabase_flutter](supabase_flutter.md) | 2.14.2 | Flutter wrapper for Supabase |
| [supabase_dart](supabase_dart.md) | 2.12.2 | Core Dart client (no Flutter dep) |
| [postgrest_dart](postgrest_dart.md) | 2.7.1 | PostgREST query builder |
| [storage_client](storage_client.md) | 2.5.6 | Supabase Storage Dart client |
| [functions_client](functions_client.md) | 2.6.2 | Supabase Edge Functions Dart client |

---

> For architectural patterns (how packages fit together), see the domain files:  
> [flutter/](../flutter/_index.md) · [firebase/](../firebase/_index.md) · [supabase/](../supabase/_index.md)
