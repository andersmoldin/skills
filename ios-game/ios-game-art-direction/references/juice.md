# Juice recipes

Read this when the core loop works and actions need impact. Juice amplifies good mechanics; it cannot fix weak ones, so tune feel first (`ios-game-ux-design`). Layer several small responses on each important event, and scale every effect down or off when Reduce Motion is on.

## Easing

- Things arriving ease out (fast start, soft landing); things leaving ease in; things moving between two rest points ease in and out.
- Overshoot (back) and elastic curves suit playful moments such as a button popping in or a coin landing; use them sparingly.
- Use the standard families (sine, quad, cubic, back, elastic, bounce) from Robert Penner's equations. SpriteKit: `SKAction.timingMode` or a custom `timingFunction`; RealityKit: `move(to:relativeTo:duration:timingFunction:)`; SwiftUI: spring animations.
- Typical durations: 0.1 to 0.2 s for feedback, 0.25 to 0.4 s for interface transitions.

## Screen shake

Drive shake from a decaying trauma value instead of fixed offsets:

```swift
struct ScreenShake {
    var trauma: Float = 0                        // 0...1
    let maxOffset: Float = 12                    // points
    let maxAngle: Float = 0.05                   // radians, 2D only
    let decayPerSecond: Float = 1.5
    private var time: Float = 0

    mutating func add(_ amount: Float) { trauma = min(1, trauma + amount) }

    mutating func update(dt: Float, reduceMotion: Bool) -> (x: Float, y: Float, angle: Float) {
        time += dt
        trauma = max(0, trauma - decayPerSecond * dt)
        let shake = (reduceMotion ? 0.25 : 1) * trauma * trauma          // squared: small hits stay subtle
        func wave(_ seed: Float) -> Float {                              // smooth pseudo-noise in -1...1
            (sin(time * 37 + seed) + sin(time * 23.3 + seed * 2)) / 2
        }
        return (maxOffset * shake * wave(1), maxOffset * shake * wave(7), maxAngle * shake * wave(13))
    }
}
```

Apply the result to the camera each frame (`SKCameraNode` position and `zRotation`, or the camera entity's transform) on top of its follow position. Add about 0.2 trauma for a light hit, 0.5 for an explosion.

## Hit-stop and flashes

- Freeze the attacker and the target for about 0.05 s on a light hit and up to 0.15 s on a heavy one; keep input buffered during the freeze.
- Flash the hit target white for one or two frames (a shader attribute in SpriteKit, a brief emissive or unlit material in RealityKit).
- Knock the target back slightly, and squash it on impact.

## Squash and stretch

Stretch along the direction of fast motion, squash on landing and impact, and preserve volume (scale x by 1.2 when y is 0.8). Return with an ease-out over about 0.1 s.

## Particles

- Every hit, pickup, landing and destruction emits a short burst: 5 to 20 particles, short lifetimes, palette colors.
- Persistent effects (trails, dust, ambient motes) use low birth rates.
- Leave some permanence: debris, marks and scorch decals that fade slowly make actions feel consequential. Cap their number for performance.

## Camera and light

- Smooth camera follow with slight lag and look-ahead; a small zoom punch (2 to 5 %) on big moments.
- A vignette and one warm key light focus the eye; flicker light sources gently for life.
- Bloom on bright effects sells energy: in 3D, iOS 27's `BloomComponent` or a custom post-process effect on iOS 26; in 2D, additive-blend glow sprites.

## Interface juice

Buttons scale down on press and spring back on release; numbers count up instead of jumping; rewards fly to their counter; new items pop in with a slight overshoot.
