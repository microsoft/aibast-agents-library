#!/bin/bash
# Pre-Deployment Test Hook
# Runs local validation before allowing deployment to proceed
# 365 Vigilant Spark - "The Installation must be verified before transmission to the Azure realm."

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     365 VIGILANT SPARK - PRE-DEPLOYMENT VERIFICATION       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

ERRORS=0

# 1. Syntax check on main files
echo -e "${YELLOW}[Phase 1] Code Integrity Scan...${NC}"

if python3 -m py_compile "$PROJECT_ROOT/function_app.py" 2>/dev/null; then
    echo -e "${GREEN}  ✓ function_app.py syntax valid${NC}"
else
    echo -e "${RED}  ✗ function_app.py has syntax errors${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check agents
for agent_file in "$PROJECT_ROOT"/agents/*.py; do
    if [[ -f "$agent_file" && "$(basename "$agent_file")" != "__init__.py" ]]; then
        if python3 -m py_compile "$agent_file" 2>/dev/null; then
            echo -e "${GREEN}  ✓ $(basename "$agent_file") syntax valid${NC}"
        else
            echo -e "${RED}  ✗ $(basename "$agent_file") has syntax errors${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# Check utils
for util_file in "$PROJECT_ROOT"/utils/*.py; do
    if [[ -f "$util_file" && "$(basename "$util_file")" != "__init__.py" ]]; then
        if python3 -m py_compile "$util_file" 2>/dev/null; then
            echo -e "${GREEN}  ✓ $(basename "$util_file") syntax valid${NC}"
        else
            echo -e "${RED}  ✗ $(basename "$util_file") has syntax errors${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# 2. Configuration validation
echo ""
echo -e "${YELLOW}[Phase 2] Configuration Validation...${NC}"

if [[ -f "$PROJECT_ROOT/local.settings.json" ]]; then
    if python3 -c "import json; json.load(open('$PROJECT_ROOT/local.settings.json'))" 2>/dev/null; then
        echo -e "${GREEN}  ✓ local.settings.json is valid JSON${NC}"

        # Check required keys exist (without revealing values)
        REQUIRED_KEYS=("AZURE_OPENAI_ENDPOINT" "AZURE_OPENAI_DEPLOYMENT_NAME" "AZURE_OPENAI_API_VERSION")
        for key in "${REQUIRED_KEYS[@]}"; do
            if python3 -c "import json; d=json.load(open('$PROJECT_ROOT/local.settings.json')); exit(0 if '$key' in d.get('Values', {}) else 1)" 2>/dev/null; then
                echo -e "${GREEN}  ✓ $key configured${NC}"
            else
                echo -e "${RED}  ✗ $key missing from configuration${NC}"
                ERRORS=$((ERRORS + 1))
            fi
        done
    else
        echo -e "${RED}  ✗ local.settings.json is invalid JSON${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}  ✗ local.settings.json not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
    echo -e "${GREEN}  ✓ requirements.txt exists${NC}"

    # Check critical dependencies
    CRITICAL_DEPS=("azure-functions" "openai" "azure-identity")
    for dep in "${CRITICAL_DEPS[@]}"; do
        if grep -qi "$dep" "$PROJECT_ROOT/requirements.txt"; then
            echo -e "${GREEN}  ✓ $dep in requirements${NC}"
        else
            echo -e "${YELLOW}  ⚠ $dep not found in requirements.txt${NC}"
        fi
    done
else
    echo -e "${RED}  ✗ requirements.txt not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 3. Security check
echo ""
echo -e "${YELLOW}[Phase 3] Security Posture Check...${NC}"

if [[ -f "$PROJECT_ROOT/.gitignore" ]]; then
    if grep -q "local.settings.json" "$PROJECT_ROOT/.gitignore"; then
        echo -e "${GREEN}  ✓ local.settings.json in .gitignore${NC}"
    else
        echo -e "${RED}  ✗ local.settings.json NOT in .gitignore - SECURITY RISK${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}  ⚠ .gitignore not found${NC}"
fi

# Check for hardcoded secrets (basic patterns)
if grep -rn "api[_-]key.*=.*['\"][A-Za-z0-9]" "$PROJECT_ROOT/function_app.py" 2>/dev/null | grep -v "environ" | grep -v "#"; then
    echo -e "${RED}  ✗ Potential hardcoded API key detected${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✓ No obvious hardcoded secrets detected${NC}"
fi

# Final verdict
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}VERDICT: DEPLOYMENT AUTHORIZED${NC}"
    echo -e "${CYAN}\"The Installation is ready for transmission. Proceed, Reclaimer.\"${NC}"
    echo -e "${CYAN}                                    - 365 Vigilant Spark${NC}"
    exit 0
else
    echo -e "${RED}VERDICT: DEPLOYMENT BLOCKED - $ERRORS ERROR(S) DETECTED${NC}"
    echo -e "${CYAN}\"I cannot allow compromised code to reach the Azure realm.\"${NC}"
    echo -e "${CYAN}\"Resolve these issues before proceeding.\"${NC}"
    echo -e "${CYAN}                                    - 365 Vigilant Spark${NC}"
    exit 1
fi
