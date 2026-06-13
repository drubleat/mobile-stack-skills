---
title: Flutter — domain index
impact: MEDIUM-HIGH
impactDescription: "Routes to project setup, navigation, Supabase, push, RevenueCat, AI, UI, animations, networking, storage, and CI/CD"
tags: flutter, dart, index
---

# Flutter domain index

Flutter files in this domain cover production Flutter app development with the same tech stack: Supabase, Firebase, RevenueCat, and AI integration via Edge Functions.

## Package versions (pub.dev, 2026)

| Package | Version | Purpose |
|---|---|---|
| `flutter_riverpod` | 3.3.2 | State management |
| `go_router` | 17.3.0 | Navigation |
| `dio` | 5.9.2 | HTTP client |
| `supabase_flutter` | 2.14.2 | Supabase SDK |
| `purchases_flutter` | 10.2.3 | RevenueCat |
| `firebase_core` | 4.10.0 | Firebase base |
| `firebase_messaging` | 16.3.0 | FCM push |
| `firebase_crashlytics` | 5.2.3 | Crash reporting |
| `firebase_analytics` | 11.4.2 | Analytics |
| `firebase_remote_config` | 6.5.2 | Feature flags |
| `google_maps_flutter` | 2.17.1 | Maps |
| `lottie` | 3.3.3 | Lottie animations |
| `flutter_animate` | 4.5.2 | UI animations |
| `freezed` | 3.2.5 | Immutable models |
| `permission_handler` | 12.0.3 | Runtime permissions |
| `dio` | 5.9.2 | Networking |
| `cached_network_image` | latest | Image caching |

## Files in this domain

**Foundation**
- [project-setup.md](project-setup.md) — flutter create, folder structure, build flavors, Riverpod
- [navigation.md](navigation.md) — go_router routes, guards, deep links
- [networking.md](networking.md) — dio interceptors, auth headers, error handling
- [local-storage.md](local-storage.md) — shared_preferences + flutter_secure_storage

**Backend integration**
- [supabase-flutter.md](supabase-flutter.md) — supabase_flutter auth + database
- [revenuecat-flutter.md](revenuecat-flutter.md) — purchases_flutter paywalls + entitlements
- [push-firebase.md](push-firebase.md) — firebase_messaging + flutter_local_notifications
- [ai-integration.md](ai-integration.md) — AI via Supabase Edge Function proxy

**UI & Platform**
- [ui-patterns.md](ui-patterns.md) — theming, responsive layout, platform adaptations
- [animation.md](animation.md) — lottie, flutter_animate
- [maps.md](maps.md) — google_maps_flutter markers, polylines, permissions
- [image-media.md](image-media.md) — image_picker, cached_network_image, video

**Quality & CI**
- [testing.md](testing.md) — unit, widget, integration tests
- [cicd.md](cicd.md) — Codemagic vs GitHub Actions + flutter build
