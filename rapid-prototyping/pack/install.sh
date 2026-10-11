#!/usr/bin/env bash
# Rapid prototyping expansion pack. Run right after the Brainstem one-liner.
# Installs beside the Brainstem (~/.brainstem-proto) and a `brainstem-proto` command. It never writes
# inside ~/.brainstem and installs nothing into the Brainstem's Python.
set -euo pipefail
SRC="${PACK_SOURCE:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)}"
PROTO_HOME="${PROTO_HOME:-$HOME/.brainstem-proto}"
BIN="${PROTO_BIN:-$HOME/.local/bin}"
[ -f "$HOME/.brainstem/src/rapp_brainstem/brainstem.py" ] && [ -x "$HOME/.brainstem/venv/bin/python" ] \
  || { echo "No Brainstem found. Run the Brainstem one-liner first, then this."; exit 1; }
if [ ! -d "$SRC/template" ]; then  # piped from curl: fetch only the pack's folder from the library repo
  command -v git >/dev/null || { echo "git is needed (the Brainstem one-liner installs it)."; exit 1; }
  tmp="$(mktemp -d)"
  git clone -q --depth 1 --filter=blob:none --sparse --branch "${PACK_BRANCH:-main}" \
    "${PACK_REPO:-https://github.com/microsoft/aibast-agents-library.git}" "$tmp/lib"
  git -C "$tmp/lib" sparse-checkout set "${PACK_PATH:-rapid-prototyping}" >/dev/null
  SRC="$tmp/lib/${PACK_PATH:-rapid-prototyping}"
  [ -d "$SRC/template" ] || { echo "Couldn't find the pack in that repository."; exit 1; }
fi
mkdir -p "$PROTO_HOME" "$BIN"
rm -rf "$PROTO_HOME/template"; cp -R "$SRC/template" "$PROTO_HOME/template"; rm -rf "$PROTO_HOME/template/out"
cp "$SRC/pack/bin/brainstem-proto" "$PROTO_HOME/brainstem-proto"; chmod +x "$PROTO_HOME/brainstem-proto"
cp "$SRC/pack/bridge.py" "$PROTO_HOME/bridge.py"; cp "$SRC/pack/templates.py" "$PROTO_HOME/templates.py"
mkdir -p "$PROTO_HOME/guide"; cp "$SRC/pack/guide/rapp-guide-live.html" "$PROTO_HOME/guide/rapp-guide-live.html"
ln -sf "$PROTO_HOME/brainstem-proto" "$BIN/brainstem-proto"
echo "Installed. Try:  brainstem-proto new \"an expense approval app for my team\""
case ":$PATH:" in *":$BIN:"*) ;; *) echo "(Add $BIN to your PATH, or run $BIN/brainstem-proto)";; esac
