---
title: ASO & store assets: screenshots, icon, keywords
impact: MEDIUM
impactDescription: "Keyword field (100 chars, iOS) is the highest-leverage ASO lever; screenshots drive 60%+ of conversion"
tags: store, aso, screenshots, icon, keywords, metadata
---

# ASO & store assets: screenshots, icon, keywords

## App icon

One source file → all sizes. Use a **1024×1024 PNG** (no transparency on iOS; Android allows transparency). EAS generates all required sizes from this file automatically:

```ts
// app.config.ts
icon: './assets/icon.png',              // iOS (1024×1024, no alpha)
android: {
  adaptiveIcon: {
    foregroundImage: './assets/adaptive-icon.png',   // Android adaptive icon foreground
    backgroundColor: '#FFFFFF',
  },
}
```

Android adaptive icons: the foreground is centered in a 108dp area with a 72dp "safe zone" for the visible part. Keep important content within the safe zone.

## Screenshots (required sizes — 2026)

### iOS (required device families)

| Device | Size (portrait) | Required? |
|---|---|---|
| iPhone 6.9" (16 Pro Max) | 1320×2868 px | ✅ Required |
| iPhone 6.7" (15 Plus, 14 Pro Max) | 1290×2796 px | ✅ Required |
| iPad 13" Pro | 2064×2752 px | Required if iPad supported |

Apple accepts screenshots from larger devices for smaller ones — submit 6.9" and it covers all iPhones. Submit at least 1 screenshot per device family you support. Maximum 10 screenshots per device.

### Android

- Minimum 2 screenshots required.
- Recommended: 1080×1920 px (portrait) or 1920×1080 px (landscape).
- No strict required sizes, but Play Console recommends 16:9 or 9:16 aspect ratio.

## Screenshot best practices

- **First screenshot = most important.** 70% of users don't scroll past the first two. Lead with your core value prop, not a login screen.
- Use **device frames** for iOS (Apple's official frames or Figma mockups). Apple recommends it but doesn't require it.
- **Localize screenshots** for major markets if you support multiple languages — it meaningfully improves conversion.
- Show the actual app, not marketing imagery — Apple rejects screenshots that don't accurately represent the UI.
- **Feature graphic** (Android): 1024×500 px — displayed at the top of your Play Store listing.

## App name, subtitle & keywords (iOS ASO)

| Field | Limit | Impact |
|---|---|---|
| **Name** | 30 chars | Highest keyword weight |
| **Subtitle** | 30 chars | High keyword weight |
| **Keywords** | 100 chars total | Comma-separated, no spaces after commas |
| **Description** | 4000 chars | Low keyword weight (mostly for conversion) |

ASO strategy:
1. Include your primary keyword in the **name** (e.g. "Calorie Counter — Meal Tracker").
2. Use the **subtitle** for a secondary keyword cluster ("AI Nutrition & Diet Journal").
3. **Keywords field**: don't repeat words already in name/subtitle; use singular forms only; separate by comma with no space.
4. Avoid competitor names in keywords — Apple may reject or remove them.

## Android ASO (Play Console)

- **Short description**: 80 chars — appears in search results.
- **Full description**: 4000 chars — keyword-indexed.
- **Title**: 30 chars.
- Play Store uses the full description for keyword indexing more heavily than Apple does.

## Promo text (iOS)

A 170-char field that sits above the description and can be changed **without a new app review** — useful for time-sensitive announcements ("🎉 Now with AI meal scanning!").
