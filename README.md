# skills

Agent skills for Claude Code that I use in my own work, published so they install the same way on every machine. What belongs here, and what does not, is in [`VISION.md`](VISION.md).

## Skills

| Skill | What it does |
|---|---|
| [`github-repo-setup`](github/github-repo-setup/SKILL.md) | Protects `main` in a GitHub repo where agents write the code: ruleset, merge settings, CI guards, versioning, CODEOWNERS, VISION.md, and the review workflow. Audits drift and has a logged emergency switch. Run by the repo owner. |
| [`github-pr-review`](github/github-pr-review/SKILL.md) | The review agent: reads a pull request against `VISION.md` and the PR policy, approves ordinary changes and escalates the rest to the owner. Runs in GitHub Actions. |
| [`github-pr-author`](github/github-pr-author/SKILL.md) | How a coding agent gets work onto `main`: branch, Conventional Commits title, PR, answering review, all as a GitHub App instead of the owner's account. |
| [`youtube-research`](research/youtube-research/SKILL.md) | Reads YouTube videos through transcript, metadata and frames, with no account or API key. |

## Install

Copy or symlink a skill folder into `~/.claude/skills/`, for example:

```bash
git clone https://github.com/andersmoldin/skills.git
ln -s "$PWD/skills/github/github-pr-author" ~/.claude/skills/github-pr-author
```

The GitHub skills need two GitHub Apps first; [`apps.md`](github/github-repo-setup/references/apps.md) walks through creating them.

## How this repo is maintained

Agents open the pull requests, a review agent approves ordinary changes, and I approve protected paths and escalations. This repo is the first one set up with its own `github-repo-setup`.

## License

[MIT](LICENSE)
