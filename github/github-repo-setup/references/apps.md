# The two GitHub Apps

Created once per account, installed per repo. Only the captain can do this.

App names are global on GitHub, so prefix them with your handle: `HANDLE-pr-author` and `HANDLE-pr-review` below. The skills never depend on the names; the author's keychain entry is found by service name (`github-pr-author`, override with `PR_AUTHOR_KEYCHAIN_SERVICE`).

| App | Repository permissions | Key lives in |
|---|---|---|
| `HANDLE-pr-author` | Contents: write, Pull requests: write, Workflows: write, Checks: read, Actions: read | Agent Vault; macOS keychain until Agent Vault exists |
| `HANDLE-pr-review` | Contents: read, Pull requests: write, Checks: read, Actions: read | the repo's `pr-review` environment (repo secrets on ADVISORY repos) |

Webhooks off, installable only on the owner's account. Neither app has Administration permission, so neither can change rulesets or settings.

## Create

Prefilled forms (click **Create GitHub App** at the bottom):

- author: `https://github.com/settings/apps/new?name=HANDLE-pr-author&url=https://github.com/OWNER&public=false&webhook_active=false&contents=write&pull_requests=write&workflows=write&checks=read&actions=read`
- reviewer: `https://github.com/settings/apps/new?name=HANDLE-pr-review&url=https://github.com/OWNER&public=false&webhook_active=false&contents=read&pull_requests=write&checks=read&actions=read`

On each app's page: note the **App ID** (*General*), then *Credentials* → *Key pairs* → **New key** (downloads a `.pem`).

## Install on a repo

App page → **Install App** (first time) or **Configure** → *Only select repositories* → add the repo.

## Store the keys

The captain runs these; the key never passes through an agent's context.

```bash
REPO=OWNER/REPO
# reviewer: environment secret on ENFORCED repos; drop "--env pr-review" on ADVISORY repos
gh secret set PR_REVIEW_APP_PRIVATE_KEY -R $REPO --env pr-review < ~/Downloads/HANDLE-pr-review.*.pem
gh variable set PR_REVIEW_APP_ID -R $REPO --env pr-review --body <REVIEW_APP_ID>
claude setup-token   # prints a subscription token for Actions; paste it into the next command
gh secret set CLAUDE_CODE_OAUTH_TOKEN -R $REPO --env pr-review
rm ~/Downloads/HANDLE-pr-review.*.pem

# author: once per machine, not per repo
security add-generic-password -U -s github-pr-author -a key -w "$(base64 < ~/Downloads/HANDLE-pr-author.*.pem)"
security add-generic-password -U -s github-pr-author -a app-id -w <AUTHOR_APP_ID>
rm ~/Downloads/HANDLE-pr-author.*.pem
```

Keep a copy of each `.pem` only if you want to re-add a repo without generating a new key; a new key can be generated any time on the app page.

## Limits until the sandbox exists

Coding agents still run as the captain's macOS user, so they can read the keychain and the captain's `gh` login. Until they run in a sandbox behind Agent Vault, the split holds against mistakes, not against a hijacked agent. Say so when reporting the setup.

The subscription token runs the reviewer on the captain's Claude plan (no per-token billing). Anthropic's Actions docs offer it for this; their terms assume ordinary individual use, so keep it to the captain's own repos.
