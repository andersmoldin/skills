# Touch Controller framework (iOS 26)

Read this when the game renders through its own Metal pipeline and needs on-screen controls. The framework (module `TouchController`, prefix `TC`) draws controls with Metal and exposes them as a `GCController`, so gameplay code reads them like a physical pad.

## Setup

```swift
import TouchController
import MetalKit

@MainActor func makeTouchControls(for view: MTKView) -> TCTouchController? {
    guard TCTouchController.isSupported else { return nil }      // creating one otherwise is fatal
    let controller = TCTouchController(descriptor: TCTouchControllerDescriptor(mtkView: view))

    let move = TCThumbstickDescriptor()
    move.label = .leftThumbstick
    move.colliderShape = .leftSide                               // whole left half accepts the thumb
    move.hidesWhenNotPressed = true                              // floating stick
    controller.addThumbstick(descriptor: move)

    let jump = TCButtonDescriptor()
    jump.label = .buttonA
    jump.anchor = .bottomRight
    jump.offset = CGPoint(x: -40 - view.safeAreaInsets.right, y: -100 - view.safeAreaInsets.bottom)
    jump.contents = .buttonContents(forSystemImageNamed: "arrow.up", size: jump.size, shape: .circle,
                                    controller: controller)
    controller.addButton(descriptor: jump)

    controller.connect()                                         // creates controller.controller (a GCController)
    return controller
}
```

## Every frame and every touch

- Draw: call `touchController.render(using: encoder)` inside your render pass, after the game scene.
- Forward touches from the view's `touchesBegan`, `touchesMoved`, `touchesEnded` and `touchesCancelled`: `touchController.handleTouchBegan(at: touch.location(in: view), index: touch.hash)` and the matching moved and ended calls. A `true` result means the control consumed the touch.

## Controls

- Types: `TCButton`, `TCThumbstick`, `TCDirectionPad`, `TCTouchpad`, `TCSwitch`, `TCThrottle`, each created from its descriptor with the matching `add…(descriptor:)` call.
- `label` maps a control to a gamepad element (`.buttonA`…`.buttonY`, `.leftThumbstick`, `.rightThumbstick`, `.directionPad`, `.buttonMenu`) or a custom `TCControlLabel(name:role:)`.
- Camera drag: a `TCTouchpad` with `label = .rightThumbstick`, `colliderShape = .rightSide`, `reportsRelativeValues = true`.
- Layout uses one of nine `TCControlLayoutAnchor` values plus `offset`. The framework does not apply safe-area insets for you; add them to the offset.
- `isEnabled = false` hides a control; use it to show only the controls that apply right now.
- Visuals: SF Symbols through `TCControlContents.buttonContents(forSystemImageNamed:size:shape:controller:)`, or your own textures through `TCControlContents(images:)` so controls match the art direction.
