# RealityKit assets and performance

Read this before importing 3D assets, setting up Reality Composer Pro, or when a 3D game misses its frame budget.

## Asset pipeline

- Ship models as USDZ. Export from Blender, Maya or Houdini directly to USD; `.usda` is text (diffable), `.usdc` binary (heavy geometry), `.usdz` the zipped package that ships.
- RealityKit uses meters, +Y up, and −Z forward. Blender is Z-up, so expect a −90° rotation about X on import; fix it at export rather than in code.
- Normal maps must be OpenGL-style (DirectX-style maps have the green channel inverted).
- Pack roughness, metallic and ambient occlusion into the R, G and B channels of one texture. Scalar material slots read the red channel by default, so give each slot its channel with a swizzle: `var t = MaterialParameters.Texture(orm); t.swizzle = MTLTextureSwizzleChannels(red: .green, green: .green, blue: .green, alpha: .one); material.metallic = .init(texture: t)`.
- About 2048 px per side is enough on iPhone and iPad. Texture memory is roughly width × height × 4 bytes × 4/3 with mipmaps, so one 2048² RGBA texture costs about 22 MB.
- Converting an old SceneKit `.scn` file: Xcode File > Export as USD, or `xcrun scntool --convert in.scn --format usdz`. SceneKit particle files have no converter; rebuild them with `ParticleEmitterComponent`.
- Load asynchronously (`try await Entity(named:in:)`), load before gameplay starts, and reuse `MeshResource` and material instances across entities.

## Reality Composer Pro

- Reality Composer Pro authors scenes, Shader Graph materials, particle emitters, lights and audio, and loads into the app through a Swift package bundle (`Entity(named: "Scene", in: realityKitContentBundle)`).
- Reality Composer Pro 3 (WWDC26) is a separate download for macOS 26.5 or later, needs Xcode 27 to link a project, and exports `.reality` files. Its graph components (behavior trees, animation graphs, compute graphs) need iOS 27. For an iOS 26 target, verify on an iOS 26 device that exported content loads, or author iOS 26 content as USDZ plus code.

## Frame budget

- At 60 fps a frame is 16.6 ms; at 120 fps 8.3 ms. Keep average CPU work on the main and render threads well under the budget.
- Draw calls: each mesh-material pair is a draw call. Merge nearby meshes that share a material; keep far-apart parts separate so culling still works. Flatten deep entity hierarchies.
- Repeated meshes (grass, coins, debris): `MeshInstancesComponent` in chunks.
- GPU cost drivers: transparency (overdraw), each shadow-casting light, skeletal joints, depth of field and motion blur. Bake lighting into textures where the scene is static and keep one shadow-casting light.
- Turn shadows off for entities that do not need them: `DynamicLightShadowComponent(castsShadow: false)`.
- Physics: few rigid bodies, primitive collision shapes, no per-frame shape rebuilds.
- Thermal state: observe `ProcessInfo.thermalStateDidChangeNotification` and lower shadow quality, effects or frame rate when it rises.

## Tools

- Xcode RealityKit debugger: Debug area > Capture Entity Hierarchy.
- Instruments: RealityKit Trace (triangles, draw calls, bottlenecks), Game Performance, Time Profiler for custom systems, Metal System Trace.
- Metal Performance HUD on device for live frame time and memory.
