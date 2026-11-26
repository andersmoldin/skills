# Core Haptics for games

Read this when gameplay needs custom haptics: impacts with varying strength, continuous rumbles, or patterns synced to sound.

## Engine lifecycle

```swift
import CoreHaptics

@MainActor final class Haptics {
    private var engine: CHHapticEngine?

    init() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics,
              let engine = try? CHHapticEngine() else { return }      // iPad: no haptics
        engine.playsHapticsOnly = true                              // false if patterns contain audio events
        engine.isAutoShutdownEnabled = true                           // stops when idle, restarts on demand
        engine.stoppedHandler = { reason in print("Haptics stopped: \(reason.rawValue)") }
        engine.resetHandler = { [weak engine] in try? engine?.start() }   // then recreate players
        try? engine.start()
        self.engine = engine
    }

    func impact(intensity: Float, sharpness: Float) {
        guard let engine else { return }
        let event = CHHapticEvent(eventType: .hapticTransient, parameters: [
            CHHapticEventParameter(parameterID: .hapticIntensity, value: intensity),
            CHHapticEventParameter(parameterID: .hapticSharpness, value: sharpness)], relativeTime: 0)
        do {
            let player = try engine.makePlayer(with: CHHapticPattern(events: [event], parameters: []))
            try player.start(atTime: CHHapticTimeImmediate)
        } catch {
            print("Haptic failed: \(error)")
        }
    }
}
```

- `playsHapticsOnly = true` lowers latency but makes the engine ignore audio events. For patterns that carry their own sound, create the engine with `CHHapticEngine(audioSession: .sharedInstance())` and leave `playsHapticsOnly` false.
- Create the engine at launch and keep a strong reference. Set `stoppedHandler` and `resetHandler` before `start()`.
- `stoppedHandler` fires when the system stops the engine (backgrounding, audio interruption, errors). `resetHandler` fires after the haptic server restarts: start the engine again and recreate every player.
- Starting a stopped engine on first play adds noticeable latency; start it before gameplay.

## Patterns

- `.hapticTransient` is a tap; `.hapticContinuous` with a `duration` is a rumble. Intensity and sharpness run from 0 to 1.
- Modulate a running pattern with `CHHapticDynamicParameter` or `CHHapticParameterCurve` (an engine revving, a charge building up). Use `makeAdvancedPlayer(with:)` for looping and seeking.
- AHAP files are JSON patterns that designers can edit without code. Load with `CHHapticPattern(contentsOf:)` or `engine.playPattern(from:)`.
- Map haptic strength to game events consistently: the same event always feels the same, bigger events feel stronger. Keep continuous haptics short; long rumbles drain the battery.

## Controller rumble

- `controller.haptics?.createEngine(withLocality: .default)` returns a `CHHapticEngine` for the controller; other localities target handles or triggers.
- That engine's `supportsHaptics` describes the phone, not the controller. Check `controller.haptics?.supportedLocalities` instead.
