---
name: ios-game-gamekit
description: Integrates Game Center and the Apple Games app into iOS games (iOS 26+, Swift 6) - authentication, leaderboards, achievements, challenges, activities and deep links, party codes, access point and Game Overlay, real-time and turn-based multiplayer. Use when adding Game Center features, multiplayer, or Games app visibility, or when GameKit code fails to compile or authenticate.
license: MIT
---

# GameKit

Game Center feeds the Apple Games app, which ships on every iOS 26 device. A game that authenticates and has leaderboards, achievements, challenges or activities shows up on more Games app surfaces. iOS 27 added no GameKit API, so everything here works on an iOS 26 target.

## Setup

1. Add the Game Center capability (entitlement `com.apple.developer.game-center`) and enable Game Center for the app in App Store Connect. Set the primary or secondary App Store category to Games.
2. Define achievements, leaderboards, challenges and activities in an Xcode GameKit bundle: File > New > File from Template > GameKit Bundle. Push it to App Store Connect from the bundle editor (Push to / Pull from App Store Connect). Pushed items start as Not Live and go live with the version you submit.
3. Test on a physical device: Scheme > Run > Options > GameKit Configuration > Enable Debug Mode, then Debug > GameKit > Manage Game Progress. Data stays local in debug mode.

## Authenticate at launch

Set the handler on the title screen, never behind a menu. The game stays fully playable when Game Center is unavailable.

```swift
import GameKit
import UIKit

@MainActor final class GameCenter: NSObject {
    private(set) var isAvailable = false
    private var listenerRegistered = false

    func authenticate(presenter: @escaping @MainActor () -> UIViewController?) {
        GKLocalPlayer.local.authenticateHandler = { [weak self] viewController, error in
            guard let self else { return }
            if let viewController { presenter()?.present(viewController, animated: true); return }
            guard error == nil, GKLocalPlayer.local.isAuthenticated else { self.isAvailable = false; return }
            self.isAvailable = true
            if !self.listenerRegistered {                 // register exactly once
                GKLocalPlayer.local.register(self)
                self.listenerRegistered = true
            }
        }
    }
}
```

- The handler runs several times: with a view controller (present it), with neither (signed in), or with an error (hide Game Center UI).
- Never wait for the handler before starting play; it may not be called if the player dismisses the sign-in sheet.
- After sign-in, respect `isUnderage`, `isMultiplayerGamingRestricted` and `isPersonalizedCommunicationRestricted` (hide chat when true).

## Scores and achievements

```swift
func finishAttempt(score: Int) async {
    do {
        try await GKLeaderboard.submitScore(score, context: 0, player: GKLocalPlayer.local,
                                            leaderboardIDs: ["com.example.leaderboard.daily"])
        let firstWin = GKAchievement(identifier: "com.example.achievement.first-win")
        firstWin.percentComplete = 100
        try await GKAchievement.report([firstWin])
    } catch {
        // Keep the result locally and retry later; never block the game on this.
    }
}
```

- Submit one score at the end of every attempt, even when it is not a best; the server keeps the best. Never submit running totals or per-point updates.
- The same score submission drives challenges, so challenges need no extra code.
- Achievement progress only increases. Batch reports. Limits: 100 achievements, 1000 points total.
- Read entries with `GKLeaderboard.loadLeaderboards(IDs:)` then `loadEntries(for:timeScope:range:)`.

## Challenges and activities (iOS 26)

- **Challenges** are built from a leaderboard plus metadata in the GameKit bundle (name, image, allowed durations). Offer an in-game entry point with `await GKAccessPoint.shared.trigger(challengeDefinitionID:)` or `triggerForPlayTogether()`.
- **Activities** (`GKGameActivityDefinition`) are deep links into a mode or level, optionally with a party code. They arrive through `GKLocalPlayerListener`; route on `activity.activityDefinition.identifier`, `activity.properties` and `activity.partyCode`, and skip intros on both cold and warm launch.
- Track a running activity with `GKGameActivity.start(definition:)`, `pause()`, `resume()`, `end()`. Scores and achievements set on the activity are submitted once at `end()`.

```swift
extension GameCenter: @MainActor GKLocalPlayerListener {   // isolated conformance (Swift 6.2+)
    func player(_ player: GKPlayer, wantsToPlay activity: GKGameActivity) async -> Bool {
        route(activityID: activity.activityDefinition.identifier, partyCode: activity.partyCode)
    }
    private func route(activityID: String, partyCode: String?) -> Bool { /* open the mode */ true }
}
```

## Access point and Game Overlay

- `GKAccessPoint.shared` opens the system Game Overlay on iOS 26. Show it (`isActive = true`) on menus and settings only, never during play, splash screens or tutorials.
- Pause the game while `isPresentingGameCenter` is true; keep HUD clear of `frameInScreenCoordinates`.
- A custom "Leaderboards" button calls `GKAccessPoint.shared.trigger(leaderboardID:playerScope:timeScope:handler:)`, `trigger(achievementID:handler:)` or `trigger(state:handler:)`.

## Multiplayer

- Real-time: `GKMatchRequest` → `try await GKMatchmaker.shared().findMatch(for:)` or `GKMatchmakerViewController`; exchange data with `match.sendData(toAllPlayers:with:)` and `GKMatchDelegate`. Treat received data as untrusted input and validate it.
- Turn-based: `GKTurnBasedMatch.find(for:)`, `endTurn(withNextParticipants:turnTimeout:match:)`, `endMatchInTurn(withMatch:leaderboardScores:achievements:)`. `GKTurnTimeoutDefault` is rejected in Swift 6 as unsafe global state; use your own constant.
- Voice chat: SharePlay (Group Activities capability) replaces `GKVoiceChat`.
- Cloud saves: the GameSave framework (iOS 26) is Apple's current path; check its documentation before use.

## Deprecated: do not use

`GKGameCenterViewController` and its delegate (iOS 26; use `GKAccessPoint` triggers), `GKAccessPoint.showHighlights`, the old `GKChallenge` classes and `GKShowChallengeBanners`, `GKScore`, `GKVoiceChat`, `authenticate(completionHandler:)`, `GKLocalPlayer.localPlayer`, `GKSession`.

## Related skills

Meta-progression and rewards: `ios-game-system-design`. Menus and where the access point appears: `ios-game-ui-design`.
