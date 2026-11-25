---
name: ios-game-spritekit
description: Builds 2D iOS games with SpriteKit hosted in SwiftUI (iOS 26+, Swift 6) - scenes, frame loop, actions, physics, cameras, tile maps, particles, shaders, lighting and draw-call performance. Use when writing or debugging SpriteKit code (SKScene, SKNode, SpriteView) or when a 2D game renders slowly or looks wrong.
license: MIT
---

# SpriteKit

SpriteKit is the default renderer for 2D iOS games. It is supported and not deprecated, but its API has been frozen since iOS 12, so every SpriteKit call works on iOS 26 without `#available` checks. Project-wide settings (Game Mode, ProMotion, app category) live in the `ios-game-design` skill.

Avoid `SK3DNode`: it embeds SceneKit, which is deprecated since iOS 26. Use the `ios-game-realitykit` skill for 3D.

## Host the scene in SwiftUI

```swift
import SwiftUI
import SpriteKit

struct GameView: View {
    @State private var scene: GameScene = {          // create once; never inside body
        let s = GameScene(size: CGSize(width: 390, height: 844))
        s.scaleMode = .resizeFill
        s.anchorPoint = CGPoint(x: 0.5, y: 0.5)
        return s
    }()
    @State private var paused = false

    var body: some View {
        SpriteView(scene: scene, isPaused: paused, preferredFramesPerSecond: 120,
                   options: [.ignoresSiblingOrder, .shouldCullNonVisibleNodes],
                   debugOptions: [.showsFPS, .showsNodeCount, .showsDrawCount]) // debug builds only
            .ignoresSafeArea()
            .statusBarHidden()
            .persistentSystemOverlays(.hidden)
    }
}
```

`SpriteView` defaults are wrong for games; override them:
- `preferredFramesPerSecond` defaults to 60. Pass 120 and add `CADisableMinimumFrameDurationOnPhone` to Info.plist, or iPhone stays at 60 Hz.
- `options` defaults to `[.shouldCullNonVisibleNodes]`, so `.ignoresSiblingOrder` is off. Turn it on and set `zPosition` wherever draw order matters.

Scale modes: `.aspectFit` letterboxes, `.aspectFill` crops, `.resizeFill` tracks the view size (re-layout in `didChangeSize(_:)`). Pick a fixed design size with an aspect mode, or `.resizeFill` with adaptive layout. Keep the world full-bleed and inset only HUD and touch targets by `view.safeAreaInsets`, or draw the HUD as a SwiftUI overlay.

## Swift 6 concurrency

- `SKNode` (and so `SKScene`) is `@MainActor`, inherited from `UIResponder`. Closures created in a scene (`SKAction.run`, `customAction`) inherit the main actor.
- `SKPhysicsContactDelegate` is nonisolated, so without default main-actor isolation `class GameScene: SKScene, SKPhysicsContactDelegate` fails to compile in Swift 6. Write an isolated conformance, which compiles under every setting: `SKScene, @MainActor SKPhysicsContactDelegate`.
- Preload with the async forms (`await atlas.preload()`, `await SKTexture.preload(textures)`); the completion-handler forms are `@Sendable` and warn when they touch nodes.
- `await node.run(action)` resumes when the action ends, which suits short sequences. It never resumes for `repeatForever`.
- New Xcode projects default to Swift 5 language mode; set `SWIFT_VERSION = 6` explicitly.

## Frame loop

Order per frame: `update(_:)` → actions → `didEvaluateActions()` → physics (contact callbacks fire here) → `didSimulatePhysics()` → constraints → `didApplyConstraints()` → `didFinishUpdate()` → render.

- `currentTime` is absolute. Compute `dt` yourself and clamp it (for example to 1/30 s) so a pause or hitch never teleports objects.
- Frame rate varies with Low Power Mode and thermal state. Scale all motion by `dt`.
- Never add, remove or reshape physics bodies inside `didBegin`/`didEnd`. Queue the change and apply it in `didSimulatePhysics()` or the next `update`.
- Action order within a frame is unspecified. Read final positions in `didEvaluateActions()` or later.

## Scene skeleton

```swift
enum Category { static let player: UInt32 = 1 << 0; static let enemy: UInt32 = 1 << 1; static let wall: UInt32 = 1 << 2 }

final class GameScene: SKScene, @MainActor SKPhysicsContactDelegate {
    private var lastTime: TimeInterval = 0
    private let cam = SKCameraNode()
    private let player = SKSpriteNode(imageNamed: "player")
    private var pendingRemovals: [SKNode] = []

    override func didMove(to view: SKView) {
        physicsWorld.contactDelegate = self          // held unowned: the scene must stay alive
        addChild(cam); camera = cam                  // children of cam form a screen-fixed HUD
        let body = SKPhysicsBody(circleOfRadius: 12)
        body.categoryBitMask = Category.player
        body.collisionBitMask = Category.wall
        body.contactTestBitMask = Category.enemy     // default 0: no didBegin calls at all
        player.physicsBody = body
        addChild(player)
    }

    override func update(_ currentTime: TimeInterval) {
        let dt = lastTime == 0 ? 0 : min(currentTime - lastTime, 1.0 / 30.0)
        lastTime = currentTime
        step(dt)
        cam.position = player.position
    }

    override func didSimulatePhysics() {             // safe point to mutate physics
        pendingRemovals.forEach { $0.removeFromParent() }
        pendingRemovals.removeAll()
    }

    func didBegin(_ contact: SKPhysicsContact) {     // record only; never mutate here
        let a = contact.bodyA, b = contact.bodyB
        guard a.categoryBitMask | b.categoryBitMask == Category.player | Category.enemy,
              let enemy = (a.categoryBitMask == Category.enemy ? a : b).node else { return }
        pendingRemovals.append(enemy)
    }

    private func step(_ dt: TimeInterval) { /* game logic scaled by dt */ }
}
```

## Building blocks

| Need | Use |
|---|---|
| Camera, HUD | `SKCameraNode`; HUD nodes as camera children |
| Tweens, easing | `SKAction` with `timingMode` or a custom `timingFunction` |
| Sprite animation | `SKAction.animate(with:timePerFrame:)` over atlas textures |
| Physics | `SKPhysicsBody` (circle/rect cheapest), masks set explicitly, `usesPreciseCollisionDetection` for small fast bodies |
| Grid levels | `SKTileMapNode` + `SKTileSet`; tiles are not nodes, so build collision separately |
| Textures | Sprite Atlas in the asset catalog, `SKTextureAtlas(named:)`; preload before gameplay |
| Pixel art | `texture.filteringMode = .nearest` on every texture, including each atlas frame |
| Particles | `.sks` emitter files, `SKEmitterNode(fileNamed:)`; set `targetNode = scene` for trails |
| Shaders, lights, filters, warps | Read [references/effects.md](references/effects.md) |
| One-shot sound | `SKAction.playSoundFileNamed`; anything more uses the `ios-game-audio-engine` skill |
| Metal integration | `SKRenderer` draws a scene inside your own Metal pass |

## Performance

- Batching: nodes that share a texture or atlas draw in one call. Mixed atlases and overlapping nodes at different `zPosition`s split batches. Watch `showsDrawCount`.
- Remove offscreen nodes with `removeFromParent()`; culling still visits every node each frame.
- Expensive, use sparingly: `SKEffectNode` with `CIFilter`, `SKCropNode`, many `SKShapeNode`s, one `SKShader` per sprite, and shader source changes at runtime (each recompiles).
- `SKShapeNode` is for debug drawing. Bake a shape once with `view.texture(from:)` and draw sprites.
- Profile on a device with the Instruments **Game Performance** template and the Metal Performance HUD (Scheme > Run > Diagnostics > Show Graphics Overview).

## Gotchas

- `contactTestBitMask` defaults to 0, while `categoryBitMask` and `collisionBitMask` default to all bits. Set all three for every body.
- `UIScreen.main` is deprecated in iOS 26. Read the refresh rate from `view.window?.windowScene?.screen.maximumFramesPerSecond`.
- `SKShader` source is GLSL ES, not the Metal Shading Language.
- `physicsWorld.contactDelegate` is not retained.
- With `.ignoresSiblingOrder`, nodes at equal `zPosition` draw in arbitrary order.

## Related skills

Input and haptics: `ios-game-controller`. Sound: `ios-game-audio-engine`. Look, palette and juice: `ios-game-art-direction`. Grid and room layout: `ios-game-level-design`.
