# iOS game skills

Agent skills for designing and building iOS games, distilled from game design disciplines and Apple developer sources. They install with the rest of this repo as the `moldin-skills` plugin; the skill table is in the [root README](../README.md#ios-games).

The skills teach coding agents two things: what makes a game good (the design disciplines from Wikipedia's [Video game design](https://en.wikipedia.org/wiki/Video_game_design) article, supplemented by recognized game design sources), and how to build it on current Apple frameworks (WWDC 2024–2026, iOS 26 and later).

`ios-game-design` is the router: start there. Discipline skills decide what the game is and point to technology skills for the code. All of them share one design doc, `GAME_DESIGN.md`, in the game's repository. Terms are defined in [GLOSSARY.md](GLOSSARY.md); the choice of native frameworks is recorded in [docs/adr/0001-native-apple-over-unity.md](docs/adr/0001-native-apple-over-unity.md).

## Scope

- iOS only, minimum deployment target iOS 26, Swift 6, SwiftUI app shell.
- SpriteKit for 2D, RealityKit for 3D. SceneKit is deprecated and not taught; Metal appears only as a pointer for effects the renderers cannot express.
- Out of scope: Unity, Three.js and other engines, other Apple platforms, Game Porting Toolkit.

## Changing the skills

No automated test checks what the skills teach. They are evaluated by building games with them and checking where agents go wrong. Before opening a pull request:

1. Keep each `SKILL.md` short: steps and defaults first, longer material in that skill's `references/` folder, linked from `SKILL.md`.
2. Keep sources here in the README, under the skill they support, not in skill files.
3. Verify every Apple API you add against its documentation (`https://developer.apple.com/tutorials/data/documentation/<framework>/<symbol>.json`, iOS entry in `metadata.platforms`) and typecheck code samples: `xcrun --sdk iphoneos swiftc -parse-as-library -typecheck -swift-version 6 -target arm64-apple-ios26.0 Sample.swift`.
4. Run the repo's checks listed in [AGENTS.md](../AGENTS.md#checks).

Skill writing follows Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), the [Agent Skills specification](https://agentskills.io/specification), and the Claude Code [plugin](https://code.claude.com/docs/en/plugins-reference) and [marketplace](https://code.claude.com/docs/en/plugin-marketplaces) references.

## Sources

Wikipedia content is paraphrased, not copied. Every other source is summarized in the skills' own words.

### ios-game-design

- Wikipedia, [Video game design](https://en.wikipedia.org/wiki/Video_game_design) (structure of the discipline skills)
- WWDC25 [Level up your games](https://developer.apple.com/videos/play/wwdc2025/209/)
- WWDC24 [Design advanced games for Apple platforms](https://developer.apple.com/videos/play/wwdc2024/10085/)
- WWDC26 [Platforms State of the Union](https://developer.apple.com/videos/play/wwdc2026/102/), [Modernize your UIKit app](https://developer.apple.com/videos/play/wwdc2026/278/)
- WWDC25 [Discover Metal 4](https://developer.apple.com/videos/play/wwdc2025/205/)
- Meet with Apple [Level up with Apple game technologies](https://developer.apple.com/videos/play/meet-with-apple/240/), [Explore power, performance, and scale for games on iPhone and iPad](https://developer.apple.com/videos/play/meet-with-apple/242/)
- Apple documentation: [LSSupportsGameMode](https://developer.apple.com/documentation/bundleresources/information-property-list/lssupportsgamemode), [CADisableMinimumFrameDurationOnPhone](https://developer.apple.com/documentation/bundleresources/information-property-list/cadisableminimumframedurationonphone), [Optimizing iPhone and iPad apps to support ProMotion displays](https://developer.apple.com/documentation/quartzcore/optimizing-iphone-and-ipad-apps-to-support-promotion-displays)
- Apple [Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/); Apple Support [Use Game Mode](https://support.apple.com/en-us/105118)

### ios-game-world-design

- Wikipedia, [Video game design § World design](https://en.wikipedia.org/wiki/Video_game_design#World_design) and [Worldbuilding](https://en.wikipedia.org/wiki/Worldbuilding)
- Henry Jenkins, [Game Design as Narrative Architecture](https://web.mit.edu/~21fms/People/henry3/games&narrative.html) (2004)
- Fujibayashi, Takizawa, Dohta, [Change and Constant: Breaking Conventions with The Legend of Zelda: Breath of the Wild](https://www.youtube.com/watch?v=QyMsF31NdNc) (GDC 2017)
- Kate Edwards, [A Geographer's Guide to Building Game Worlds](https://gdcvault.com/play/1023762/A-Geographer-s-Guide-to) (GDC Europe 2016)
- Ken Wong, [Designing Monument Valley: Less Game, More Experience](https://gdcvault.com/play/1020878/Designing-Monument-Valley-Less-Game) (GDC Europe 2014)
- Raylene Deck, [World Design for Different Player Types](https://gdcvault.com/play/1025881/Level-Design-Workshop-World-Design) (GDC 2019)
- Jesse Schell, [The Art of Game Design: A Book of Lenses](https://www.routledge.com/The-Art-of-Game-Design-A-Book-of-Lenses-Third-Edition/Schell/p/book/9781138632059), 3rd ed. (2019)

### ios-game-system-design

- Wikipedia, [Video game design § System design](https://en.wikipedia.org/wiki/Video_game_design#System_design)
- Hunicke, LeBlanc, Zubek, [MDA: A Formal Approach to Game Design and Game Research](https://users.cs.northwestern.edu/~hunicke/MDA.pdf) (2004)
- Sid Meier, [Interesting Decisions](https://www.youtube.com/watch?v=WggIdtrqgKg) (GDC 2012)
- Daniel Cook, [The Chemistry of Game Design](https://www.gamedeveloper.com/design/the-chemistry-of-game-design) (2007) and [Loops and Arcs](https://lostgarden.com/2012/04/30/loops-and-arcs/) (2012)
- Ian Schreiber, [Game Balance Concepts](https://gamebalanceconcepts.wordpress.com/) (2010)
- Michael Sellers, [Advanced Game Design: A Systems Approach](https://www.informit.com/store/advanced-game-design-a-systems-approach-9780134667607) (2017)
- Raph Koster, [A Theory of Fun for Game Design](https://www.theoryoffun.com/) (2004)
- Apple [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) (3.1.1, randomized items)

### ios-game-content-design

- Wikipedia, [Video game design § Content design](https://en.wikipedia.org/wiki/Video_game_design#Content_design)
- Tanya Short and Tarn Adams (eds.), [Procedural Generation in Game Design](https://www.routledge.com/Procedural-Generation-in-Game-Design/Short-Adams/p/book/9781498799195) (2017)
- Kate Compton, [So you want to build a generator…](https://web.archive.org/web/20260823043804/https://galaxykate0.tumblr.com/post/139774965871/so-you-want-to-build-a-generator) (2016, archived)
- Jonathan Blow and Marc ten Bosch, [Designing to Reveal the Nature of the Universe](https://www.youtube.com/watch?v=OGSeLSmOALU) (IndieCade 2011)
- Mark Brown, [What Makes a Good Puzzle?](https://www.youtube.com/watch?v=zsjC6fa_YBg) (Game Maker's Toolkit, 2018)
- Travis Day, [Rewards in Video Games](https://gdcvault.com/play/1023948/Rewards-in-Video) (GDC 2017)
- Ian Schreiber and Brenda Romero, [Game Balance](https://www.routledge.com/Game-Balance/Schreiber-Romero/p/book/9781498799577) (2021)

### ios-game-writing

- Wikipedia, [Video game design § Game writing](https://en.wikipedia.org/wiki/Video_game_design#Game_writing) and [Video game writing](https://en.wikipedia.org/wiki/Video_game_writing)
- Clint Hocking, [Ludonarrative Dissonance in Bioshock](https://web.archive.org/web/20250924215901/https://clicknothing.typepad.com/click_nothing/2007/10/ludonarrative-d.html) (2007, archived)
- Harvey Smith and Matthias Worch, [What Happened Here? Environmental Storytelling](https://www.gdcvault.com/play/1012647) (GDC 2010)
- Sam Kabo Ashwell, [Standard Patterns in Choice-Based Games](https://heterogenoustasks.wordpress.com/2015/01/26/standard-patterns-in-choice-based-games/) (2015)
- Emily Short, [Beyond Branching: Quality-Based, Salience-Based, and Waypoint Narrative Structures](https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/) (2016)
- inkle, [Writing with ink](https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md)
- WWDC26 [What's new in the Foundation Models framework](https://developer.apple.com/videos/play/wwdc2026/241/); WWDC25 [Meet the Foundation Models framework](https://developer.apple.com/videos/play/wwdc2025/286/)

### ios-game-level-design

- Wikipedia, [Video game design § Level design](https://en.wikipedia.org/wiki/Video_game_design#Level_design) and [Level design](https://en.wikipedia.org/wiki/Level_design)
- Dan Taylor, [Ten Principles for Good Level Design](https://www.youtube.com/watch?v=iNEe3KhMvXM) (GDC 2013)
- Christian Nutt, [The Structure of Fun: Learning from Super Mario 3D Land's Director](https://www.gamedeveloper.com/design/the-structure-of-fun-learning-from-i-super-mario-3d-land-i-s-director) (2012)
- Mark Brown, [Super Mario 3D World's 4 Step Level Design](https://www.youtube.com/watch?v=dBmIkEvEBtA) (Game Maker's Toolkit, 2015)
- Christopher W. Totten, [An Architectural Approach to Level Design](https://www.routledge.com/An-Architectural-Approach-to-Level-Design-Second-edition/Totten/p/book/9780815361367), 2nd ed. (2019)

### ios-game-ui-design

- Wikipedia, [Video game design § User interface design](https://en.wikipedia.org/wiki/Video_game_design#User_interface_design)
- Apple Human Interface Guidelines: [Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games), [Game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls), [Layout](https://developer.apple.com/design/human-interface-guidelines/layout), [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility), [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- WWDC26 [Make your game great with touch](https://developer.apple.com/videos/play/wwdc2026/358/); WWDC25 [Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/)
- Meet with Apple [Design great interfaces for handheld games](https://developer.apple.com/videos/play/meet-with-apple/243/)
- Celia Hodent, [The Gamer's Brain](https://www.routledge.com/The-Gamers-Brain-How-Neuroscience-and-UX-Can-Impact-Video-Game-Design/Hodent/p/book/9780367638184)
- [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/full-list/)
- Erik Fagerholt and Magnus Lorentzon, [Beyond the HUD](https://publications.lib.chalmers.se/records/fulltext/111921.pdf) (Chalmers, 2009)

### ios-game-audio-design

- Wikipedia, [Video game design § Audio design](https://en.wikipedia.org/wiki/Video_game_design#Audio_design)
- Karen Collins, [Game Sound](https://mitpress.mit.edu/9780262033787/game-sound/) (MIT Press, 2008)
- Winifred Phillips, [A Composer's Guide to Game Music](https://mitpress.mit.edu/9780262026642/a-composers-guide-to-game-music/) (MIT Press, 2014) and [From 'Spyder' to 'Sackboy'](https://www.youtube.com/watch?v=XPV258XyNy8) (GDC 2021)
- Apple Human Interface Guidelines: [Playing audio](https://developer.apple.com/design/human-interface-guidelines/playing-audio), [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- Tomas Pettersson, [sfxr](https://www.drpetter.se/project_sfxr.html); [jsfxr](https://sfxr.me/)
- [Freesound FAQ](https://freesound.org/help/faq/) (licenses)
- ITU-R [BS.2434](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BS.2434-2018-PDF-E.pdf) (loudness, citing Sony ASWG-R001)

### ios-game-ux-design

- Wikipedia, [Video game design § User experience design](https://en.wikipedia.org/wiki/Video_game_design#User_experience_design) and [Game feel](https://en.wikipedia.org/wiki/Game_feel)
- Steve Swink, [Game Feel](https://www.routledge.com/Game-Feel-A-Game-Designers-Guide-to-Virtual-Sensation/Swink/p/book/9780123743282) (2008) and [Game Feel: The Secret Ingredient](https://www.gamedeveloper.com/design/game-feel-the-secret-ingredient) (2007)
- Maddy Thorson, [Celeste & Forgiveness](https://maddymakesgames.com/articles/celeste_and_forgiveness/index.html) (2020)
- Kyle Pittman, [Math for Game Programmers: Building a Better Jump](https://www.youtube.com/watch?v=hG9SzQxaCm8) (GDC 2016)
- Jenova Chen, [Flow in Games](https://www.jenovachen.com/flowingames/) (2006); Mihaly Csikszentmihalyi, *Flow: The Psychology of Optimal Experience* (1990)
- Celia Hodent, [The Gamer's Brain, Part 2: UX of Onboarding and Player Engagement](https://www.youtube.com/watch?v=Paf6B1jleCo)
- Microsoft, [Xbox Accessibility Guidelines](https://learn.microsoft.com/en-us/xbox/accessibility/guidelines)
- Apple Human Interface Guidelines: [Onboarding](https://developer.apple.com/design/human-interface-guidelines/onboarding), [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)

### ios-game-art-direction

- Martin Jonasson and Petri Purho, [Juice it or lose it](https://www.youtube.com/watch?v=Fy0aCDmgnxg) (2012)
- Jan Willem Nijman, [The Art of Screenshake](https://www.youtube.com/watch?v=AJdEqssNZ-U) (2013)
- Squirrel Eiserloh, [Math for Game Programmers: Juicing Your Cameras With Math](https://www.youtube.com/watch?v=tu-Qe66AvtY) (GDC 2016)
- Masahiro Sakurai, [Eight Hit Stop Techniques](https://www.youtube.com/watch?v=tycbMSjDDLg) (2022)
- Hicks, Gerling, Dickinson, Vanden Abeele, *Juicy Game Design: Understanding the Impact of Visual Embellishments on Player Experience* (CHI PLAY 2019, [doi:10.1145/3311350.3347171](https://doi.org/10.1145/3311350.3347171))
- Robert Penner, [Easing functions](https://robertpenner.com/easing/); [easings.net](https://easings.net/)
- Mitchell, Francke, Eng, [Illustrative Rendering in Team Fortress 2](https://steamcdn-a.akamaihd.net/apps/valve/2007/NPAR07_IllustrativeRenderingInTeamFortress2.pdf) (NPAR 2007)
- Ken Wong, [The Art of Monument Valley](https://gdcvault.com/play/1022299/The-Art-of-Monument) (GDC 2015)
- Asset licenses: [Kenney](https://kenney.nl/support), [Poly Haven](https://polyhaven.com/license), [Quaternius](https://quaternius.com/faq.html), [OpenGameArt FAQ](https://opengameart.org/content/faq), [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Apple [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) (5.2)
- WWDC25 [Create icons with Icon Composer](https://developer.apple.com/videos/play/wwdc2025/361/); WWDC26 [Create high-quality images using Image Playground](https://developer.apple.com/videos/play/wwdc2026/375/)

### ios-game-spritekit

- Apple documentation: [SpriteKit](https://developer.apple.com/documentation/spritekit), [SpriteView](https://developer.apple.com/documentation/spritekit/spriteview), [Responding to frame-cycle events](https://developer.apple.com/documentation/spritekit/responding-to-frame-cycle-events), [Maximizing node drawing performance](https://developer.apple.com/documentation/spritekit/maximizing-node-drawing-performance), [Maximizing texture performance](https://developer.apple.com/documentation/spritekit/maximizing-texture-performance), [Optimizing emitter node performance](https://developer.apple.com/documentation/spritekit/optimizing-emitter-node-performance), [Creating a custom fragment shader](https://developer.apple.com/documentation/spritekit/creating-a-custom-fragment-shader), [Lighting a sprite with light nodes](https://developer.apple.com/documentation/spritekit/lighting-a-sprite-with-light-nodes), [SKPhysicsContactDelegate](https://developer.apple.com/documentation/spritekit/skphysicscontactdelegate), [SKRenderer](https://developer.apple.com/documentation/spritekit/skrenderer)
- Apple Developer Forums, [SpriteKit Continued Support](https://developer.apple.com/forums/thread/830810) (2026)
- Swift Evolution [SE-0470 Global-actor isolated conformances](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0470-isolated-conformances.md)
- WWDC25 [Bring your SceneKit project to RealityKit](https://developer.apple.com/videos/play/wwdc2025/288/) (SceneKit deprecation)
- WWDC26 [Find and fix performance issues in your Metal games](https://developer.apple.com/videos/play/wwdc2026/388/)

### ios-game-realitykit

- Apple documentation: [RealityKit](https://developer.apple.com/documentation/realitykit), [RealityView](https://developer.apple.com/documentation/realitykit/realityview), [RealityViewCameraContent](https://developer.apple.com/documentation/realitykit/realityviewcameracontent), [PostProcessEffect](https://developer.apple.com/documentation/realitykit/postprocesseffect), [Implementing systems for entities in a scene](https://developer.apple.com/documentation/realitykit/implementing-systems-for-entities-in-a-scene), [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit), [Improving the performance of a RealityKit app](https://developer.apple.com/documentation/realitykit/improving-the-performance-of-a-realitykit-app), [Reality Composer Pro](https://developer.apple.com/documentation/realitycomposerpro), [SceneKit](https://developer.apple.com/documentation/scenekit) (deprecation notice)
- WWDC25 [Bring your SceneKit project to RealityKit](https://developer.apple.com/videos/play/wwdc2025/288/), [What's new in RealityKit](https://developer.apple.com/videos/play/wwdc2025/287/), [Better together: SwiftUI and RealityKit](https://developer.apple.com/videos/play/wwdc2025/274/), [Discover Metal 4](https://developer.apple.com/videos/play/wwdc2025/205/)
- WWDC24 [Discover RealityKit APIs for iOS, macOS, and visionOS](https://developer.apple.com/videos/play/wwdc2024/10103/), [Break into the RealityKit debugger](https://developer.apple.com/videos/play/wwdc2024/10172/), [Optimize your 3D assets for spatial computing](https://developer.apple.com/videos/play/wwdc2024/10186/)
- WWDC23 [Meet RealityKit Trace](https://developer.apple.com/videos/play/wwdc2023/10099/)
- WWDC26 [Explore advances in RealityKit](https://developer.apple.com/videos/play/wwdc2026/279/), [Iterate your spatial scenes faster with Reality Composer Pro 3](https://developer.apple.com/videos/play/wwdc2026/280/), [Design no-code games with Reality Composer Pro 3](https://developer.apple.com/videos/play/wwdc2026/252/), [Discover USDKit and what's new in OpenUSD](https://developer.apple.com/videos/play/wwdc2026/285/)

### ios-game-gamekit

- Apple documentation: [GameKit](https://developer.apple.com/documentation/gamekit), [Initializing and configuring Game Center](https://developer.apple.com/documentation/gamekit/initializing-and-configuring-game-center), [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player), [Adding an access point to your game](https://developer.apple.com/documentation/gamekit/adding-an-access-point-to-your-game), [Creating activities for your game](https://developer.apple.com/documentation/gamekit/creating-activities-for-your-game), [Creating engaging challenges from leaderboards](https://developer.apple.com/documentation/gamekit/creating-engaging-challenges-from-leaderboards), [GKTurnBasedMatch](https://developer.apple.com/documentation/gamekit/gkturnbasedmatch), [GameSave](https://developer.apple.com/documentation/gamesave)
- Apple Human Interface Guidelines, [Game Center](https://developer.apple.com/design/human-interface-guidelines/game-center); Apple [Games app for developers](https://developer.apple.com/games-app/)
- WWDC25 [Get started with Game Center](https://developer.apple.com/videos/play/wwdc2025/214/), [Engage players with the Apple Games app](https://developer.apple.com/videos/play/wwdc2025/215/)
- Apple Developer Forums, [replacing GKGameCenterViewController with access point triggers](https://developer.apple.com/forums/thread/814455)

### ios-game-controller

- Apple documentation: [Game Controller](https://developer.apple.com/documentation/gamecontroller), [Discovering game controllers](https://developer.apple.com/documentation/gamecontroller/discovering-game-controllers), [Handling input events](https://developer.apple.com/documentation/gamecontroller/handling-input-events), [GCVirtualController](https://developer.apple.com/documentation/gamecontroller/gcvirtualcontroller), [Touch Controller](https://developer.apple.com/documentation/touchcontroller), [Core Haptics](https://developer.apple.com/documentation/corehaptics), [Preparing your app to play haptics](https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics), [Representing haptic patterns in AHAP files](https://developer.apple.com/documentation/corehaptics/representing-haptic-patterns-in-ahap-files)
- Apple Human Interface Guidelines, [Game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls)
- WWDC26 [Make your game great with touch](https://developer.apple.com/videos/play/wwdc2026/358/); WWDC25 [Level up your games](https://developer.apple.com/videos/play/wwdc2025/209/); WWDC24 [Port advanced games to Apple platforms](https://developer.apple.com/videos/play/wwdc2024/10089/) (Game Mode on iPhone)
- WWDC21 [Tap into virtual and physical game controllers](https://developer.apple.com/videos/play/wwdc2021/10081/); WWDC20 [Bring keyboard and mouse gaming to iPad](https://developer.apple.com/videos/play/wwdc2020/10617/); WWDC19 [Introducing Core Haptics](https://developer.apple.com/videos/play/wwdc2019/520/)

### ios-game-audio-engine

- Apple documentation: [AVFAudio](https://developer.apple.com/documentation/avfaudio), [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions), [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes), [AVAudioPlayerNode](https://developer.apple.com/documentation/avfaudio/avaudioplayernode), [AVAudioEnvironmentNode](https://developer.apple.com/documentation/avfaudio/avaudioenvironmentnode), [Building an audio sequencer to arrange and play clips](https://developer.apple.com/documentation/avfaudio/building-an-audio-sequencer-to-arrange-and-play-clips), [AVGameBypassSystemSpatialAudio](https://developer.apple.com/documentation/bundleresources/information-property-list/avgamebypasssystemspatialaudio), [PHASE](https://developer.apple.com/documentation/phase), [SKAudioNode](https://developer.apple.com/documentation/spritekit/skaudionode), [SpatialAudioComponent](https://developer.apple.com/documentation/realitykit/spatialaudiocomponent)
- Apple Human Interface Guidelines, [Playing audio](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- WWDC24 [Enhance your spatial computing app with RealityKit audio](https://developer.apple.com/videos/play/wwdc2024/111801/); WWDC21 [Discover geometry-aware audio with the Physical Audio Spatialization Engine (PHASE)](https://developer.apple.com/videos/play/wwdc2021/10079/); WWDC19 [What's New in AVAudioEngine](https://developer.apple.com/videos/play/wwdc2019/510/)
- Apple Developer Forums, [scheduling buffers under Swift 6](https://developer.apple.com/forums/thread/762550)
- ITU-R [BS.2434](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BS.2434-2018-PDF-E.pdf) (loudness for portable game devices)

