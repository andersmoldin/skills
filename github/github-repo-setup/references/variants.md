# Variants

Add one only when the repo needs it. Each changes files through a PR and, where noted, reruns `apply`.

## Beta channel

For installable things (an HA integration via HACS) and sites that want a `dev.<domain>`.

- Branch `beta`, protected like main: `apply --beta` adds it to the ruleset.
- Merges to `beta` release `x.y.z-beta.n`; merging `beta` into `main` releases `x.y.z`.
- `.releaserc.json`: `"branches": ["main", {"name": "beta", "prerelease": true}]`.
- `beta` → `main` is a **merge commit**, not a squash: semantic-release needs main to contain the beta history to number versions correctly. `--beta` therefore allows merge commits and drops linear history. The policy file gets a rule: merge commits only for `beta` → `main`.
- Web repos: the deploy job (below) deploys `beta` to `dev.<domain>` and `main` to production.

## release-please instead of a release per merge

For repos others install, where ten patch releases a day would be ten update notifications. [release-please](https://github.com/googleapis/release-please) keeps a release PR open with the changelog and next version; merging it releases. Same PR titles drive it. Replace `release.yml` with release-please's workflow; give it the author app's token (not `GITHUB_TOKEN`), or its release PR will not trigger CI. `Release-As: x.y.z` in a commit body overrides the version.

## Cloudflare deploy

The question is who holds the Cloudflare API token, and what starts the deploy.

| Level | Deploy via | Token lives in |
|---|---|---|
| ENFORCED (public, or paid plan) | `cloudflare/wrangler-action` in `deploy.yml`, `on: push: branches: [main]`, job `environment: production` | `production` environment, deployment branches: `main` only |
| ADVISORY (private on Free) | **Workers Builds** (Cloudflare's own Git integration) | Cloudflare. GitHub never sees it |

ADVISORY steps:

1. Captain connects the repo in Cloudflare dashboard → Workers → the Worker → Settings → Builds. Production branch `main`. The *Cloudflare Workers and Pages* GitHub app gets access to this repo only.
2. Build command runs the tests first (`npm ci && npm test && npm run build`), so red tests stop the deploy.
3. Remove the GitHub deploy workflow and delete the `CLOUDFLARE_API_TOKEN` repo secret, so a branch workflow cannot read it. Never run both paths: that deploys twice.

Either way the token is scoped to the one Worker (template *Edit Cloudflare Workers*, limited to the account and zone). Sources: [Cloudflare GitHub Actions](https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/), [Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/).

## GitHub Pages

Pattern only until a repo needs it: `actions/deploy-pages` from `main`, the built-in `github-pages` environment restricted to `main`.
