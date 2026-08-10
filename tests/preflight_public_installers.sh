#!/bin/bash
# End-to-end compatibility matrix for the public mainline and beta installers.
#
# Required for fork staging:
#   PUBLIC_BASE_URL=https://kody-w.github.io/aibast-agents-library \
#   BETA_REPO_URL=https://github.com/kody-w/aibast-agents-library.git \
#   BETA_REF=easy-mode-copilot-chat-pilot \
#   bash tests/preflight_public_installers.sh

set -euo pipefail

PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-https://microsoft.github.io/aibast-agents-library}"
BETA_REPO_URL="${BETA_REPO_URL:-https://github.com/microsoft/aibast-agents-library.git}"
BETA_REF="${BETA_REF:-main}"
if [ -n "${PUBLIC_PREFLIGHT_PORT:-}" ]; then
    PORT="$PUBLIC_PREFLIGHT_PORT"
else
    PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
fi
SANDBOX="$(mktemp -d /tmp/brainstem-public-preflight-XXXXXX)"
HOME_ONE="$SANDBOX/home-mainline-first"
HOME_TWO="$SANDBOX/home-beta-first"
MAIN_INSTALLER="$SANDBOX/install.sh"
BETA_INSTALLER="$SANDBOX/beta-install.sh"

mkdir -p "$HOME_ONE" "$HOME_TWO"

ACTIVE_PID=""
SHARED_PID=""

cleanup() {
    if [[ "$ACTIVE_PID" =~ ^[0-9]+$ ]] && kill -0 "$ACTIVE_PID" 2>/dev/null; then
        kill "$ACTIVE_PID" 2>/dev/null || true
        wait "$ACTIVE_PID" 2>/dev/null || true
    fi
    echo ""
    echo "Public installer sandbox kept at: $SANDBOX"
}
trap cleanup EXIT

curl -fsSL "$PUBLIC_BASE_URL/install.sh" -o "$MAIN_INSTALLER"
curl -fsSL "$PUBLIC_BASE_URL/beta/install.sh" -o "$BETA_INSTALLER"
bash -n "$MAIN_INSTALLER"
bash -n "$BETA_INSTALLER"

pass_count=0
pass() {
    pass_count=$((pass_count + 1))
    echo "  [OK] $1"
}

assert_sparse_global() {
    local home="$1"
    local source="$home/.brainstem/src"
    [ "$(git -C "$source" config --get remote.origin.partialclonefilter)" = "blob:none" ]
    [ "$(git -C "$source" config --bool core.sparseCheckout)" = "true" ]
    [ ! -e "$source/solutions" ]
    local kib
    kib=$(du -sk "$source" | awk '{print $1}')
    [ "$kib" -lt 25000 ]
    pass "global Brainstem checkout is sparse and ${kib} KiB"
}

assert_sparse_beta() {
    local home="$1"
    local source="$home/.brainstem/beta-launcher/src"
    [ "$(git -C "$source" config --get remote.origin.partialclonefilter)" = "blob:none" ]
    [ "$(git -C "$source" config --bool core.sparseCheckout)" = "true" ]
    [ ! -e "$source/solutions" ]
    [ -f "$source/beta/package.json" ]
    pass "beta source checkout is partial, sparse, and excludes solutions/"
}

install_mainline() {
    local home="$1"
    HOME="$home" bash "$MAIN_INSTALLER" --no-launch
    [ -x "$home/.local/bin/brainstem" ]
    assert_sparse_global "$home"
}

install_beta() {
    local home="$1"
    HOME="$home" \
    BRAINSTEM_BETA_REPO_URL="$BETA_REPO_URL" \
    BRAINSTEM_BETA_REF="$BETA_REF" \
    BRAINSTEM_BETA_NO_LAUNCH=1 \
        bash "$BETA_INSTALLER"
    [ -x "$home/.brainstem/beta-launcher/launch.sh" ]
    assert_sparse_global "$home"
    assert_sparse_beta "$home"
}

start_mainline() {
    local home="$1"
    local log="$2"
    HOME="$home" PORT="$PORT" "$home/.local/bin/brainstem" >"$log" 2>&1 &
    local pid=$!
    ACTIVE_PID="$pid"
    for _ in $(seq 1 120); do
        if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
            pass "mainline CLI launched the shared Brainstem"
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
            ACTIVE_PID=""
            return
        fi
        if ! kill -0 "$pid" 2>/dev/null; then break; fi
        sleep 1
    done
    tail -80 "$log" >&2 || true
    return 1
}

electron_binary() {
    local app_dir="$1"
    case "$(uname -s)" in
        Darwin) echo "$app_dir/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron" ;;
        Linux) echo "$app_dir/node_modules/electron/dist/electron" ;;
        *) return 1 ;;
    esac
}

start_beta_owned() {
    local home="$1"
    local log="$2"
    local app_dir="$home/.brainstem/beta-launcher/src/beta"
    local electron
    electron=$(electron_binary "$app_dir")
    [ -x "$electron" ]
    HOME="$home" \
    BRAINSTEM_HOME="$home/.brainstem" \
    BRAINSTEM_BETA_PORT="$PORT" \
    BRAINSTEM_BETA_HEADLESS=1 \
    BRAINSTEM_BETA_SMOKE_EXIT_MS=20000 \
        "$electron" "$app_dir" >"$log" 2>&1 &
    local pid=$!
    ACTIVE_PID="$pid"
    local healthy=false
    for _ in $(seq 1 20); do
        if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
            healthy=true
            break
        fi
        if ! kill -0 "$pid" 2>/dev/null; then break; fi
        sleep 1
    done
    [ "$healthy" = true ] || {
        tail -100 "$log" >&2 || true
        return 1
    }
    pass "beta desktop launcher started the same global Brainstem"
    wait "$pid"
    ACTIVE_PID=""
    for _ in $(seq 1 10); do
        if ! curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
            pass "beta launcher disposed the Brainstem process it owned"
            return
        fi
        sleep 1
    done
    return 1
}

start_mainline_shared() {
    local home="$1"
    local log="$2"
    HOME="$home" PORT="$PORT" "$home/.local/bin/brainstem" >"$log" 2>&1 &
    SHARED_PID=$!
    ACTIVE_PID="$SHARED_PID"
    for _ in $(seq 1 120); do
        if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
            pass "mainline started the shared process for beta reuse"
            return
        fi
        if ! kill -0 "$SHARED_PID" 2>/dev/null; then break; fi
        sleep 1
    done
    tail -80 "$log" >&2 || true
    return 1
}

start_beta_reusing() {
    local home="$1"
    local log="$2"
    local app_dir="$home/.brainstem/beta-launcher/src/beta"
    local electron
    electron=$(electron_binary "$app_dir")
    [ -x "$electron" ]
    HOME="$home" \
    BRAINSTEM_HOME="$home/.brainstem" \
    BRAINSTEM_BETA_PORT="$PORT" \
    BRAINSTEM_BETA_HEADLESS=1 \
    BRAINSTEM_BETA_SMOKE_EXIT_MS=10000 \
        "$electron" "$app_dir" >"$log" 2>&1 &
    local beta_pid=$!
    ACTIVE_PID="$beta_pid"
    wait "$beta_pid"
    ACTIVE_PID="$SHARED_PID"
    kill -0 "$SHARED_PID"
    curl -sf "http://127.0.0.1:$PORT/health" >/dev/null
    pass "beta reused and preserved the independently started Brainstem"
}

stop_shared() {
    if [[ "$SHARED_PID" =~ ^[0-9]+$ ]] && kill -0 "$SHARED_PID" 2>/dev/null; then
        kill "$SHARED_PID" 2>/dev/null || true
        wait "$SHARED_PID" 2>/dev/null || true
    fi
    SHARED_PID=""
    ACTIVE_PID=""
}

echo "=== mainline first ==="
install_mainline "$HOME_ONE"
start_mainline "$HOME_ONE" "$SANDBOX/mainline-first.log"
install_beta "$HOME_ONE"
start_beta_owned "$HOME_ONE" "$SANDBOX/beta-after-mainline.log"
start_mainline_shared "$HOME_ONE" "$SANDBOX/shared-for-beta.log"
start_beta_reusing "$HOME_ONE" "$SANDBOX/beta-reused-mainline.log"
stop_shared

echo ""
echo "=== mainline rerun after beta ==="
install_mainline "$HOME_ONE"
[ -x "$HOME_ONE/.brainstem/beta-launcher/launch.sh" ]
start_beta_owned "$HOME_ONE" "$SANDBOX/beta-after-mainline-rerun.log"
pass "mainline rerun preserved the beta launcher"

echo ""
echo "=== remove beta only ==="
rm -rf "$HOME_ONE/.brainstem/beta-launcher"
start_mainline "$HOME_ONE" "$SANDBOX/mainline-after-beta-removal.log"
pass "removing beta did not break mainline"

echo ""
echo "=== beta repairs a removed global runtime ==="
install_beta "$HOME_ONE"
rm -rf "$HOME_ONE/.brainstem/src" "$HOME_ONE/.brainstem/venv"
install_beta "$HOME_ONE"
start_beta_owned "$HOME_ONE" "$SANDBOX/beta-rebuilt-global.log"
pass "beta rebuilt the shared global runtime"

echo ""
echo "=== beta first on a clean home ==="
install_beta "$HOME_TWO"
start_beta_owned "$HOME_TWO" "$SANDBOX/beta-first.log"
install_mainline "$HOME_TWO"
start_mainline "$HOME_TWO" "$SANDBOX/mainline-after-beta-first.log"
pass "beta-first and mainline-second remain compatible"

echo ""
echo "=== public installer matrix: $pass_count checks passed ==="
