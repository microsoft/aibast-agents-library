#!/usr/bin/env bash
# Stops only what start-local.sh started: the listeners on the prototype ports whose command is ours.
for port in "${BS_PORT:-7096}" "${APP_PORT:-7097}"; do
  for pid in $(lsof -nP -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null); do
    if ps -o args= -p "$pid" | grep -qE "brainstem.py|app.server"; then kill "$pid" && echo "stopped $port ($pid)"; fi
  done
done
