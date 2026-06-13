---
title: Image & media: image_picker + cached_network_image
impact: MEDIUM
impactDescription: "iOS requires NSPhotoLibraryUsageDescription or App Review rejects; CachedNetworkImage prevents redundant downloads"
tags: flutter, images, media, image-picker, caching
---

# Image & media: image_picker + cached_network_image

## image_picker

```yaml
dependencies:
  image_picker: ^1.1.2
```

### iOS Info.plist strings (required)

```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>We access your photo library to let you upload images.</string>
<key>NSCameraUsageDescription</key>
<string>We use the camera to capture images for analysis.</string>
<key>NSMicrophoneUsageDescription</key>
<string>We use the microphone to record video.</string>
```

For Flutter (not Expo), add these directly to `ios/Runner/Info.plist`.

### Pick image

```dart
import 'package:image_picker/image_picker.dart';

final picker = ImagePicker();

// From gallery
final image = await picker.pickImage(
  source: ImageSource.gallery,
  maxWidth: 1024,
  maxHeight: 1024,
  imageQuality: 85,       // 0–100 JPEG quality
);

// From camera
final photo = await picker.pickImage(source: ImageSource.camera);

if (image != null) {
  final bytes = await image.readAsBytes();
  final path = image.path;    // local file path
}
```

### Pick multiple images

```dart
final images = await picker.pickMultiImage(
  maxWidth: 1024,
  imageQuality: 80,
);
for (final image in images) {
  // process each
}
```

### Pick video

```dart
final video = await picker.pickVideo(
  source: ImageSource.gallery,
  maxDuration: const Duration(minutes: 2),
);
```

### Upload to Supabase Storage

```dart
Future<String> uploadImage(XFile image, String userId) async {
  final bytes = await image.readAsBytes();
  final fileName = '${userId}/${DateTime.now().millisecondsSinceEpoch}.jpg';

  await Supabase.instance.client.storage
      .from('user-images')
      .uploadBinary(fileName, bytes, fileOptions: const FileOptions(
        contentType: 'image/jpeg',
        upsert: true,
      ));

  final url = Supabase.instance.client.storage
      .from('user-images')
      .getPublicUrl(fileName);

  return url;
}
```

---

## cached_network_image

```yaml
dependencies:
  cached_network_image: ^3.4.1
```

Caches remote images to disk automatically. Avoids re-downloading images on every widget rebuild.

### Basic usage

```dart
import 'package:cached_network_image/cached_network_image.dart';

CachedNetworkImage(
  imageUrl: 'https://example.com/avatar.jpg',
  placeholder: (context, url) => const CircleAvatar(
    backgroundColor: Colors.grey,
    child: Icon(Icons.person),
  ),
  errorWidget: (context, url, error) => const Icon(Icons.error),
  width: 80,
  height: 80,
  fit: BoxFit.cover,
)
```

### Circular avatar

```dart
CachedNetworkImage(
  imageUrl: avatarUrl,
  imageBuilder: (context, imageProvider) => CircleAvatar(
    radius: 24,
    backgroundImage: imageProvider,
  ),
  placeholder: (_, __) => const CircleAvatar(
    radius: 24,
    child: Icon(Icons.person),
  ),
)
```

### Clear cache

```dart
// Clear a specific URL from cache
await CachedNetworkImage.evictFromCache(url);

// Clear all cached images
await DefaultCacheManager().emptyCache();
```

### Cache configuration

```dart
import 'package:flutter_cache_manager/flutter_cache_manager.dart';

class CustomCacheManager extends CacheManager with ImageCacheManager {
  static const key = 'customCache';
  static final CustomCacheManager _instance = CustomCacheManager._();
  factory CustomCacheManager() => _instance;

  CustomCacheManager._() : super(Config(
    key,
    stalePeriod: const Duration(days: 7),
    maxNrOfCacheObjects: 200,
  ));
}

CachedNetworkImage(
  imageUrl: url,
  cacheManager: CustomCacheManager(),
)
```

## Image compression before upload

For AI vision tasks or user uploads, compress images client-side before sending:

```dart
import 'package:flutter_image_compress/flutter_image_compress.dart';

Future<Uint8List> compressImage(String filePath, {int quality = 80}) async {
  final compressed = await FlutterImageCompress.compressWithFile(
    filePath,
    minWidth: 1024,
    minHeight: 1024,
    quality: quality,
    format: CompressFormat.jpeg,
  );
  return compressed!;
}
```

Add: `flutter_image_compress: ^2.4.0`

## Permission handling

On Android 13+, `READ_MEDIA_IMAGES` replaces `READ_EXTERNAL_STORAGE`. `image_picker` handles the permission dialog automatically, but you can pre-check with `permission_handler`:

```dart
import 'package:permission_handler/permission_handler.dart';

Future<bool> checkPhotoPermission() async {
  if (Platform.isAndroid) {
    final sdk = await DeviceInfoPlugin().androidInfo;
    if (sdk.version.sdkInt >= 33) {
      return await Permission.photos.isGranted;
    }
    return await Permission.storage.isGranted;
  }
  return await Permission.photos.isGranted;
}
```

## Gotchas

- `image_picker` on iOS doesn't request permissions before opening the picker — the system handles it. If the user previously denied, the picker silently fails. Show a custom "Please grant photo access in Settings" message.
- `imageQuality` in `image_picker` applies only to JPEG. PNG images are returned at full quality regardless.
- `CachedNetworkImage` requires an internet connection for first load. If offline support matters, cache images explicitly to local storage.
- Images from `image_picker` on iOS have a `file://` URI prefix; on Android they vary. Always use `image.readAsBytes()` rather than opening the path directly.
