---
name: ios-game-controller
description: Implements game input and haptics on iPhone and iPad (iOS 26+, Swift 6) - on-screen touch controls (Touch Controller, GCVirtualController, custom), physical controllers via GCController, keyboard and mouse, Game Controllers capability, Core Haptics and controller rumble. Use when adding or debugging controls, touch joysticks, controller support, or haptic feedback in an iOS game.
license: MIT
---

# Game Controller and haptics

Write gameplay against one input model, then attach every device to it. Physical controllers, the Touch Controller framework and `GCVirtualController` all appear as a `GCController`, so one code path reads them all.

## Pick the touch approach

| Game renders with | Touch controls |
|---|---|
| Own Metal pipeline (`MTKView`, or SpriteKit through `SKRenderer`) | Touch Controller framework (`TCTouchController`, iOS 26). Read [references/touch-controller.md](references/touch-controller.md). |
| SpriteKit `SpriteView`, RealityKit `RealityView`, SwiftUI | `GCVirtualController` (system-drawn), or custom controls drawn as nodes or SwiftUI views that feed the same input model |

Touch layout rules that apply to every approach:
- Movement on the left (a floating stick that appears where the thumb lands), camera on the right (direct drag), actions bottom-right.
- Frequent controls at least 44 × 44 pt, minor ones at least 28 × 28 pt; keep them inside the safe area, clear of the Dynamic Island and Home indicator.
- Label buttons with action glyphs (a jump arrow), not controller letters. Hide controls the player cannot use right now.
- Every press shows a pressed state and gets a sound or haptic.

## Read input once per frame

```swift
import GameController

@MainActor final class InputModel {
    var move: SIMD2<Float> = .zero
    var jumpPressed = false
    private var controller: GCController?
    private var tokens: [Any] = []

    func start() {
        controller = GCController.current ?? GCController.controllers().first
        tokens.append(NotificationCenter.default.addObserver(
            forName: .GCControllerDidBecomeCurrent, object: nil, queue: .main) { [weak self] note in
            let current = note.object as? GCController
            MainActor.assumeIsolated { self?.controller = current }
        })
    }

    func poll() {                                   // call at the start of each game update
        guard let input = controller?.input.capture() else { return }
        if let stick = input.dpads[.leftThumbstick] {
            move = SIMD2(stick.xyAxes.value.x, stick.xyAxes.value.y)
        }
        jumpPressed = input.buttons[.a]?.pressedInput.isPressed ?? false
    }
}
```

- `controller.input` (`GCControllerLiveInput`, iOS 17) is the current input API. Its subscripts return optionals because not every controller has every element. `capture()` gives a consistent snapshot for one frame.
- `extendedGamepad` still works and is not deprecated; `GCGamepad`, snapshots and `controllerPausedHandler` are deprecated (read `buttons[.menu]` instead).
- Pause the game when a controller disconnects mid-play.
- Set `playerIndex` on connected controllers so their light shows the player number.
- Follow conventions: A confirms, B goes back, Menu pauses. The Home button belongs to the system.
- Show button prompts with the connected controller's own symbols, and fall back to touch prompts when none is connected.

## Keyboard and mouse

- `GCKeyboard.coalesced?.keyboardInput?.button(forKeyCode: .keyW)?.isPressed` for held keys; `keyChangedHandler` for events.
- `GCMouse.current?.mouseInput?.mouseMovedHandler` gives raw deltas for camera control. For pointer lock, override `prefersPointerLocked` in the hosting view controller; the system grants it only to a full-screen, active scene.
- Allow rebinding, and keep every action reachable with one key.

## Capabilities and Info.plist

- Add the Game Controllers capability. It writes `GCSupportsControllerUserInteraction` and `GCSupportedGameControllers` (profile `ExtendedGamepad`), which enable the controller badge in the App Store and Games app and system remapping.
- `GCRequiresControllerUserInteraction` shows "Controller Recommended" on iOS; the game still needs working touch controls.
- Game Mode is set with `LSSupportsGameMode`; see the `ios-game-design` skill.

## Haptics

| Feedback | Use |
|---|---|
| Menu taps, selection, success or failure | SwiftUI `.sensoryFeedback(_:trigger:)`, or `UIImpactFeedbackGenerator(style:view:)` and its siblings (the `view:` initializers; the plain ones are deprecated in iOS 27) |
| Gameplay impacts, engines, rumbles, patterns synced to sound | Core Haptics `CHHapticEngine`. Read [references/haptics.md](references/haptics.md). |
| Controller rumble | `controller.haptics?.createEngine(withLocality: .default)` |

- iPads have no haptic engine. Check `CHHapticEngine.capabilitiesForHardware().supportsHaptics` and pair every haptic with sound or visuals.
- Give players a setting to turn haptics off.

## Gotchas

- Creating a `TCTouchController` on an unsupported device is a fatal error; guard with `TCTouchController.isSupported`.
- When counting players, exclude the touch controller: compare `productCategory` with `TCGameControllerProductCategoryTouchController`.
- Changing `GCControllerLiveInput.queue` off the main queue makes main-actor-isolated handlers trap in Swift 6.
- A controller's haptic engine reports the phone's `supportsHaptics`, not the controller's; check `controller.haptics?.supportedLocalities`.
- `GCControllerHomeButtonSettingsManager` is iOS 27-only; gate it with `if #available(iOS 27, *)`.

## Related skills

Responsiveness, input buffering and forgiveness: `ios-game-ux-design`. On-screen control layout and HUD: `ios-game-ui-design`.
