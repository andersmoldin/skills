# RealityKit API availability on iOS

Read this before using a RealityKit symbol you have not used on iOS before. The deployment target is iOS 26, so iOS 27 symbols need `if #available(iOS 27.0, *)` and a fallback. To check a symbol not listed here, fetch `https://developer.apple.com/tutorials/data/documentation/realitykit/<symbol-lowercased>.json` and read the iOS entry in `metadata.platforms`.

## Available on iOS 26 (safe without checks)

- View: `RealityView`, `RealityViewCameraContent`, `content.camera = .virtual`, `realityViewCameraControls(_:)`, `content.renderingEffects`, `content.environment`, `content.audioListener`, `subscribe(to:on:_:)`, hit testing and projection (`entity(at:in:)`, `hitTest(point:in:query:mask:)`, `ray(through:in:to:)`, `project`, `unproject`).
- ECS: `Entity`, `Component`, `System`, `EntityQuery`, `SceneUpdateContext.entities(matching:updatingSystemWhen:)`, `SystemDependency`.
- Input: `InputTargetComponent`, `HoverEffectComponent`, SwiftUI `targetedToAnyEntity()` / `targetedToEntity(_:)`.
- Rendering: `ModelEntity`, `MeshResource.generate*`, `MeshDescriptor`, `LowLevelMesh`, `LowLevelTexture`, all material types including `CustomMaterial`, all three light components, `DirectionalLightComponent.Shadow`, `SpotLightComponent.Shadow`, `DynamicLightShadowComponent`, `GroundingShadowComponent`, `ImageBasedLightComponent`, `ImageBasedLightReceiverComponent`, `OrthographicCameraComponent`, `BillboardComponent`, `OpacityComponent`, `TextComponent`, `ParticleEmitterComponent`.
- Physics: `PhysicsBodyComponent`, `CollisionComponent`, `PhysicsMotionComponent`, `ShapeResource`, `CollisionEvents`, `CollisionFilter`, `PhysicsSimulationComponent`, `ForceEffectComponent`, `PhysicsJoints`, `CharacterControllerComponent`.
- Animation and audio: `AnimationResource`, `FromToByAnimation`, `AnimationLibraryComponent`, `BlendShapeWeightsComponent`, `SkeletalPosesComponent`, `IKComponent`, `AudioFileResource`, `SpatialAudioComponent`, `AmbientAudioComponent`, `ChannelAudioComponent`, `AudioLibraryComponent`, `ReverbComponent`.
- New in iOS 26: `PostProcessEffect` with `renderingEffects.customPostProcessing`, `MeshInstancesComponent`, `LowLevelInstanceData`, `GestureComponent`, `Entity.observable`, `Entity.attach(_:to:)`, `content.animate(body:completion:)`.

## iOS 27 only (WWDC26): gate and provide a fallback

- Navigation: `NavigationMeshResource`, `NavigationMeshComponent`, `NavigationComponent`, `NavigationController` (`computePath(to:)`). Fallback: your own grid or waypoint pathfinding, for example GameplayKit `GKGridGraph`.
- Level of detail: `LevelOfDetailComponent`. Fallback: swap meshes by camera distance in a system.
- Bloom and tone mapping: `BloomComponent`, `BloomOptionsComponent`, `ToneMappingComponent`. Fallback: a `PostProcessEffect`.
- Lighting: soft spot shadows (`SpotLightComponent.Shadow.lightSize` with `.quality` `.medium` or `.high`), `DirectionalLightComponent.Shadow.cascades`, `LightmapComponent`, `DiffuseLightProbeGroupComponent`.
- Also: cloth simulation components, `GaussianSplatComponent`, `MeshDeformerComponent`, `ReverbMeshResource`, Reality Composer Pro 3 runtime graphs (`AnimationGraphComponent`, `BehaviorTreeComponent`, `ComputeGraphComponent`), and the `USDKit` framework.
- Two initializers changed in iOS 27; on an iOS 26 target keep the older ones: `Entity(from:named:)` and `EnvironmentResource(named:in:)`.

## visionOS only: do not use on iOS

`RealityViewContent`, `RealityView(make:update:attachments:)` and `Attachment`, `ViewAttachmentComponent`, `ManipulationComponent`, `PresentationComponent`, `Model3D`, `SurroundingsLight`. On iOS, draw menus and HUD in SwiftUI over the view.
