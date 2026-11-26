# skills

Agent skills for Claude Code that I use in my own work, published so they install the same way on every machine. What belongs here, and what does not, is in [`VISION.md`](VISION.md).

## Skills

| Skill | What it does |
|---|---|
| [`github-repo-setup`](github/github-repo-setup/SKILL.md) | Protects `main` in a GitHub repo where agents write the code: ruleset, merge settings, CI guards, versioning, CODEOWNERS, VISION.md, and the review workflow. Audits drift and has a logged emergency switch. Run by the repo owner. |
| [`github-pr-review`](github/github-pr-review/SKILL.md) | The review agent: reads a pull request against `VISION.md` and the PR policy, approves ordinary changes and escalates the rest to the owner. Runs in GitHub Actions. |
| [`github-pr-author`](github/github-pr-author/SKILL.md) | How a coding agent gets work onto `main`: branch, Conventional Commits title, PR, answering review, all as a GitHub App instead of the owner's account. |
| [`youtube-research`](research/youtube-research/SKILL.md) | Reads YouTube videos through transcript, metadata and frames, with no account or API key. |
| [`im-stuck-on`](productivity/im-stuck-on/SKILL.md) | Gets you started on a task you keep putting off: say what it is and how much time you have, and get one small first step sized to that time. Only you can invoke it. |

### iOS games

Designing and building iOS games with Apple's native frameworks (iOS 26 and later, Swift 6, SwiftUI, SpriteKit, RealityKit). Start with the router, `ios-game-design`. Discipline skills decide what the game is; technology skills write the code. Scope, glossary and sources are in [`ios-game/README.md`](ios-game/README.md).

| Skill | Type | Loads when the agent is… |
|---|---|---|
| [`ios-game-design`](ios-game/ios-game-design/SKILL.md) | Router | starting or unsure where to begin; holds the project baseline |
| [`ios-game-world-design`](ios-game/ios-game-world-design/SKILL.md) | Discipline | defining premise, setting, theme, world rules, map |
| [`ios-game-system-design`](ios-game/ios-game-system-design/SKILL.md) | Discipline | defining the core loop, rules, economy, balance |
| [`ios-game-content-design`](ios-game/ios-game-content-design/SKILL.md) | Discipline | adding characters, items, puzzles, missions, generators |
| [`ios-game-writing`](ios-game/ios-game-writing/SKILL.md) | Discipline | writing story, dialogue and text |
| [`ios-game-level-design`](ios-game/ios-game-level-design/SKILL.md) | Discipline | building levels, pacing, guiding the player |
| [`ios-game-ui-design`](ios-game/ios-game-ui-design/SKILL.md) | Discipline | designing HUD, menus, touch-control layout |
| [`ios-game-audio-design`](ios-game/ios-game-audio-design/SKILL.md) | Discipline | deciding what the game sounds like |
| [`ios-game-ux-design`](ios-game/ios-game-ux-design/SKILL.md) | Discipline | tuning game feel, forgiveness, onboarding, accessibility |
| [`ios-game-art-direction`](ios-game/ios-game-art-direction/SKILL.md) | Discipline | choosing style and palette, sourcing assets, adding juice |
| [`ios-game-spritekit`](ios-game/ios-game-spritekit/SKILL.md) | Technology | writing 2D rendering code |
| [`ios-game-realitykit`](ios-game/ios-game-realitykit/SKILL.md) | Technology | writing 3D rendering code |
| [`ios-game-gamekit`](ios-game/ios-game-gamekit/SKILL.md) | Technology | adding Game Center, the Games app, multiplayer |
| [`ios-game-controller`](ios-game/ios-game-controller/SKILL.md) | Technology | adding touch controls, controllers, keyboard, haptics |
| [`ios-game-audio-engine`](ios-game/ios-game-audio-engine/SKILL.md) | Technology | playing sound and music in code |

## Install

The repo is a Claude Code plugin marketplace, `moldin`, with one plugin, `moldin-skills`, that holds every skill above. In Claude Code:

```
/plugin marketplace add andersmoldin/skills
/plugin install moldin-skills@moldin
```

Each skill gets the plugin name as a prefix, for example `/moldin-skills:youtube-research`. Run `/reload-plugins` or start a new session to load them.

Auto-update is off by default for marketplaces other than Anthropic's. To keep every machine current, turn it on once per machine: run `/plugin`, open the **Marketplaces** tab, select `moldin` and turn on auto-update. Claude Code then pulls new commits in the background after a session starts. Without it, update by hand from a terminal with `claude plugin marketplace update moldin`, then `claude plugin update moldin-skills@moldin`.

The GitHub skills need two GitHub Apps first; [`apps.md`](github/github-repo-setup/references/apps.md) walks through creating them.

## How this repo is maintained

Agents open the pull requests, a review agent approves ordinary changes, and I approve protected paths and escalations. This repo is the first one set up with its own `github-repo-setup`.

## License

[MIT](LICENSE)
