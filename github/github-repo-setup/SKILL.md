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
| Review app (`<handle>-pr-review`) | key in the `pr-review` environment, locked to `main` | approves ordinary changes |

Main accepts only squash-merged PRs with one approval from someone other than the last pusher, green required checks, resolved threads, and code-owner approval for protected paths (`/.github/`, `/VISION.md`). No bypass actors, ever. Why each rule exists, and its source: [`references/sources.md`](references/sources.md).

## Protection level

Run `SETUP level OWNER/REPO` first. It prints one of:

- `enforced`: public repo, or private on a paid plan. GitHub refuses rule violations.
- `advisory`: private repo on GitHub Free. Rulesets, CODEOWNERS enforcement, auto-merge and environments do not exist there. Everything else still applies, plus the daily `main-audit` workflow that flags commits on main which did not arrive through an approved PR. Say **advisory** to the captain in plain words every time you report on such a repo: the rules hold against agent mistakes, and nothing on GitHub's side stops a bypass.

The level is detected, never assumed. When the plan changes, rerun the skill.

## Setup

Each step ends when its check passes.

1. **Level.** `SETUP level OWNER/REPO`. Done when you have reported the level to the captain.
2. **Apps installed.** The two apps exist and are installed on this repo. If not, walk the captain through [`references/apps.md`](references/apps.md). Done when the captain confirms both apps list this repo under *Repository access*, and `SETUP secrets OWNER/REPO` reports all three reviewer credentials present.
3. **Repo files on a branch.** On a branch named `chore/repo-setup`, add from `TEMPLATES`:
   - `CODEOWNERS` → `.github/CODEOWNERS` (replace `@OWNER`)
   - `VISION.md` → repo root. Use the [`vision`](https://github.com/kunchenguid/vision) skill when it is installed; otherwise draft it from the README and history and put each section to the captain as a question. The review agent judges every PR against this file, so a vague vision is a weak reviewer.
   - `pr-policy.md` → `.github/pr-policy.md`
   - `SECURITY.md` → repo root
   - `dependabot.yml` → `.github/dependabot.yml`, adding the repo's package ecosystems
   - `workflows/guard.yml` and `workflows/release.yml` → `.github/workflows/`, `releaserc.json` → `.releaserc.json`
   - `../github-pr-review/templates/pr-review.yml` → `.github/workflows/pr-review.yml` and `../github-pr-review/SKILL.md` → `.github/pr-review/INSTRUCTIONS.md`
   - level `advisory` only: `workflows/main-audit.yml` → `.github/workflows/`
   - a `ci` job for this repo's own tests and lint, in `.github/workflows/ci.yml`, job `name: ci`. Read the repo's scripts and config to find the commands; ask the captain only when there are none.
   - a `LICENSE` if missing: ask the captain which.

   Every `uses:` is pinned to a full commit SHA with the version in a comment. Done when `actionlint` passes locally (`docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint` or the binary) and the branch is pushed.
4. **First PR.** Open it as the author app (see `github-pr-author`). Its title is `chore: protect main`. Done when every job in `guard.yml` and `ci.yml` has reported on it. The protection does not exist yet, so the captain reviews and merges this one by hand.
5. **Settings.** `SETUP apply OWNER/REPO --checks ci,pr-title,gitleaks,actionlint`, adding `--beta` for repos with a beta channel. It sets merge options, Actions permissions, security features, labels, the `pr-review` environment and the ruleset, and reports anything it could not set. Done when `SETUP audit OWNER/REPO --checks …` exits 0.
6. **Observe week.** Set the variable `PR_REVIEW_MODE` to `observe` in the `pr-review` environment. The reviewer comments *would approve* instead of approving, and the captain approves. After a week of PRs where its verdicts matched the captain's, the captain sets it to `enforce`.

## Audit and adjust

`SETUP audit OWNER/REPO --checks …` compares live settings, ruleset and files with this skill and exits non-zero on any drift, listing each item. Fix drift by rerunning `apply` for settings, and by a PR for files: a file that differs from its template is either a deliberate local change (record why in the PR that made it) or stale (update it from the template).

## Variants

Read [`references/variants.md`](references/variants.md) when the repo needs any of: a beta channel (`x.y.z-beta.n`, optionally deploying to `dev.<domain>`), release-please instead of a release per merge, a Cloudflare deploy, or GitHub Pages.

## Emergency

When required checks cannot pass for a reason outside the change itself (Actions outage, a broken external action, the reviewer out of quota):

1. `SETUP emergency-off OWNER/REPO "reason"`: disables the ruleset and opens an issue labelled `needs-captain` that records who, when and why.
2. Land the fix.
3. `SETUP emergency-on OWNER/REPO`: re-enables the ruleset and closes the issue.

Step 3 is the completion criterion; the open issue keeps it visible until it is done.
