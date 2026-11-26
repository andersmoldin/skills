---
name: ios-game-design
description: Routes iOS game work to the right design or technology skill and sets the project baseline (iOS 26+, Swift 6, SwiftUI, SpriteKit for 2D, RealityKit for 3D, Game Mode, frame rate, power). Use first when designing, building or polishing an iOS game, or when unsure which game skill applies.
license: MIT
---

# iOS game design

This router names the skill for each part of building an iOS game and holds the project baseline every game shares. Discipline skills decide what the game is; technology skills implement it on Apple frameworks.

## Which skill

| Working on | Skill |
|---|---|
| Premise, setting, theme, world rules, map | `ios-game-world-design` |
| Core loop, rules, economy, progression, balance, difficulty numbers | `ios-game-system-design` |
| Characters, items, puzzles, missions, rewards, procedural content | `ios-game-content-design` |
| Story, dialogue, text, branching, environmental storytelling | `ios-game-writing` |
| Level layout, pacing, teaching through space, guiding the eye | `ios-game-level-design` |
| HUD, menus, touch-control layout, information shown to the player | `ios-game-ui-design` |
| What the game sounds like: effects, music, voice, adaptive audio | `ios-game-audio-design` |
| Game feel, responsiveness, forgiveness, onboarding, flow, accessibility | `ios-game-ux-design` |
| Visual style, palette, assets, particles, screen shake, easing, lighting mood | `ios-game-art-direction` |
| 2D rendering, scenes, physics | `ios-game-spritekit` |
| 3D rendering, entities, physics | `ios-game-realitykit` |
| Game Center, leaderboards, achievements, Games app, multiplayer | `ios-game-gamekit` |
| Touch controls, controllers, keyboard and mouse, haptics | `ios-game-controller` |
| Playing sound and music in code | `ios-game-audio-engine` |

## The design doc

Every game keeps one design doc, `GAME_DESIGN.md`, at the root of the game's repository. Each discipline skill owns one section of it (World, Systems, Content, Writing, Levels, UI, Audio, Feel, Art direction). Read the doc before changing the game, and update the owning section when a decision changes. Tuning numbers live only in data files: global values in `Tuning.json`, per-entry values in content files. The doc names the keys it relies on and never repeats their values.

## Building a new game

1. Write the pitch at the top of `GAME_DESIGN.md`: one-sentence premise, target player, core verb, session length, 2D or 3D. Done when a stranger could tell from it what the player does in the first minute.
2. `ios-game-world-design` and `ios-game-system-design`: the world brief and the core loop.
3. `ios-game-art-direction`: the style guide, before any asset is made.
4. Build a playable prototype of the core loop with `ios-game-spritekit` or `ios-game-realitykit` plus `ios-game-controller`, and tune it with `ios-game-ux-design` until moving and acting feel good with placeholder art.
5. `ios-game-level-design` and `ios-game-content-design`, then `ios-game-writing`.
6. `ios-game-ui-design` and `ios-game-audio-design`, implemented with `ios-game-audio-engine`.
7. `ios-game-gamekit`, then a polish pass with `ios-game-art-direction` (juice) and a performance pass on a real device.

Keep the game original: borrow genre conventions and mechanics, never another game's names, characters, art, music or levels.

## Project baseline

- **Toolchain:** deployment target iOS 26. App Store uploads must be built with Xcode 26 or later and the iOS 26 SDK; current Xcode is 27. Gate iOS 27 APIs with `if #available(iOS 27, *)` and provide a fallback. Swift 6 language mode (`SWIFT_VERSION = 6`; templates still default to 5). Xcode 27 app templates also set `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` and `SWIFT_APPROACHABLE_CONCURRENCY = YES`; keep both, and write code that also compiles without them, as the skills' samples do.
- **App shell:** SwiftUI `App` with the game view (`SpriteView` or `RealityView`) full-bleed via `.ignoresSafeArea()`, HUD and menus as SwiftUI overlays or engine nodes.
- **Renderer:** SpriteKit for 2D, RealityKit for 3D. SceneKit is deprecated since iOS 26; do not start new work on it. These skills cover Apple's native frameworks only, not third-party engines.
- **Metal:** only when the renderer cannot express an effect. Prefer custom shaders inside SpriteKit or RealityKit first. Metal 4 needs an A14 or newer, while iOS 26 still runs on A13 devices, so keep a Metal 3 path.
- **Game Mode:** add `LSSupportsGameMode = YES` to Info.plist by hand (Xcode's "Supports Game Mode" setting writes the deprecated `GCSupportsGameMode`). Set the Xcode App Category to a games category (`LSApplicationCategoryType`, for example `public.app-category.action-games`) and the App Store category to Games, which also makes the game eligible for the Games app. Game Mode engages when the game runs full screen.
- **Frame rate:** add `CADisableMinimumFrameDurationOnPhone = YES` to Info.plist so iPhones can run above 60 Hz, request the rate in the renderer, and scale all motion by elapsed time; refresh rate varies from 30 to 120 Hz.
- **Power and heat:** observe `ProcessInfo.thermalStateDidChangeNotification` and `NSProcessInfoPowerStateDidChange` (Low Power Mode); lower effects or frame rate when either rises. Read `thermalState` once at launch.
- **Lifecycle:** pause when `scenePhase` leaves `.active`, save progress at safe points, restore it on relaunch.
- **Screen:** size layout from the view or window bounds, never `UIScreen.main` (deprecated in iOS 26). Apps built with the iOS 27 SDK can be resized on iPad and on foldable iPhones; re-read the size on every change and keep HUD inside the current safe area.
- **AI features:** Foundation Models and Image Playground need Apple Intelligence hardware and are optional on iOS 26 devices; never make gameplay depend on them.

## Verifying an Apple API

Before using a symbol you have not used on iOS 26, fetch `https://developer.apple.com/tutorials/data/documentation/<framework>/<symbol>.json` (lowercased path) and read `metadata.platforms` for the iOS entry: `introducedAt` and `deprecatedAt`. Then typecheck against the iOS 26 target: `xcrun --sdk iphoneos swiftc -parse-as-library -typecheck -swift-version 6 -target arm64-apple-ios26.0 File.swift`.
