#!/usr/bin/env bash
# Run one command as the author GitHub App instead of the captain's account.
#
#   as-author.sh git push -u origin HEAD
#   as-author.sh gh pr create --title "fix: ..." --body-file body.md
#
# Mints a one-hour installation token scoped to the current repo (from `git remote get-url origin`)
# and hands it to the command through the environment: GH_TOKEN for gh, an HTTP header for git,
# and the app's bot identity for commits. The captain's gh login is never used.
#
# Key source: macOS keychain, service "github-pr-author" (override: PR_AUTHOR_KEYCHAIN_SERVICE), accounts "key" (base64 PEM) and "app-id".
# When Agent Vault replaces the keychain, only mint_token changes.
set -euo pipefail

SERVICE="${PR_AUTHOR_KEYCHAIN_SERVICE:-github-pr-author}"
API="https://api.github.com"

die() { echo "as-author: $*" >&2; exit 2; }
[[ $# -gt 0 ]] || die "usage: as-author.sh <command> [args...]"
for c in openssl curl jq git security; do command -v "$c" >/dev/null || die "$c is required"; done

b64url() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }

repo_from_remote() {
  # HTTPS only: the app token is injected as an HTTPS header, so an SSH remote (or an insteadOf
  # rewrite to SSH) would push with the captain's own SSH key, silently.
  local fetch push
  fetch=$(git remote get-url origin 2>/dev/null) || die "no 'origin' remote here"
  push=$(git remote get-url --push origin)
  for u in "$fetch" "$push"; do
    [[ "$u" == https://github.com/* ]] \
      || die "origin must be an https://github.com/ URL (fetch and push, after insteadOf); got: $u"
  done
  fetch="${fetch%.git}"
  echo "${fetch#https://github.com/}"
}

api() { # api METHOD PATH AUTH [BODY]
  curl -fsS -X "$1" "$API$2" -H "Authorization: $3" -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" ${4:+--data "$4"}
}

mint_token() {
  local app_id pem now header payload unsigned sig jwt repo inst
  app_id=$(security find-generic-password -s "$SERVICE" -a app-id -w 2>/dev/null) \
    || die "no app-id in keychain service $SERVICE (see github-repo-setup/references/apps.md)"
  pem=$(security find-generic-password -s "$SERVICE" -a key -w 2>/dev/null | openssl base64 -d -A) \
    || die "no key in keychain service $SERVICE"

  now=$(date +%s)
  header=$(printf '{"alg":"RS256","typ":"JWT"}' | b64url)
  payload=$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' $((now - 60)) $((now + 540)) "$app_id" | b64url)
  unsigned="$header.$payload"
  sig=$(printf '%s' "$unsigned" | openssl dgst -sha256 -sign <(printf '%s\n' "$pem") | b64url)
  jwt="$unsigned.$sig"

  repo=$(repo_from_remote)
  inst=$(api GET "/repos/$repo/installation" "Bearer $jwt" | jq -r .id) \
    || die "the author app is not installed on $repo"
  APP_SLUG=$(api GET "/app" "Bearer $jwt" | jq -r .slug)
  TOKEN=$(api POST "/app/installations/$inst/access_tokens" "Bearer $jwt" \
    "$(jq -nc --arg r "${repo#*/}" '{repositories: [$r]}')" | jq -r .token)
  [[ -n "$TOKEN" && "$TOKEN" != null ]] || die "could not mint an installation token"
}

mint_token
bot="${APP_SLUG}[bot]"
bot_id=$(api GET "/users/$(jq -rn --arg b "$bot" '$b|@uri')" "Bearer $TOKEN" | jq -r .id)
basic=$(printf 'x-access-token:%s' "$TOKEN" | openssl base64 -A)

export GH_TOKEN="$TOKEN" GITHUB_TOKEN="$TOKEN"
export GIT_AUTHOR_NAME="$bot" GIT_COMMITTER_NAME="$bot"
export GIT_AUTHOR_EMAIL="${bot_id}+${bot}@users.noreply.github.com" GIT_COMMITTER_EMAIL="${bot_id}+${bot}@users.noreply.github.com"
# git: authenticate as the app and ignore any stored credentials for github.com
export GIT_CONFIG_COUNT=2
export GIT_CONFIG_KEY_0="http.https://github.com/.extraheader" GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $basic"
export GIT_CONFIG_KEY_1="credential.https://github.com.helper" GIT_CONFIG_VALUE_1=""
exec "$@"
