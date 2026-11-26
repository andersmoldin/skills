---
name: ios-game-realitykit
description: Builds 3D iOS games with RealityKit in a SwiftUI RealityView (iOS 26+, Swift 6) - non-AR camera, entity-component-system game logic, physics, character controller, lights, materials, particles, post-processing, USDZ assets and performance. Use when writing or debugging RealityKit code, porting from SceneKit, or choosing how to render a 3D game.
license: MIT
---

# RealityKit

RealityKit is the 3D renderer for iOS games. SceneKit is deprecated as of iOS 26 (maintenance mode, critical fixes only), so new games use RealityKit; `ARView` is legacy UIKit, so new code uses `RealityView`. Project-wide settings (Game Mode, frame rate, app category) live in the `ios-game-design` skill.

Many RealityKit symbols are visionOS-only. Before using an API, confirm its iOS availability; [references/availability.md](references/availability.md) lists what is iOS 26, iOS 27-only, or visionOS-only.

## Minimal non-AR game scene

```swift
import SwiftUI
import RealityKit

struct SpinComponent: Component { var radiansPerSecond: Float = .pi }

final class SpinSystem: System {
    private static let query = EntityQuery(where: .has(SpinComponent.self))
    required init(scene: RealityKit.Scene) {}
    func update(context: SceneUpdateContext) {
        let dt = Float(context.deltaTime)
        for entity in context.entities(matching: Self.query, updatingSystemWhen: .rendering) {
            guard let spin = entity.components[SpinComponent.self] else { continue }
            entity.orientation *= simd_quatf(angle: spin.radiansPerSecond * dt, axis: [0, 1, 0])
        }
    }
}

@main struct MiniGameApp: App {
    init() { SpinComponent.registerComponent(); SpinSystem.registerSystem() }  // once, before any view
    var body: some SwiftUI.Scene { WindowGroup { GameView() } }                // RealityKit also has `Scene`
}

struct GameView: View {
    @State private var score = 0
    @State private var collisions: EventSubscription?

    var body: some View {
        RealityView { content in                       // async, runs once
            content.camera = .virtual                  // iOS default is the AR camera feed
            let camera = Entity()
            camera.components.set(PerspectiveCameraComponent(near: 0.05, far: 100, fieldOfViewInDegrees: 60))
            camera.look(at: .zero, from: [0, 3, 5], relativeTo: nil)
            content.add(camera)

            let sun = Entity()
            sun.components.set(DirectionalLightComponent(color: .white, intensity: 4000))
            sun.components.set(DirectionalLightComponent.Shadow(maximumDistance: 15, depthBias: 1))
            sun.look(at: .zero, from: [3, 6, 2], relativeTo: nil)
            content.add(sun)

            let ground = ModelEntity(mesh: .generatePlane(width: 10, depth: 10),
                                     materials: [SimpleMaterial(color: .darkGray, isMetallic: false)])
            ground.components.set(CollisionComponent(shapes: [.generateBox(width: 10, height: 0.01, depth: 10)]))
            ground.components.set(PhysicsBodyComponent(massProperties: .default, material: nil, mode: .static))
            content.add(ground)

            var material = PhysicallyBasedMaterial()
            material.baseColor = .init(tint: .systemOrange)
            material.roughness = 0.4
            let mesh = MeshResource.generateBox(size: 0.5, cornerRadius: 0.05)   // share mesh and material
            for i in 0..<5 {
                let cube = ModelEntity(mesh: mesh, materials: [material])
                cube.position = [Float(i) - 2, 0.25, 0]
                cube.components.set(SpinComponent(radiansPerSecond: .pi / Float(i + 1)))
                cube.components.set(InputTargetComponent())                       // tappable needs both
                cube.components.set(CollisionComponent(shapes: [.generateBox(size: [0.5, 0.5, 0.5])]))
                content.add(cube)
            }
            collisions = content.subscribe(to: CollisionEvents.Began.self, on: nil) { _ in }  // retain it
        }
        .gesture(SpatialTapGesture().targetedToAnyEntity().onEnded { value in
            score += 1
            value.entity.components[SpinComponent.self]?.radiansPerSecond *= 2
        })
        .overlay(alignment: .top) { Text("Score: \(score)").font(.title.bold()).padding() }
        .ignoresSafeArea()
    }
}
```

## Game logic: entity-component-system

- Put per-entity state in a `Component` struct; put behavior in a `System` that queries components each frame. Systems hold no per-entity state.
- Register every component and system once in `App.init`, before any `RealityView` appears.
- Order systems with `static var dependencies: [SystemDependency]` (`.before(...)`, `.after(...)`).
- Use systems for per-frame logic rather than `SceneEvents.Update` closures.
- The `update:` closure of `RealityView` reruns on SwiftUI state changes. Writing observed state there loops forever. Mutate entities in systems or gesture handlers.
- `entity.observable` (iOS 26) exposes entity properties to SwiftUI, for example a HUD that reads `entity.observable.position`.

## Building blocks (iOS 26)

| Need | Use |
|---|---|
| Camera | Entity with `PerspectiveCameraComponent` or `OrthographicCameraComponent`; `look(at:from:relativeTo:)` |
| Debug camera | `.realityViewCameraControls(.orbit)` |
| Tap or drag an entity | SwiftUI gesture `.targetedToAnyEntity()`, or `GestureComponent` on the entity; needs `InputTargetComponent` + `CollisionComponent` |
| HUD and menus | SwiftUI `.overlay` or `ZStack` over the `RealityView` |
| Physics | `PhysicsBodyComponent` (`.static` level, `.kinematic` scripted, `.dynamic` simulated), `CollisionComponent` with primitive shapes |
| Walking character | `CharacterControllerComponent` + `entity.moveCharacter(by:deltaTime:relativeTo:)` |
| Lights | `DirectionalLightComponent`, `SpotLightComponent` (both cast shadows), `PointLightComponent` (no shadows) |
| Environment light | `ImageBasedLightComponent` on a light entity + `ImageBasedLightReceiverComponent` on lit entities; skybox via `content.environment = .skybox(...)` |
| Materials | `PhysicallyBasedMaterial`, `UnlitMaterial`, `ShaderGraphMaterial` (Reality Composer Pro), `CustomMaterial` (Metal shaders) |
| Particles | `ParticleEmitterComponent` (presets such as `.Presets.sparks`) |
| Many copies of one mesh | `MeshInstancesComponent` (iOS 26); split large fields into chunks so culling still works |
| Screen effects | `content.renderingEffects` (antialiasing, motion blur, depth of field); custom `PostProcessEffect` via `renderingEffects.customPostProcessing` (iOS 26) |
| Animation | `AnimationLibraryComponent` from USDZ, `playAnimation(_:transitionDuration:startsPaused:)`, `move(to:relativeTo:duration:timingFunction:)` |
| Sound | `SpatialAudioComponent` + `AudioFileResource`; see the `ios-game-audio-engine` skill |
| Assets | `Entity(named:in:)` async from USDZ or a Reality Composer Pro bundle |

Assets, Reality Composer Pro and performance budgets: read [references/assets-and-performance.md](references/assets-and-performance.md) before importing models or when frame time exceeds budget.

## When to drop to Metal

Stay in RealityKit first: `CustomMaterial` for surface and geometry shaders, `LowLevelMesh` / `LowLevelTexture` for GPU-written data, `PostProcessEffect` for full-screen passes. A fully custom Metal renderer is a last resort for pipelines RealityView cannot express. Metal 4 (`MTL4CommandQueue`) needs an A14 or newer, while iOS 26 still runs on A13 devices, so keep a fallback path. MetalFX offers spatial and temporal upscaling.

## Gotchas

- Set `content.camera = .virtual` or the game opens the AR camera.
- Cameras and lights point down their −Z axis; place them with `look(at:from:relativeTo:)`.
- On iOS the content type is `RealityViewCameraContent`; `RealityViewContent`, attachments, `ManipulationComponent` and `Model3D` are visionOS-only and do not compile.
- An unretained `EventSubscription` silently stops delivering events.
- An image-based light without a receiver component lights nothing.
- Never rebuild meshes or collision shapes per frame; avoid `generateCollisionShapes(recursive:)` on detailed meshes.
- Sample code types such as `CharacterMovementComponent` or `ThumbStickView` (from Apple's PyroPanda sample) are not RealityKit API.

## Related skills

Input and haptics: `ios-game-controller`. Sound: `ios-game-audio-engine`. Look, lighting mood and juice: `ios-game-art-direction`. Spaces and pacing: `ios-game-level-design`.
