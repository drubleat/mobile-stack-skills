# mobile-stack-toolkit

A Claude Code skill for production mobile development. Covers the full stack for AI-first, paywalled mobile apps — from project setup through App Store submission.

## Stack

| Layer | Technology |
|---|---|
| Mobile (React Native) | Expo SDK 56 + EAS Build/Update |
| Mobile (Flutter) | Flutter stable + FlutterFire |
| Database + Auth | Supabase (Postgres + RLS + Edge Functions) |
| Monetization | RevenueCat |
| AI | OpenAI Responses API + Google Gemini |
| Push | Firebase Cloud Messaging |
| Crash / Analytics | Firebase Crashlytics + Analytics |

## Installation

Add to your Claude Code project:

```bash
# Clone into your project's skills directory
git clone https://github.com/yourusername/mobile-stack-toolkit.git .claude/skills/mobile-stack-toolkit
```

Or reference it in your `CLAUDE.md`:

```md
@.claude/skills/mobile-stack-toolkit/SKILL.md
```

## What's covered

**Expo / React Native**
- SDK 56 project setup, Continuous Native Generation (CNG), EAS Build + EAS Update
- OTA update strategy with fingerprint policy
- Dev builds, config plugins, `useFrameworks: 'static'`

**Supabase**
- Schema design with RLS, security-definer functions, subscription tracking
- Auth (OTP, Google/Apple native sign-in with `signInWithIdToken`)
- Edge Functions (Deno.serve, webhook patterns, streaming)
- Realtime, Storage, local dev + migration workflow

**AI integration**
- OpenAI Responses API (multi-turn, vision, audio, image generation, tool use)
- Google Gemini 3.5 (text, vision, audio/TTS, Imagen 4, tool use)
- Prompt engineering, streaming, structured output, guardrails
- Edge Function proxy architecture (AI keys never in mobile bundle)

**Monetization**
- RevenueCat SDK v10 setup + paywall UI
- Subscription webhook → Supabase sync
- Two-layer entitlement model (client UI gating + server action gating)
- App Store / Play Store compliance

**Push notifications**
- Expo Push vs FCM decision matrix
- FCM setup (APNs Auth Key, foreground handler, deep linking)
- Server-side fan-out via Supabase Edge Functions

**Firebase**
- Crashlytics, Analytics, Remote Config
- Supabase + Firebase hybrid patterns (what to use from each)
- Firebase Auth + Firestore for standalone projects
- App Distribution for beta testing

**Flutter**
- Riverpod 3.x, go_router 17, dio 5.9, freezed
- supabase_flutter, purchases_flutter, firebase_messaging
- google_maps_flutter, lottie, flutter_animate
- Codemagic + GitHub Actions CI/CD

**Store submission**
- App Store Connect, TestFlight, EAS Submit
- Play Console, Data Safety form, release tracks
- Screenshot sizes, ASO strategy, common rejection reasons

**Playbooks**
- Zero-to-store build sequence
- AI-first hard paywall app recipe
- Cross-cutting gotchas (RC↔Supabase drift, Firebase iOS config, API key leakage)

## Usage

Once installed, Claude Code will use the skill when you ask about any of the covered technologies. The skill uses progressive disclosure — `SKILL.md` routes to domain `_index.md` files, which route to focused leaf files.

Example prompts that activate this skill:
- "Set up Expo SDK 56 with Supabase and RevenueCat"
- "Write a RevenueCat webhook Edge Function"
- "Implement Gemini 3.5 vision in my Flutter app"
- "Configure FCM push notifications for iOS"

## Structure

```
SKILL.md                   # master router (loaded by Claude Code)
references/
  expo/                    # 7 files: setup, EAS, OTA, architecture
  supabase/                # 8 files: auth, schema, RLS, edge functions
  ai/                      # 12+ files: OpenAI, Gemini, streaming, guardrails
  monetization/            # 7 files: RC setup, webhooks, testing
  push/                    # 6 files: FCM, APNs, server send, deep linking
  firebase/                # 9 files: Crashlytics, FCM, hybrid patterns
  flutter/                 # 14 files: Riverpod, navigation, maps, animations
  store/                   # 6 files: ASC, Play Console, ASO, rejections
  cicd/                    # 4 files: EAS Workflows, GitHub Actions, secrets
  playbooks/               # 3 files: zero-to-store, AI recipe, gotchas
```

## Contributing

Corrections and additions welcome — especially for version bumps, new SDK breaking changes, and store policy updates. Open a PR with the specific file changed and the source for the update.

## License

MIT — see [LICENSE](LICENSE).
