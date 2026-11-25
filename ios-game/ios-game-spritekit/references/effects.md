# SpriteKit effects: shaders, lights, filters, warps

Read this when a 2D game needs a custom look beyond plain sprites and particles. Every effect here costs GPU time; measure with `showsDrawCount` and the Game Performance template after adding one.

## Fragment shaders (`SKShader`)

- Source is GLSL ES 2.0, not Metal Shading Language. SpriteKit translates it to Metal.
- Built-ins: `u_texture`, `u_time`, `v_tex_coord`, `v_color_mix`, `SKDefaultShading()`. Write the result to `gl_FragColor`.
- Create shaders at launch. Changing `source`, `uniforms` or `attributes` recompiles the shader.
- Share one `SKShader` across many sprites so they still batch. Pass per-sprite values as attributes, not separate shader instances:

```swift
let flash = SKShader(source: """
void main() {
    vec4 c = texture2D(u_texture, v_tex_coord);
    gl_FragColor = vec4(mix(c.rgb, vec3(1.0), a_flash * c.a), c.a);
}
""")
flash.attributes = [SKAttribute(name: "a_flash", type: .float)]
sprite.shader = flash
sprite.setValue(SKAttributeValue(float: 1), forAttribute: "a_flash")   // hit flash on
```

- `SKUniform` values are shared by every node using the shader; use them for global parameters such as time of day.

## 2D lighting (`SKLightNode`)

- Add an `SKLightNode` and set its `categoryBitMask`. A sprite is lit when its `lightingBitMask` shares a bit with the light; `shadowCastBitMask` and `shadowedBitMask` work the same way.
- Normal maps give flat sprites depth: `SKSpriteNode(texture:normalMap:)`, or `texture.generatingNormalMap()` for a quick automatic one.
- Tune `lightColor`, `ambientColor` and `falloff`. Each light adds per-pixel work for every lit sprite, so keep lights few.

## Filters (`SKEffectNode` + `CIFilter`)

- An effect node renders its children offscreen every frame, applies the filter, and composites the result. That is expensive on every frame.
- `shouldRasterize = true` caches a static subtree; filter parameter changes do not invalidate the cache.
- Toggle with `shouldEnableEffects`. Prefer a full-screen effect node over many small ones.

## Masks and warps

- `SKCropNode` with a `maskNode` clips children. Each crop node adds an offscreen pass; use it sparingly.
- `SKWarpGeometryGrid(columns:rows:sourcePositions:destinationPositions:)` bends sprites (squash, wobble, jelly). Apply through `warpGeometry`, or animate with `SKAction.warp(to:duration:)`.

## Particles

- Author emitters as `.sks` files in Xcode's particle editor and load them with `SKEmitterNode(fileNamed:)`.
- `targetNode = scene` lets emitted particles stay in world space while the emitter moves (trails, exhaust).
- Prefer fewer, larger particles with short lifetimes. Avoid changing emitter properties every frame and never run actions on particles.
- `advanceSimulationTime(_:)` pre-warms an emitter so smoke or rain is already full on the first frame.
- Remove finished emitters: set `numParticlesToEmit`, then remove the node after the particle lifetime.
