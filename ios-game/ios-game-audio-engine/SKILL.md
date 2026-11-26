---
name: ios-game-audio-engine
description: Implements game audio on iOS (iOS 26+, Swift 6) with AVAudioSession and AVAudioEngine - session category, interruptions, pooled sound effects with pitch variation, gapless music loops and stingers, 3D positional sound, PHASE, SpriteKit and RealityKit audio, file formats and loudness. Use when adding sound or music to an iOS game, or when game audio stops, cuts out, lags or stops the player's own music.
license: MIT
---

# Game audio engine

One `@MainActor` audio object owns an `AVAudioEngine` for the whole game: sound-effect voices and music players feed per-bus mixers (sfx, music, ui), which feed the main mixer. Decide what the game sounds like with the `ios-game-audio-design` skill; this skill makes it play.

## Session: set it before any sound plays

```swift
import AVFoundation

@MainActor final class GameAudio {
    let engine = AVAudioEngine()
    private var observers: [Task<Void, Never>] = []
    var onMusicShouldBeSilenced: ((Bool) -> Void)?
    var onEngineRestarted: (() -> Void)?

    func start() throws {
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.ambient, mode: .default, options: [])  // mixes with the player's music
        try session.setActive(true)
        onMusicShouldBeSilenced?(session.secondaryAudioShouldBeSilencedHint)
        observe()
        engine.prepare()
        try engine.start()
    }

    private func observe() {
        let center = NotificationCenter.default
        let session = AVAudioSession.sharedInstance()
        observers.append(Task { [weak self] in        // hardware change (AirPods) stops the engine
            for await _ in center.notifications(named: .AVAudioEngineConfigurationChange, object: self?.engine) {
                self?.restart()
            }
        })
        observers.append(Task { [weak self] in        // a call or alarm ended
            for await note in center.notifications(named: AVAudioSession.interruptionNotification, object: session) {
                guard let raw = note.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt,
                      AVAudioSession.InterruptionType(rawValue: raw) == .ended else { continue }
                self?.restart()
            }
        })
        observers.append(Task { [weak self] in        // another app started non-mixable audio
            for await note in center.notifications(named: AVAudioSession.silenceSecondaryAudioHintNotification,
                                                   object: session) {
                guard let raw = note.userInfo?[AVAudioSessionSilenceSecondaryAudioHintTypeKey] as? UInt else { continue }
                self?.onMusicShouldBeSilenced?(AVAudioSession.SilenceSecondaryAudioHintType(rawValue: raw) == .begin)
            }
        })
    }

    private func restart() {
        guard !engine.isRunning else { return }
        do {
            try AVAudioSession.sharedInstance().setActive(true)
            try engine.start()
            onEngineRestarted?()                       // players were stopped: restart the music
        } catch {
            print("Audio engine restart failed: \(error)")   // fail visibly, retry on next foreground
        }
    }
}
```

- `.ambient` is the game category: it mixes with the player's own music and respects the Silent switch. The default, `.soloAmbient`, stops the player's music the moment the game starts. Choose `.soloAmbient` deliberately when the soundtrack is part of the experience and should replace the player's music; use `.playback` only when sound is the game itself (rhythm games), since it ignores the Silent switch.
- While `secondaryAudioShouldBeSilencedHint` is true, mute your music and keep sound effects.
- Resume after interruptions without asking; games do not need to check the interruption options.
- `mediaServicesWereResetNotification` invalidates every audio object: rebuild the engine and graph, and set the category again.
- iOS 27 adds `AVAudioSession.resumptionRecommendationNotification`; keep `interruptionNotification` for the iOS 26 path.

## Effects and music

Read [references/engine-code.md](references/engine-code.md) for a verified sound-effect pool and music player. The rules they follow:

- Decode every sound effect into an `AVAudioPCMBuffer` at load time. Never read files or allocate buffers when a sound fires.
- Play effects through a fixed pool of `AVAudioPlayerNode` voices (8 to 16) with round-robin voice stealing. Each voice has an `AVAudioUnitVarispeed`; set `rate = pow(2, cents / 1200)` for random pitch of about ±100 cents and vary volume slightly, so repeated sounds do not fatigue.
- Stream music from file: queue segments with `scheduleSegment(..., at: nil)` and keep one loop iteration queued ahead. That is gapless and keeps memory flat. Re-queue on `.dataConsumed`.
- Start stingers and layer changes on a beat or bar boundary computed from the music player's sample time (`playerTime(forNodeTime:)`, `nodeTime(forPlayerTime:)`).
- iOS 27 renames `connect` and `play` to throwing `connectNode` and `playAudio`; wrap both behind `if #available(iOS 27, *)` helpers as the reference code does.

## 3D sound

- 2D games: pan (`player.pan`) by screen position and attenuate by distance yourself.
- 3D games on `AVAudioEngine`: connect mono players to an `AVAudioEnvironmentNode`, set `renderingAlgorithm = .auto`, and update `position` and `listenerPosition` each frame. Stereo sources are never spatialized.
- RealityKit games: use `SpatialAudioComponent` on entities and `entity.playAudio(_:)`, `ChannelAudioComponent` for music and UI, and `AudioFileResource` with `.preload` for effects and `.stream` for music.
- PHASE (iOS 15) when sound must react to level geometry (occlusion, reverb from meshes) or designers need random, switch and blend sound-event trees. It needs more setup than `AVAudioEngine`.
- iOS spatializes game audio automatically for headphones. If you spatialize yourself, opt out with the Info.plist key `AVGameBypassSystemSpatialAudio`.

## SpriteKit audio

`SKAction.playSoundFileNamed(_:waitForCompletion:)` suits rare incidental sounds only: it has no volume, pitch or stop control. `SKAudioNode` loops by default and is positional relative to `scene.listener`; set the listener to the camera or player node. Anything frequent goes through the effect pool.

## Files and loudness

- Sound effects: 16-bit PCM `.caf`, mono, all in one sample rate (for example 48 kHz) so the pool has one connection format. Convert: `afconvert -f caff -d LEI16@48000 -c 1 in.wav out.caf`.
- Music and long ambience: AAC `.m4a` (`afconvert -f m4af -d aac -b 128000 in.wav out.m4a`). AAC loops gaplessly with segment queueing; avoid MP3 for loops.
- Memory: decoded audio is 4 bytes per sample per channel. One second of 48 kHz mono is about 188 KB; three minutes of stereo music decoded would be about 66 MB, which is why music streams.
- Loudness target for handheld games: about −18 LUFS integrated (±2), true peak below −1 dBTP. Mix relative levels; never change the system volume.

## Haptics synced to sound

For a haptic that must land with a sound, put the sound inside the Core Haptics pattern (`registerAudioResource(_:options:)` plus an `.audioCustom` event), so both share one clock. Such an engine is created with `CHHapticEngine(audioSession: .sharedInstance())` and must keep `playsHapticsOnly` false, or it drops the audio events. See the `ios-game-controller` skill for the haptics engine.

## Gotchas

- Never call `stop()` on a player inside its own completion handler; it deadlocks.
- The configuration-change notification arrives on an internal queue; never tear down the engine inside it.
- `routeChangeNotification` is posted on a background thread; hop to the main actor (the `for await` pattern above does).
- AirPlay and Bluetooth add output latency; read `session.outputLatency` before syncing audio to visuals.
- SceneKit audio (`SCNAudioSource`, `SCNAudioPlayer`) is deprecated with SceneKit.
- `AVAudioPCMBuffer` is not `Sendable`; keep buffers on the audio object's actor.
