# PR policy

The review agent reads this file from the default branch on every pull request. It decides what the agent may approve on its own and what goes to the captain. Edit it to fit this repo; it is a protected file.

## The reviewer approves on its own

A change it has read in full that:

- serves the purpose in `VISION.md`,
- keeps every behaviour listed under *Behaviour that must not change silently*,
- has a PR title whose type matches the change (`fix:` for a fix, `feat:` only for a new capability the captain asked for),
- carries tests or evidence in proportion to its risk.

## The reviewer escalates to the captain

Label `needs-captain`, request the captain's review, and say why in one comment. Escalate when the change:

1. touches a protected path (`/.github/`, `/VISION.md`, `/github/*/scripts/`); CODEOWNERS enforces this too,
2. changes a default or other existing behaviour users rely on, even when it looks like an improvement,
3. contains or exposes a secret, token, key, password, personal data or other sensitive information the captain has not explicitly approved,
4. sits outside `VISION.md`, or the vision does not settle it,
5. is a breaking change (`!` or `BREAKING CHANGE`), which would release a new major version,
6. is something the reviewer cannot judge with confidence after reading it, or the author and reviewer have gone two rounds without converging.

PRs from forks and from Dependabot never reach the reviewer: the workflow labels them `needs-captain`.

The captain answers an escalation by approving, by requesting changes, or by a comment starting with `@review` that states the decision; that comment re-runs the review.

A risk classification never lowers these bars: a "low-risk" label on a change that hits any item above is still escalated.

## Repo-specific rules

<!-- Add rules that only apply here, e.g. "schema changes need a migration", "no new runtime dependencies". -->
