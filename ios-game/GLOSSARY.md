# iOS game skills

A collection of agent skills that teach coding agents to design and build iOS games with Apple's native frameworks.

## Language

**Skill**:
A folder under `ios-game/` with a `SKILL.md` that an agent loads when its description matches the task.
_Avoid_: Prompt, command

**Router**:
The one skill, `ios-game-design`, that names which skill to use for each part of building a game and holds the project baseline shared by every game.
_Avoid_: Index skill, master skill

**Discipline skill**:
A skill that covers one game design discipline from the Disciplines section of Wikipedia's "Video game design" article, or art direction, and decides what the game should be without teaching framework APIs.
_Avoid_: Design skill, theory skill

**Technology skill**:
A skill that teaches one Apple framework area for iOS games and owns all API knowledge for it.
_Avoid_: API skill, framework skill

**Design doc**:
The single `GAME_DESIGN.md` file at the root of a game's repository, in which each discipline skill owns one section.
_Avoid_: Game design document, GDD, spec

**Project baseline**:
The settings every game in this collection shares (deployment target, language mode, renderer choice, Info.plist keys), kept in the router.
_Avoid_: Defaults, config
