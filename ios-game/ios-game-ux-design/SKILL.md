---
name: ios-game-ux-design
description: Designs the user experience and game feel of an iOS game - input responsiveness, movement tuning, forgiveness (coyote time, input buffering), flow and difficulty, onboarding, session flow and accessibility of play. Use when controls feel sluggish, floaty, unfair or confusing, when tuning jumps, movement or difficulty, or when designing the first minutes and accessibility options.
license: MIT
---

# Game UX design and game feel

User experience design combines all the other disciplines into how playing the game feels, often called game feel: whether the flow of play and every interaction with the game work smoothly. Tune it first, in a prototype with placeholder art, because no polish can rescue controls that feel wrong.

## Steps

1. Build a test room: one flat level with a few gaps, walls, slopes and targets, reachable from a debug menu.
2. Tune movement and actions there using the rules below. Done when moving and acting feel good with grey boxes and no sound.
3. Add forgiveness (below) and verify each window by playing deliberately late and early inputs.
4. Store the movement values and every forgiveness window (in seconds) in `Tuning.json`. Write the **Feel** section of `GAME_DESIGN.md`: the target feel in three words and the `Tuning.json` keys that produce it.
5. Design the first five minutes and the accessibility options (below). Done when a first-time player reaches the core loop without reading text.

## Responsiveness

- React on the frame the input arrives. Start the animation, sound or haptic immediately, even when the action resolves later.
- Express every time window in seconds, never in frames: iPhones run anywhere from 30 to 120 Hz.
- Keep total input-to-screen latency low: poll input at the start of each update, avoid extra frames of animation wind-up for frequent actions.
- Feel has three layers: instant response to input, a space whose obstacles give movement meaning, and polish that sells weight and material (`ios-game-art-direction`).

## Movement tuning

- Tune from designer-facing values, not physics constants: choose jump height and time to apex, then derive gravity `g = 2h / t²` and launch speed `v = 2h / t`.
- Fall faster than you rise (gravity multiplier of about 1.5 to 2 when falling), and cut the jump short when the button is released early, for variable jump height.
- Accelerate and decelerate quickly; slow ramps feel floaty, instant stops feel stiff. Tune both.
- Camera follows with slight lag and looks ahead in the movement direction.

## Forgiveness

- **Coyote time:** allow a jump for about 0.1 s after walking off a ledge.
- **Input buffering:** remember a jump or attack pressed about 0.1 to 0.15 s before it becomes possible, and perform it as soon as it is.
- **Corner correction:** nudge the player around a corner they barely clip.
- **Generous hitboxes:** the player's hurtbox is slightly smaller than the sprite, pickups slightly larger.
- Forgiveness is invisible; players notice only that the game feels fair.

## Flow and difficulty

- Keep challenge matched to skill: too easy is boring, too hard is anxious.
- Let players pick their challenge through visible options (optional harder routes, assist toggles such as slower game speed, extra health, skip a section) rather than hidden adjustment.
- Measure where players die, retry and quit (local analytics events in debug builds) and smooth the spikes.

## The first minutes

- Playable within seconds: no account wall, no settings questions; defaults come from the device.
- Teach one mechanic at a time, through play. Written tutorials are optional reference and stay findable after being skipped.
- Ask for permissions when the feature needs them, and for an App Store rating only after real play.
- Resume where the player left off; save often.

## Accessibility of play

- Remappable or simplified controls, one-handed play where possible, no required multi-finger gestures.
- Game speed and assist options; no time-limited prompts that cannot be extended.
- Respect Reduce Motion (`@Environment(\.accessibilityReduceMotion)` or `UIAccessibility.isReduceMotionEnabled`): tone down shake, zoom and flashes, prefer fades.
- Captions for voice, visual and haptic forms of audio cues, color-independent signals.
- Haptics off switch and adjustable intensity.

## Related skills

Implementing input: `ios-game-controller`. Visual feedback and juice: `ios-game-art-direction`. Audio feedback: `ios-game-audio-design`. Interface accessibility: `ios-game-ui-design`.
