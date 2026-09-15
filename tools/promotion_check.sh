#!/usr/bin/env bash
# Reports whether the staging ring is green enough to promote to production.
#
# Green means: the ring branch is not behind upstream main, and the ring
# branch's current head has a successful preflight, Pages deploy, and
# one-liner smoke run. The script only reports; opening the promotion pull
# request is a human action and the command is printed at the end.
#
# Usage: tools/promotion_check.sh
#   FORK=OWNER/aibast-agents-library UPSTREAM=microsoft/aibast-agents-library RING_BRANCH=staging
# FORK defaults to the GitHub repository configured as the origin remote.
set -euo pipefail

if [ -z "${FORK:-}" ]; then
  if ! origin_url="$(git remote get-url origin 2>/dev/null)"; then
    printf '%s\n' "Cannot infer the staging repository; set FORK=OWNER/REPOSITORY." >&2
    exit 2
  fi
  case "$origin_url" in
    https://github.com/*) FORK="${origin_url#https://github.com/}" ;;
    git@github.com:*) FORK="${origin_url#git@github.com:}" ;;
    ssh://git@github.com/*) FORK="${origin_url#ssh://git@github.com/}" ;;
    *)
      printf '%s\n' "Origin is not a supported GitHub URL; set FORK=OWNER/REPOSITORY." >&2
      exit 2
      ;;
  esac
  FORK="${FORK%/}"
  FORK="${FORK%.git}"
fi
if [[ ! "$FORK" =~ ^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+$ ]]; then
  printf '%s\n' "FORK must be a GitHub OWNER/REPOSITORY." >&2
  exit 2
fi
UPSTREAM="${UPSTREAM:-microsoft/aibast-agents-library}"
RING_BRANCH="${RING_BRANCH:-staging}"
PROD_BRANCH="${PROD_BRANCH:-main}"
FORK_OWNER="${FORK%%/*}"

red=0
say() { printf '%s\n' "$*"; }
fail() { say "  RED   $*"; red=1; }
pass() { say "  GREEN $*"; }

head_sha="$(gh api "repos/$FORK/commits/$RING_BRANCH" --jq .sha)"
say "ring: $FORK@$RING_BRANCH ($head_sha)"

compare="$(gh api "repos/$UPSTREAM/compare/$PROD_BRANCH...$FORK_OWNER:$RING_BRANCH")"
ahead="$(printf '%s' "$compare" | python3 -c 'import sys,json; print(json.load(sys.stdin)["ahead_by"])')"
behind="$(printf '%s' "$compare" | python3 -c 'import sys,json; print(json.load(sys.stdin)["behind_by"])')"
if [ "$behind" = "0" ]; then pass "ring contains $UPSTREAM:$PROD_BRANCH (ahead by $ahead)"; else fail "ring is behind $UPSTREAM:$PROD_BRANCH by $behind commit(s); run the sync first"; fi
if [ "$ahead" = "0" ]; then say "  NOTE  nothing to promote"; fi

check_run() {
  local workflow="$1" label="$2"
  local conclusion
  conclusion="$(gh run list -R "$FORK" --workflow "$workflow" --branch "$RING_BRANCH" -L 20 \
    --json headSha,conclusion,status,url \
    --jq "[.[] | select(.headSha == \"$head_sha\")] | first | \"\\(.status) \\(.conclusion) \\(.url)\"" 2>/dev/null || true)"
  case "$conclusion" in
    "completed success"*) pass "$label: ${conclusion#completed success }" ;;
    "") fail "$label: no run for the ring head" ;;
    *) fail "$label: $conclusion" ;;
  esac
}
check_run preflight.yml "preflight"
check_run pages.yml "Pages deploy"
check_run ring-smoke.yml "one-liner smoke"

say
if [ "$red" = "0" ]; then
  say "GREEN — promote with:"
  say "  gh pr create -R $UPSTREAM --base $PROD_BRANCH --head $FORK_OWNER:$RING_BRANCH --title \"release: promote $RING_BRANCH\" --body-file <(git log --oneline upstream/$PROD_BRANCH..origin/$RING_BRANCH)"
  exit 0
fi
say "RED — do not promote yet."
exit 1
