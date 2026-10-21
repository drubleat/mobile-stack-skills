---
title: "Maps: google_maps_flutter"
impact: MEDIUM
impactDescription: "Restrict native API keys, request location only when needed, and handle map/controller lifecycle"
tags: flutter, maps, google-maps, location
---

# Maps: google_maps_flutter

Resolve `google_maps_flutter` and `geolocator` against the app SDK; inspect their platform setup guides.

## Setup

### API keys

1. Google Cloud Console → APIs & Services → Enable **Maps SDK for Android** and **Maps SDK for iOS**.
2. Create API keys (separate keys for Android and iOS; restrict by platform).
3. Add to project:

```xml
<!-- android/app/src/main/AndroidManifest.xml, inside <application> -->
<meta-data
    android:name="com.google.android.geo.API_KEY"
    android:value="${MAPS_API_KEY}" />
```

In the native iOS AppDelegate, import `GoogleMaps` and call `GMSServices.provideAPIKey(...)` before registering plugins. Supply the Android manifest placeholder through Gradle; a Dart `--dart-define` does not automatically create a native manifest placeholder or configure the iOS SDK. Restrict Android keys by package **and signing certificate SHA-1** (including Play App Signing), iOS keys by bundle ID, and each key to the required APIs.

## Basic map

```dart
import 'package:google_maps_flutter/google_maps_flutter.dart';

GoogleMap(
  initialCameraPosition: const CameraPosition(
    target: LatLng(41.0082, 28.9784),  // Istanbul
    zoom: 13,
  ),
  onMapCreated: (GoogleMapController controller) {
    _controller.complete(controller);
  },
  myLocationEnabled: locationPermissionGranted, // app state; false until permission is granted
  myLocationButtonEnabled: true,
)
```

## Markers

```dart
final Set<Marker> _markers = {};

// Add a marker
_markers.add(Marker(
  markerId: const MarkerId('restaurant_1'),
  position: const LatLng(41.0082, 28.9784),
  infoWindow: const InfoWindow(
    title: 'My Restaurant',
    snippet: 'Tap for details',
  ),
  onTap: () => context.push('/restaurant/1'),
  icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueAzure),
));

// Custom marker icon from asset
final icon = await BitmapDescriptor.asset(
  const ImageConfiguration(size: Size(48, 48)),
  'assets/icons/restaurant_pin.png',
);

// Rebuild GoogleMap with new markers
setState(() {});
```

## Controlling camera

```dart
import 'dart:async';
import 'dart:math';

final Completer<GoogleMapController> _controller = Completer();

// Animate to position
Future<void> animateTo(LatLng target) async {
  final controller = await _controller.future;
  await controller.animateCamera(
    CameraUpdate.newLatLngZoom(target, 15),
  );
}

// Fit multiple markers in view
Future<void> fitMarkers(List<LatLng> positions) async {
  if (positions.isEmpty) return;
  if (positions.length == 1) {
    await animateTo(positions.single);
    return;
  }
  final controller = await _controller.future;
  final bounds = _boundsFromLatLng(positions);
  await controller.animateCamera(
    CameraUpdate.newLatLngBounds(bounds, 50.0),  // 50px padding
  );
}

LatLngBounds _boundsFromLatLng(List<LatLng> points) {
  final lats = points.map((p) => p.latitude);
  final lngs = points.map((p) => p.longitude);
  return LatLngBounds(
    southwest: LatLng(lats.reduce(min), lngs.reduce(min)),
    northeast: LatLng(lats.reduce(max), lngs.reduce(max)),
  );
}
```

This min/max bounds helper is for local points that do not cross the antimeridian. Handle date-line crossing separately. Fit bounds only after the map has a nonzero layout size, and dispose the retained controller when its owning screen is disposed.

## Polylines (routes)

```dart
Set<Polyline> _polylines = {
  Polyline(
    polylineId: const PolylineId('route'),
    points: routeCoordinates,   // List<LatLng>
    color: Colors.blue,
    width: 4,
    patterns: [PatternItem.dash(20), PatternItem.gap(10)],  // dashed
  ),
};

GoogleMap(
  polylines: _polylines,
  ...
)
```

## User location

```dart
import 'package:geolocator/geolocator.dart';  // separate package

Future<LatLng?> getCurrentLocation() async {
  if (!await Geolocator.isLocationServiceEnabled()) return null;
  var permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
  }
  if (permission != LocationPermission.always &&
      permission != LocationPermission.whileInUse) return null;

  final position = await Geolocator.getCurrentPosition(
    locationSettings: const LocationSettings(
      accuracy: LocationAccuracy.high, timeLimit: Duration(seconds: 15),
    ),
  );
  return LatLng(position.latitude, position.longitude);
}
```

Configure native foreground location permissions and iOS usage strings; handle disabled services, denied permission, timeout and approximate accuracy in the UI. A map without the location layer does not require location permission.

## Custom map style

```dart
final mapStyle = await rootBundle.loadString('assets/map_style.json');
// Pass the loaded JSON string as GoogleMap(style: mapStyle, ...).
// Use widget state to rebuild once loading completes.
```

Generate dark/custom map styles at [mapstyle.withgoogle.com](https://mapstyle.withgoogle.com).

## Performance with many markers

`google_maps_flutter` can handle hundreds of markers, but rendering thousands causes jank. Options:
- **Clustering**: use `google_maps_cluster_manager` package to group nearby markers.
- **Viewport filtering**: only add markers visible in the current camera bounds.
- **Custom tiles**: for very large datasets, use tile overlays instead of individual markers.

## Gotchas

- Diagnose native linker failures from the actual SDK setup and build logs; do not paste Xcode build-setting syntax into a Podfile.
- `myLocationEnabled: true` requires location permission to be granted first. Show the permission request before enabling this — if permission is denied, the map silently disables the "My Location" button.
- The map widget is heavy — avoid placing it in a list that frequently rebuilds. Use `const CameraPosition` and stable `MarkerId` values to minimize unnecessary redraws.
- Keys are extractable from mobile binaries. Platform and API restrictions reduce misuse; they do not turn embedded keys into secrets.

Reviewed 2026-10-21: [GoogleMap API](https://pub.dev/documentation/google_maps_flutter/latest/google_maps_flutter/GoogleMap-class.html), [geolocator setup](https://pub.dev/packages/geolocator).
