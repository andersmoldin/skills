---
name: ios-game-level-design
description: Designs the levels of an iOS game - layout, pacing, teaching mechanics through space, guiding the player with light, framing, color and contrast, level size for short phone sessions, and levels stored as data with automated solvability checks. Use when building or fixing levels, rooms, stages or maps, or when players get lost, stuck or bored.
license: MIT
---

# Game level design

Level design builds the game's levels and what is in them. Light and color, contrast, camera framing and the shape of the space pull the player's eye; the designer uses them to steer the player through the world, or to mislead them on purpose.

## Steps

1. Write the **Levels** section of `GAME_DESIGN.md`: the list of levels in order, and for each one its single idea, the mechanic it teaches or tests, and its target play time.
2. Put the movement metrics in `Tuning.json`: jump height and distance, run speed, reach, attack range. Derive every gap, ledge and corridor from them, so levels stay valid when tuning changes.
3. Store each level as data (a tile map in `SKTileMapNode` terms, a JSON grid, or a USDZ scene plus a JSON entity list), never as layout code.
4. Write an automated check that loads every level and proves it completable: a pathfinder or solver over the level data using the movement metrics. Run it in the test suite. Done when every level passes and a level with an impossible gap fails.
5. Playtest each level and watch where the player hesitates, gets lost, or dies repeatedly; fix the space before adding signs or text.

## Shape each level around one idea

Use four beats: **introduce** the idea where failure is cheap, **develop** it with more pressure, **twist** it so the player uses it a new way, then let the player **prove** mastery. Start the next idea in the next level. This also gives a natural rhythm of tension and release.

## Guide without words

- The goal is visible early; the route to it is for the player to work out.
- Lead with light, contrast and color: the brightest, most saturated thing is where the eye goes. Keep the path readable against a calmer background.
- Use landmarks and sightlines so the player can orient themselves, and reveal spaces gradually to create curiosity.
- Teach each hazard or tool where the player can only learn, not lose much: the first spike pit is shallow, the first enemy is alone.
- Frame important moments with the camera; on a phone, the screen is the frame, so compose each screen.

## Size for phones

- Most levels are a few minutes long and can be finished between two stops of a commute.
- Save progress at level boundaries and checkpoints; restarting a level takes under a second.
- Keep important action and pickups away from the screen edges where thumbs and system UI sit.

## Build efficiently

Reuse a small set of modules (tiles, rooms, set pieces) and combine them in new ways. Variety comes from new combinations of known parts and from one new element per level, not from one-off geometry.

## Related skills

Tile maps and cameras: `ios-game-spritekit`. 3D scenes and navigation: `ios-game-realitykit`. What fills the level: `ios-game-content-design`. Environmental storytelling: `ios-game-writing`. Lighting mood: `ios-game-art-direction`.
