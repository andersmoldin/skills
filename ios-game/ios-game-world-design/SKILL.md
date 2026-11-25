---
name: ios-game-world-design
description: Designs the world of an iOS game - premise, setting, theme, backstory, world rules and the map that every other part of the game references. Use when starting a new game, when the setting feels generic or inconsistent, or before writing story, levels or art that depend on where and when the game takes place.
license: MIT
---

# Game world design

World design creates the backstory, setting and theme of a game, and the map of places and topics the player is likely to pursue. It comes first because writing, levels, content and art all read from it, and it sets the direction the rest of the game takes.

## Steps

1. Write the **World** section of `GAME_DESIGN.md` (see the `ios-game-design` skill) with:
   - premise in two sentences, and the tone in three adjectives;
   - who the player is in this world and what they want;
   - three to five world rules: what is possible and what is not;
   - a scope limit: the number of places (screens, rooms or levels) the game will have.
   Done when another agent could make a level, a character and a line of dialogue that all fit without asking a question.
2. Turn every world rule into a mechanic, or confirm that no mechanic contradicts it. List the mapping in the section ("ice is slippery → friction 0.1 on ice tiles"). Done when no rule is decoration only.
3. Draw the map as data: a list of places with their purpose, what the player learns or gets there, and how they connect. Store it next to the level data (for example `Levels/world.json`) and point to it from the doc.
4. Hand the world brief to `ios-game-art-direction` (style guide) and `ios-game-writing` (voice).

## Principles

- **One strong idea.** A small iOS game serves a single premise on every screen; cut setting details that the player never meets.
- **Fiction and rules agree.** If the world says fire burns wood, fire burns every wooden thing in the game. Players learn the rules from the world and expect them to hold.
- **Few general rules over many special cases.** Systemic rules (materials, elements, light and dark) combine on their own, so each new object adds depth without new code.
- **Familiar first, then a twist.** Genre cues explain the setting instantly; change one or two details to make it the game's own. Keep it original: genre conventions are shared, specific games' names, characters and places are not.
- **Places tell their history.** Wear, props and arrangement let the player infer what happened without a text box.
- **Internal causes.** Climate, resources and culture explain why things look and work as they do. Check names, symbols and maps for unintended real-world meanings.
- **Something for each player type.** Explorers get optional corners and secrets, achievers get visible goals, completionists get countable collections, all expressed through the world itself.
- **The phone frame is the stage.** Each screen is a composed picture; design places so their purpose reads at phone size.

## Related skills

Rules into numbers: `ios-game-system-design`. Story and voice: `ios-game-writing`. Spaces and routes: `ios-game-level-design`. Look: `ios-game-art-direction`.
