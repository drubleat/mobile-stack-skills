---
title: Maps: google_maps_flutter 2.17.x
impact: MEDIUM
impactDescription: "API key must be restricted by bundle ID/package name before production; debug key works locally but breaks on device"
tags: flutter, maps, google-maps, location
---

# Maps: google_maps_flutter

Version: `google_maps_flutter: ^2.17.1`

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

```xml
<!-- ios/Runner/AppDelegate.swift (or AppDelegate.m) -->
<!-- Add before GeneratedPluginRegistrant: -->
GMSServices.provideAPIKey("YOUR_IOS_MAPS_API_KEY")
```

For Flutter with dart-define:

```dart
// lib/main.dart — iOS only
import 'package:google_maps_flutter/google_maps_flutter.dart';

// Call before runApp on iOS
if (Platform.isIOS) {
  // API key is injected via native AppDelegate, not Dart
}
```

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
  myLocationEnabled: true,
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
import 'package:permission_handler/permission_handler.dart';
import 'package:geolocator/geolocator.dart';  // separate package

Future<LatLng?> getCurrentLocation() async {
  final permission = await Permission.location.request();
  if (!permission.isGranted) return null;

  final position = await Geolocator.getCurrentPosition(
    desiredAccuracy: LocationAccuracy.high,
  );
  return LatLng(position.latitude, position.longitude);
}
```

Add `geolocator: ^13.0.0` to pubspec.yaml for location access.

## Custom map style

```dart
final mapStyle = await rootBundle.loadString('assets/map_style.json');
final controller = await _controller.future;
controller.setMapStyle(mapStyle);
```

Generate dark/custom map styles at [mapstyle.withgoogle.com](https://mapstyle.withgoogle.com).

## Performance with many markers

`google_maps_flutter` can handle hundreds of markers, but rendering thousands causes jank. Options:
- **Clustering**: use `google_maps_cluster_manager` package to group nearby markers.
- **Viewport filtering**: only add markers visible in the current camera bounds.
- **Custom tiles**: for very large datasets, use tile overlays instead of individual markers.

## Gotchas

- **iOS linker flag**: add `OTHER_LDFLAGS = $(inherited) -ObjC` to your iOS Podfile if you get runtime crashes.
- `myLocationEnabled: true` requires location permission to be granted first. Show the permission request before enabling this — if permission is denied, the map silently disables the "My Location" button.
- The map widget is heavy — avoid placing it in a list that frequently rebuilds. Use `const CameraPosition` and stable `MarkerId` values to minimize unnecessary redraws.
- API key restrictions: restrict your Android key to `com.yourcompany.app` and your iOS key to your bundle ID to prevent unauthorized usage.
