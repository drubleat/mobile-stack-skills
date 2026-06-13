---
title: UI patterns: theming, responsive, platform adaptations
impact: MEDIUM-HIGH
impactDescription: "Material 3 ColorScheme.fromSeed is the 2024+ theming baseline; adaptive widgets prevent platform uncanny valley"
tags: flutter, ui, theming, material3, responsive
---

# UI patterns: theming, responsive, platform adaptations

## Theming with Material 3

```dart
// lib/core/theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  static const _seedColor = Color(0xFF6750A4);

  static ThemeData light() => ThemeData(
    colorScheme: ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: Brightness.light,
    ),
    useMaterial3: true,
    textTheme: _textTheme,
    cardTheme: const CardThemeData(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(16)),
      ),
    ),
  );

  static ThemeData dark() => ThemeData(
    colorScheme: ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: Brightness.dark,
    ),
    useMaterial3: true,
    textTheme: _textTheme,
  );

  static const _textTheme = TextTheme(
    displayLarge: TextStyle(fontSize: 57, fontWeight: FontWeight.w400),
    headlineMedium: TextStyle(fontSize: 28, fontWeight: FontWeight.w600),
    bodyLarge: TextStyle(fontSize: 16, height: 1.5),
    labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
  );
}

// In app.dart
MaterialApp.router(
  theme: AppTheme.light(),
  darkTheme: AppTheme.dark(),
  themeMode: ThemeMode.system,  // or use Riverpod provider for manual toggle
)
```

## Dynamic colors (Android 12+ wallpaper colors)

```yaml
dependencies:
  dynamic_color: ^1.7.0
```

```dart
DynamicColorBuilder(
  builder: (lightDynamic, darkDynamic) {
    return MaterialApp.router(
      theme: lightDynamic != null
          ? ThemeData(colorScheme: lightDynamic, useMaterial3: true)
          : AppTheme.light(),
      darkTheme: darkDynamic != null
          ? ThemeData(colorScheme: darkDynamic, useMaterial3: true)
          : AppTheme.dark(),
    );
  },
)
```

## Responsive layout

### LayoutBuilder for widget-level breakpoints

```dart
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth > 600) {
      return Row(
        children: [Sidebar(), Expanded(child: Content())],
      );
    }
    return Content();
  },
)
```

### MediaQuery for screen-level decisions

```dart
final screenWidth = MediaQuery.sizeOf(context).width;
final isTablet = screenWidth > 600;
final padding = isTablet ? 32.0 : 16.0;
```

Use `MediaQuery.sizeOf(context)` (not `MediaQuery.of(context).size`) — it only rebuilds when size changes, not on every MediaQuery update.

### Safe area

```dart
Scaffold(
  body: SafeArea(
    child: YourContent(),
  ),
)
```

Always wrap content in `SafeArea` to avoid the notch, Dynamic Island, and home indicator.

## Platform-adaptive widgets

```dart
import 'dart:io' show Platform;

// Button style
Widget buildButton(String label, VoidCallback onTap) {
  if (Platform.isIOS) {
    return CupertinoButton.filled(onPressed: onTap, child: Text(label));
  }
  return FilledButton(onPressed: onTap, child: Text(label));
}

// Date picker
void showDatePicker(BuildContext context) {
  if (Platform.isIOS) {
    showCupertinoModalPopup(
      context: context,
      builder: (_) => CupertinoDatePicker(
        onDateTimeChanged: (date) {},
      ),
    );
  } else {
    showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime(2030),
    );
  }
}
```

## Loading states pattern

```dart
// Consistent loading UX across the app
class AsyncValueWidget<T> extends StatelessWidget {
  final AsyncValue<T> value;
  final Widget Function(T data) data;

  const AsyncValueWidget({required this.value, required this.data, super.key});

  @override
  Widget build(BuildContext context) {
    return value.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 8),
            Text(error.toString(), textAlign: TextAlign.center),
          ],
        ),
      ),
      data: data,
    );
  }
}

// Usage
AsyncValueWidget(
  value: ref.watch(profileProvider),
  data: (profile) => Text(profile['display_name']),
)
```

## Empty states

Always show something meaningful when lists are empty:

```dart
Widget buildList(List<Post> posts) {
  if (posts.isEmpty) {
    return const Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.article_outlined, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('No posts yet', style: TextStyle(fontSize: 18)),
          SizedBox(height: 8),
          Text('Your posts will appear here.', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
  return ListView.builder(
    itemCount: posts.length,
    itemBuilder: (_, i) => PostCard(post: posts[i]),
  );
}
```

## Gotchas

- `useMaterial3: true` is the default in Flutter 3.16+. Set it explicitly to avoid behavior changes when upgrading Flutter.
- `const` constructors for widgets are critical for performance — mark widgets `const` whenever possible to prevent unnecessary rebuilds.
- Platform checks with `Platform.isIOS` / `Platform.isAndroid` work at runtime only. Don't use them at the top level (before `runApp`) — use `defaultTargetPlatform` or `kIsWeb` alternatives for compile-time decisions.
