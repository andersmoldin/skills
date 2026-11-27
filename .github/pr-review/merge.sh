#!/usr/bin/env bash
# Merge a pull request the review app has approved. pr-review.yml runs this in its merge job, from a
# checkout of the default branch, with the review app's token. See ../SKILL.md.
#
# Merges only where GitHub enforces no review (private repos on GitHub Free); elsewhere auto-merge does.
# Every answer is assigned before it is compared with the one value that allows the merge, so a failed
# read stops the script instead of letting the merge through.
set -euo pipefail
shopt -s inherit_errexit # a failed read inside $(...) stops the script too

: "${GH_REPO:?}" "${PR:?}" "${SHA:?}" "${SINCE:?}" "${BOT:?}" "${CAPTAIN:?}" "${GITHUB_WORKFLOW:?}"
: "${REQUIRED_CHECKS:?comma-separated check names that must report before a merge}"
MODE="${MODE:-}"
CODEOWNERS="${CODEOWNERS:-.github/CODEOWNERS}"
WAIT_SECONDS="${WAIT_SECONDS:-1200}" # for checks still running when the review ends
POLL_SECONDS="${POLL_SECONDS:-30}"

# Not merging, and nothing the PR needs to hear about.
skip() { echo "not merging: $*"; exit 0; }

# Approved but not merged, for a reason someone has to act on: say it on the PR and fail the job.
hold() {
  # shellcheck disable=SC2016 # the backticks are Markdown for the comment
  local next='The review app does not merge it: the captain merges it, or a push or an `@review` comment runs the review and this merge again.'
  gh pr comment "$PR" --body "Approved, not merged: $1. $next"
  echo "::error::not merged: $1"
  exit 1
}

# Does GitHub itself require an approval on this branch? Prints yes, no or the error.
# Private repos on GitHub Free have no rules and answer "Upgrade to GitHub Pro".
github_enforces_review() {
  local out
  if out=$(gh api "repos/$GH_REPO/rules/branches/$1" 2>&1); then
    jq -r 'if type != "array" then error("not a list")
           elif any(.[]; .type == "pull_request" and (.parameters.required_approving_review_count // 0) > 0)
           then "yes" else "no" end' <<<"$out" 2>/dev/null || echo "unreadable answer: $out"
  elif grep -q "Upgrade to GitHub Pro" <<<"$out"; then
    echo no
  else
    echo "$out"
  fi
}

# All pages of a list endpoint as one JSON array; anything else (an error body) fails.
api_list() {
  gh api --paginate "$1" | jq -s 'if all(.[]; type == "array") then add // [] else error("not a list") end'
}

# Sets pr to the PR as it is now. A closed PR, or one with commits the review did not read, is not ours
# to merge: a push starts a new review, and that run decides.
read_pr() {
  pr=$(gh api "repos/$GH_REPO/pulls/$PR")
  [[ "$(jq -r .state <<<"$pr")" == open ]] || skip "the PR is closed or already merged"
  [[ "$(jq -r .head.sha <<<"$pr")" == "$SHA" ]] || skip "the PR has commits pushed after the review of $SHA"
}

# What the review and the captain decided, read afresh before every merge attempt.
gates() {
  local reviews comments approved requested stop escalated_at decided labelled draft
  read_pr
  reviews=$(api_list "repos/$GH_REPO/pulls/$PR/reviews?per_page=100")
  approved=$(jq --arg bot "$BOT" --arg sha "$SHA" --arg since "$SINCE" 'any(.[]; .user.login == $bot
      and .state == "APPROVED" and .commit_id == $sha and .submitted_at >= $since)' <<<"$reviews")
  [[ "$approved" == true ]] || skip "no approval of $SHA from this review run"
  # A reviewer's state is their latest approval, request for changes or dismissal; comments leave it as is.
  requested=$(jq -r '[.[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "DISMISSED")]
      | group_by(.user.login) | map(max_by(.submitted_at) | select(.state == "CHANGES_REQUESTED") | .user.login)
      | join(", ")' <<<"$reviews")
  [[ -z "$requested" ]] || hold "changes requested by $requested"

  comments=$(api_list "repos/$GH_REPO/issues/$PR/comments?per_page=100")
  # The reviewer itself ends a run that starts after a stop; this catches one written during the run.
  stop=$(jq --arg captain "$CAPTAIN" --arg since "$SINCE" 'any(.[]; .user.login == $captain
      and .created_at >= $since and (.body | startswith("@agent stop")))' <<<"$comments")
  [[ "$stop" == false ]] || skip "the captain wrote @agent stop"
  # Once escalated, the PR waits for the captain: an approval of a later push alone does not merge it.
  escalated_at=$(jq -r --arg bot "$BOT" '[.[] | select(.user.login == $bot
      and (.body | startswith("<!-- needs-captain -->"))) | .created_at] | max // ""' <<<"$comments")
  if [[ -n "$escalated_at" ]]; then
    decided=$(printf '%s\n%s\n' "$comments" "$reviews" | jq -s --arg captain "$CAPTAIN" --arg at "$escalated_at" '
        any(.[0][]; .user.login == $captain and .created_at > $at and (.body | startswith("@review")))
        or any(.[1][]; .user.login == $captain and .submitted_at > $at and .state == "APPROVED")')
    [[ "$decided" == true ]] \
      || hold "the reviewer escalated this PR at $escalated_at and the captain has not answered since"
  fi

  labelled=$(jq 'any(.labels[]; .name == "needs-captain")' <<<"$pr")
  [[ "$labelled" == false ]] || hold "the PR is labelled needs-captain"
  draft=$(jq .draft <<<"$pr")
  [[ "$draft" == false ]] || hold "the PR is a draft"
  # The beta variant (github-repo-setup references/variants.md) merges beta into main with a merge commit.
  [[ "$(jq -r .head.ref <<<"$pr")" != beta ]] || hold "beta goes into $base with a merge commit, which this job never makes"
}

# CODEOWNERS patterns as bash globs, erring towards protecting too much: "*" also crosses "/", a pattern
# with no slash before its end (or starting with "**/") matches at any depth, and each pattern also
# covers everything under it.
protected_globs() {
  local pat anchored
  while read -r pat _ || [[ -n "$pat" ]]; do # the last line may lack a newline
    [[ -n "$pat" && "$pat" != \#* ]] || continue
    if [[ "$pat" == '**/'* ]]; then
      pat="${pat#'**/'}"; anchored=false
    elif [[ "$pat" == /* || "${pat%/}" == */* ]]; then
      anchored=true
    else
      anchored=false
    fi
    pat="${pat#/}"; pat="${pat%/}"
    printf '%s\n' "$pat" "$pat/*"
    "$anchored" || printf '%s\n' "*/$pat" "*/$pat/*"
  done < "$CODEOWNERS"
}

# Sets touched to the first changed path (or path a file moved from) that CODEOWNERS protects; holds
# when unsure.
protected_change() {
  local listed globs files paths f g
  touched=""
  [[ -f "$CODEOWNERS" ]] || hold "cannot read $CODEOWNERS on the default branch"
  listed=$(protected_globs)
  [[ -n "$listed" ]] || hold "$CODEOWNERS on the default branch lists no protected paths"
  mapfile -t globs <<<"$listed"
  files=$(api_list "repos/$GH_REPO/pulls/$PR/files?per_page=100")
  [[ "$(jq length <<<"$files")" == "$(jq .changed_files <<<"$pr")" ]] \
    || hold "GitHub's file list for the PR is incomplete, so protected paths cannot be ruled out"
  paths=$(jq -r '.[] | .filename, (.previous_filename // empty)' <<<"$files")
  while read -r f; do
    for g in "${globs[@]}"; do
      # shellcheck disable=SC2053 # g is a glob on purpose
      if [[ "$f" == $g ]]; then touched=$f; return; fi
    done
  done <<<"$paths"
}

# Returns once every check on the PR has passed or been skipped and every REQUIRED_CHECKS name has
# reported, leaving out this workflow's own jobs: they are the review and this merge, not checks of
# the change. Holds on a failed check, or at the deadline with what it was still waiting for.
wait_for_checks() {
  local deadline=$((SECONDS + WAIT_SECONDS)) err checks state waiting
  err=$(mktemp)
  while :; do
    read_pr
    # gh can exit non-zero while checks are pending; what it printed decides, and anything unreadable waits.
    checks=$(gh pr checks "$PR" --json name,bucket,workflow 2>"$err" || true)
    state=$(jq -r --arg wf "$GITHUB_WORKFLOW" --arg required "$REQUIRED_CHECKS" 'if type != "array" then "unknown" else
        [.[] | select(.workflow != $wf)] as $c
        | ([$c[] | select(.bucket == "fail" or .bucket == "cancel") | .name] | join(", ")) as $failed
        | (($required | split(",") | map(select(. != ""))) - [$c[].name] | join(", ")) as $missing
        | if $failed != "" then "failed: \($failed)"
          elif $missing != "" then "missing: \($missing)"
          elif all($c[]; .bucket == "pass" or .bucket == "skipping") then "passed"
          else "pending" end end' <<<"$checks" 2>/dev/null || echo unknown)
    case "$state" in
      passed) return ;;
      failed:*) hold "a check did not pass (${state#failed: })" ;;
      missing:*) waiting="required checks not reported: ${state#missing: }" ;;
      unknown) waiting="cannot read the checks ($(cat "$err") $checks)" ;;
      *) waiting="the checks had not all passed" ;;
    esac
    (( SECONDS < deadline )) || hold "$waiting, $((WAIT_SECONDS / 60)) minutes after the review"
    sleep "$POLL_SECONDS"
  done
}

[[ "$MODE" == enforce ]] || skip "observe mode: the reviewer does not approve, the captain merges"

read_pr
base=$(jq -r .base.ref <<<"$pr")

enforced=$(github_enforces_review "$base")
case "$enforced" in
  yes) skip "GitHub enforces the review on $base, so auto-merge lands the PR" ;;
  no) ;;
  *) hold "cannot tell whether GitHub enforces the review on $base ($enforced)" ;;
esac

gates
protected_change
[[ -z "$touched" ]] || hold "it changes the protected path $touched (CODEOWNERS), which only the captain approves and merges"

wait_for_checks
gates # again: the PR may have changed while the checks ran

# Squash, so the PR title becomes the commit and decides the version; GitHub refuses if the head moved.
if ! out=$(gh pr merge "$PR" --squash --match-head-commit "$SHA" 2>&1); then
  hold "GitHub refused the merge: $out"
fi
echo "merged #$PR at $SHA"
