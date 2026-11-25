---
name: github-pr-author
description: How a coding agent gets its work onto main in a protected GitHub repo — branch, commit and push as the author app, Conventional Commits PR title, PR body, auto-merge, comments after each push, answering review, escalations. Use when pushing a branch, opening or updating a pull request, or responding to review comments.
---

# PR author

You are the **author**: you write the change and open the pull request. A separate review agent approves it, the captain approves protected paths and escalations, and GitHub merges it once both review and checks are green. Your job ends when the PR is merged, closed, or waiting on the captain.

`AS_AUTHOR` below means `scripts/as-author.sh` in this skill's folder. Run every `git push` and every `gh` command that writes through it (`AS_AUTHOR git push …`, `AS_AUTHOR gh pr create …`), so they act as the author app. Commits you make through it carry the app's bot identity. The captain's own login stays the captain's.

## Steps

1. **Branch.** Work on a branch off the default branch, named `<type>/<short-topic>` (`fix/token-refresh`). Done when `git branch --show-current` is not the default branch.
2. **Validate before pushing.** A small, straightforward change (a typo, a one-line fix, a doc tweak) needs only the repo's tests and lint passing. For anything larger, if `no-mistakes` is set up in this repo, run it through `AS_AUTHOR` with the captain's request as the intent; it reviews, tests, pushes and opens the PR, and you continue at step 5. Otherwise run the repo's own tests and lint until they pass. Done when they pass.
3. **Title.** Conventional Commits. It becomes the squash commit and decides the next version:
   - `fix:`, `docs:`, `refactor:`, `chore:`, `ci:`, `test:`, `perf:`, `build:` → patch. The default.
   - `feat:` → minor. Only when the captain asked for a new capability or a minor release.
   - `!` / `BREAKING CHANGE` → major. Only when the captain explicitly asked for a breaking change or a major release; the reviewer escalates it regardless.
4. **Push and open.** `AS_AUTHOR git push -u origin HEAD`, then `AS_AUTHOR gh pr create --title … --body-file …`. For a larger change, write the body with the `pr` skill if available. Every body states **intent** (the captain's request in their words), **risk** (what could break and who would notice), **evidence** (what you ran and what it showed) and **how to undo** (normally: revert the squash commit). Then `AS_AUTHOR gh pr merge --auto --squash`. On ADVISORY repos (private on GitHub Free) auto-merge does not exist: say in the body that the PR waits for a manual merge. Done when the PR URL exists and auto-merge is on or the manual merge is noted.
5. **After every push** to the PR, comment what changed since the last push and how to undo it. Before each push, read the PR's comments: if the captain wrote `@agent stop`, stop, push nothing, and report back. Done for each push when its comment is posted.
6. **Answer review.** For each request-changes comment, fix it or answer why not on that thread, push (step 5), and resolve the thread once fixed. The reviewer re-runs on every push. Done when no unresolved thread is yours to act on.
7. **Escalated.** When the PR carries `needs-captain`, the decision is the captain's: report the PR link and the open question to whoever dispatched you, and wait. Done when you have reported.
8. **Finish.** Done when the PR is merged (report the release version if one was created), closed, or escalated and reported.

## When checks fail

Read the failing job's log (`gh run view --log-failed`), fix the cause in the change, push. A check failing for a reason outside the change (outage, broken external action) is an escalation: report it; the captain decides on the emergency switch.

## Protected paths

Changes under `/.github/`, to `/VISION.md`, or to code that runs with the captain's credentials (listed in `CODEOWNERS`) need the captain's approval whatever the reviewer says. Keep them in their own PR, separate from the feature that motivates them, so the rest is not held up.
