#!/usr/bin/env bash
# git-molt acceptance tests. Drives the real CLI against a real Git repository.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
GIT_MOLT="$HERE/../bin/git-molt"
WORK="$(mktemp -d)"
export GIT_MOLT_DIR="$WORK/lineage.git"
trap 'rm -rf "$WORK"' EXIT

pass=0; fail=0
ok()   { if [ "$2" = "0" ] || [ "$2" = "true" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$1";
         else fail=$((fail+1)); printf '  FAIL %s\n' "$1"; fi }
eq()   { if [ "$2" = "$3" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$1";
         else fail=$((fail+1)); printf '  FAIL %s\n    expected: %s\n    actual:   %s\n' "$1" "$3" "$2"; fi }
ne()   { if [ "$2" != "$3" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$1";
         else fail=$((fail+1)); printf '  FAIL %s (values are equal: %s)\n' "$1" "$2"; fi }

molt() { "$GIT_MOLT" "$@"; }

printf '\n# repository\n'
molt init >/dev/null
ok "init creates a molt repository" "$([ -d "$GIT_MOLT_DIR" ] && echo 0 || echo 1)"
git --git-dir="$GIT_MOLT_DIR" rev-parse --is-bare-repository >/dev/null 2>&1
ok "it is an ordinary git repository" "$?"

printf '\n# baseline\n'
cat > "$WORK/memory.py" <<'PY'
class MemoryAgent:
    def perform(self): return "baseline"
PY
LOCUS="$(molt baseline memory "$WORK/memory.py")"
ok "baseline records ring 0" "$([ -n "$LOCUS" ] && echo 0 || echo 1)"

# Determinism: the same baseline bytes must yield the same locus id and the
# same root commit on a completely separate instance.
OTHER="$WORK/other.git"
BASE1="$(git --git-dir="$GIT_MOLT_DIR" rev-parse "refs/molt/base/$LOCUS")"
GIT_MOLT_DIR="$OTHER" molt init >/dev/null
LOCUS2="$(GIT_MOLT_DIR="$OTHER" molt baseline memory "$WORK/memory.py")"
BASE2="$(git --git-dir="$OTHER" rev-parse "refs/molt/base/$LOCUS2")"
eq "same bytes -> same locus id on an unrelated instance" "$LOCUS2" "$LOCUS"
eq "same bytes -> same baseline commit id (shared identity)" "$BASE2" "$BASE1"

printf '\n# recording and the gate\n'
cat > "$WORK/memory2.py" <<'PY'
class MemoryAgent:
    def perform(self): return "molted"
PY
RING="$(molt record "$LOCUS" "$WORK/memory2.py")"
ok "record appends a generation" "$([ -n "$RING" ] && echo 0 || echo 1)"
ne "the generation is not the baseline" "$RING" "$BASE1"

molt activate "$LOCUS" "$RING" >/dev/null 2>&1
ok "activating an UNVERIFIED generation is refused" "$([ $? -ne 0 ] && echo 0 || echo 1)"

VRING="$(molt verify "$LOCUS" "$RING")"
ok "verify records a verdict" "$([ -n "$VRING" ] && echo 0 || echo 1)"
eq "the verdict lives in the commit (trailer)" \
   "$(git --git-dir="$GIT_MOLT_DIR" show -s --format=%B "$VRING" | sed -n 's/^Molt-Verified: //p')" "yes"
ne "recording a verdict changes the ring id (tamper-evident)" "$VRING" "$RING"

molt activate "$LOCUS" "$VRING" >/dev/null
eq "a verified generation activates" \
   "$(git --git-dir="$GIT_MOLT_DIR" rev-parse "refs/molt/live/$LOCUS")" "$VRING"
eq "the live agent is the molted source" "$(molt show "$LOCUS" | tail -1 | tr -d '[:space:]')" \
   "$(printf 'def perform(self): return "molted"' | tr -d '[:space:]')"

printf '\n# a hostile gate refuses\n'
cat > "$WORK/reject.sh" <<'SH'
#!/usr/bin/env bash
exit 1
SH
chmod +x "$WORK/reject.sh"
cat > "$WORK/memory3.py" <<'PY'
BROKEN = True
PY
R3="$(molt record "$LOCUS" "$WORK/memory3.py")"
GIT_MOLT_VERIFIER="$WORK/reject.sh" molt verify "$LOCUS" "$R3" >/dev/null 2>&1
ok "the gate's refusal is final" "$([ $? -ne 0 ] && echo 0 || echo 1)"

printf '\n# time travel\n'
molt revert "$LOCUS" >/dev/null
eq "revert returns the locus to baseline" \
   "$(git --git-dir="$GIT_MOLT_DIR" rev-parse "refs/molt/live/$LOCUS")" "$BASE1"
eq "the live agent is pristine again" "$(molt show "$LOCUS" | tail -1 | tr -d '[:space:]')" \
   "$(printf 'def perform(self): return "baseline"' | tr -d '[:space:]')"
eq "history was NOT destroyed by reverting" \
   "$(git --git-dir="$GIT_MOLT_DIR" rev-list --count "refs/molt/loci/$LOCUS")" "3"
molt restore "$LOCUS" >/dev/null
eq "restore re-activates the newest verified generation" \
   "$(git --git-dir="$GIT_MOLT_DIR" rev-parse "refs/molt/live/$LOCUS")" "$VRING"

printf '\n# policy\n'
eq "loci default to mutable" "$(molt policy "$LOCUS")" "mutable"
molt policy "$LOCUS" pinned >/dev/null
eq "pinning takes effect immediately" \
   "$(git --git-dir="$GIT_MOLT_DIR" rev-parse "refs/molt/live/$LOCUS")" "$BASE1"
molt activate "$LOCUS" "$VRING" >/dev/null 2>&1
ok "a pinned locus refuses to molt" "$([ $? -ne 0 ] && echo 0 || echo 1)"
molt restore "$LOCUS" >/dev/null
eq "a fleet restore honors the pin" \
   "$(git --git-dir="$GIT_MOLT_DIR" rev-parse "refs/molt/live/$LOCUS")" "$BASE1"
molt policy "$LOCUS" mutable >/dev/null

printf '\n# composition\n'
cat > "$WORK/news.py" <<'PY'
class NewsAgent:
    def perform(self): return "news"
PY
NEWS="$(molt baseline news "$WORK/news.py")"
molt compose "$WORK/agents" >/dev/null
ok "compose materializes a plain directory" "$([ -d "$WORK/agents" ] && echo 0 || echo 1)"
ok "every locus is present" "$([ -f "$WORK/agents/memory.py" ] && [ -f "$WORK/agents/news.py" ] && echo 0 || echo 1)"
# Zero-adaptation identity: with all loci at baseline the output is the input.
molt revert >/dev/null
molt compose "$WORK/agents2" >/dev/null
eq "with no molts the composed source is byte-identical to the baseline" \
   "$(cat "$WORK/agents2/memory.py")" "$(tr -d '\r' < "$WORK/memory.py")"

printf '\n# fail-safe composition\n'
molt activate "$LOCUS" "$VRING" >/dev/null
# Point live at a generation that was never verified.
git --git-dir="$GIT_MOLT_DIR" update-ref "refs/molt/live/$LOCUS" "$R3"
molt compose "$WORK/agents3" >/dev/null
eq "an unverified live ring falls back to baseline, never fails" \
   "$(cat "$WORK/agents3/memory.py")" "$(tr -d '\r' < "$WORK/memory.py")"

printf '\n# interchange\n'
molt activate "$LOCUS" "$VRING" >/dev/null 2>&1 || true
molt frame export "$LOCUS" "$WORK/memory.frame" >/dev/null
ok "frame export writes a git bundle" "$([ -f "$WORK/memory.frame" ] && echo 0 || echo 1)"
git bundle verify "$WORK/memory.frame" >/dev/null 2>&1
ok "the frame is a valid git bundle (git verifies it, not us)" "$?"
RECV="$WORK/recv.git"
GIT_MOLT_DIR="$RECV" molt init >/dev/null
GIT_MOLT_DIR="$RECV" molt frame import "$WORK/memory.frame" >/dev/null
eq "the receiver derives the same baseline id" \
   "$(git --git-dir="$RECV" rev-parse "refs/molt/base/$LOCUS")" "$BASE1"
eq "an imported generation is NOT active (trust does not transfer)" \
   "$(git --git-dir="$RECV" rev-parse "refs/molt/live/$LOCUS" 2>/dev/null || echo none)" "$BASE1"

printf '\n# git compatibility\n'
git --git-dir="$GIT_MOLT_DIR" log --oneline "refs/molt/loci/$LOCUS" >/dev/null 2>&1
ok "git log reads a lineage" "$?"
git --git-dir="$GIT_MOLT_DIR" diff "$BASE1" "$VRING" >/dev/null 2>&1
ok "git diff compares two generations" "$?"
git --git-dir="$GIT_MOLT_DIR" fsck --no-progress >/dev/null 2>&1
ok "git fsck reports a healthy object store" "$?"

printf '\n==== %d passed, %d failed ====\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
