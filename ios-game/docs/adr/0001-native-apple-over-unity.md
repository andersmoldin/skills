# Native Apple frameworks over Unity

The skills teach SpriteKit for 2D and RealityKit for 3D, hosted in SwiftUI, instead of Unity (or Three.js and other web or cross-platform engines). The audience is coding agents building iOS-only games, and agents work best in plain Swift and text files: an Xcode project builds, typechecks and tests from the command line, while a Unity project depends on an editor, binary scene and asset files, and a separate runtime that agents cannot inspect or verify as easily. Native frameworks also get Apple's newest game APIs first (Game Mode, Touch Controller, Game Center challenges and activities, Liquid Glass), add no engine runtime or license to the app, and keep the knowledge in one language.

## Considered options

- **Unity:** larger asset store and cross-platform reach, rejected because cross-platform is out of scope and its editor-centric workflow suits agents poorly.
- **SceneKit:** rejected because Apple deprecated it in iOS 26 (soft deprecation, maintenance mode) and recommends RealityKit.
- **Metal only:** maximum control, rejected as the default because it multiplies the code an agent must write and verify; the technology skills point to Metal only for effects the renderers cannot express.

## Consequences

Games built with these skills run on Apple platforms only. Porting a game to Android or consoles means a rewrite, which is an accepted cost of the iOS-only scope.
