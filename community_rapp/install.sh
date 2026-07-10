#!/bin/bash
# CommunityRAPP — One-line installer (Hippocampus / Tier 2)
# Usage: curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/community_rapp/install.sh | bash
#
# Creates a ready-to-run CommunityRAPP project with persistent memory,
# auto-discovered agents, and GitHub Copilot device-code auth through the UI.
# No API keys, no Azure account, no cloud services needed to start.

set -e

RED="\033[0;31m" GREEN="\033[0;32m" YELLOW="\033[1;33m" BLUE="\033[0;34m" NC="\033[0m"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RAPP Hippocampus — Local Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ── Helpers ─────────────────────────────────────────────────

die() { echo -e "${RED}ERROR: $1${NC}" >&2; exit 1; }

find_python() {
    for cmd in python3.11 python3.12 python3; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" --version 2>&1 | awk '{print $2}')
            local major minor
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" = "3" ] && [ "$minor" -ge 11 ] && [ "$minor" -le 12 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# ── Prerequisites ───────────────────────────────────────────
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Git
command -v git &>/dev/null || die "Git is required. Install from https://git-scm.com"
echo -e "${GREEN}[OK] Git${NC}"

# Python
PYTHON_CMD=$(find_python) || {
    echo -e "${YELLOW}Python 3.11+ required (3.13+ not supported). Attempting install...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python@3.11 2>/dev/null || die "Install Python 3.11 via Homebrew: brew install python@3.11"
    else
        sudo apt-get update -qq && sudo apt-get install -y -qq python3.11 python3.11-venv 2>/dev/null || \
        die "Install Python 3.11: https://python.org/downloads/"
    fi
    PYTHON_CMD=$(find_python) || die "Python 3.11-3.12 required. Install from https://python.org"
}
echo -e "${GREEN}[OK] $PYTHON_CMD ($($PYTHON_CMD --version 2>&1))${NC}"

# Azure Functions Core Tools
if ! command -v func &>/dev/null; then
    echo -e "${YELLOW}Installing Azure Functions Core Tools...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew tap azure/functions 2>/dev/null && brew install azure-functions-core-tools@4 2>/dev/null || \
        die "Install Azure Functions Core Tools: brew tap azure/functions && brew install azure-functions-core-tools@4"
    else
        if command -v npm &>/dev/null; then
            npm install -g azure-functions-core-tools@4 2>/dev/null || \
            die "Install Azure Functions Core Tools: npm install -g azure-functions-core-tools@4"
        else
            die "Install Node.js and Azure Functions Core Tools: https://learn.microsoft.com/azure/azure-functions/functions-run-local"
        fi
    fi
fi
echo -e "${GREEN}[OK] Azure Functions Core Tools${NC}"

# ── Project name ────────────────────────────────────────────

PROJECT_NAME="${1:-}"
if [ -z "$PROJECT_NAME" ]; then
    echo ""
    printf "Project name (e.g. my-project): "
    read -r PROJECT_NAME
    [ -z "$PROJECT_NAME" ] && die "Project name is required."
fi

if ! echo "$PROJECT_NAME" | grep -qE '^[a-z0-9][a-z0-9-]*$'; then
    die "Invalid name '$PROJECT_NAME'. Use lowercase letters, numbers, and hyphens."
fi

PROJECTS_DIR="${RAPP_PROJECTS_DIR:-$HOME/rapp-projects}"
PROJECT_DIR="$PROJECTS_DIR/$PROJECT_NAME"

[ -d "$PROJECT_DIR" ] && die "Project '$PROJECT_NAME' already exists at $PROJECT_DIR"

# ── Clone ───────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}Creating project '$PROJECT_NAME'...${NC}"

mkdir -p "$PROJECTS_DIR"

echo -e "${YELLOW}Cloning CommunityRAPP...${NC}"
git clone --depth 1 --quiet https://github.com/kody-w/CommunityRAPP.git "$PROJECT_DIR"
echo -e "${GREEN}[OK] Cloned${NC}"

# ── Venv + deps ─────────────────────────────────────────────
echo -e "${YELLOW}Creating virtual environment...${NC}"
"$PYTHON_CMD" -m venv "$PROJECT_DIR/.venv"

echo -e "${YELLOW}Installing dependencies...${NC}"
"$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt" --quiet 2>/dev/null
echo -e "${GREEN}[OK] Dependencies installed${NC}"

# ── Settings ────────────────────────────────────────────────
if [ -f "$PROJECT_DIR/local.settings.template.json" ]; then
    cp "$PROJECT_DIR/local.settings.template.json" "$PROJECT_DIR/local.settings.json"
fi

# ── Port + start script ────────────────────────────────────
BASE_PORT=7072
PORT=$BASE_PORT

if [ -f "$PROJECTS_DIR/.hatchery.json" ]; then
    max=$(grep -o '"port": [0-9]*' "$PROJECTS_DIR/.hatchery.json" 2>/dev/null | awk '{print $2}' | sort -n | tail -1)
    if [ -n "$max" ] && [ "$max" -ge "$PORT" ]; then
        PORT=$((max + 1))
    fi
fi

cat > "$PROJECT_DIR/start.sh" << EOF
#!/usr/bin/env bash
cd "\$(dirname "\$0")"
source .venv/bin/activate
func start --port $PORT
EOF
chmod +x "$PROJECT_DIR/start.sh"

cat > "$PROJECT_DIR/start.ps1" << EOF
\$ErrorActionPreference = 'Stop'
Set-Location \$PSScriptRoot
.venv\\Scripts\\Activate.ps1
func start --port $PORT
EOF

# Inject port into chat UI
if [ -f "$PROJECT_DIR/index.html" ]; then
    sed -i '' "s|</head>|<script>window.__RAPP_PORT__='${PORT}';</script></head>|" "$PROJECT_DIR/index.html" 2>/dev/null || \
    sed -i "s|</head>|<script>window.__RAPP_PORT__='${PORT}';</script></head>|" "$PROJECT_DIR/index.html" 2>/dev/null || true
fi

# Remove hatchery/ (it's for brainstem distribution, not the running project)
rm -rf "$PROJECT_DIR/hatchery" 2>/dev/null || true

# ── Business Mode UI (first hatch deploys it) ──────────────
BIZ_HTML="$PROJECTS_DIR/business.html"
if [ ! -f "$BIZ_HTML" ]; then
    curl -fsSL "https://raw.githubusercontent.com/kody-w/CommunityRAPP/main/business.html" -o "$BIZ_HTML" 2>/dev/null || true
fi

# ── Update manifest ─────────────────────────────────────────
MANIFEST="$PROJECTS_DIR/.hatchery.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ -f "$MANIFEST" ]; then
    "$PYTHON_CMD" -c "
import json
with open('$MANIFEST', 'r') as f:
    data = json.load(f)
data.setdefault('projects', {})['$PROJECT_NAME'] = {
    'path': '$PROJECT_DIR',
    'port': $PORT,
    'created_at': '$TIMESTAMP',
    'python': '$PYTHON_CMD'
}
with open('$MANIFEST', 'w') as f:
    json.dump(data, f, indent=2)
"
else
    cat > "$MANIFEST" << EOF
{
  "projects": {
    "$PROJECT_NAME": {
      "path": "$PROJECT_DIR",
      "port": $PORT,
      "created_at": "$TIMESTAMP",
      "python": "$PYTHON_CMD"
    }
  }
}
EOF
fi

# ── Done ────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Project '$PROJECT_NAME' is ready!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  Location:  $PROJECT_DIR"
echo "  Port:      $PORT"
echo "  Python:    $PYTHON_CMD"
echo ""
echo "Next steps:"
echo ""
echo "  1. Start it:"
echo "     cd $PROJECT_DIR && ./start.sh"
echo ""
echo "  2. Open the chat UI:"
echo "     open $PROJECT_DIR/index.html"
echo ""
echo "  3. Send a message — the UI walks you through GitHub auth."
echo "     No API keys needed."
echo ""
if [ -f "$BIZ_HTML" ]; then
echo "  4. Business Mode (multi-instance side-by-side):"
echo "     open $BIZ_HTML"
echo ""
fi
echo "  When you're ready for Azure:"
echo "     Edit $PROJECT_DIR/local.settings.json"
echo "     Then: func azure functionapp publish YOUR_APP --build remote"
echo ""
