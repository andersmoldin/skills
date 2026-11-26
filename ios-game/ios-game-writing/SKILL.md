---
name: ios-game-writing
description: Writes the story, dialogue and text of an iOS game and decides how they are presented - narrative structure, branching, story state, environmental storytelling, voice, on-screen text and localization. Use when adding story, dialogue, tutorials or item text, choosing a branching structure, or when story and gameplay contradict each other.
license: MIT
---

# Game writing

Game writing covers the dialogue, text and story of a game, and also how they reach the player: on-screen text, voice acting, images and music all carry the writing. It starts early, because the story shapes what the levels, characters and systems need to say.

## Steps

1. Write the **Writing** section of `GAME_DESIGN.md`: the story in five sentences (start, turn, climax, end, what it means), the narrator's voice with one sample line, and the chosen structure (below).
2. Check the story against the mechanics: list what the systems reward the player for doing, and confirm the story does not argue against it. If the story praises mercy while the systems reward greed, change one of them.
3. Author the story's structure outside Swift, in data files (`Story/*.json`) read by a small Swift interpreter; each line in them is a string key (step 4). For large branching stories, inkle's ink language compiles to JSON, and its JavaScript runtime (inkjs) runs on iOS inside JavaScriptCore. Track story state in named variables (`metTheKeeper`, `trust`), not in code paths.
4. Keep the text itself in a String Catalog (`Localizable.xcstrings`) from the first line; story data holds only string keys (`"line": "keeper.greeting"`). Xcode extracts keys only from code, so add data-driven keys to the catalog by hand and look them up with `Bundle.main.localizedString(forKey:value:table:)`. Never bake text into images.
5. Read every line on a real phone at the game's text size. Done when every line fits its box at the largest supported text size and does one job.

## Structure: choose on purpose

- **Linear spine** with optional side scenes: cheapest, best for short games.
- **Branch and rejoin**: choices change scenes but return to shared key events. Most choice-driven small games should use this.
- **Quality-based or storylet**: small self-contained scenes unlocked by story-state variables. Scales well and lets new scenes slot in without rewiring.
- **Free branching**: content multiplies with every choice; avoid unless branching is the game.

## Principles

- **Show before telling.** Objects, traces and arrangements in the level let players assemble the story themselves. Use text for what the world cannot show.
- **Every line does a job:** teach, characterize, motivate or reward. Cut lines that restate what is on screen.
- **Write for the phone.** Short lines, one idea per box, player-paced advancement, legible text size (17 pt default, never under 11 pt).
- **Tutorial text is reference.** Teach by play (`ios-game-ux-design`); written help stays skippable and findable later.
- **Voice is consistent.** Each character has a speech pattern stated in the doc; check new lines against it.

## Generated dialogue

Apple's on-device Foundation Models framework can generate NPC lines and flavor text, but only on Apple Intelligence devices, with a small context window and safety guardrails that may refuse combat topics. Always ship authored lines as the fallback, keep game logic independent of generated text, and disclose AI use.

## Related skills

World and setting: `ios-game-world-design`. Places that tell the story: `ios-game-level-design`. Text layout and size: `ios-game-ui-design`. Voice-over playback: `ios-game-audio-engine`.
