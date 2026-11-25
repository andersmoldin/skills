# Sound-effect pool and music player

Read this when implementing sound effects or music on `AVAudioEngine`. The code compiles in Swift 6 for an iOS 26 target and uses the iOS 27 API names when available. An offline render confirmed that the music loop is gapless and that stingers land exactly on the bar.

## iOS 26 / iOS 27 helpers

```swift
import AVFoundation

extension AVAudioEngine {
    func link(_ a: AVAudioNode, to b: AVAudioNode, format: AVAudioFormat?) throws {
        if #available(iOS 27, *) { try connectNode(a, to: b, format: format) } else { connect(a, to: b, format: format) }
    }
}

extension AVAudioPlayerNode {
    func start(at time: AVAudioTime? = nil) throws {
        if #available(iOS 27, *) { try playAudio(at: time) } else { play(at: time) }
    }
}
```

## Sound-effect pool

```swift
@MainActor final class SFXPool {
    private let engine: AVAudioEngine
    private let bus = AVAudioMixerNode()
    private let format: AVAudioFormat                       // the one authored format, e.g. 48 kHz mono
    private var voices: [(player: AVAudioPlayerNode, varispeed: AVAudioUnitVarispeed)] = []
    private var next = 0
    private var buffers: [String: AVAudioPCMBuffer] = [:]

    var volume: Float { get { bus.outputVolume } set { bus.outputVolume = newValue } }

    init(engine: AVAudioEngine, format: AVAudioFormat, voiceCount: Int = 12) throws {
        self.engine = engine
        self.format = format
        engine.attach(bus)
        try engine.link(bus, to: engine.mainMixerNode, format: nil)
        for _ in 0..<voiceCount {
            let player = AVAudioPlayerNode(), varispeed = AVAudioUnitVarispeed()
            engine.attach(player); engine.attach(varispeed)
            try engine.link(player, to: varispeed, format: format)
            try engine.link(varispeed, to: bus, format: format)
            voices.append((player, varispeed))
        }
    }

    func preload(_ name: String, url: URL) throws {          // at load time, never when the sound fires
        let file = try AVAudioFile(forReading: url)
        guard file.processingFormat == format,               // convert assets offline; fail loudly here
              let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: AVAudioFrameCount(file.length))
        else { throw CocoaError(.fileReadCorruptFile) }
        try file.read(into: buffer)
        buffers[name] = buffer
    }

    func play(_ name: String, volume: Float = 1, pitchCents: Float = 0, pan: Float = 0) {
        guard engine.isRunning, let buffer = buffers[name] else { return }
        let voice = voices[next]
        next = (next + 1) % voices.count
        voice.player.stop()                                  // steal the oldest voice
        voice.player.volume = volume
        voice.player.pan = pan
        voice.varispeed.rate = powf(2, pitchCents / 1200)
        voice.player.scheduleBuffer(buffer, at: nil, options: [], completionHandler: nil)
        try? voice.player.start()
    }
}
```

Call with variation: `sfx.play("hit", volume: .random(in: 0.85...1), pitchCents: .random(in: -100...100))`.

## Music player with intro, gapless loop and stingers

```swift
@MainActor final class MusicPlayer {
    private let player = AVAudioPlayerNode()
    private let stinger = AVAudioPlayerNode()
    private var file: AVAudioFile?
    private var loopStart: AVAudioFramePosition = 0
    private var generation = 0                               // invalidates callbacks from old tracks

    init(engine: AVAudioEngine, format: AVAudioFormat) throws {
        engine.attach(player); engine.attach(stinger)
        try engine.link(player, to: engine.mainMixerNode, format: format)
        try engine.link(stinger, to: engine.mainMixerNode, format: format)
    }

    /// Plays [0, loopStartFrame) once, then loops [loopStartFrame, end) forever, streaming from disk.
    func play(url: URL, loopStartFrame: AVAudioFramePosition = 0) throws {
        let file = try AVAudioFile(forReading: url)
        stop()
        self.file = file
        loopStart = loopStartFrame
        if loopStartFrame > 0 {
            player.scheduleSegment(file, startingFrame: 0, frameCount: AVAudioFrameCount(loopStartFrame), at: nil)
        }
        enqueueLoop(generation); enqueueLoop(generation)     // always one iteration ahead
        try player.start()
    }

    func stop() { generation += 1; player.stop(); stinger.stop() }

    private func enqueueLoop(_ gen: Int) {
        guard gen == generation, let file else { return }
        player.scheduleSegment(file, startingFrame: loopStart, frameCount: AVAudioFrameCount(file.length - loopStart),
                               at: nil, completionCallbackType: .dataConsumed) { [weak self] _ in
            Task { @MainActor in self?.enqueueLoop(gen) }    // audio thread → main actor
        }
    }

    func playStingerOnNextBar(_ buffer: AVAudioPCMBuffer, bpm: Double, beatsPerBar: Double = 4) throws {
        guard let now = player.lastRenderTime, now.isSampleTimeValid,
              let playerTime = player.playerTime(forNodeTime: now) else { return }
        let bar = AVAudioFramePosition((60 / bpm * beatsPerBar * playerTime.sampleRate).rounded())
        let target = (playerTime.sampleTime / bar + 1) * bar
        guard let at = player.nodeTime(forPlayerTime: AVAudioTime(sampleTime: target, atRate: playerTime.sampleRate))
        else { return }
        stinger.stop()
        stinger.scheduleBuffer(buffer, at: nil, options: [], completionHandler: nil)
        try stinger.start(at: at)
    }
}
```

- Use the music file's `processingFormat` as `format` for the music player.
- For vertical layering (adding instruments with intensity), run one player per stem, start all of them at the same `AVAudioTime`, and fade each stem's volume.
- Call `play(url:)` again from the session's engine-restart callback; a stopped engine stops all players.
