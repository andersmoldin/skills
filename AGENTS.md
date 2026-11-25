# Agent notes

What belongs here is in `VISION.md`; what the reviewer approves is in `.github/pr-policy.md`.

## Layout

- Each skill is `<area>/<skill-name>/SKILL.md` (areas today: `github/`, `research/`), with its scripts, templates and references beside it.
- The repo root is a Claude Code plugin: `.claude-plugin/marketplace.json` (marketplace `moldin`) and `.claude-plugin/plugin.json` (plugin `moldin-skills`).

## Rules

- Adding, renaming or removing a skill changes the `skills` list in `.claude-plugin/plugin.json` (one `./` path per skill folder) and the table in `README.md` in the same change. `scripts/check_skills.py` fails CI when the list and the skill folders disagree.
- Neither `plugin.json` nor the marketplace entry has a `version`: installs then track the commit SHA, so auto-update picks up every merge. A `version` nobody bumps stops every machine from updating; the check rejects it.
- A command in a skill reaches the skill's own files through `${CLAUDE_SKILL_DIR}/...`, never a path under `~/.claude/skills/`, which does not exist when the skill comes from the plugin.

## Checks

```bash
python3 scripts/check_skills.py
python3 -m unittest discover -s scripts
claude plugin validate .   # the "No version specified" warnings are intended
```

Test installs with `CLAUDE_CONFIG_DIR` set to a throwaway directory, never against your own Claude Code setup.
