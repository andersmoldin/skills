# Why each rule, and where it comes from

Sources:

- **SC**: [OpenSSF Scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md)
- **SCM**: [OpenSSF SCM Best Practices](https://best.openssf.org/SCM-BestPractices/)
- **GH**: [GitHub Actions secure use reference](https://docs.github.com/en/actions/reference/security/secure-use), [Quickstart for securing your repository](https://docs.github.com/en/code-security/getting-started/quickstart-for-securing-your-repository)
- **local**: a choice made for this setup, not taken from a list

| Rule | Why | Source |
|---|---|---|
| No deletion, no force push of main | History on main is the record; nobody rewrites it | SC Branch-Protection, SCM |
| PR required, 1 approval | Every change is read by a second identity before it lands | SC Code-Review, SCM (recommends 2; 1 because there is one human) |
| Approval from someone other than the last pusher | The author cannot approve its own last push | SCM |
| New commits dismiss approvals | An approval covers the code that was read, not later code | SCM |
| Conversations resolved before merge | Review comments are answered, not ignored | SCM |
| Code owners for `/.github/`, `/VISION.md` and code that runs with the captain's credentials | The files that define the checks cannot be changed by the agents they check | SCM, GH (CODEOWNERS for workflows) |
| Required checks bound to GitHub Actions | Another app cannot fake a green check | SC Branch-Protection, local |
| No bypass actors | An exception for the owner is an exception for anything running as the owner; emergencies use the logged switch instead | SCM (limit who can bypass), local |
| Squash only, linear history | One commit per PR, titled by the PR, which drives the version | local (convention) |
| Auto-merge, delete branch after merge | Approved and green means merged, with no manual step | local (convenience) |
| Advisory: auto-merge off, the review app merges after its approval | Auto-merge waits only for what GitHub enforces, so without rules it merges before the review; the app merges only the commit it approved, with every check passed and no protected path | local |
| `GITHUB_TOKEN` read-only by default | A workflow gets write access only where it asks for it | SC Token-Permissions, SCM, GH |
| Actions cannot approve PRs | `GITHUB_TOKEN` must not satisfy the review requirement | SCM, GH |
| Actions pinned to full commit SHA | A moved tag cannot change what runs | SC Pinned-Dependencies, GH |
| Dependabot for actions and packages | Pinned SHAs and dependencies stay current | SC Dependency-Update-Tool, GH |
| Secret scanning + push protection (public) | A leaked key is blocked at push | SCM, GH |
| gitleaks in CI | Same, on private Free repos where GitHub's scanning is unavailable | local (gap filler) |
| actionlint | Broken or dangerous workflow syntax fails before merge | SC Dangerous-Workflow (partly), local |
| Conventional Commits PR titles | The title decides patch/minor/major | local |
| `SECURITY.md`, private vulnerability reporting | People know how to report a hole privately | SC Security-Policy, GH |
| License | Others know what they may do with the code | SC License |
| Reviewer runs from `pull_request_target`, never executes PR code | Its key is unreachable from a PR branch | GH (`pull_request_target` guidance), [claude-code-action security](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md) |

Left out on purpose: two approvers, signed commits, fuzzing, SBOM, signed releases. Add signed releases in the release variant if others install the artifacts.
