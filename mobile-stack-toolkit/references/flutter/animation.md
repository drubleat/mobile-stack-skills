---
title: Animations: lottie + flutter_animate
impact: MEDIUM
impactDescription: "lottie for designer-authored animations; flutter_animate for code-driven micro-interactions with chained effects"
tags: flutter, animation, lottie, flutter_animate
---

# Animations: lottie + flutter_animate

Versions: `lottie: ^3.3.3`, `flutter_animate: ^4.5.2`

## lottie: JSON animations

Lottie renders After Effects animations exported as JSON. Best for: loading spinners, onboarding illustrations, empty states, success/error feedback.

### Load from assets

```yaml
# pubspec.yaml
flutter:
  assets:
    - assets/animations/
```

```dart
import 'package:lottie/lottie.dart';

// Simple loop
Lottie.asset('assets/animations/loading.json')

// Controlled animation
class _SuccessAnimationState extends State<SuccessAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    return Lottie.asset(
      'assets/animations/success.json',
      controller: _controller,
      onLoaded: (composition) {
        _controller
          ..duration = composition.duration
          ..forward().whenComplete(() {
            widget.onComplete?.call();
          });
      },
      width: 200,
      height: 200,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

### Load from network

```dart
Lottie.network(
  'https://assets.example.com/animations/confetti.json',
  frameRate: FrameRate.max,
)
```

### Optimization tips

- Use `renderCache: RenderCache.raster` for complex animations that don't change at runtime — rasterizes frames to improve performance.
- Set `frameRate: FrameRate(30)` if 60fps isn't needed — halves the rendering work.
- Keep Lottie files small (< 500KB). Complex AE effects with many layers are slow.

```dart
Lottie.asset(
  'assets/animations/hero.json',
  renderCache: RenderCache.raster,
  frameRate: FrameRate(30),
)
```

### Sources for Lottie files

- [LottieFiles](https://lottiefiles.com) — free and paid. Download as JSON.
- Design team exports from After Effects with the Bodymovin plugin.

---

## flutter_animate: widget animation chain

`flutter_animate` adds a `.animate()` extension to any widget, letting you chain multiple effects with a clean API.

### Entrance animations

```dart
Text('Hello')
  .animate()
  .fadeIn(duration: 400.ms)
  .slideY(begin: 0.3, end: 0, curve: Curves.easeOut)

// Staggered list items
ListView.builder(
  itemBuilder: (context, index) => ListTile(title: Text('Item $index'))
    .animate(delay: (50 * index).ms)
    .fadeIn()
    .slideX(begin: -0.2),
)
```

### Chaining effects

```dart
Container(color: Colors.blue, width: 100, height: 100)
  .animate()
  .scale(begin: const Offset(0.5, 0.5), duration: 300.ms)
  .then()                     // waits for previous to finish
  .shake(hz: 4, duration: 300.ms)
  .then()
  .fade(end: 0.5)
```

### Loop / ping-pong

```dart
Icon(Icons.star, color: Colors.yellow)
  .animate(onPlay: (controller) => controller.repeat(reverse: true))
  .scale(begin: const Offset(0.8, 0.8), end: const Offset(1.2, 1.2))
```

### Conditional animation

```dart
// Only animate when isVisible changes to true
myWidget
  .animate(target: isVisible ? 1 : 0)
  .fade()
  .scale()
```

### Controller for manual triggering

```dart
final controller = AnimationController(vsync: this);

myWidget
  .animate(controller: controller)
  .slideY(begin: 1, end: 0)

// Trigger programmatically
controller.forward();
controller.reverse();
```

## Choosing between lottie and flutter_animate

| Use case | lottie | flutter_animate |
|---|---|---|
| Complex illustrated animations (designed in AE) | ✅ | ❌ |
| Simple widget entrance/exit | ❌ | ✅ |
| Loading spinners | ✅ | ✅ |
| Staggered list animations | ❌ | ✅ |
| Confetti / celebration effects | ✅ | ❌ |
| Micro-interactions (button press) | ❌ | ✅ |

Use lottie when design assets exist. Use flutter_animate for code-defined UI motion.

## Performance notes

- Both lottie and flutter_animate render on the UI thread. Keep animations short (< 1s for UI responses, 2–3s max for illustrations).
- Avoid running multiple complex Lottie animations simultaneously.
- `flutter_animate` effects are composited by Flutter's engine — they're efficient for simple property animations.
- Test on mid-range Android devices (not just flagship). Animation jank is most visible on lower-end hardware.
