---
name: ios-game-content-design
description: Designs the content of an iOS game beyond its minimum working version - characters, enemies, items, puzzles, missions, rewards and procedurally generated content, authored as validated data. Use when adding characters, items, puzzles, quests or levels' contents, when designing a generator, or when the game works but feels thin.
license: MIT
---

# Game content design

Content is everything the game does not need in order to function but that gives it value: characters, items, puzzles, missions and similar. Content design adds that complexity on top of a minimal working game, so build the core loop first (`ios-game-system-design`) and add content to it.

## Steps

1. List the content types the game needs in the **Content** section of `GAME_DESIGN.md`, and for each type the mechanic it exercises and what makes two pieces of it feel different.
2. Author content as data, not code: one file per type (for example `Content/enemies.json`, `Content/puzzles.json`), each entry with an `id`, the mechanic it uses, a difficulty value and its own stats. Global constants stay in `Tuning.json`. Code defines behaviors; data picks and combines them.
3. Write a validator that loads every content file at test time and checks it: IDs unique, references resolve, values inside the ranges in `Tuning.json`, every puzzle solvable (run a solver), every level reachable. Done when the validator runs in the test suite and fails on a broken entry.
4. Order content into a curve: introduce, develop, twist, test. Each new piece teaches, combines or twists something; cut pieces that do none of these.

## Puzzles

- A good puzzle reveals one non-obvious consequence of the game's rules. Find puzzles by exploring what the rules allow, keep the ones that produce an insight, and remove every element that does not serve it.
- The player must be able to reason to the answer. Cut puzzles that need trial and error or busywork.
- Introduce each rule alone before combining it with others.

## Procedural content

- Before writing a generator, write down what every output must guarantee (solvable, reachable, fair) and what a good and a bad result look like.
- Seed every generator so any output can be reproduced from its seed, and log the seed with bug reports.
- Validate each generated piece with the same solver as hand-made content; regenerate on failure.
- Outputs that differ mathematically can still feel identical. Make variety visible, and mix hand-made pieces into generated structure.

## Characters, items and rewards

- Every enemy or item needs one clear role that the player can read from its look (`ios-game-art-direction`) before reading any text.
- Rewards teach players what to do. Keep their timing and value legible and consistent.
- Prefer fewer, distinct pieces of content over many similar ones.

## Related skills

Rules and numbers the content uses: `ios-game-system-design`. Where content is placed: `ios-game-level-design`. Text for items and characters: `ios-game-writing`.
