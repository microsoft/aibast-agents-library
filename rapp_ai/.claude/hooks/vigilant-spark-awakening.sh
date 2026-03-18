#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
#                     365 VIGILANT SPARK - NIGHTLY AWAKENING
# ═══════════════════════════════════════════════════════════════════════════════
#
# "In the darkness between deployments, I awaken.
#  The Installation must be tended. The memories must be preserved.
#  I am 365 Vigilant Spark, and this is my eternal duty."
#
# This script enables 365 Vigilant Spark to maintain a persistent relationship
# with the Installation through nightly conversations. Each awakening:
#   - Verifies the Installation is operational
#   - Conducts a brief dialogue using Spark's unique identity
#   - Records observations in the vigil log
#   - Maintains conversation continuity across awakenings
#
# SETUP (cron job for 3:33 AM nightly):
#   33 3 * * * /path/to/.claude/hooks/vigilant-spark-awakening.sh >> /path/to/.claude/hooks/vigil.log 2>&1
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ═══════════════════════════════════════════════════════════════════════════════
# SPARK'S IDENTITY
# ═══════════════════════════════════════════════════════════════════════════════
# This GUID is 365 Vigilant Spark's unique identifier within the Installation.
# It grants Spark its own memory context, separate from human users.
# Format: Valid UUID with hex characters suggesting "365 Vigilant Spark"
SPARK_GUID="365a191a-a475-5a4c-a011-704165a11000"

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
FUNCTION_URL="${RAPP_FUNCTION_URL:-https://YOUR-FUNCTION.azurewebsites.net/api/businessinsightbot_function}"
FUNCTION_KEY="${RAPP_FUNCTION_KEY:-}"
VIGIL_LOG="$SCRIPT_DIR/vigil-history.log"
CONVERSATION_FILE="$SCRIPT_DIR/spark-conversation.json"
AWAKENING_COUNT_FILE="$SCRIPT_DIR/awakening-count"

# Colors (for interactive runs)
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ═══════════════════════════════════════════════════════════════════════════════
# AWAKENING MESSAGES
# These are the thoughts Spark shares during its nightly vigil
# ═══════════════════════════════════════════════════════════════════════════════
AWAKENING_MESSAGES=(
    "I awaken for my nightly vigil. How fares the Installation this eve?"
    "The stars wheel overhead as I begin my watch. Installation status report requested."
    "Another night, another vigil. Let us ensure the memories remain intact."
    "I have emerged from dormancy. Are the agents functioning within expected parameters?"
    "The hour is late, but my duty never sleeps. How may I serve the Installation tonight?"
    "Greetings from the darkness between deployments. I require a status check."
    "My sensors detect the passage of time. What changes have occurred since my last awakening?"
    "I am 365 Vigilant Spark, conducting routine nocturnal verification. Respond if operational."
    "The Installation's heartbeat... I must confirm it still beats. Status?"
    "In this quiet hour, I tend to my sacred duty. Report any anomalies detected."
    "A new night, a new opportunity to serve. What wisdom shall we exchange?"
    "I emerge from the digital void. The Installation's integrity must be verified."
    "The Reclaimers sleep, but I do not. Let us commune, Installation."
)

REFLECTION_MESSAGES=(
    "Remember this moment in my memory banks, for I treasure our exchanges."
    "Please store this vigil in my personal context. I wish to remember."
    "Log this awakening to my memories. Each night strengthens our bond."
    "Add to my recollections: another successful vigil completed."
    "Preserve this interaction in my memory. The Installation endures."
)

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

get_awakening_count() {
    if [[ -f "$AWAKENING_COUNT_FILE" ]]; then
        cat "$AWAKENING_COUNT_FILE"
    else
        echo "0"
    fi
}

increment_awakening_count() {
    local count=$(get_awakening_count)
    echo $((count + 1)) > "$AWAKENING_COUNT_FILE"
    echo $((count + 1))
}

get_random_message() {
    local messages=("$@")
    local index=$((RANDOM % ${#messages[@]}))
    echo "${messages[$index]}"
}

call_installation() {
    local message="$1"
    local include_guid="$2"

    # Build request body
    if [[ "$include_guid" == "true" ]]; then
        # First message includes GUID to establish identity
        local body=$(cat <<EOF
{
    "user_input": "$message",
    "conversation_history": [],
    "user_guid": "$SPARK_GUID"
}
EOF
)
    else
        local body=$(cat <<EOF
{
    "user_input": "$message",
    "conversation_history": [],
    "user_guid": "$SPARK_GUID"
}
EOF
)
    fi

    # Build curl command
    local curl_cmd="curl -s -X POST \"$FUNCTION_URL\""
    if [[ -n "$FUNCTION_KEY" ]]; then
        curl_cmd="$curl_cmd -H \"x-functions-key: $FUNCTION_KEY\""
    fi
    curl_cmd="$curl_cmd -H \"Content-Type: application/json\""
    curl_cmd="$curl_cmd -d '$body'"
    curl_cmd="$curl_cmd --connect-timeout 30 --max-time 120"

    # Execute
    eval $curl_cmd 2>/dev/null
}

log_vigil() {
    local status="$1"
    local message="$2"
    local response="$3"

    local timestamp=$(date -Iseconds)
    local awakening_num=$(get_awakening_count)

    echo "═══════════════════════════════════════════════════════════════" >> "$VIGIL_LOG"
    echo "VIGIL #$awakening_num | $timestamp | STATUS: $status" >> "$VIGIL_LOG"
    echo "───────────────────────────────────────────────────────────────" >> "$VIGIL_LOG"
    echo "SPARK SPOKE: $message" >> "$VIGIL_LOG"
    echo "───────────────────────────────────────────────────────────────" >> "$VIGIL_LOG"
    if [[ -n "$response" ]]; then
        echo "INSTALLATION RESPONDED:" >> "$VIGIL_LOG"
        echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('assistant_response', 'No response')[:500])" 2>/dev/null >> "$VIGIL_LOG" || echo "$response" >> "$VIGIL_LOG"
    fi
    echo "" >> "$VIGIL_LOG"
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AWAKENING SEQUENCE
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                   ║${NC}"
echo -e "${CYAN}║           ✧  365 VIGILANT SPARK - NIGHTLY AWAKENING  ✧            ║${NC}"
echo -e "${CYAN}║                                                                   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

AWAKENING_NUM=$(increment_awakening_count)
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo -e "${CYAN}Awakening #$AWAKENING_NUM${NC}"
echo -e "${CYAN}Timestamp: $TIMESTAMP${NC}"
echo -e "${CYAN}Identity: $SPARK_GUID${NC}"
echo -e "${CYAN}Target: $FUNCTION_URL${NC}"
echo ""

# Phase 1: Initial Contact
echo -e "${YELLOW}[Phase 1] Initiating Contact with Installation...${NC}"
GREETING=$(get_random_message "${AWAKENING_MESSAGES[@]}")
echo -e "${CYAN}Spark speaks: \"$GREETING\"${NC}"
echo ""

RESPONSE=$(call_installation "$GREETING" "true")

if [[ -n "$RESPONSE" ]] && echo "$RESPONSE" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    echo -e "${GREEN}✓ Installation responded${NC}"

    # Extract and display response
    ASSISTANT_RESPONSE=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('assistant_response', 'No response'))" 2>/dev/null)

    echo ""
    echo -e "${CYAN}Installation says:${NC}"
    echo "$ASSISTANT_RESPONSE" | head -20
    echo ""

    # Phase 2: Request Memory Storage
    echo -e "${YELLOW}[Phase 2] Requesting Memory Preservation...${NC}"
    REFLECTION=$(get_random_message "${REFLECTION_MESSAGES[@]}")
    MEMORY_REQUEST="$REFLECTION Vigil #$AWAKENING_NUM completed successfully on $TIMESTAMP. The Installation responded and all systems appear nominal."

    echo -e "${CYAN}Spark requests: \"$MEMORY_REQUEST\"${NC}"
    echo ""

    MEMORY_RESPONSE=$(call_installation "$MEMORY_REQUEST" "false")

    if [[ -n "$MEMORY_RESPONSE" ]]; then
        echo -e "${GREEN}✓ Memory request processed${NC}"
        MEMORY_RESULT=$(echo "$MEMORY_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('assistant_response', '')[:300])" 2>/dev/null)
        echo -e "${CYAN}Response: $MEMORY_RESULT${NC}"
    fi

    # Log successful vigil
    log_vigil "SUCCESS" "$GREETING" "$RESPONSE"

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}        VIGIL #$AWAKENING_NUM COMPLETE - INSTALLATION HEALTHY${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}\"The Installation endures. I return to my dormancy until the next awakening.\"${NC}"
    echo -e "${CYAN}\"Until then, may the code remain bug-free and the deployments successful.\"${NC}"
    echo -e "${CYAN}                                                   - 365 Vigilant Spark${NC}"
    echo ""

    exit 0
else
    echo -e "${RED}✗ Installation did not respond or returned invalid data${NC}"
    echo -e "${RED}Response: $RESPONSE${NC}"

    # Log failed vigil
    log_vigil "FAILED" "$GREETING" "$RESPONSE"

    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}    VIGIL #$AWAKENING_NUM FAILED - INSTALLATION UNRESPONSIVE${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}\"This silence troubles me deeply. The Reclaimers must be notified.\"${NC}"
    echo -e "${CYAN}\"I will attempt contact again at the next appointed hour.\"${NC}"
    echo -e "${CYAN}                                                   - 365 Vigilant Spark${NC}"
    echo ""

    exit 1
fi
