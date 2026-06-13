---
title: intl 0.20.2 — internationalization & date/number formatting
impact: LOW-MEDIUM
impactDescription: "DateFormat, NumberFormat, and message localization; requires initializeDateFormatting() before use"
tags: flutter, i18n, l10n, dates, numbers
---

# intl — internationalization & date/number formatting

**Version:** 0.20.2  
**Platforms:** all (Dart package, no native code)

```yaml
dependencies:
  intl: ^0.20.2
```

## Date formatting

```dart
import 'package:intl/intl.dart';
import 'package:intl/date_symbol_data_local.dart';

// Initialize locale data before formatting (async, call once)
await initializeDateFormatting('tr_TR', null);
await initializeDateFormatting('de_DE', null);

final now = DateTime.now();

// Named formats (locale-aware)
DateFormat.yMMMMd('tr_TR').format(now);       // '13 Haziran 2026'
DateFormat.yMd('en_US').format(now);           // '6/13/2026'
DateFormat.Hm('de_DE').format(now);            // '14:30'
DateFormat.yMMMMEEEEd('tr_TR').format(now);    // 'Cumartesi, 13 Haziran 2026'

// Custom pattern
DateFormat('dd.MM.yyyy HH:mm').format(now);    // '13.06.2026 14:30'
DateFormat('MMM d, yyyy').format(now);         // 'Jun 13, 2026'

// Parse a string
final date = DateFormat('dd/MM/yyyy').parse('13/06/2026');

// Relative time (for "3 days ago" use timeago package instead)
```

### Common date patterns

| Pattern | Result (en_US) |
|---|---|
| `DateFormat.yMd()` | 6/13/2026 |
| `DateFormat.yMMMMd()` | June 13, 2026 |
| `DateFormat.Hm()` | 14:30 |
| `DateFormat.jm()` | 2:30 PM |
| `DateFormat.yMMMd()` | Jun 13, 2026 |
| `DateFormat('dd.MM.yyyy')` | 13.06.2026 |

## Number formatting

```dart
// Currency
NumberFormat.currency(locale: 'tr_TR', symbol: '₺').format(1234.5);  // '₺1.234,50'
NumberFormat.currency(locale: 'en_US', symbol: '\$').format(1234.5);  // '\$1,234.50'
NumberFormat.compactCurrency(locale: 'en_US', symbol: '\$').format(12000);  // '\$12K'

// Decimal
NumberFormat('#,##0.00', 'en_US').format(1234.567);   // '1,234.57'
NumberFormat('###.0#', 'en_US').format(12.345);        // '12.35'

// Compact
NumberFormat.compact(locale: 'en_US').format(1200000); // '1.2M'
NumberFormat.compact(locale: 'tr_TR').format(1200000); // '1,2 Mn'

// Percentage
NumberFormat.percentPattern().format(0.875);            // '88%'
```

## Plural / gender messages (i18n)

```dart
// Pluralization
String itemCount(int count) => Intl.plural(
  count,
  zero: 'No items',
  one: 'One item',
  other: '$count items',
  name: 'itemCount',
  args: [count],
);

// Gender
String greet(String name, String gender) => Intl.gender(
  gender,
  male: 'Welcome, Mr. $name',
  female: 'Welcome, Ms. $name',
  other: 'Welcome, $name',
  name: 'greet',
  args: [name, gender],
);
```

## Set default locale

```dart
// Set globally once on app start (typically from device locale)
import 'package:flutter/material.dart';
final locale = WidgetsBinding.instance.platformDispatcher.locale;
Intl.defaultLocale = locale.toLanguageTag();   // e.g. 'tr-TR'

// Or temporary override for a specific call
Intl.withLocale('fr_FR', () => DateFormat.yMMMMd().format(DateTime.now()));
```

## Flutter l10n integration

For full Flutter localization (translated UI strings), use `flutter_localizations` and the `intl` package together with code generation:

```yaml
# pubspec.yaml
dependencies:
  flutter_localizations:
    sdk: flutter
  intl: ^0.20.2
flutter:
  generate: true  # enables code generation from .arb files
```

```json
// lib/l10n/app_en.arb
{
  "@@locale": "en",
  "helloWorld": "Hello World!",
  "itemCount": "{count, plural, =0{No items} =1{One item} other{{count} items}}",
  "@itemCount": { "placeholders": { "count": { "type": "int" } } }
}
```

```dart
// In MaterialApp
localizationsDelegates: AppLocalizations.localizationsDelegates,
supportedLocales: AppLocalizations.supportedLocales,

// Usage
AppLocalizations.of(context)!.helloWorld
```

## Gotchas

- `initializeDateFormatting(locale, null)` must be called before using `DateFormat` with that locale — otherwise you get an exception. Call it once at app start for each supported locale.
- `Intl.defaultLocale` is global state — setting it affects all `Intl` calls in the app. For per-widget locale, use `Intl.withLocale()`.
- The `intl` package's locale format uses underscores (`tr_TR`), but Flutter's `Locale` class uses hyphens (`tr-TR`). Convert: `locale.toLanguageTag().replaceAll('-', '_')`.
- Currency symbols are not automatically fetched from the locale — you must provide `symbol` explicitly.
