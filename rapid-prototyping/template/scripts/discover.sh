#!/usr/bin/env bash
# RAPP Step 2: discovery transcript -> DISCOVERY.md, through this prototype's Brainstem.
#   scripts/discover.sh discovery/call.txt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; APP_PORT="${APP_PORT:-7097}"
f="${1:?usage: scripts/discover.sh discovery/<transcript>}"; name="$(basename "$f")"
[ -f "$ROOT/discovery/$name" ] || cp "$f" "$ROOT/discovery/$name"
curl -s -m 400 "localhost:$APP_PORT/api/chat" -H "Content-Type: application/json" \
  -d "{\"user_input\":\"Use the Discovery agent with transcript $name. Then just say done.\"}" > "$ROOT/out/discover.json"
grep -q '\[Discovery\] {\\"ok\\": true\|\[Discovery\] {"ok": true' "$ROOT/out/discover.json" && echo "✓ Wrote DISCOVERY.md. Read it, fix anything wrong, then tell your AI to build the MVP poke." \
  || { echo "✗ Discovery didn't finish. See out/discover.json"; exit 1; }
