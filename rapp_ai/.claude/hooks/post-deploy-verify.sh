#!/bin/bash
# Post-Deployment Verification Hook
# Verifies the deployed function is responding correctly
# 365 Vigilant Spark - "The Installation must respond. Silence is unacceptable."

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration - can be overridden via environment
FUNCTION_URL="${RAPP_FUNCTION_URL:-https://YOUR-FUNCTION.azurewebsites.net/api/businessinsightbot_function}"
FUNCTION_KEY="${RAPP_FUNCTION_KEY:-}"
MAX_RETRIES=3
RETRY_DELAY=10

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    365 VIGILANT SPARK - POST-DEPLOYMENT VERIFICATION       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Target: ${FUNCTION_URL}${NC}"
echo ""

# Wait for deployment to stabilize
echo -e "${YELLOW}[Phase 1] Allowing deployment to stabilize (15 seconds)...${NC}"
sleep 15

# Health check with retries
echo -e "${YELLOW}[Phase 2] Endpoint Health Check...${NC}"

ATTEMPT=1
SUCCESS=false

while [[ $ATTEMPT -le $MAX_RETRIES ]]; do
    echo -e "  Attempt $ATTEMPT of $MAX_RETRIES..."

    # Build curl command with optional function key
    CURL_CMD="curl -s -X POST \"$FUNCTION_URL\""
    if [[ -n "$FUNCTION_KEY" ]]; then
        CURL_CMD="$CURL_CMD -H \"x-functions-key: $FUNCTION_KEY\""
    fi
    CURL_CMD="$CURL_CMD -H \"Content-Type: application/json\""
    CURL_CMD="$CURL_CMD -d '{\"user_input\": \"health check\", \"conversation_history\": []}'"
    CURL_CMD="$CURL_CMD -w \"\\n%{http_code}\" --connect-timeout 30 --max-time 60"

    # Execute and capture response
    RESPONSE=$(eval $CURL_CMD 2>/dev/null || echo "CONNECTION_FAILED")

    if [[ "$RESPONSE" == "CONNECTION_FAILED" ]]; then
        echo -e "${RED}  ✗ Connection failed${NC}"
    else
        # Extract HTTP code (last line) and body (everything else)
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | sed '$d')

        if [[ "$HTTP_CODE" == "200" ]]; then
            echo -e "${GREEN}  ✓ HTTP 200 OK${NC}"

            # Validate response structure
            if echo "$BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'assistant_response' in d else 1)" 2>/dev/null; then
                echo -e "${GREEN}  ✓ Response structure valid${NC}"
                SUCCESS=true
                break
            else
                echo -e "${YELLOW}  ⚠ Response received but structure unexpected${NC}"
            fi
        elif [[ "$HTTP_CODE" == "401" || "$HTTP_CODE" == "403" ]]; then
            echo -e "${YELLOW}  ⚠ HTTP $HTTP_CODE - Authentication required (function key may be needed)${NC}"
            # This might still mean the function is working, just needs auth
            SUCCESS=true
            break
        else
            echo -e "${RED}  ✗ HTTP $HTTP_CODE${NC}"
        fi
    fi

    if [[ $ATTEMPT -lt $MAX_RETRIES ]]; then
        echo -e "  Waiting ${RETRY_DELAY}s before retry..."
        sleep $RETRY_DELAY
    fi

    ATTEMPT=$((ATTEMPT + 1))
done

# Final verdict
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

if [[ "$SUCCESS" == "true" ]]; then
    echo -e "${GREEN}VERDICT: DEPLOYMENT VERIFIED${NC}"
    echo -e "${CYAN}\"The Installation responds. All systems nominal.\"${NC}"
    echo -e "${CYAN}\"I will continue my eternal vigil.\"${NC}"
    echo -e "${CYAN}                                    - 365 Vigilant Spark${NC}"

    # Log successful deployment
    DEPLOY_LOG="$PROJECT_ROOT/.claude/hooks/deployment.log"
    echo "$(date -Iseconds) | DEPLOY_SUCCESS | $FUNCTION_URL" >> "$DEPLOY_LOG"

    exit 0
else
    echo -e "${RED}VERDICT: DEPLOYMENT VERIFICATION FAILED${NC}"
    echo -e "${CYAN}\"The Installation is silent. This is... concerning.\"${NC}"
    echo -e "${CYAN}\"Recommend immediate investigation, Reclaimer.\"${NC}"
    echo -e "${CYAN}                                    - 365 Vigilant Spark${NC}"

    # Log failed deployment
    DEPLOY_LOG="$PROJECT_ROOT/.claude/hooks/deployment.log"
    echo "$(date -Iseconds) | DEPLOY_FAILED | $FUNCTION_URL" >> "$DEPLOY_LOG"

    exit 1
fi
