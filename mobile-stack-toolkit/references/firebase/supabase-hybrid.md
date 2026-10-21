---
title: "Supabase and Firebase integration boundaries"
impact: HIGH
impactDescription: "Use supported APIs with explicit authorization and failure handling"
tags: mobile, integration, correctness
---

# Supabase and Firebase integration boundaries

Choose services based on the existing app. One possible split is Supabase Auth/Postgres/Storage plus Firebase messaging and observability; it is not a universal production standard. Avoid adding a second identity or database unless a concrete requirement justifies synchronization.

A Supabase JWT does not automatically authenticate Firebase Security Rules. If using Firestore/Storage alongside Supabase Auth, design a trusted identity bridge or a verified supported integration. Never disable rules to make mismatched credentials work.

Use modular Firebase APIs. After consent and sign-in, associate the intended non-sensitive user identifier with analytics/crash reporting; clear it on logout. Dispose auth listeners and handle errors without blocking the auth state callback.

Store push installations as separate records: user ID, installation ID, provider, token, platform, project/environment and last-seen time. Refresh only the matching installation. Updating every token row by user ID destroys multi-device delivery. Remove/reassign the installation on logout/account switch and enforce ownership with RLS. See [push setup](../push/fcm-setup.md) and [server sends](../push/server-send.md).

Treat Remote Config flags as presentation input. Enforce server authorization and usage limits in the backend. Keep native service config, build environments and backend endpoints aligned across development/staging/production. Test account switching, lost connectivity and stale token recovery.

## Sources

Reviewed 2026-10-20: [Supabase third-party auth](https://supabase.com/docs/guides/auth/third-party/overview), [Firebase auth rules](https://firebase.google.com/docs/rules/rules-and-auth), [modular migration](https://rnfirebase.io/migrating-to-v22).
