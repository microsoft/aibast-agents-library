#!/usr/bin/env bash
# Rapid prototyping on the Brainstem the one-liner installed. Nothing else to install.
#   Dedicated Brainstem (unchanged kernel, ONLY this project's agents)  http://localhost:7096
#   App + /api sidecar                                                   http://localhost:7097
# The Brainstem you use every day (7071) is not touched.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BRAINSTEM_HOME="${BRAINSTEM_HOME:-$HOME/.brainstem}"
KERNEL="$BRAINSTEM_HOME/src/rapp_brainstem/brainstem.py"
PY="$BRAINSTEM_HOME/venv/bin/python"
BS_PORT="${BS_PORT:-7096}"; APP_PORT="${APP_PORT:-7097}"
[ -f "$KERNEL" ] && [ -x "$PY" ] || { echo "No Brainstem found at $BRAINSTEM_HOME. Run the Brainstem one-liner first."; exit 1; }
mkdir -p "$ROOT/out"

if ! curl -s -m 2 "localhost:$BS_PORT/health" >/dev/null; then
  PORT="$BS_PORT" AGENTS_PATH="$ROOT/brainstem/agents" PM_BRAINSTEM_URL="http://localhost:$BS_PORT" \
    nohup "$PY" "$KERNEL" > "$ROOT/out/brainstem.log" 2>&1 < /dev/null &
  for _ in $(seq 1 40); do curl -s -m 2 "localhost:$BS_PORT/health" >/dev/null && break; sleep 1; done
fi
curl -s -m 3 "localhost:$BS_PORT/health" | grep -q '"agents"' || { echo "Brainstem did not start; see out/brainstem.log"; exit 1; }

if ! curl -s -m 2 "localhost:$APP_PORT/api/health" >/dev/null; then
  (cd "$ROOT" || exit 1; PM_BRAINSTEM_URL="http://localhost:$BS_PORT" nohup "$PY" -m app.server --port "$APP_PORT" > "$ROOT/out/app.log" 2>&1 < /dev/null &) < /dev/null > /dev/null 2>&1
  for _ in $(seq 1 10); do curl -s -m 2 "localhost:$APP_PORT/api/health" >/dev/null && break; sleep 1; done
fi
echo "App: http://localhost:$APP_PORT"
echo "Brainstem: $(curl -s "localhost:$BS_PORT/health" | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print("model", d.get("model"), "agents", d.get("agents"))')"
[ "${1:-}" = "--no-open" ] || { command -v open >/dev/null && open "http://localhost:$APP_PORT" || xdg-open "http://localhost:$APP_PORT" 2>/dev/null || true; }
