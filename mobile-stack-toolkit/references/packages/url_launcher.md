---
title: url_launcher 6.3.2 — open URLs, tel:, email:, sms:
impact: LOW-MEDIUM
impactDescription: "canLaunchUrl check required before launch; iOS requires URL scheme declarations in Info.plist"
tags: flutter, url, browser, deep-linking
---

# url_launcher — open URLs, tel:, email:, sms:

**Version:** 6.3.2  
**Platforms:** Android, iOS, Linux, macOS, Web, Windows

```yaml
dependencies:
  url_launcher: ^6.3.2
```

## iOS: add query schemes (required for canLaunchUrl)

```xml
<!-- ios/Runner/Info.plist -->
<key>LSApplicationQueriesSchemes</key>
<array>
  <string>tel</string>
  <string>mailto</string>
  <string>sms</string>
  <string>https</string>
</array>
```

## Launch a URL

```dart
import 'package:url_launcher/url_launcher.dart';

Future<void> openUrl(String url) async {
  final uri = Uri.parse(url);
  if (!await canLaunchUrl(uri)) {
    throw Exception('Cannot launch $url');
  }
  await launchUrl(uri);
}
```

## Launch modes

```dart
// Opens in the device's default external browser (recommended for web URLs)
await launchUrl(uri, mode: LaunchMode.externalApplication);

// Opens inside the app with a browser chrome (back button, URL bar)
await launchUrl(uri, mode: LaunchMode.inAppBrowserView);

// Opens inside the app as a WebView (no browser chrome)
await launchUrl(uri, mode: LaunchMode.inAppWebView);

// Let the platform decide (default)
await launchUrl(uri, mode: LaunchMode.platformDefault);

// Close an in-app WebView/browser
await closeInAppWebView();
```

`externalApplication` is the safest choice for external links — respects the user's default browser preferences.

## Common URL schemes

```dart
// Open a web URL
await launchUrl(Uri.parse('https://example.com'));

// Phone call
final tel = Uri(scheme: 'tel', path: '+905551234567');
if (await canLaunchUrl(tel)) await launchUrl(tel);

// SMS
final sms = Uri(scheme: 'sms', path: '+905551234567');
await launchUrl(sms);

// Email
final email = Uri(
  scheme: 'mailto',
  path: 'support@example.com',
  queryParameters: {
    'subject': 'App feedback',
    'body': 'Hi,',
  },
);
await launchUrl(email);

// Map location (opens in Google Maps / Apple Maps)
final maps = Uri.parse('https://maps.google.com/?q=41.0082,28.9784');
await launchUrl(maps, mode: LaunchMode.externalApplication);

// App Store
await launchUrl(Uri.parse('https://apps.apple.com/app/id1234567890'));
await launchUrl(Uri.parse('market://details?id=com.yourcompany.app'));
```

## Check availability first

Web URLs (`https://`) are always launchable — skip `canLaunchUrl`. For `tel:`, `sms:`, and custom schemes, always check:

```dart
final uri = Uri(scheme: 'tel', path: '123');
final canCall = await canLaunchUrl(uri);
if (canCall) {
  await launchUrl(uri);
} else {
  // Show "calling not available on this device"
}
```

## Link widget (tap-to-open)

```dart
import 'package:url_launcher/link.dart';

Link(
  uri: Uri.parse('https://example.com'),
  target: LinkTarget.blank,
  builder: (context, followLink) => GestureDetector(
    onTap: followLink,
    child: Text(
      'Open website',
      style: TextStyle(
        color: Colors.blue,
        decoration: TextDecoration.underline,
      ),
    ),
  ),
)
```

## Gotchas

- On iOS, `canLaunchUrl` for `tel:` and `sms:` requires adding the scheme to `LSApplicationQueriesSchemes` in `Info.plist` — without this it always returns `false`.
- On Android 11+, package visibility restrictions affect `canLaunchUrl`. Add an `<queries>` block to `AndroidManifest.xml` if you check for custom schemes.
- `LaunchMode.inAppWebView` has no navigation controls by default. Users can't navigate back easily — prefer `inAppBrowserView` for external links.
- `launchUrl` can throw on some platforms if the URL can't be handled. Always wrap in try/catch or check `canLaunchUrl` first.
