---
name: ios-game-system-design
description: Designs the rules and underlying math of an iOS game - core loop, mechanics, resources and economy, progression, difficulty curves and balance, with all tuning numbers in one data file and headless simulations to check them. Use when defining how the game works, when a strategy dominates, progression feels too fast or slow, or numbers need tuning.
license: MIT
---

# Game system design

System design creates the rules of the game and the mathematical patterns beneath them: the simulation that reacts to the player. How the player experiences the game comes from how these systems interact; deeper, interacting systems produce less predictable, more absorbing play.

## Steps

1. Name the target experience first (for example tension, mastery, discovery or expression), then the player behavior that would produce it, then the mechanics that create that behavior. Write all three in the **Systems** section of `GAME_DESIGN.md`.
2. Write the core loop as one line: what the player does every few seconds, what that earns, and what the earnings unlock. Done when every mechanic in the game appears in the loop or in a loop that feeds it.
3. Map resources as sources, stores, converters and sinks. Mark each feedback loop as reinforcing (snowballs, needs a brake or cap) or balancing (stabilizes).
4. Put every global tuning number in one data file, `Tuning.json`, decoded into a `Tuning` struct at launch: speeds, costs, rewards, timers, spawn rates, difficulty steps. Values that belong to one enemy, item or puzzle live in that entry's content file (`ios-game-content-design`). Game code reads from these files; Swift files contain no gameplay constants.
5. Write a headless simulation (a unit-test target or command-line tool that runs the rules without rendering) that plays thousands of sessions with simple bot strategies. Check the outputs against the targets in the doc: time to first reward, session length, win rate per difficulty step, economy inflation. Done when every target has a measured number next to it.

## Principles

- **Interesting decisions.** Each recurring choice is a real tradeoff whose best answer depends on the situation. Remove options that always win or always lose, show the information needed to choose, and confirm the choice with clear feedback.
- **Randomness varies situations, skill resolves them.** Use chance to create new problems, not to decide the outcome of a decision.
- **Learning loops.** Every mechanic is a cycle: act, the simulation responds, feedback shows the result, the player's understanding grows. Chain the cycles so each learned skill feeds the next, and retire skills nobody needs anymore.
- **Loops over arcs.** Repeatable systems give a small game its lifespan; one-shot content is expensive per minute of play.
- **Plan for mastery.** Fun fades once a pattern is fully mastered; schedule a new rule, a variation or an ending before that point.
- **Cost curves.** Price items so value per cost is consistent; use rock-paper-scissors relationships so no single strategy dominates.
- **Difficulty is a sawtooth.** Ramp up within a set, drop when a new mechanic arrives, end the set with a test.
- **Fair rewards.** Reward what you want the player to do, and never make the efficient path the boring one.
- **Store and progression rules.** Randomized paid items must show their odds before purchase (App Review Guidelines 3.1.1); deterministic rewards are simpler and safer for a small game.

## Related skills

Concrete items, enemies and puzzles built on these rules: `ios-game-content-design`. Leaderboards and achievements: `ios-game-gamekit`. Feel of moment-to-moment control: `ios-game-ux-design`.
