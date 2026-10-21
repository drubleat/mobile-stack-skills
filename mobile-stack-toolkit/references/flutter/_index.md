---
title: "Flutter — domain index"
impact: MEDIUM-HIGH
impactDescription: "Routes to project setup, navigation, Supabase, push, RevenueCat, AI, UI, animations, networking, storage, and CI/CD"
tags: flutter, dart, index
---

# Flutter domain index

Flutter files in this domain cover production Flutter app development with the same tech stack: Supabase, Firebase, RevenueCat, and AI integration via Edge Functions.

Resolve packages against the project's Flutter/Dart SDK and commit its lockfile. The domain index is a router, not a synchronized package version matrix. Preserve existing state/navigation choices unless a migration is requested.

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
