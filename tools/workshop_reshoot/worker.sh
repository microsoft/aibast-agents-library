#!/bin/bash
# worker.sh <queue file>: take "<slug> <manual|assisted>" tasks from the queue (atomic mkdir locks), run them, and when a
# solution has both run records, write its evidence, retake flagged frames, and write the evidence again.
# Run several workers on the same queue to go in parallel. Logs: ~/.cache/aibast-reshoot/out/<slug>/<mode>.log
D=$(cd "$(dirname "$0")"; pwd); WT=$(cd "$D/../.."; pwd)
C=${RESHOOT_CACHE:-$HOME/.cache/aibast-reshoot}; PW=${RESHOOT_PLAYWRIGHT_PY:-$C/venv/bin/python}
mkdir -p "$C/locks"
while read -r slug mode; do
  [ -n "$slug" ] || continue
  mkdir "$C/locks/$slug-$mode" 2>/dev/null || continue
  mkdir -p "$C/out/$slug"
  echo "=== $slug $mode $(date +%H:%M)"
  if [ "$mode" != finish ]; then
    (cd "$D" && "$PW" "$mode.py" "$WT" "$slug" > "$C/out/$slug/$mode.log" 2>&1)
    echo "    $mode exit $? $(grep '\[done\]' "$C/out/$slug/$mode.log" | tail -1)"
  fi
  touch "$C/locks/$slug-$mode/done"
  if [ -f "$C/out/$slug/manual.json" ] && [ -f "$C/out/$slug/assisted.json" ] && mkdir "$C/locks/$slug-evidence" 2>/dev/null; then
    (cd "$D" && { "$PW" evidence.py "$WT" "$slug"; "$PW" retake.py "$WT" "$slug"; "$PW" evidence.py "$WT" "$slug"; } > "$C/out/$slug/evidence.log" 2>&1)
    echo "    evidence: $(grep '\[evidence\]' "$C/out/$slug/evidence.log" | tail -1 | sed 's/.*{/{/')"
  fi
done < "$1"
echo "WORKER DONE"
