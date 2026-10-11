#!/usr/bin/env bash
# End-to-end test of the expansion pack, the way a person runs it after the one-liner:
# install into scratch folders, create a prototype from the sample transcript, check it, stop it,
# and prove the Brainstem kernel didn't change by a single byte.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; T="$(mktemp -d)"
# The one-liner installs the kernel as a sparse checkout (only rapp_brainstem/ is on disk), so hash
# exactly the checked-out tracked files ("H" in git ls-files -t), plus git's own view of changes.
fp() { (cd "$HOME/.brainstem/src" && git ls-files -t | awk '$1=="H"{print substr($0,3)}' | tr '\n' '\0' | xargs -0 shasum -a 256 | shasum -a 256 | cut -c1-16
        git status --porcelain --untracked-files=no | wc -l | tr -d ' ') | tr '\n' ' '; }
before="$(fp)"
PROTO_HOME="$T/proto" PROTO_BIN="$T/bin" bash "$ROOT/pack/install.sh" >/dev/null
export PROTO_HOME="$T/proto" BRAINSTEM_PROTOTYPES="$T/projects" PROTO_NO_EDITOR=1
start=$(date +%s)
"$T/bin/brainstem-proto" new --transcript "$ROOT/pack/samples/discovery-call.txt" "equipment requests" > "$T/new.log" 2>&1
secs=$(( $(date +%s) - start )); dir="$T/projects/equipment-requests"; fail=0
grep -q "Your prototype is working." "$T/new.log" && echo "✓ prototype working (${secs}s)" || { echo "✗ check failed"; fail=1; }
grep -q "^## The MVP" "$dir/DISCOVERY.md" && echo "✓ DISCOVERY.md written" || { echo "✗ no DISCOVERY.md"; fail=1; }
(cd "$dir" && "$T/bin/brainstem-proto" stop >/dev/null)
"$T/bin/brainstem-proto" usage > "$T/usage.txt"
grep -qE "prototype_created +1" "$T/usage.txt" && grep -qE "check_passed +1" "$T/usage.txt" && echo "✓ usage counted (local only)" || { echo "✗ usage not counted"; cat "$T/usage.txt"; fail=1; }
grep -qiE "equipment|discovery-call|ops lead" "$PROTO_HOME/usage.jsonl" && { echo "✗ usage log contains content"; fail=1; } || echo "✓ usage log holds no content"
after="$(fp)"; [ "$before" = "$after" ] && echo "✓ kernel unchanged ($after)" || { echo "✗ KERNEL CHANGED: $before -> $after"; fail=1; }
exit $fail
