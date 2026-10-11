#!/usr/bin/env bash
# "Is it working?" in plain words. Exit 0 only if the whole loop answers.
BRAINSTEM_HOME="${BRAINSTEM_HOME:-$HOME/.brainstem}"; PY="$BRAINSTEM_HOME/venv/bin/python"
BS_PORT="${BS_PORT:-7096}"; APP_PORT="${APP_PORT:-7097}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; ok=1
say() { printf '%s %s\n' "$1" "$2"; }
if (cd "$ROOT" && "$PY" -m unittest discover -s tests >/dev/null 2>&1); then say "✓" "The building blocks pass their tests."; else say "✗" "Some tests fail (run: $PY -m unittest discover -s tests)."; ok=0; fi
H=$(curl -s -m 3 "localhost:$BS_PORT/health") && say "✓" "Your prototype's Brainstem is running ($(echo "$H" | "$PY" -c 'import json,sys; print(", ".join(json.load(sys.stdin).get("agents",[])) or "no agents")'))." || { say "✗" "The prototype's Brainstem isn't running. Run scripts/start-local.sh."; ok=0; }
curl -s -m 3 "localhost:$APP_PORT/" | grep -q "<title>" && say "✓" "The app is up at http://localhost:$APP_PORT" || { say "✗" "The app isn't up. Run scripts/start-local.sh."; ok=0; }
if [ $ok = 1 ]; then
  R=$(curl -s -m 120 "localhost:$APP_PORT/api/chat" -H "Content-Type: application/json" -d '{"user_input":"Reply with exactly: pong. Do not call any tools."}')
  echo "$R" | grep -qi pong && say "✓" "It answers through the app, end to end." || { say "✗" "The app is up but the AI didn't answer. See out/brainstem.log."; ok=0; }
fi
[ $ok = 1 ] && echo "Your prototype is working." || echo "Not working yet. Ask your AI: \"scripts/check.sh fails, fix it\"."
[ $ok = 1 ]
