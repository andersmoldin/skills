---
name: github-repo-setup
description: Set up, audit or adjust main-branch protection for a GitHub repo where agents write the code and a review agent approves it — rulesets, merge settings, CI guards, versioning, CODEOWNERS, VISION.md and the review workflow. Also the emergency switch. Captain-only.
disable-model-invocation: true
---

# GitHub repo setup

You are acting for the **captain**: the repo owner, whose own account is the only one with admin rights. Every command here runs on the captain's `gh` login. Run this skill only in a session the captain started for this purpose. A coding agent uses [`github-pr-author`](../github-pr-author/SKILL.md) instead.

`SETUP` below means `scripts/repo-setup.sh` in this skill's folder. `TEMPLATES` means `templates/` beside it.

## The model this skill builds

| Identity | Holds | Can land on main |
|---|---|---|
| Captain (owner account) | browser, admin | approves **protected files** and escalations |
| Author app (`<handle>-pr-author`) | key in Agent Vault (keychain until then) | nothing alone: pushes branches, opens PRs |
| Review app (`<handle>-pr-review`) | key in the `pr-review` environment, locked to `main` | approves ordinary changes; on advisory repos also merges them |

Main accepts only squash-merged PRs with one approval from someone other than the last pusher, green required checks, resolved threads, and code-owner approval for protected paths (`/.github/`, `/VISION.md`, and code that runs with the captain's credentials). No bypass actors, ever. Why each rule exists, and its source: [`references/sources.md`](references/sources.md).

## Protection level

Run `SETUP level OWNER/REPO` first. Its first line is one of:

- `enforced`: public repo, or private on a paid plan. GitHub refuses rule violations.
- `advisory`: private repo on GitHub Free. Rulesets, CODEOWNERS enforcement and environments do not exist there. Auto-merge stays off: with nothing enforced it merges before any review. The review app merges what it approves instead, in enforce mode only, once every check has passed, and never a change to a protected path. Everything else still applies, plus the daily `main-audit` workflow that flags commits on main which did not arrive through an approved PR.

Every time you report on an advisory repo, tell the captain, in these words: **Main is NOT protected. Anyone with write access, including an agent on your login, can push to main. main-audit detects it afterwards; nothing prevents it.**

GitHub's banner "Your main branch isn't protected" is expected at advisory level; its button leads to an upgrade.

`level` and `apply` print both sentences.

The level is detected, never assumed. When the plan changes, rerun the skill.

## Setup

Each step ends when its check passes.

1. **Level.** `SETUP level OWNER/REPO`. On `enforced`, done when you have reported the level to the captain. On `advisory`, stop here: report it in the words above and put three paths to the captain. Continue only after the captain chooses one. A repo that is already set up is not asked again: rerunning the skill on it, report the level and go on (see *Audit and adjust*).
   - **Make the repo public.** First offer to check what going public would expose. If the captain accepts, run `gitleaks git --log-opts=--all --redact` in a fresh clone, then read the full history (`git log --all -p`), the commit author and committer lines, and the repo's issues and PR text, and list everything that points at private infrastructure or people: hostnames, IP addresses, e-mail addresses, names, home-directory paths. The captain then changes the visibility in GitHub themselves (*Settings* → *General* → *Danger Zone* → *Change repository visibility*). Then run `SETUP level OWNER/REPO` again.
   - **A paid GitHub plan** (Pro or higher, see [GitHub's pricing page](https://github.com/pricing)). After the captain upgrades, run `SETUP level OWNER/REPO` again.
   - **Keep advisory.** Go on with step 2. The choice is not stored in the repo.
2. **Apps installed.** The two apps exist and are installed on this repo. If not, walk the captain through [`references/apps.md`](references/apps.md). Done when the captain confirms both apps list this repo under *Repository access*, and `SETUP secrets OWNER/REPO` reports all three reviewer credentials present.
3. **Repo files on a branch.** On a branch named `chore/repo-setup`, add from `TEMPLATES`:
   - `CODEOWNERS` → `.github/CODEOWNERS` (replace `@OWNER`), adding every path whose code runs with the captain's credentials
   - `VISION.md` → repo root. Use the [`vision`](https://github.com/kunchenguid/vision) skill when it is installed; otherwise draft it from the README and history and put each section to the captain as a question. The review agent judges every PR against this file, so a vague vision is a weak reviewer.
   - `pr-policy.md` → `.github/pr-policy.md`
   - `SECURITY.md` → repo root
   - `dependabot.yml` → `.github/dependabot.yml`, adding the repo's package ecosystems
   - `workflows/guard.yml` and `workflows/release.yml` → `.github/workflows/`, `releaserc.json` → `.releaserc.json`, `release/` → `.github/release/` (pinned release tooling with its lockfile)
   - `../github-pr-review/templates/pr-review.yml` → `.github/workflows/pr-review.yml`, `../github-pr-review/SKILL.md` → `.github/pr-review/INSTRUCTIONS.md` and `../github-pr-review/templates/merge.sh` → `.github/pr-review/merge.sh`
   - level `advisory` only: `workflows/main-audit.yml` → `.github/workflows/`
   - a `ci` job for this repo's own tests and lint, in `.github/workflows/ci.yml`, job `name: ci`. Read the repo's scripts and config to find the commands; ask the captain only when there are none.
   - a `LICENSE` if missing: ask the captain which.

   Templates say `main`: use the repo's default branch instead wherever they name a branch. Every `uses:` is pinned to a full commit SHA with the version in a comment. Done when `actionlint` passes locally (`docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint` or the binary) and the branch is pushed.
4. **First PR.** Open it as the author app (see `github-pr-author`). Its title is `chore: protect main`. Done when every job in `guard.yml` and `ci.yml` has reported on it. The protection does not exist yet, so the captain reviews and merges this one by hand.
5. **Settings.** `SETUP apply OWNER/REPO --checks ci,pr-title,gitleaks,actionlint`, adding `--beta` for repos with a beta channel. It sets merge options, Actions permissions, security features, labels, the `pr-review` environment and the ruleset, and reports anything it could not set. Done when `SETUP audit OWNER/REPO --checks …` exits 0.
6. **Observe week.** Set the variable `PR_REVIEW_MODE` to `observe` in the `pr-review` environment. The reviewer comments *would approve* instead of approving, and the captain approves (and on advisory repos merges). After a week of PRs where its verdicts matched the captain's, the captain sets it to `enforce`; on advisory repos the review app then merges what it approves.

## Audit and adjust

`SETUP audit OWNER/REPO --checks …` compares live settings, ruleset and files with this skill and exits non-zero on any drift, listing each item. On an advisory repo it also prints `main not protected (advisory)` and still exits 0 when nothing else drifts. For a repo that is already set up, that line is the reminder: do not put the three paths of step 1 to the captain again. Fix drift by rerunning `apply` for settings, and by a PR for files: a file that differs from its template is either a deliberate local change (record why in the PR that made it) or stale (update it from the template).

## Variants

Read [`references/variants.md`](references/variants.md) when the repo needs any of: a beta channel (`x.y.z-beta.n`, optionally deploying to `dev.<domain>`), release-please instead of a release per merge, a Cloudflare deploy, or GitHub Pages.

## Emergency

When required checks cannot pass for a reason outside the change itself (Actions outage, a broken external action, the reviewer out of quota):

1. `SETUP emergency-off OWNER/REPO "reason"`: disables the ruleset and opens an issue labelled `needs-captain` that records who, when and why.
2. Land the fix.
3. `SETUP emergency-on OWNER/REPO`: re-enables the ruleset and closes the issue.

Step 3 is the completion criterion; the open issue keeps it visible until it is done.
