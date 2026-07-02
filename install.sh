#!/bin/bash
set -e

# RAPP Brainstem Installer
# Usage: curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash
# Pin a version: curl ... install.sh | bash -s -- --version v0.6.0

BRAINSTEM_HOME="$HOME/.brainstem"
BRAINSTEM_BIN="$HOME/.local/bin"
VENV_DIR="$BRAINSTEM_HOME/venv"
REPO_URL="https://github.com/microsoft/aibast-agents-library.git"
REMOTE_VERSION_URL="https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/rapp_brainstem/VERSION"
PIN_VERSION=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

read_input() {
    local prompt="$1" default="$2" result
    if [ -t 0 ]; then
        read -p "$prompt" result
    else
        read -p "$prompt" result < /dev/tty
    fi
    echo "${result:-$default}"
}

print_banner() {
    echo ""
    echo -e "${CYAN}"
    echo "  🧠 RAPP Brainstem"
    echo -e "${NC}"
    echo "  Local-first AI agent server"
    echo "  Powered by GitHub Copilot — no API keys needed"
    echo ""
}

detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then echo "linux"
    else echo "unknown"
    fi
}

# Ensure Homebrew is on PATH — curl|bash sessions don't source shell profiles
ensure_brew_on_path() {
    if command -v brew &> /dev/null; then return 0; fi
    if [[ -x "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -x "/usr/local/bin/brew" ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
}

find_python() {
    for cmd in python3.11 python3.12 python3.13 python3; do
        if command -v "$cmd" &> /dev/null; then
            version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null) || continue
            major=$(echo "$version" | cut -d. -f1)
            minor=$(echo "$version" | cut -d. -f2)
            if [[ -n "$major" && -n "$minor" ]] && [ "$major" -ge 3 ] 2>/dev/null && [ "$minor" -ge 11 ] 2>/dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    if [[ "$(detect_os)" == "macos" ]]; then
        for p in /opt/homebrew/bin/python3.11 /usr/local/bin/python3.11 /opt/homebrew/bin/python3.12 /usr/local/bin/python3.12; do
            if [[ -x "$p" ]]; then echo "$p"; return 0; fi
        done
    fi
    return 1
}

install_python() {
    local os_type=$(detect_os)
    echo -e "  ${YELLOW}Installing Python 3.11...${NC}"
    if [[ "$os_type" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            echo -e "  ${YELLOW}Installing Homebrew first...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            if [[ -f "/opt/homebrew/bin/brew" ]]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
        fi
        brew install python@3.11
        export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
    elif [[ "$os_type" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3.11 python3.11-venv python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3.11 python3-pip
        else
            echo -e "  ${RED}✗${NC} Cannot auto-install Python 3.11 on this system"
            echo "    Install manually from https://python.org"
            exit 1
        fi
    fi
}

# Compare two semver strings. Returns 0 if $1 > $2, 1 otherwise.
version_gt() {
    local IFS=.
    local i a=($1) b=($2)
    for ((i=0; i<${#a[@]}; i++)); do
        local va=${a[i]:-0}
        local vb=${b[i]:-0}
        if (( va > vb )); then return 0; fi
        if (( va < vb )); then return 1; fi
    done
    return 1  # equal
}

check_for_upgrade() {
    local version_file="$BRAINSTEM_HOME/src/rapp_brainstem/VERSION"

    # No existing install — always proceed
    if [ ! -f "$version_file" ]; then
        return 0
    fi

    local local_version
    local_version=$(cat "$version_file" 2>/dev/null | tr -d '[:space:]')

    # Fetch remote version
    local remote_version
    remote_version=$(curl -fsSL "$REMOTE_VERSION_URL" 2>/dev/null | tr -d '[:space:]') || true

    if [[ -z "$remote_version" ]]; then
        echo -e "  ${YELLOW}⚠${NC} Could not check remote version — upgrading anyway"
        return 0
    fi

    echo -e "  Local version:  ${CYAN}${local_version}${NC}"
    echo -e "  Remote version: ${CYAN}${remote_version}${NC}"

    if [[ "$local_version" == "$remote_version" ]]; then
        echo ""
        echo -e "  ${GREEN}✓ Already up to date (v${local_version})${NC}"
        echo ""
        return 1  # no upgrade needed
    fi

    if version_gt "$remote_version" "$local_version"; then
        echo -e "  ${YELLOW}⬆${NC} Upgrade available: ${local_version} → ${remote_version}"
        return 0
    fi

    echo -e "  ${GREEN}✓ Already up to date (v${local_version})${NC}"
    echo ""
    return 1
}

check_prereqs() {
    echo "Checking prerequisites..."

    # On macOS, ensure Homebrew is on PATH (curl|bash doesn't source shell profiles)
    if [[ "$(detect_os)" == "macos" ]]; then
        ensure_brew_on_path
    fi

    # Python 3.11+
    PYTHON_CMD=$(find_python) || true
    if [[ -n "$PYTHON_CMD" ]]; then
        version=$("$PYTHON_CMD" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        echo -e "  ${GREEN}✓${NC} Python $version ($PYTHON_CMD)"
    else
        echo -e "  ${YELLOW}⚠${NC} Python 3.11+ not found"
        install_python
        PYTHON_CMD=$(find_python) || true
        if [[ -z "$PYTHON_CMD" ]]; then
            echo -e "  ${RED}✗${NC} Failed to install Python 3.11"
            exit 1
        fi
        version=$("$PYTHON_CMD" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        echo -e "  ${GREEN}✓${NC} Python $version installed"
    fi
    export PYTHON_CMD

    # Git
    if command -v git &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Git $(git --version | cut -d' ' -f3)"
    else
        echo -e "  ${YELLOW}⚠${NC} Git not found, installing..."
        if [[ "$(detect_os)" == "macos" ]]; then
            xcode-select --install 2>/dev/null || brew install git
        elif command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y git
        else
            echo -e "  ${RED}✗${NC} Git required — install from https://git-scm.com"
            exit 1
        fi
    fi

    # GitHub CLI (required for Copilot token auth)
    if command -v gh &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} GitHub CLI $(gh --version | head -1 | awk '{print $3}')"
    else
        echo -e "  ${YELLOW}⚠${NC} GitHub CLI not found, installing..."
        local os_type=$(detect_os)
        if [[ "$os_type" == "macos" ]]; then
            if command -v brew &> /dev/null; then
                brew install gh
            else
                echo -e "  ${YELLOW}⚠${NC} Installing Homebrew first..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                ensure_brew_on_path
                brew install gh
            fi
        elif [[ "$os_type" == "linux" ]]; then
            if command -v apt-get &> /dev/null; then
                (type -p wget >/dev/null || sudo apt-get install -y wget) \
                    && sudo mkdir -p -m 755 /etc/apt/keyrings \
                    && out=$(mktemp) && wget -nv -O"$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg \
                    && cat "$out" | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
                    && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
                    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
                    && sudo apt-get update && sudo apt-get install -y gh
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y 'dnf-command(config-manager)' \
                    && sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo \
                    && sudo dnf install -y gh
            else
                echo -e "  ${YELLOW}⚠${NC} Cannot auto-install GitHub CLI — install from https://cli.github.com"
            fi
        fi
        if command -v gh &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} GitHub CLI installed"
        else
            echo -e "  ${YELLOW}!${NC} GitHub CLI not installed — install later from https://cli.github.com"
        fi
    fi
}

install_brainstem() {
    echo ""
    echo "Installing RAPP Brainstem..."
    mkdir -p "$BRAINSTEM_HOME"

    local AGENTS_DIR="$BRAINSTEM_HOME/src/rapp_brainstem/agents"
    local SOUL_FILE="$BRAINSTEM_HOME/src/rapp_brainstem/soul.md"
    local ENV_FILE="$BRAINSTEM_HOME/src/rapp_brainstem/.env"
    local LOCAL_VERSION_FILE="$BRAINSTEM_HOME/src/rapp_brainstem/VERSION"

    if [ -d "$BRAINSTEM_HOME/src/.git" ]; then
        # ── SMART UPDATE: preserve local files, upgrade framework ──
        local LOCAL_VER="0.0.0"
        [ -f "$LOCAL_VERSION_FILE" ] && LOCAL_VER=$(cat "$LOCAL_VERSION_FILE" 2>/dev/null || echo "0.0.0")

        local TARGET_VER
        if [ -n "$PIN_VERSION" ]; then
            # Strip leading 'v' for comparison (v0.6.0 → 0.6.0)
            TARGET_VER="${PIN_VERSION#v}"
        else
            TARGET_VER=$(curl -sf "$REMOTE_VERSION_URL" 2>/dev/null || echo "0.0.0")
        fi

        echo "  Local:  v${LOCAL_VER}"
        echo "  Target: v${TARGET_VER}${PIN_VERSION:+ (pinned)}"

        if [ "$LOCAL_VER" = "$TARGET_VER" ]; then
            echo -e "  ${GREEN}✓${NC} Already on v${LOCAL_VER}"
        else
            echo "  Switching v${LOCAL_VER} → v${TARGET_VER}..."

            # 1. Backup user's local files (soul, custom agents, .env)
            local BACKUP="/tmp/brainstem-upgrade-$$"
            mkdir -p "$BACKUP"
            [ -f "$SOUL_FILE" ] && cp "$SOUL_FILE" "$BACKUP/soul.md"
            [ -f "$ENV_FILE" ] && cp "$ENV_FILE" "$BACKUP/.env"
            if [ -d "$AGENTS_DIR" ]; then
                mkdir -p "$BACKUP/agents"
                # Backup ALL agents — user-created ones will be restored
                cp "$AGENTS_DIR"/*.py "$BACKUP/agents/" 2>/dev/null || true
            fi
            echo -e "  ${GREEN}✓${NC} Backed up soul, agents, config"

            # 2. Fetch and checkout target version.
            # Guard the fetch: offline (or a black-holed github) must not abort the
            # whole script under `set -e` — we fall back to whatever is already local.
            cd "$BRAINSTEM_HOME/src"
            git stash --quiet 2>/dev/null || true
            git fetch origin --tags --quiet 2>/dev/null || true
            if [ -n "$PIN_VERSION" ]; then
                # Resolve the pin against every tag form we ship: the documented
                # v0.6.0 UX, a bare 0.6.0, and the actual release tag brainstem-v0.6.0.
                TAG_REF=""
                for cand in "$PIN_VERSION" "v${PIN_VERSION#v}" "brainstem-${PIN_VERSION#v}" "brainstem-v${PIN_VERSION#v}"; do
                    if git rev-parse "$cand" >/dev/null 2>&1; then TAG_REF="$cand"; break; fi
                done
                if [ -n "$TAG_REF" ]; then
                    git checkout "$TAG_REF" --quiet 2>/dev/null
                    echo -e "  ${GREEN}✓${NC} Checked out ${TAG_REF}"
                else
                    echo -e "  ${RED}✗${NC} Version ${PIN_VERSION} not found. Available versions:"
                    git tag -l 'brainstem-v*' 'v*' | sort -V | sed 's/^/    /'
                    exit 1
                fi
            else
                git pull --quiet 2>/dev/null || git reset --hard origin/main --quiet 2>/dev/null || echo -e "  ${YELLOW}Warning: Could not update${NC}"
                echo -e "  ${GREEN}✓${NC} Framework updated"
            fi

            # 3. Restore user's local files (merge, don't overwrite)
            [ -f "$BACKUP/soul.md" ] && cp "$BACKUP/soul.md" "$SOUL_FILE"
            [ -f "$BACKUP/.env" ] && cp "$BACKUP/.env" "$ENV_FILE"
            if [ -d "$BACKUP/agents" ]; then
                # Restore user agents that aren't in the repo (custom ones)
                for agent_file in "$BACKUP/agents"/*.py; do
                    local fname=$(basename "$agent_file")
                    # Skip core agents that the repo manages
                    case "$fname" in
                        basic_agent.py|__init__.py) continue ;;
                    esac
                    # If user has a custom agent, keep it
                    cp "$agent_file" "$AGENTS_DIR/$fname"
                done
                echo -e "  ${GREEN}✓${NC} Restored custom agents + soul + config"
            fi

            # 4. Clean up backup
            rm -rf "$BACKUP"
            echo -e "  ${GREEN}✓${NC} ${PIN_VERSION:+Pinned to}${PIN_VERSION:-Upgrade complete:} v${TARGET_VER}"
        fi
    else
        echo "  Fresh install — cloning repository..."
        # A broken prior install (src present but .git gone) may still hold the user's
        # soul, .env, and custom agents — none of which are in git. Preserve them
        # before wiping so a re-run can't silently destroy the user's work. The common
        # case (no existing src) leaves FRESH_BACKUP empty and skips all of this.
        local FRESH_BACKUP=""
        if [ -d "$BRAINSTEM_HOME/src/rapp_brainstem" ]; then
            FRESH_BACKUP=$(mktemp -d "${TMPDIR:-/tmp}/brainstem-fresh-XXXXXX")
            mkdir -p "$FRESH_BACKUP/agents"
            [ -f "$SOUL_FILE" ] && cp "$SOUL_FILE" "$FRESH_BACKUP/soul.md" 2>/dev/null || true
            [ -f "$ENV_FILE" ] && cp "$ENV_FILE" "$FRESH_BACKUP/.env" 2>/dev/null || true
            [ -d "$AGENTS_DIR" ] && cp "$AGENTS_DIR"/*.py "$FRESH_BACKUP/agents/" 2>/dev/null || true
        fi
        rm -rf "$BRAINSTEM_HOME/src" 2>/dev/null || true
        git clone --quiet "$REPO_URL" "$BRAINSTEM_HOME/src"
        # If pinning, checkout the specific tag after clone (accepts every tag form).
        if [ -n "$PIN_VERSION" ]; then
            cd "$BRAINSTEM_HOME/src"
            git fetch origin --tags --quiet 2>/dev/null || true
            TAG_REF=""
            for cand in "$PIN_VERSION" "v${PIN_VERSION#v}" "brainstem-${PIN_VERSION#v}" "brainstem-v${PIN_VERSION#v}"; do
                if git rev-parse "$cand" >/dev/null 2>&1; then TAG_REF="$cand"; break; fi
            done
            if [ -n "$TAG_REF" ]; then
                git checkout "$TAG_REF" --quiet 2>/dev/null
                echo -e "  ${GREEN}✓${NC} Checked out ${TAG_REF}"
            else
                echo -e "  ${RED}✗${NC} Version ${PIN_VERSION} not found. Available versions:"
                git tag -l 'brainstem-v*' 'v*' | sort -V | sed 's/^/    /'
                exit 1
            fi
        fi
        # Restore any preserved user files over the fresh checkout.
        if [ -n "$FRESH_BACKUP" ]; then
            [ -f "$FRESH_BACKUP/soul.md" ] && cp "$FRESH_BACKUP/soul.md" "$SOUL_FILE" 2>/dev/null || true
            [ -f "$FRESH_BACKUP/.env" ] && cp "$FRESH_BACKUP/.env" "$ENV_FILE" 2>/dev/null || true
            for af in "$FRESH_BACKUP/agents"/*.py; do
                [ -f "$af" ] || continue
                fn=$(basename "$af")
                case "$fn" in basic_agent.py|__init__.py) continue ;; esac
                cp "$af" "$AGENTS_DIR/$fn" 2>/dev/null || true
            done
            rm -rf "$FRESH_BACKUP"
            echo -e "  ${GREEN}✓${NC} Preserved your soul, agents, and config"
        fi
    fi
    echo -e "  ${GREEN}✓${NC} Source code ready"
}

setup_venv() {
    local venv_python="$VENV_DIR/bin/python"

    # Check if venv exists and is healthy
    if [ -x "$venv_python" ]; then
        if "$venv_python" -c "import sys; sys.exit(0)" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Virtual environment OK"
            return 0
        fi
        echo -e "  ${YELLOW}⚠${NC} Virtual environment broken — recreating..."
        rm -rf "$VENV_DIR"
    fi

    echo "  Creating virtual environment..."
    "$PYTHON_CMD" -m venv "$VENV_DIR" 2>/dev/null || {
        # Some systems need ensurepip first
        "$PYTHON_CMD" -m ensurepip 2>/dev/null || true
        "$PYTHON_CMD" -m venv "$VENV_DIR" || {
            echo -e "  ${RED}✗${NC} Failed to create virtual environment"
            echo "    Try: $PYTHON_CMD -m pip install virtualenv"
            exit 1
        }
    }
    # Ensure pip is up to date inside the venv
    "$VENV_DIR/bin/python" -m pip install --upgrade pip --quiet 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Virtual environment ready"
}

setup_deps() {
    echo ""
    echo "Installing dependencies..."
    local req_file="$BRAINSTEM_HOME/src/rapp_brainstem/requirements.txt"
    "$VENV_DIR/bin/pip" install -r "$req_file" --quiet 2>/dev/null || \
        "$VENV_DIR/bin/pip" install -r "$req_file"

    # Verify the critical imports actually work
    if ! "$VENV_DIR/bin/python" -c "import flask, flask_cors, requests, dotenv" 2>/dev/null; then
        echo -e "  ${RED}✗${NC} Dependencies failed to install"
        echo "    Try: $VENV_DIR/bin/pip install -r $req_file"
        exit 1
    fi
    echo -e "  ${GREEN}✓${NC} Dependencies installed"
}

ensure_deps() {
    # Quick import check — only install if something is missing
    if "$VENV_DIR/bin/python" -c "import flask, flask_cors, requests, dotenv" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Dependencies verified"
        return 0
    fi

    echo -e "  ${YELLOW}⚠${NC} Missing dependencies — installing..."
    local req_file="$BRAINSTEM_HOME/src/rapp_brainstem/requirements.txt"
    "$VENV_DIR/bin/pip" install -r "$req_file" --quiet 2>/dev/null || \
        "$VENV_DIR/bin/pip" install -r "$req_file"

    if ! "$VENV_DIR/bin/python" -c "import flask, flask_cors, requests, dotenv" 2>/dev/null; then
        echo -e "  ${RED}✗${NC} Dependencies failed — try: $VENV_DIR/bin/pip install -r $req_file"
        exit 1
    fi
    echo -e "  ${GREEN}✓${NC} Dependencies installed"
}

install_cli() {
    echo ""
    echo "Installing CLI..."
    mkdir -p "$BRAINSTEM_BIN"

    cat > "$BRAINSTEM_BIN/brainstem" << 'WRAPPER'
#!/bin/bash
BRAINSTEM_HOME="$HOME/.brainstem"
VENV_PYTHON="$BRAINSTEM_HOME/venv/bin/python"
cd "$BRAINSTEM_HOME/src/rapp_brainstem"

# Use venv Python; fall back to creating venv if missing
if [ ! -x "$VENV_PYTHON" ]; then
    echo "  Setting up environment..."
    PYTHON_CMD=$(command -v python3.11 || command -v python3.12 || command -v python3.13 || command -v python3)
    "$PYTHON_CMD" -m venv "$BRAINSTEM_HOME/venv" 2>/dev/null
    "$BRAINSTEM_HOME/venv/bin/pip" install -r requirements.txt --quiet 2>/dev/null || \
        "$BRAINSTEM_HOME/venv/bin/pip" install -r requirements.txt
    VENV_PYTHON="$BRAINSTEM_HOME/venv/bin/python"
fi

# Verify deps on every launch (fast no-op if already installed)
if ! "$VENV_PYTHON" -c "import flask, flask_cors, requests, dotenv" 2>/dev/null; then
    "$BRAINSTEM_HOME/venv/bin/pip" install -r requirements.txt --quiet 2>/dev/null || true
fi

exec "$VENV_PYTHON" brainstem.py "$@"
WRAPPER

    chmod +x "$BRAINSTEM_BIN/brainstem"

    add_to_path() {
        local file="$1"
        # Create shell config if it doesn't exist (common on fresh macOS)
        touch "$file"
        if ! grep -q '\.local/bin' "$file" 2>/dev/null; then
            echo '' >> "$file"
            echo '# RAPP Brainstem' >> "$file"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$file"
        fi
    }
    add_to_path "$HOME/.bashrc"
    add_to_path "$HOME/.zshrc"
    add_to_path "$HOME/.bash_profile"

    echo -e "  ${GREEN}✓${NC} CLI installed to $BRAINSTEM_BIN/brainstem"
}

create_env() {
    local env_file="$BRAINSTEM_HOME/src/rapp_brainstem/.env"
    if [ ! -f "$env_file" ]; then
        cp "$BRAINSTEM_HOME/src/rapp_brainstem/.env.example" "$env_file" 2>/dev/null || true
    fi
}

launch_brainstem() {
    export PATH="$BRAINSTEM_BIN:/opt/homebrew/bin:/usr/local/bin:$PATH"

    # Always pull latest code before launching
    if [ -d "$BRAINSTEM_HOME/src/.git" ]; then
        cd "$BRAINSTEM_HOME/src"
        git pull --quiet 2>/dev/null || true
    fi

    local venv_python="$VENV_DIR/bin/python"

    # Ensure venv exists (handles edge case where only launch is called)
    if [ ! -x "$venv_python" ]; then
        if [[ -z "$PYTHON_CMD" ]]; then
            PYTHON_CMD=$(find_python) || true
        fi
        if [[ "$(detect_os)" == "macos" ]]; then
            ensure_brew_on_path
        fi
        setup_venv
        ensure_deps
    fi

    local token_file="$BRAINSTEM_HOME/src/rapp_brainstem/.copilot_token"
    local client_id="Iv1.b507a08c87ecfe98"

    # Step 1: Copilot authentication (device code flow)
    local needs_auth=true
    if [ -f "$token_file" ]; then
        # Validate existing token against Copilot API
        local saved_token
        saved_token=$("$venv_python" -c "
import json, sys
try:
    with open('$token_file') as f:
        raw = f.read().strip()
    if raw.startswith('{'):
        print(json.loads(raw).get('access_token',''))
    else:
        print(raw)
except: pass
" 2>/dev/null)
        if [[ -n "$saved_token" ]]; then
            local auth_prefix="token"
            if [[ "$saved_token" != ghu_* ]]; then auth_prefix="Bearer"; fi
            local check_status
            check_status=$(curl -s --max-time 15 -o /dev/null -w "%{http_code}" \
                -H "Authorization: $auth_prefix $saved_token" \
                -H "Accept: application/json" \
                -H "Editor-Version: vscode/1.95.0" \
                -H "Editor-Plugin-Version: copilot/1.0.0" \
                "https://api.github.com/copilot_internal/v2/token" 2>/dev/null) || true
            if [[ "$check_status" == "200" ]]; then
                echo -e "  ${GREEN}✓${NC} Already authenticated with GitHub Copilot"
                needs_auth=false
            elif [[ -z "$check_status" || "$check_status" == "000" ]]; then
                # curl never reached GitHub (offline, captive portal, timeout) — that
                # says nothing about the token. Keep it; the server retries live.
                echo -e "  ${YELLOW}⚠${NC} Couldn't verify the saved token (no network) — keeping it"
                needs_auth=false
            else
                echo -e "  ${YELLOW}⚠${NC} Saved token expired — re-authenticating..."
                rm -f "$token_file"
            fi
        else
            rm -f "$token_file"
        fi
    fi

    if [[ "$needs_auth" == true ]]; then
        echo ""
        echo -e "  ${CYAN}Authenticating with GitHub Copilot...${NC}"
        echo ""

        # Best-effort auth: disable `set -e` for the whole block. Every curl and JSON
        # parse below tolerates failure (empty response when offline), and the code
        # already handles those cases gracefully — but under `set -e` the very first
        # failed command substitution would abort the installer before the server can
        # start. The user can always finish signing in later at /login.
        set +e

        # Request device code
        local device_resp
        device_resp=$(curl -fsSL --max-time 15 -X POST "https://github.com/login/device/code" \
            -H "Accept: application/json" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "client_id=${client_id}" 2>/dev/null)

        local user_code device_code interval verify_uri
        user_code=$(echo "$device_resp" | "$venv_python" -c "import sys,json; print(json.load(sys.stdin)['user_code'])" 2>/dev/null)
        device_code=$(echo "$device_resp" | "$venv_python" -c "import sys,json; print(json.load(sys.stdin)['device_code'])" 2>/dev/null)
        interval=$(echo "$device_resp" | "$venv_python" -c "import sys,json; print(json.load(sys.stdin).get('interval',5))" 2>/dev/null)
        verify_uri=$(echo "$device_resp" | "$venv_python" -c "import sys,json; print(json.load(sys.stdin)['verification_uri'])" 2>/dev/null)

        if [[ -z "$user_code" || -z "$device_code" ]]; then
            echo -e "  ${YELLOW}!${NC} Could not start auth — you can sign in at http://localhost:7071/login"
        else
            echo "  ┌─────────────────────────────────────────┐"
            echo -e "  │  Your code: ${CYAN}${user_code}${NC}                  │"
            echo "  └─────────────────────────────────────────┘"
            echo ""
            echo "  Opening browser to authorize..."

            # Open browser
            open "$verify_uri" 2>/dev/null || xdg-open "$verify_uri" 2>/dev/null || true

            echo "  Waiting for authorization..."
            echo ""

            local token_json=""
            for i in $(seq 1 60); do
                sleep "${interval:-5}"
                local poll_resp
                poll_resp=$(curl -fsSL --max-time 15 -X POST "https://github.com/login/oauth/access_token" \
                    -H "Accept: application/json" \
                    -H "Content-Type: application/x-www-form-urlencoded" \
                    -d "client_id=${client_id}&device_code=${device_code}&grant_type=urn:ietf:params:oauth:grant-type:device_code" 2>/dev/null) || true

                local access_token error
                access_token=$(echo "$poll_resp" | "$venv_python" -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)
                error=$(echo "$poll_resp" | "$venv_python" -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',''))" 2>/dev/null)

                if [[ -n "$access_token" ]]; then
                    # Save token file (same format brainstem.py expects)
                    "$venv_python" -c "
import sys, json
d = json.loads(sys.argv[1])
out = {'access_token': d['access_token']}
if d.get('refresh_token'): out['refresh_token'] = d['refresh_token']
with open(sys.argv[2], 'w') as f: json.dump(out, f)
" "$poll_resp" "$token_file"

                    # Validate Copilot access immediately
                    local copilot_check copilot_status
                    copilot_check=$(curl -s --max-time 15 -w "\n%{http_code}" \
                        -H "Authorization: token $access_token" \
                        -H "Accept: application/json" \
                        -H "Editor-Version: vscode/1.95.0" \
                        -H "Editor-Plugin-Version: copilot/1.0.0" \
                        "https://api.github.com/copilot_internal/v2/token" 2>/dev/null) || true
                    copilot_status=$(echo "$copilot_check" | tail -1)

                    if [[ "$copilot_status" == "200" ]]; then
                        echo -e "  ${GREEN}✓${NC} Authenticated — Copilot access confirmed"
                    elif [[ "$copilot_status" == "403" ]]; then
                        echo ""
                        echo -e "  ${RED}✗${NC} This GitHub account does NOT have Copilot access."
                        echo ""
                        echo -e "  Either:"
                        echo -e "    1. Sign up for Copilot: ${CYAN}https://github.com/github-copilot/signup${NC}"
                        echo -e "    2. Re-run this installer and sign in with a different GitHub account"
                        echo ""
                        rm -f "$token_file"
                    else
                        echo -e "  ${GREEN}✓${NC} Authenticated with GitHub"
                    fi
                    break
                fi

                if [[ "$error" == "expired_token" ]]; then
                    echo -e "  ${YELLOW}!${NC} Auth timed out — sign in at http://localhost:7071/login"
                    break
                fi

                if [[ "$error" != "authorization_pending" && "$error" != "slow_down" && -n "$error" ]]; then
                    echo -e "  ${YELLOW}!${NC} Auth error: $error — sign in at http://localhost:7071/login"
                    break
                fi
            done
        fi
        set -e   # end best-effort auth block
    fi

    # Step 2: Launch brainstem
    echo ""
    echo -e "  ${CYAN}Starting RAPP Brainstem...${NC}"
    echo ""

    cd "$BRAINSTEM_HOME/src/rapp_brainstem"

    # Kill any existing brainstem on port 7071 before starting
    local existing_pid
    existing_pid=$(lsof -ti:7071 2>/dev/null | head -1)
    if [ -n "$existing_pid" ]; then
        echo -e "  ${YELLOW}⚠${NC} Stopping existing server (PID $existing_pid)..."
        kill "$existing_pid" 2>/dev/null
        sleep 1
    fi

    # Open the browser after a short delay
    (sleep 3 && (open "http://localhost:7071" 2>/dev/null || xdg-open "http://localhost:7071" 2>/dev/null)) &

    # Final dep safety net — if somehow we got here without deps, fix it
    if ! "$venv_python" -c "import flask, flask_cors, requests, dotenv" 2>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} Fixing missing dependencies..."
        "$VENV_DIR/bin/pip" install -r "$BRAINSTEM_HOME/src/rapp_brainstem/requirements.txt" --quiet 2>/dev/null || \
            "$VENV_DIR/bin/pip" install -r "$BRAINSTEM_HOME/src/rapp_brainstem/requirements.txt"
    fi

    # Use exec to replace shell — but only if stdin is a terminal.
    # When piped (curl | bash), exec can lose the TTY and hang.
    if [ -t 0 ]; then
        exec "$venv_python" brainstem.py
    elif ( : </dev/tty ) 2>/dev/null; then
        # Piped installer with a USABLE controlling terminal — reattach stdin.
        # Test by opening it: the /dev/tty node exists even without a controlling
        # terminal (ssh without -t, CI), where only the open fails — a bare `-e`
        # check would take this branch and die on the redirect.
        "$venv_python" brainstem.py </dev/tty
    else
        # No controlling terminal at all (ssh without -t, CI, a container). Reattaching
        # /dev/tty would error out; just run the server on the inherited stdin.
        "$venv_python" brainstem.py
    fi
}

main() {
    # Parse arguments (e.g. --version v0.6.0)
    while [ $# -gt 0 ]; do
        case "$1" in
            --version)
                PIN_VERSION="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    print_banner

    if [ -n "$PIN_VERSION" ]; then
        echo -e "  ${CYAN}Pinning to version: ${PIN_VERSION}${NC}"
        echo ""
    fi

    # Check if this is an upgrade of an existing install
    # Skip the shortcut when --version is specified (always go through install_brainstem)
    if [ -z "$PIN_VERSION" ] && [ -d "$BRAINSTEM_HOME/src/.git" ]; then
        echo "Checking for updates..."
        if ! check_for_upgrade; then
            # Already up to date — still verify everything works before launching
            check_prereqs
            setup_venv
            ensure_deps
            install_cli
            create_env
            export PATH="$BRAINSTEM_BIN:/opt/homebrew/bin:/usr/local/bin:$PATH"
            launch_brainstem
            exit $?  # launch uses exec, but guard against fall-through
        fi
        # Upgrade available — fall through to full install path
    fi

    check_prereqs
    install_brainstem
    setup_venv
    setup_deps
    install_cli
    create_env

    # Make sure brainstem and gh are on PATH for this session
    export PATH="$BRAINSTEM_BIN:/opt/homebrew/bin:/usr/local/bin:$PATH"

    local installed_version
    installed_version=$(cat "$BRAINSTEM_HOME/src/rapp_brainstem/VERSION" 2>/dev/null | tr -d '[:space:]')

    echo ""
    echo "═══════════════════════════════════════════════════"
    echo -e "  ${GREEN}✓ RAPP Brainstem v${installed_version} installed!${NC}"
    echo "═══════════════════════════════════════════════════"
    echo ""

    launch_brainstem
}

main "$@"
