#!/bin/bash
# Tests for RAPP Brainstem installer and server
# Run: bash tests/test_installer.sh

set -e
PASS=0
FAIL=0
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1"; }

echo "=== RAPP Brainstem Tests ==="
echo ""

# ── install.sh tests ──────────────────────────────────────────────────────────

echo "--- install.sh ---"

if bash -n "$REPO_ROOT/install.sh" 2>/dev/null; then
    pass "install.sh is valid bash"
else
    fail "install.sh has syntax errors"
fi

if grep -q "RAPP Brainstem" "$REPO_ROOT/install.sh"; then
    pass "install.sh has brainstem branding"
else
    fail "install.sh missing brainstem branding"
fi

if grep -q '\.brainstem' "$REPO_ROOT/install.sh" && ! grep -q 'RAPP_HOME=.*\.rapp"' "$REPO_ROOT/install.sh"; then
    pass "install.sh targets ~/.brainstem"
else
    fail "install.sh should target ~/.brainstem"
fi

if grep -q 'BRAINSTEM_BIN.*local/bin' "$REPO_ROOT/install.sh" && grep -q 'brainstem.*WRAPPER' "$REPO_ROOT/install.sh"; then
    pass "install.sh creates brainstem CLI"
else
    fail "install.sh should create brainstem CLI wrapper"
fi

if grep -q 'rapp-installer.git' "$REPO_ROOT/install.sh" && ! grep -q 'RAPPAI' "$REPO_ROOT/install.sh"; then
    pass "install.sh clones public repo"
else
    fail "install.sh should clone public rapp-installer repo"
fi

echo ""

# ── install.ps1 tests ────────────────────────────────────────────────────────

echo "--- install.ps1 ---"

if grep -q "RAPP Brainstem" "$REPO_ROOT/install.ps1"; then
    pass "install.ps1 has brainstem branding"
else
    fail "install.ps1 missing brainstem branding"
fi

if grep -q '\.brainstem' "$REPO_ROOT/install.ps1"; then
    pass "install.ps1 targets ~/.brainstem"
else
    fail "install.ps1 should target ~/.brainstem"
fi

echo ""

# ── install.cmd tests ────────────────────────────────────────────────────────

echo "--- install.cmd ---"

if grep -qi "brainstem" "$REPO_ROOT/install.cmd"; then
    pass "install.cmd references brainstem"
else
    fail "install.cmd should reference brainstem"
fi

echo ""

# ── skill.md tests ────────────────────────────────────────────────────────────

echo "--- skill.md ---"

if head -1 "$REPO_ROOT/skill.md" | grep -q '^---'; then
    pass "skill.md has YAML frontmatter"
else
    fail "skill.md missing YAML frontmatter"
fi

TIER_COUNT=$(grep -c "## .* Tier" "$REPO_ROOT/skill.md" || true)
if [ "$TIER_COUNT" -ge 3 ]; then
    pass "skill.md has all 3 tiers"
else
    fail "skill.md missing tier content (found $TIER_COUNT)"
fi

PAUSE_COUNT=$(grep -c "⏸️" "$REPO_ROOT/skill.md" || true)
if [ "$PAUSE_COUNT" -ge 3 ]; then
    pass "skill.md has $PAUSE_COUNT pause points"
else
    fail "skill.md needs at least 3 pause points (found $PAUSE_COUNT)"
fi

if grep -q 'state.json' "$REPO_ROOT/skill.md"; then
    pass "skill.md saves state to disk"
else
    fail "skill.md should save state like Moltbook pattern"
fi

if grep -q "Do not proceed" "$REPO_ROOT/skill.md"; then
    pass "skill.md gates tier progression"
else
    fail "skill.md should gate tier progression"
fi

echo ""

# ── index.html tests ─────────────────────────────────────────────────────────

echo "--- index.html ---"

if grep -q "Brainstem" "$REPO_ROOT/index.html" && grep -q "Spinal Cord" "$REPO_ROOT/index.html" && grep -q "Nervous System" "$REPO_ROOT/index.html"; then
    pass "index.html has all 3 tiers"
else
    fail "index.html missing tier content"
fi

if grep -q "curl -fsSL" "$REPO_ROOT/index.html"; then
    pass "index.html has one-liner install command"
else
    fail "index.html missing one-liner"
fi

if grep -q "localhost:7071" "$REPO_ROOT/index.html"; then
    pass "index.html has health check"
else
    fail "index.html missing health check"
fi

echo ""

# ── README.md tests ───────────────────────────────────────────────────────────

echo "--- README.md ---"

if head -5 "$REPO_ROOT/README.md" | grep -q "Brainstem"; then
    pass "README.md leads with brainstem"
else
    fail "README.md should lead with brainstem"
fi

if grep -q "curl -fsSL" "$REPO_ROOT/README.md"; then
    pass "README.md has one-liner"
else
    fail "README.md missing one-liner"
fi

if grep -q "Tier 1" "$REPO_ROOT/README.md" && grep -q "Tier 2" "$REPO_ROOT/README.md" && grep -q "Tier 3" "$REPO_ROOT/README.md"; then
    pass "README.md has all 3 tiers"
else
    fail "README.md missing tier content"
fi

echo ""

# ── copilot-instructions.md tests ────────────────────────────────────────────

echo "--- .github/copilot-instructions.md ---"

if grep -q "Brainstem" "$REPO_ROOT/.github/copilot-instructions.md" && grep -q "Spinal Cord" "$REPO_ROOT/.github/copilot-instructions.md"; then
    pass "copilot-instructions.md has progressive architecture"
else
    fail "copilot-instructions.md missing progressive architecture"
fi

if grep -q "pytest" "$REPO_ROOT/.github/copilot-instructions.md"; then
    pass "copilot-instructions.md has test commands"
else
    fail "copilot-instructions.md missing test commands"
fi

echo ""

# ── brainstem server tests ────────────────────────────────────────────────────

echo "--- brainstem server ---"

if [ -f "$REPO_ROOT/rapp_brainstem/requirements.txt" ]; then
    pass "requirements.txt exists"
else
    fail "requirements.txt missing"
fi

for endpoint in "/chat" "/health" "/login" "/models" "/repos"; do
    if grep -q "\"$endpoint\"" "$REPO_ROOT/rapp_brainstem/brainstem.py"; then
        pass "brainstem.py has $endpoint endpoint"
    else
        fail "brainstem.py missing $endpoint endpoint"
    fi
done

if grep -q "def perform" "$REPO_ROOT/rapp_brainstem/basic_agent.py" && grep -q "def to_tool" "$REPO_ROOT/rapp_brainstem/basic_agent.py"; then
    pass "basic_agent.py has perform() and to_tool()"
else
    fail "basic_agent.py missing required methods"
fi

echo ""

# ── onboarding agent tests ───────────────────────────────────────────────────

echo "--- onboarding agent ---"

if grep -q "OnboardingGuide" "$REPO_ROOT/rapp_brainstem/agents/hello_agent.py"; then
    pass "onboarding agent has OnboardingGuide class"
else
    fail "onboarding agent missing OnboardingGuide class"
fi

if grep -q "skill.md" "$REPO_ROOT/rapp_brainstem/agents/hello_agent.py"; then
    pass "onboarding agent reads skill.md"
else
    fail "onboarding agent should read skill.md"
fi

if grep -q "state.json" "$REPO_ROOT/rapp_brainstem/agents/hello_agent.py"; then
    pass "onboarding agent reads saved state"
else
    fail "onboarding agent should read user progress state"
fi

# Test that the agent actually loads and runs
AGENT_TEST=$(cd "$REPO_ROOT/rapp_brainstem" && python3 -c "
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
sys.path.insert(0, '.')
from agents.hello_agent import OnboardingAgent
a = OnboardingAgent()
assert a.name == 'OnboardingGuide'
tool = a.to_tool()
assert tool['type'] == 'function'
result = a.perform(topic='overview')
assert 'Tier 1' in result and 'Tier 2' in result and 'Tier 3' in result
result = a.perform(topic='agents')
assert 'BasicAgent' in result
result = a.perform(topic='next')
assert len(result) > 0
result = a.perform(topic='install')
assert 'skill.md' in result and 'curl' in result and 'irm' in result
print('ok')
" 2>&1)
if [ "$AGENT_TEST" = "ok" ]; then
    pass "onboarding agent loads, runs, and returns correct content"
else
    fail "onboarding agent runtime test failed: $AGENT_TEST"
fi

echo ""

# ── docs/ & tracking tests ───────────────────────────────────────────────────

echo "--- docs & tracking ---"

if [ -f "$REPO_ROOT/docs/index.html" ] && grep -q "Brainstem" "$REPO_ROOT/docs/index.html"; then
    pass "docs/index.html has brainstem content"
else
    fail "docs/index.html missing or stale"
fi

if [ -f "$REPO_ROOT/docs/install.sh" ] && grep -q "brainstem" "$REPO_ROOT/docs/install.sh" -i; then
    pass "docs/install.sh exists for GitHub Pages curl"
else
    fail "docs/install.sh missing (needed for curl one-liner via GitHub Pages)"
fi

if [ ! -f "$REPO_ROOT/docs/copilot-install.html" ]; then
    pass "stale docs/copilot-install.html removed"
else
    fail "docs/copilot-install.html should be removed (stale)"
fi

if grep -q ".brainstem_data" "$REPO_ROOT/.gitignore" && grep -q ".remote_agents" "$REPO_ROOT/.gitignore"; then
    pass ".gitignore excludes runtime artifacts"
else
    fail ".gitignore should exclude .brainstem_data/ and .remote_agents/"
fi

echo ""

# ── unit tests ────────────────────────────────────────────────────────────────

echo "--- unit tests (test_local_agents.py) ---"
cd "$REPO_ROOT/rapp_brainstem"
if python3 -m pytest test_local_agents.py -x --tb=short -q 2>&1; then
    pass "unit tests passed"
else
    fail "unit tests failed"
fi

echo ""

# ── Summary ───────────────────────────────────────────────────────────────────

TOTAL=$((PASS + FAIL))
echo "=== Results: $PASS/$TOTAL passed ==="
if [ "$FAIL" -gt 0 ]; then
    echo "  $FAIL test(s) failed"
    exit 1
else
    echo "  All tests passed! ✓"
    exit 0
fi
