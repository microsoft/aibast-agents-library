#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  RAPP Hippocampus — Installer
#  One-liner: curl -fsSL https://raw.githubusercontent.com/kody-w/m365-agents-for-python/main/CommunityRAPP/install.sh | bash
# ═══════════════════════════════════════════════════════════════════════════════
set -e

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# ── Constants ─────────────────────────────────────────────────────────────────
VERSION="1.0.0"
INSTALL_DIR="$HOME/.communityrapp"
REPO_DIR="$INSTALL_DIR/src"
SOURCE_DIR="$REPO_DIR/CommunityRAPP"
VENV_DIR="$INSTALL_DIR/venv"
BIN_DIR="$HOME/.local/bin"
REPO_URL="https://github.com/kody-w/m365-agents-for-python.git"
SERVER_PORT=7071
SERVER_URL="http://localhost:$SERVER_PORT"

# ── Detect piped input (curl | bash) ─────────────────────────────────────────
# When piped, stdin is the script itself; we need /dev/tty for user prompts
if [ -t 0 ]; then
    INPUT_SOURCE="/dev/stdin"
else
    INPUT_SOURCE="/dev/tty"
fi

# ── OS Detection ──────────────────────────────────────────────────────────────
detect_os() {
    case "$(uname -s)" in
        Darwin*)  OS="macos" ;;
        Linux*)   OS="linux" ;;
        *)        OS="unknown" ;;
    esac

    case "$(uname -m)" in
        arm64|aarch64) ARCH="arm64" ;;
        x86_64)        ARCH="x86_64" ;;
        *)             ARCH="unknown" ;;
    esac
}

# ── Helpers ───────────────────────────────────────────────────────────────────
info()    { echo -e "${CYAN}  ℹ ${NC}$1"; }
success() { echo -e "${GREEN}  ✓ ${NC}$1"; }
warn()    { echo -e "${YELLOW}  ⚠ ${NC}$1"; }
fail()    { echo -e "${RED}  ✗ ${NC}$1"; exit 1; }
step()    { echo -e "\n${BOLD}${CYAN}  ▸ $1${NC}"; }

prompt_user() {
    local prompt="$1"
    local var_name="$2"
    local default="$3"
    if [ -n "$default" ]; then
        echo -en "${CYAN}  ? ${NC}${prompt} ${DIM}[$default]${NC}: " >&2
    else
        echo -en "${CYAN}  ? ${NC}${prompt}: " >&2
    fi
    local answer
    read -r answer < "$INPUT_SOURCE"
    if [ -z "$answer" ] && [ -n "$default" ]; then
        answer="$default"
    fi
    eval "$var_name=\"$answer\""
}

# ── Banner ────────────────────────────────────────────────────────────────────
print_banner() {
    echo ""
    echo -e "${CYAN}${BOLD}"
    echo "  ╔═══════════════════════════════════════════════════╗"
    echo "  ║                                                   ║"
    echo "  ║   🧠 RAPP Hippocampus                    ║"
    echo "  ║                                                   ║"
    echo "  ║   The memory center for your AI agents            ║"
    echo "  ║   Local-first — deploy to Azure when ready        ║"
    echo "  ║                                                   ║"
    echo "  ╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "  ${DIM}Installer v${VERSION} — $(uname -s) $(uname -m)${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Prerequisites
# ═══════════════════════════════════════════════════════════════════════════════

check_command() {
    command -v "$1" &>/dev/null
}

install_homebrew() {
    if ! check_command brew; then
        warn "Homebrew not found — installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" < "$INPUT_SOURCE"
        # Add Homebrew to PATH for Apple Silicon
        if [ -f "/opt/homebrew/bin/brew" ]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    fi
}

check_python() {
    step "Checking Python 3.11+..."

    local python_cmd=""
    for cmd in python3.11 python3.12 python3.13 python3; do
        if check_command "$cmd"; then
            local ver
            ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
            local major minor
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
                python_cmd="$cmd"
                break
            fi
        fi
    done

    if [ -n "$python_cmd" ]; then
        PYTHON_CMD="$python_cmd"
        success "Python $($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"
        return 0
    fi

    warn "Python 3.11+ not found — installing..."
    if [ "$OS" = "macos" ]; then
        install_homebrew
        brew install python@3.11
        PYTHON_CMD="python3.11"
    elif [ "$OS" = "linux" ]; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq python3.11 python3.11-venv python3-pip
        PYTHON_CMD="python3.11"
    fi

    if check_command "$PYTHON_CMD"; then
        success "Python installed: $($PYTHON_CMD --version 2>&1)"
    else
        fail "Could not install Python 3.11+. Please install manually and re-run."
    fi
}

check_git() {
    step "Checking Git..."

    if check_command git; then
        success "Git $(git --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"
        return 0
    fi

    warn "Git not found — installing..."
    if [ "$OS" = "macos" ]; then
        xcode-select --install 2>/dev/null || true
        # Wait for xcode CLI tools
        until check_command git; do
            info "Waiting for Xcode Command Line Tools..."
            sleep 5
        done
    elif [ "$OS" = "linux" ]; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq git
    fi

    if check_command git; then
        success "Git installed: $(git --version)"
    else
        fail "Could not install Git. Please install manually and re-run."
    fi
}

check_node() {
    step "Checking Node.js 18+..."

    if check_command node; then
        local node_ver
        node_ver=$(node --version | grep -oE '[0-9]+' | head -1)
        if [ "$node_ver" -ge 18 ]; then
            success "Node.js $(node --version)"
            return 0
        else
            warn "Node.js $(node --version) found but need 18+ — upgrading..."
        fi
    else
        warn "Node.js not found — installing..."
    fi

    if [ "$OS" = "macos" ]; then
        install_homebrew
        brew install node@22
        # Link if not already linked
        brew link --overwrite node@22 2>/dev/null || true
    elif [ "$OS" = "linux" ]; then
        # Use NodeSource for current LTS
        curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
        sudo apt-get install -y -qq nodejs
    fi

    if check_command node; then
        local ver
        ver=$(node --version | grep -oE '[0-9]+' | head -1)
        if [ "$ver" -ge 18 ]; then
            success "Node.js $(node --version)"
        else
            fail "Node.js 18+ required but got $(node --version). Please update manually."
        fi
    else
        fail "Could not install Node.js. Please install manually and re-run."
    fi
}

check_func_tools() {
    step "Checking Azure Functions Core Tools v4..."

    if check_command func; then
        local func_ver
        func_ver=$(func --version 2>/dev/null | head -1)
        local func_major
        func_major=$(echo "$func_ver" | cut -d. -f1)
        if [ "$func_major" -ge 4 ]; then
            success "Azure Functions Core Tools v${func_ver}"
            return 0
        else
            warn "Azure Functions Core Tools v${func_ver} found but need v4+ — upgrading..."
        fi
    else
        warn "Azure Functions Core Tools not found — installing..."
    fi

    if [ "$OS" = "macos" ]; then
        # Prefer Homebrew tap on macOS for native performance
        install_homebrew
        brew tap azure/functions 2>/dev/null || true
        brew install azure-functions-core-tools@4 2>/dev/null || {
            # Fallback to npm
            info "Homebrew install failed, falling back to npm..."
            npm install -g azure-functions-core-tools@4 --unsafe-perm true
        }
    elif [ "$OS" = "linux" ]; then
        npm install -g azure-functions-core-tools@4 --unsafe-perm true
    fi

    if check_command func; then
        success "Azure Functions Core Tools v$(func --version 2>/dev/null | head -1)"
    else
        fail "Could not install Azure Functions Core Tools. Please install manually:\n    npm install -g azure-functions-core-tools@4"
    fi
}

check_prereqs() {
    echo -e "\n${BOLD}  ── Prerequisites ──────────────────────────────────${NC}"
    detect_os
    info "Detected: ${OS} (${ARCH})"

    if [ "$OS" = "unknown" ]; then
        fail "Unsupported operating system: $(uname -s). Only macOS and Linux are supported."
    fi

    check_python
    check_git
    check_node
    check_func_tools

    echo ""
    success "All prerequisites satisfied!"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Install / Update Repository
# ═══════════════════════════════════════════════════════════════════════════════

install_communityrapp() {
    echo -e "\n${BOLD}  ── Installing CommunityRAPP ───────────────────────${NC}"

    mkdir -p "$INSTALL_DIR"

    if [ -d "$REPO_DIR/.git" ]; then
        step "Existing installation found — checking for updates..."

        local local_version="0.0.0"
        if [ -f "$SOURCE_DIR/VERSION" ]; then
            local_version=$(cat "$SOURCE_DIR/VERSION" | tr -d '[:space:]')
        fi

        cd "$REPO_DIR"
        git fetch origin main --quiet 2>/dev/null || true

        local remote_version
        remote_version=$(git show origin/main:CommunityRAPP/VERSION 2>/dev/null | tr -d '[:space:]' || echo "$local_version")

        if [ "$local_version" != "$remote_version" ]; then
            info "Upgrading: v${local_version} → v${remote_version}"
            git pull origin main --quiet
            success "Updated to v${remote_version}"
        else
            success "Already up to date (v${local_version})"
        fi
    else
        step "Cloning repository..."
        if [ -d "$REPO_DIR" ]; then
            rm -rf "$REPO_DIR"
        fi
        git clone --depth 1 "$REPO_URL" "$REPO_DIR" 2>&1 | tail -1
        success "Repository cloned"
    fi

    # Verify source directory
    if [ ! -f "$SOURCE_DIR/function_app.py" ]; then
        fail "Installation failed — CommunityRAPP source not found at $SOURCE_DIR"
    fi

    # Write local version marker
    echo "$VERSION" > "$SOURCE_DIR/VERSION"
    success "CommunityRAPP v${VERSION} ready at $SOURCE_DIR"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Virtual Environment
# ═══════════════════════════════════════════════════════════════════════════════

setup_venv() {
    echo -e "\n${BOLD}  ── Setting up Python environment ──────────────────${NC}"

    if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
        step "Existing virtual environment found — updating packages..."
        source "$VENV_DIR/bin/activate"
    else
        step "Creating virtual environment..."
        "$PYTHON_CMD" -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        success "Virtual environment created"
    fi

    step "Installing dependencies..."
    pip install --upgrade pip --quiet 2>&1 | tail -1
    pip install -r "$SOURCE_DIR/requirements.txt" --quiet 2>&1 | tail -3

    local pkg_count
    pkg_count=$(pip list --format=columns 2>/dev/null | tail -n +3 | wc -l | tr -d ' ')
    success "${pkg_count} packages installed in virtual environment"

    deactivate
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Azure OpenAI Configuration
# ═══════════════════════════════════════════════════════════════════════════════

configure_openai() {
    echo -e "\n${BOLD}  ── Azure OpenAI Configuration ─────────────────────${NC}"

    local settings_file="$SOURCE_DIR/local.settings.json"
    local template_file="$SOURCE_DIR/local.settings.template.json"

    # If local.settings.json already exists, ask about overwriting
    if [ -f "$settings_file" ]; then
        warn "local.settings.json already exists"
        prompt_user "Overwrite with new configuration? (y/N)" OVERWRITE "N"
        if [[ ! "$OVERWRITE" =~ ^[Yy] ]]; then
            success "Keeping existing configuration"
            return 0
        fi
    fi

    echo ""
    echo -e "  ${BOLD}How would you like to connect to Azure OpenAI?${NC}"
    echo ""
    echo -e "    ${CYAN}1)${NC} Enter API key manually"
    echo -e "    ${CYAN}2)${NC} Use Azure CLI login (az login) — ${DIM}recommended for Azure users${NC}"
    echo -e "    ${CYAN}3)${NC} Skip for now ${DIM}(configure later)${NC}"
    echo ""

    prompt_user "Choose [1/2/3]" AUTH_CHOICE "3"

    local api_key=""
    local endpoint=""
    local deployment="gpt-4o"
    local api_version="2024-08-01-preview"

    case "$AUTH_CHOICE" in
        1)
            step "Manual API key configuration"
            echo ""
            prompt_user "Azure OpenAI API key" api_key ""
            if [ -z "$api_key" ]; then
                warn "No API key provided — using placeholder"
                api_key="<your-openai-api-key>"
            fi
            prompt_user "Azure OpenAI endpoint (e.g. https://your-resource.openai.azure.com/)" endpoint ""
            if [ -z "$endpoint" ]; then
                endpoint="https://<your-openai-resource>.openai.azure.com/"
            fi
            prompt_user "Deployment name" deployment "gpt-4o"
            prompt_user "API version" api_version "2024-08-01-preview"
            success "API key configured"
            ;;
        2)
            step "Azure CLI authentication"
            if check_command az; then
                # Check if already logged in
                if ! az account show &>/dev/null; then
                    info "Opening Azure login..."
                    az login 2>&1 | tail -3
                fi
                success "Azure CLI authenticated as $(az account show --query user.name -o tsv 2>/dev/null || echo 'unknown')"

                # Try to auto-detect OpenAI resources
                info "Searching for Azure OpenAI resources in your subscription..."
                local oai_resources
                oai_resources=$(az cognitiveservices account list --query "[?kind=='OpenAI'].{name:name, endpoint:properties.endpoint}" -o tsv 2>/dev/null || echo "")

                if [ -n "$oai_resources" ]; then
                    echo -e "  ${GREEN}Found Azure OpenAI resources:${NC}"
                    echo "$oai_resources" | while IFS=$'\t' read -r name ep; do
                        echo -e "    • ${BOLD}$name${NC} — $ep"
                    done
                    echo ""
                fi

                prompt_user "Azure OpenAI endpoint (e.g. https://your-resource.openai.azure.com/)" endpoint ""
                if [ -z "$endpoint" ]; then
                    endpoint="https://<your-openai-resource>.openai.azure.com/"
                fi
                prompt_user "Deployment name" deployment "gpt-4o"

                # When using az login, no API key needed — Entra ID auth handles it
                api_key=""
                success "Will use Azure CLI (Entra ID) authentication — no API key needed"
            else
                warn "Azure CLI not found. Install it: https://aka.ms/installazurecliwindows"
                warn "Falling back to placeholder configuration"
                api_key="<your-openai-api-key>"
                endpoint="https://<your-openai-resource>.openai.azure.com/"
            fi
            ;;
        3|*)
            info "Skipping Azure OpenAI configuration"
            info "Edit ~/.communityrapp/src/CommunityRAPP/local.settings.json later"
            api_key="<your-openai-api-key>"
            endpoint="https://<your-openai-resource>.openai.azure.com/"
            ;;
    esac

    # Generate local.settings.json
    step "Generating local.settings.json..."

    if [ -z "$api_key" ]; then
        # Entra ID auth — no key needed
        api_key=""
    fi

    cat > "$settings_file" << SETTINGS_EOF
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "AZURE_OPENAI_API_KEY": "${api_key}",
    "AZURE_OPENAI_ENDPOINT": "${endpoint}",
    "AZURE_OPENAI_API_VERSION": "${api_version}",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "${deployment}",
    "ASSISTANT_NAME": "Memory Agent",
    "CHARACTERISTIC_DESCRIPTION": "An AI assistant with persistent memory across conversations",
    "USE_CLOUD_STORAGE": "false"
  },
  "Host": {
    "CORS": "*",
    "CORSCredentials": false
  }
}
SETTINGS_EOF

    success "Configuration saved to local.settings.json"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  CLI Launcher
# ═══════════════════════════════════════════════════════════════════════════════

install_cli() {
    echo -e "\n${BOLD}  ── Installing CLI commands ────────────────────────${NC}"

    mkdir -p "$BIN_DIR"

    # ── Main launcher: communityrapp ──────────────────────────────────────────
    cat > "$BIN_DIR/communityrapp" << 'LAUNCHER_EOF'
#!/usr/bin/env bash
# RAPP Hippocampus — CLI Launcher
set -e

INSTALL_DIR="$HOME/.communityrapp"
SOURCE_DIR="$INSTALL_DIR/src/CommunityRAPP"
VENV_DIR="$INSTALL_DIR/venv"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: CommunityRAPP not found at $SOURCE_DIR"
    echo "Run the installer: curl -fsSL https://raw.githubusercontent.com/kody-w/m365-agents-for-python/main/CommunityRAPP/install.sh | bash"
    exit 1
fi

cd "$SOURCE_DIR"
source "$VENV_DIR/bin/activate"

case "${1:-start}" in
    start)
        echo "🧠 Starting Hippocampus on http://localhost:7071"
        echo "   Press Ctrl+C to stop"
        echo ""
        # Open chat UI after a short delay (server needs a moment)
        (sleep 5 && open "$SOURCE_DIR/index.html" 2>/dev/null || xdg-open "$SOURCE_DIR/index.html" 2>/dev/null) &
        func start
        ;;
    status)
        curl -sf http://localhost:7071/api/health && echo "" || echo "Server not running"
        ;;
    test)
        echo "Sending test message..."
        curl -s -X POST http://localhost:7071/api/businessinsightbot_function \
            -H "Content-Type: application/json" \
            -d '{"user_input": "Hello! What can you do?", "conversation_history": []}' | python3 -m json.tool
        ;;
    update)
        cd "$INSTALL_DIR/src"
        git pull origin main
        source "$VENV_DIR/bin/activate"
        pip install -r "$SOURCE_DIR/requirements.txt" --quiet
        echo "✓ Updated to $(cat "$SOURCE_DIR/VERSION" 2>/dev/null || echo 'latest')"
        ;;
    version)
        cat "$SOURCE_DIR/VERSION" 2>/dev/null || echo "unknown"
        ;;
    help|--help|-h)
        echo "RAPP Hippocampus"
        echo ""
        echo "Usage: communityrapp [command]"
        echo ""
        echo "Commands:"
        echo "  start     Start the server (default)"
        echo "  status    Check if server is running"
        echo "  test      Send a test message"
        echo "  update    Pull latest updates"
        echo "  version   Show installed version"
        echo "  help      Show this help"
        ;;
    *)
        echo "Unknown command: $1 (try 'communityrapp help')"
        exit 1
        ;;
esac
LAUNCHER_EOF

    chmod +x "$BIN_DIR/communityrapp"
    success "Created: communityrapp"

    # ── Alias: crapp ──────────────────────────────────────────────────────────
    cat > "$BIN_DIR/crapp" << 'ALIAS_EOF'
#!/usr/bin/env bash
# Alias for communityrapp
exec "$HOME/.local/bin/communityrapp" "$@"
ALIAS_EOF

    chmod +x "$BIN_DIR/crapp"
    success "Created: crapp (alias)"

    # ── Add ~/.local/bin to PATH if not already there ─────────────────────────
    add_to_path() {
        local shell_rc="$1"
        local path_line='export PATH="$HOME/.local/bin:$PATH"'

        if [ -f "$shell_rc" ]; then
            if ! grep -qF '.local/bin' "$shell_rc"; then
                echo "" >> "$shell_rc"
                echo "# RAPP Hippocampus" >> "$shell_rc"
                echo "$path_line" >> "$shell_rc"
                info "Added ~/.local/bin to PATH in $(basename "$shell_rc")"
            fi
        fi
    }

    local path_updated=false
    case "$SHELL" in
        */zsh)
            add_to_path "$HOME/.zshrc"
            path_updated=true
            ;;
        */bash)
            add_to_path "$HOME/.bashrc"
            path_updated=true
            ;;
    esac

    # Also try the other shell rc just in case
    if [ -f "$HOME/.zshrc" ] && [[ "$SHELL" != */zsh ]]; then
        add_to_path "$HOME/.zshrc"
    fi
    if [ -f "$HOME/.bashrc" ] && [[ "$SHELL" != */bash ]]; then
        add_to_path "$HOME/.bashrc"
    fi

    # Add to current session
    export PATH="$BIN_DIR:$PATH"

    success "CLI commands installed to $BIN_DIR"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Launch
# ═══════════════════════════════════════════════════════════════════════════════

launch_communityrapp() {
    echo -e "\n${BOLD}  ── Launching CommunityRAPP ────────────────────────${NC}"

    cd "$SOURCE_DIR"
    source "$VENV_DIR/bin/activate"

    step "Starting Azure Functions host..."

    # Start func in background
    func start &>/dev/null &
    local func_pid=$!

    # Wait for server to be ready (max 30 seconds)
    local max_wait=30
    local waited=0
    local ready=false

    while [ $waited -lt $max_wait ]; do
        if curl -sf "$SERVER_URL/api/health" &>/dev/null; then
            ready=true
            break
        fi
        sleep 1
        waited=$((waited + 1))
        echo -n "." >&2
    done
    echo "" >&2

    if [ "$ready" = true ]; then
        success "Server is running on ${SERVER_URL}"

        # Open the chat UI in the default browser
        local chat_file="$SOURCE_DIR/index.html"
        if [ -f "$chat_file" ]; then
            step "Opening chat UI..."
            open "$chat_file" 2>/dev/null || xdg-open "$chat_file" 2>/dev/null || true
            success "Chat UI opened in browser"
        fi
    else
        warn "Server started but health check timed out (it may still be initializing)"
        info "PID: $func_pid — check with: curl $SERVER_URL/api/health"
    fi

    # Stop the background server — user will start it themselves with `communityrapp`
    kill "$func_pid" 2>/dev/null || true
    wait "$func_pid" 2>/dev/null || true

    deactivate 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Success Banner
# ═══════════════════════════════════════════════════════════════════════════════

print_success() {
    local installed_version
    installed_version=$(cat "$SOURCE_DIR/VERSION" 2>/dev/null || echo "$VERSION")

    echo ""
    echo -e "${GREEN}${BOLD}"
    echo "  ═══════════════════════════════════════════════════"
    echo "  ✓ CommunityRAPP v${installed_version} installed!"
    echo "  ═══════════════════════════════════════════════════"
    echo -e "${NC}"
    echo -e "  ${BOLD}Start the server:${NC}"
    echo -e "    ${CYAN}communityrapp${NC}"
    echo ""
    echo -e "  ${BOLD}Test memory:${NC}"
    echo -e "    ${DIM}curl -X POST http://localhost:7071/api/businessinsightbot_function \\${NC}"
    echo -e "    ${DIM}  -H \"Content-Type: application/json\" \\${NC}"
    echo -e "    ${DIM}  -d '{\"user_input\": \"Remember that I love coding\", \"conversation_history\": []}'${NC}"
    echo ""
    echo -e "  ${BOLD}Other commands:${NC}"
    echo -e "    ${CYAN}communityrapp status${NC}   — Check server health"
    echo -e "    ${CYAN}communityrapp test${NC}     — Send a test message"
    echo -e "    ${CYAN}communityrapp update${NC}   — Pull latest version"
    echo -e "    ${CYAN}crapp${NC}                  — Short alias"
    echo ""
    echo -e "  ${BOLD}Next steps:${NC}"
    echo -e "    • ${GREEN}Deploy to Azure:${NC} see docs/DEPLOYMENT.md"
    echo -e "    • ${GREEN}Add custom agents:${NC} drop *_agent.py files in agents/"
    echo -e "    • ${GREEN}Configure memory:${NC} edit local.settings.json"
    echo ""
    echo -e "  ${DIM}Installation: ~/.communityrapp/${NC}"
    echo -e "  ${DIM}Need help?  communityrapp help${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    print_banner
    check_prereqs
    install_communityrapp
    setup_venv
    configure_openai
    install_cli
    launch_communityrapp
    print_success
}

# Handle --help
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "CommunityRAPP Installer"
    echo ""
    echo "Usage:"
    echo "  curl -fsSL https://raw.githubusercontent.com/kody-w/m365-agents-for-python/main/CommunityRAPP/install.sh | bash"
    echo "  ./install.sh"
    echo ""
    echo "This script installs RAPP Hippocampus to ~/.communityrapp/"
    echo "and creates CLI commands: communityrapp, crapp"
    exit 0
fi

main
