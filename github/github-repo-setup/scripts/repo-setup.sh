#!/usr/bin/env bash
# Apply, audit and switch main-branch protection for one GitHub repo.
# Runs on the captain's gh login (admin). See ../SKILL.md.
#
#   repo-setup.sh level          OWNER/REPO
#   repo-setup.sh secrets        OWNER/REPO
#   repo-setup.sh apply          OWNER/REPO --checks a,b,c [--beta]
#   repo-setup.sh audit          OWNER/REPO --checks a,b,c [--beta]
#   repo-setup.sh emergency-off  OWNER/REPO "reason"
#   repo-setup.sh emergency-on   OWNER/REPO
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES="$HERE/../templates"
RULESET_NAME="main-protection"
ACTIONS_APP_ID=15368 # GitHub Actions: required checks must come from Actions, not another app
LABEL="needs-captain"
EMERGENCY_TITLE="Emergency: main protection disabled"

die() { echo "error: $*" >&2; exit 2; }
need() { command -v "$1" >/dev/null || die "$1 is required"; }
need gh; need jq

cmd="${1:-}"; repo="${2:-}"
[[ -n "$cmd" && "$repo" == */* ]] || die "usage: repo-setup.sh <level|secrets|apply|audit|emergency-off|emergency-on> OWNER/REPO ..."
shift 2

checks=""; beta=false; reason=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --checks) checks="${2:-}"; shift 2 ;;
    --beta) beta=true; shift ;;
    *) reason="$1"; shift ;;
  esac
done

# ---------- detection ----------

level() {
  # Fail closed: only GitHub's plan-limit answer means advisory; any other error stops here.
  local vis out
  vis=$(gh api "repos/$repo" --jq .visibility) || die "cannot read $repo"
  if [[ "$vis" == "public" ]]; then echo enforced; return; fi
  if out=$(gh api "repos/$repo/rulesets" 2>&1); then echo enforced; return; fi
  if grep -q "Upgrade to GitHub Pro" <<<"$out"; then echo advisory; return; fi
  die "cannot determine protection level for $repo: $out"
}

# What advisory means, in the words the captain reads (SKILL.md quotes the same text).
advisory_notice() {
  cat <<'EOF'
Main is NOT protected. Anyone with write access, including an agent on your login, can push to main. main-audit detects it afterwards; nothing prevents it.
GitHub's banner "Your main branch isn't protected" is expected at advisory level; its button leads to an upgrade.
EOF
}

level_cmd() {
  local lvl; lvl=$(level)
  echo "$lvl"
  [[ "$lvl" != "advisory" ]] || advisory_notice
}

default_branch() { gh api "repos/$repo" --jq .default_branch; }

ruleset_id() {
  gh api "repos/$repo/rulesets" --jq ".[] | select(.name == \"$RULESET_NAME\") | .id" 2>/dev/null || true
}

# ---------- desired state ----------

desired_ruleset() {
  [[ -n "$checks" ]] || die "--checks is required (comma-separated job names)"
  jq --arg checks "$checks" --argjson app "$ACTIONS_APP_ID" --argjson beta "$beta" '
    .rules |= map(
      if .type == "required_status_checks" then
        .parameters.required_status_checks = ($checks | split(",") | map({context: ., integration_id: $app}))
      elif .type == "pull_request" and $beta then
        .parameters.allowed_merge_methods = ["squash", "merge"]
      else . end)
    | if $beta then
        .rules |= map(select(.type != "required_linear_history"))
        | .conditions.ref_name.include += ["refs/heads/beta"]
      else . end
  ' "$TEMPLATES/ruleset.json"
}

desired_repo_settings() {
  # Auto-merge waits only for what GitHub enforces. Advisory repos enforce no review, so it would merge at
  # once; there the review app merges what it approves instead (github-pr-review merge.sh).
  local lvl="$1"
  jq -n --argjson beta "$beta" --arg lvl "$lvl" '{
    allow_squash_merge: true,
    allow_merge_commit: $beta,
    allow_rebase_merge: false,
    delete_branch_on_merge: true,
    squash_merge_commit_title: "PR_TITLE",
    squash_merge_commit_message: "PR_BODY",
    allow_auto_merge: ($lvl == "enforced")
  }'
}

# ---------- apply ----------

apply_settings() {
  local lvl; lvl=$(level)
  echo "level: $lvl"
  local failed=()

  desired_repo_settings "$lvl" | gh api -X PATCH "repos/$repo" --input - >/dev/null \
    && echo "ok   merge settings" || failed+=("merge settings")

  jq -n '{default_workflow_permissions: "read", can_approve_pull_request_reviews: false}' \
    | gh api -X PUT "repos/$repo/actions/permissions/workflow" --input - >/dev/null \
    && echo "ok   GITHUB_TOKEN read-only, Actions cannot approve PRs" || failed+=("workflow permissions")

  jq -n '{enabled: true, allowed_actions: "all", sha_pinning_required: true}' \
    | gh api -X PUT "repos/$repo/actions/permissions" --input - >/dev/null \
    && echo "ok   actions must be pinned to a full SHA" || failed+=("SHA pinning policy")

  gh api -X PUT "repos/$repo/vulnerability-alerts" >/dev/null \
    && echo "ok   Dependabot alerts" || failed+=("Dependabot alerts")
  gh api -X PUT "repos/$repo/automated-security-fixes" >/dev/null \
    && echo "ok   Dependabot security updates" || failed+=("Dependabot security updates")

  if [[ "$(gh api "repos/$repo" --jq .visibility)" == "public" ]]; then
    jq -n '{security_and_analysis: {secret_scanning: {status: "enabled"}, secret_scanning_push_protection: {status: "enabled"}}}' \
      | gh api -X PATCH "repos/$repo" --input - >/dev/null \
      && echo "ok   secret scanning + push protection" || failed+=("secret scanning")
    gh api -X PUT "repos/$repo/private-vulnerability-reporting" >/dev/null \
      && echo "ok   private vulnerability reporting" || failed+=("private vulnerability reporting")
  else
    echo "skip secret scanning: not available for private repos on this plan (gitleaks in CI covers it)"
  fi

  if gh api "repos/$repo/labels/$LABEL" >/dev/null 2>&1; then
    echo "ok   label $LABEL"
  else
    gh api -X POST "repos/$repo/labels" -f name="$LABEL" -f color=d93f0b \
      -f description="Waiting for the captain" >/dev/null \
      && echo "ok   label $LABEL" || failed+=("label")
  fi

  if [[ "$lvl" == "enforced" ]]; then
    jq -n '{deployment_branch_policy: {protected_branches: false, custom_branch_policies: true}}' \
      | gh api -X PUT "repos/$repo/environments/pr-review" --input - >/dev/null \
      && echo "ok   environment pr-review" || failed+=("environment")
    local db; db=$(default_branch)
    if ! gh api "repos/$repo/environments/pr-review/deployment-branch-policies" \
         --jq '.branch_policies[].name' | grep -qx "$db"; then
      gh api -X POST "repos/$repo/environments/pr-review/deployment-branch-policies" \
        -f name="$db" -f type=branch >/dev/null || failed+=("environment branch policy")
    fi
    echo "ok   pr-review secrets usable from $db only (audit flags any other policy)"

    local id body; id=$(ruleset_id); body=$(desired_ruleset)
    if [[ -n "$id" ]]; then
      echo "$body" | gh api -X PUT "repos/$repo/rulesets/$id" --input - >/dev/null \
        && echo "ok   ruleset updated" || failed+=("ruleset")
    else
      echo "$body" | gh api -X POST "repos/$repo/rulesets" --input - >/dev/null \
        && echo "ok   ruleset created" || failed+=("ruleset")
    fi
  else
    echo "skip ruleset, environment: not available at advisory level"
    echo "     auto-merge off: the review app merges what it approves (enforce mode); the captain merges the rest"
    echo "     reviewer secrets go in repo secrets instead of the pr-review environment"
    advisory_notice
  fi

  if [[ ${#failed[@]} -gt 0 ]]; then
    printf 'FAILED: %s\n' "${failed[@]}" >&2
    exit 1
  fi
}

# ---------- audit ----------

audit() {
  local lvl; lvl=$(level)
  local drift=()
  echo "level: $lvl"

  local live want
  want=$(desired_repo_settings "$lvl")
  live=$(gh api "repos/$repo" | jq --argjson w "$want" 'with_entries(select(.key as $k | $w | has($k)))')
  [[ "$(jq -S . <<<"$live")" == "$(jq -S . <<<"$want")" ]] || drift+=("merge settings: $(jq -c . <<<"$live")")

  live=$(gh api "repos/$repo/actions/permissions/workflow" --jq '[.default_workflow_permissions, .can_approve_pull_request_reviews] | @tsv')
  [[ "$live" == $'read\tfalse' ]] || drift+=("workflow permissions: $live")

  [[ "$(gh api "repos/$repo/actions/permissions" --jq '.sha_pinning_required // false')" == "true" ]] \
    || drift+=("SHA pinning policy off")

  gh api "repos/$repo/labels/$LABEL" >/dev/null 2>&1 || drift+=("label $LABEL missing")

  if [[ "$lvl" == "enforced" ]]; then
    local policies repo_secrets
    policies=$(gh api "repos/$repo/environments/pr-review/deployment-branch-policies" \
      --jq '[.branch_policies[].name] | sort | join(",")' 2>/dev/null || echo "missing")
    [[ "$policies" == "$(default_branch)" ]] || drift+=("pr-review environment branches: $policies (want only the default branch)")
    repo_secrets=$(gh api "repos/$repo/actions/secrets" --jq '.secrets[].name')
    for s in PR_REVIEW_APP_PRIVATE_KEY CLAUDE_CODE_OAUTH_TOKEN; do
      grep -qx "$s" <<<"$repo_secrets" && drift+=("$s is a REPO secret: any branch workflow can read it; delete it, keep only the environment copy")
    done
    local id; id=$(ruleset_id)
    if [[ -z "$id" ]]; then
      drift+=("ruleset $RULESET_NAME missing")
    else
      # Compare only what this skill sets: GitHub adds its own defaults to rule parameters.
      local norm='{name, target, enforcement, bypass_actors: (.bypass_actors // []), conditions, rules: (.rules | map({type, parameters}) | map(if .parameters == null then del(.parameters) else . end) | sort_by(.type))}'
      want=$(desired_ruleset | jq -S "$norm")
      live=$(gh api "repos/$repo/rulesets/$id" | jq -S --argjson w "$want" "$norm"'
        | .rules |= map(. as $r
            | ($w.rules[] | select(.type == $r.type) | .parameters // null) as $wp
            | if $wp == null then $r else .parameters |= with_entries(select(.key as $k | $wp | has($k))) end)')
      if [[ "$live" != "$want" ]]; then
        drift+=("ruleset differs: $(diff <(echo "$want") <(echo "$live") | grep '^[<>]' | tr '\n' ' ' || true)")
      fi
    fi
  fi

  local branch; branch=$(gh api "repos/$repo" --jq .default_branch)
  local files=(.github/CODEOWNERS VISION.md SECURITY.md .github/pr-policy.md .github/dependabot.yml
               .github/workflows/guard.yml .github/workflows/release.yml .github/workflows/pr-review.yml
               .github/workflows/ci.yml .github/pr-review/INSTRUCTIONS.md .github/pr-review/merge.sh .releaserc.json
               .github/release/package-lock.json LICENSE)
  [[ "$lvl" == "advisory" ]] && files+=(.github/workflows/main-audit.yml)
  for f in "${files[@]}"; do
    gh api "repos/$repo/contents/$f?ref=$branch" >/dev/null 2>&1 || drift+=("file missing: $f")
  done

  local unpinned
  unpinned=$(gh api "repos/$repo/contents/.github/workflows?ref=$branch" --jq '.[].path' 2>/dev/null \
    | while read -r p; do
        gh api "repos/$repo/contents/$p?ref=$branch" --jq .content | base64 -d \
          | grep -nE '^\s*-?\s*uses:' | grep -vE 'uses:\s*(\./|docker://[^ ]+@sha256:)|@[0-9a-f]{40}' \
          | sed "s|^|$p:|" || true
      done || true)
  [[ -z "$unpinned" ]] || drift+=("unpinned actions: $unpinned")

  # Not drift: the plan, not the settings, decides this, so it does not fail the audit.
  [[ "$lvl" == "advisory" ]] && echo "main not protected (advisory)"

  if [[ ${#drift[@]} -eq 0 ]]; then
    echo "no drift"
  else
    printf 'DRIFT: %s\n' "${drift[@]}"
    exit 1
  fi
}

# ---------- secrets presence ----------

secrets() {
  local lvl; lvl=$(level)
  local s v missing=()
  if [[ "$lvl" == "enforced" ]]; then
    s=$(gh api "repos/$repo/environments/pr-review/secrets" --jq '.secrets[].name' 2>/dev/null || true)
    v=$(gh api "repos/$repo/environments/pr-review/variables" --jq '.variables[].name' 2>/dev/null || true)
  else
    s=$(gh api "repos/$repo/actions/secrets" --jq '.secrets[].name')
    v=$(gh api "repos/$repo/actions/variables" --jq '.variables[].name')
  fi
  grep -qx PR_REVIEW_APP_PRIVATE_KEY <<<"$s" || missing+=(PR_REVIEW_APP_PRIVATE_KEY)
  grep -qx CLAUDE_CODE_OAUTH_TOKEN <<<"$s" || missing+=(CLAUDE_CODE_OAUTH_TOKEN)
  grep -qx PR_REVIEW_APP_ID <<<"$v" || missing+=("PR_REVIEW_APP_ID (variable)")
  if [[ ${#missing[@]} -eq 0 ]]; then echo "reviewer credentials present ($lvl)"; else
    printf 'MISSING: %s\n' "${missing[@]}"; exit 1; fi
}

# ---------- emergency ----------

set_enforcement() {
  local id; id=$(ruleset_id)
  [[ -n "$id" ]] || die "no ruleset $RULESET_NAME on $repo"
  gh api "repos/$repo/rulesets/$id" | jq --arg e "$1" '{name, target, enforcement: $e, bypass_actors, conditions, rules}' \
    | gh api -X PUT "repos/$repo/rulesets/$id" --input - >/dev/null
}

emergency_off() {
  [[ -n "$reason" ]] || die "give a reason: emergency-off OWNER/REPO \"reason\""
  [[ -n "$(ruleset_id)" ]] || die "no ruleset $RULESET_NAME on $repo"
  local who url; who=$(gh api user --jq .login)
  gh api "repos/$repo/labels/$LABEL" >/dev/null 2>&1 \
    || gh api -X POST "repos/$repo/labels" -f name="$LABEL" -f color=d93f0b >/dev/null
  # the log issue comes first, so protection is never off without a record
  url=$(gh issue create -R "$repo" --title "$EMERGENCY_TITLE" --label "$LABEL" \
    --body "Ruleset \`$RULESET_NAME\` disabled by @$who at $(date -u +%FT%TZ).

Reason: $reason

Re-enable with \`repo-setup.sh emergency-on $repo\`. This issue closes when protection is back.")
  if ! set_enforcement disabled; then
    gh issue close -R "$repo" "$url" --comment "Disabling FAILED; protection is still on." >/dev/null
    die "could not disable the ruleset; protection is still on"
  fi
  echo "PROTECTION IS OFF for $repo. Run emergency-on when the fix has landed."
}

emergency_on() {
  set_enforcement active
  local n
  n=$(gh issue list -R "$repo" --state open --search "\"$EMERGENCY_TITLE\" in:title" --json number --jq '.[].number')
  for i in $n; do
    gh issue close -R "$repo" "$i" --comment "Protection re-enabled at $(date -u +%FT%TZ)."
  done
  echo "protection is back on for $repo"
}

case "$cmd" in
  level) level_cmd ;;
  secrets) secrets ;;
  apply) apply_settings ;;
  audit) audit ;;
  emergency-off) emergency_off ;;
  emergency-on) emergency_on ;;
  *) die "unknown command: $cmd" ;;
esac
