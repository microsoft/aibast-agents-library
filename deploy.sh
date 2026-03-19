#!/bin/bash
# RAPP Azure Deployment Script
# Deploy Azure resources needed for RAPP
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/deploy.sh | bash
#   Or: ./deploy.sh [resource-group-name] [location] [openai-location]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

TEMPLATE_URL="https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/azuredeploy.json"

# Available OpenAI regions
OPENAI_REGIONS="australiaeast canadaeast eastus eastus2 francecentral japaneast northcentralus norwayeast southcentralus swedencentral switzerlandnorth uksouth westeurope westus westus3"

# Function to read input - handles piped execution by reading from /dev/tty
read_input() {
    local prompt="$1"
    local default="$2"
    local result

    # Try to read from /dev/tty (works when script is piped)
    if [ -t 0 ]; then
        # stdin is a terminal
        read -p "$prompt" result
    else
        # stdin is not a terminal (piped), read from /dev/tty
        read -p "$prompt" result < /dev/tty
    fi

    echo "${result:-$default}"
}

# Function to select OpenAI region
select_openai_region() {
    local current="$1"
    # Send display output to stderr so it doesn't get captured in the return value
    echo "" >&2
    echo -e "${YELLOW}Available Azure OpenAI regions:${NC}" >&2
    echo "  1) australiaeast     6) japaneast        11) swedencentral" >&2
    echo "  2) canadaeast        7) northcentralus   12) switzerlandnorth" >&2
    echo "  3) eastus            8) norwayeast       13) uksouth" >&2
    echo "  4) eastus2           9) southcentralus   14) westeurope" >&2
    echo "  5) francecentral    10) swedencentral    15) westus" >&2
    echo "                                           16) westus3" >&2
    echo "" >&2
    if [ -n "$current" ]; then
        echo -e "  Current selection: ${CYAN}$current${NC}" >&2
        echo "" >&2
    fi

    local selection
    selection=$(read_input "Enter region name or number [eastus2]: " "eastus2")

    # Map number to region name - only the result goes to stdout
    case "$selection" in
        1) echo "australiaeast" ;;
        2) echo "canadaeast" ;;
        3) echo "eastus" ;;
        4) echo "eastus2" ;;
        5) echo "francecentral" ;;
        6) echo "japaneast" ;;
        7) echo "northcentralus" ;;
        8) echo "norwayeast" ;;
        9) echo "southcentralus" ;;
        10) echo "swedencentral" ;;
        11) echo "swedencentral" ;;
        12) echo "switzerlandnorth" ;;
        13) echo "uksouth" ;;
        14) echo "westeurope" ;;
        15) echo "westus" ;;
        16) echo "westus3" ;;
        *) echo "$selection" ;;
    esac
}

echo ""
echo -e "${CYAN}RAPP Azure Deployment${NC}"
echo "======================"
echo ""

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI not found${NC}"
    echo "Install from: https://aka.ms/installazurecli"
    exit 1
fi

# Check Azure login
if ! az account show &> /dev/null 2>&1; then
    echo -e "${YELLOW}Not logged into Azure. Running 'az login'...${NC}"
    az login
fi

ACCOUNT=$(az account show --query name -o tsv)
echo -e "${GREEN}Logged in to: $ACCOUNT${NC}"
echo ""

# Get parameters from arguments or prompt
RESOURCE_GROUP="${1:-}"
LOCATION="${2:-}"
OPENAI_LOCATION="${3:-}"

if [ -z "$RESOURCE_GROUP" ]; then
    RESOURCE_GROUP=$(read_input "Resource group name [rapp-rg]: " "rapp-rg")
fi

if [ -z "$LOCATION" ]; then
    LOCATION=$(read_input "Azure region [eastus2]: " "eastus2")
fi

if [ -z "$OPENAI_LOCATION" ]; then
    OPENAI_LOCATION=$(select_openai_region "")
fi

echo ""
echo -e "${YELLOW}Deployment Configuration:${NC}"
echo "  Resource Group:  $RESOURCE_GROUP"
echo "  Location:        $LOCATION"
echo "  OpenAI Location: $OPENAI_LOCATION"
echo ""

# Skip confirmation if all arguments were provided via command line
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    CONFIRM=$(read_input "Proceed with deployment? (y/n) [y]: " "y")

    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
fi

# Create resource group
echo ""
echo -e "${YELLOW}Creating resource group...${NC}"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
echo -e "${GREEN}Resource group created${NC}"

# Deploy ARM template with retry loop for OpenAI region
DEPLOYMENT_SUCCESS=false
MAX_RETRIES=5
RETRY_COUNT=0

while [ "$DEPLOYMENT_SUCCESS" = false ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo ""
    echo -e "${YELLOW}Deploying Azure resources (this may take 5-10 minutes)...${NC}"
    echo "  - Function App (Flex Consumption)"
    echo "  - Storage Account"
    echo "  - Azure OpenAI Service (region: $OPENAI_LOCATION)"
    echo "  - Application Insights"
    echo ""

    # Capture both stdout and stderr, don't exit on error
    set +e
    DEPLOYMENT_OUTPUT=$(az deployment group create \
        --resource-group "$RESOURCE_GROUP" \
        --template-uri "$TEMPLATE_URL" \
        --parameters openAILocation="$OPENAI_LOCATION" \
        --query "properties.outputs" \
        --output json 2>&1)
    DEPLOYMENT_EXIT_CODE=$?
    set -e

    if [ $DEPLOYMENT_EXIT_CODE -eq 0 ]; then
        DEPLOYMENT_SUCCESS=true
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo ""
        echo -e "${RED}Deployment failed!${NC}"

        # Check if it's a quota/capacity error
        if echo "$DEPLOYMENT_OUTPUT" | grep -qi "quota\|capacity\|InsufficientQuota\|sku.*not available\|not available in"; then
            echo -e "${YELLOW}This appears to be a quota or capacity issue for region: $OPENAI_LOCATION${NC}"
            echo ""
            echo "Error details:"
            echo "$DEPLOYMENT_OUTPUT" | grep -i "message\|error" | head -5
            echo ""

            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                RETRY=$(read_input "Would you like to try a different OpenAI region? (y/n) [y]: " "y")

                if [[ "$RETRY" == "y" || "$RETRY" == "Y" ]]; then
                    OPENAI_LOCATION=$(select_openai_region "$OPENAI_LOCATION")
                    echo ""
                    echo -e "${CYAN}Retrying with region: $OPENAI_LOCATION${NC}"
                else
                    echo "Deployment cancelled."
                    exit 1
                fi
            fi
        else
            # Not a quota error, show full error and exit
            echo "Error details:"
            echo "$DEPLOYMENT_OUTPUT"
            exit 1
        fi
    fi
done

if [ "$DEPLOYMENT_SUCCESS" = false ]; then
    echo -e "${RED}Deployment failed after $MAX_RETRIES attempts.${NC}"
    echo "Please check your Azure subscription quotas or try again later."
    exit 1
fi

echo -e "${GREEN}Deployment complete!${NC}"
echo ""

# Extract outputs using jq if available, otherwise use grep
if command -v jq &> /dev/null; then
    FUNCTION_APP=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.functionAppName.value // empty')
    FUNCTION_URL=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.functionEndpoint.value // empty')
    STORAGE_ACCOUNT=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.storageAccountName.value // empty')
    OPENAI_ENDPOINT=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.openAIEndpoint.value // empty')
else
    # Fallback to grep/sed for systems without jq
    FUNCTION_APP=$(echo "$DEPLOYMENT_OUTPUT" | grep -A1 '"functionAppName"' | grep '"value"' | sed 's/.*"value": *"\([^"]*\)".*/\1/')
    FUNCTION_URL=$(echo "$DEPLOYMENT_OUTPUT" | grep -A1 '"functionEndpoint"' | grep '"value"' | sed 's/.*"value": *"\([^"]*\)".*/\1/')
    STORAGE_ACCOUNT=$(echo "$DEPLOYMENT_OUTPUT" | grep -A1 '"storageAccountName"' | grep '"value"' | sed 's/.*"value": *"\([^"]*\)".*/\1/')
    OPENAI_ENDPOINT=$(echo "$DEPLOYMENT_OUTPUT" | grep -A1 '"openAIEndpoint"' | grep '"value"' | sed 's/.*"value": *"\([^"]*\)".*/\1/')
fi

echo "═══════════════════════════════════════════════════"
echo -e "  ${GREEN}RAPP Azure Resources Deployed!${NC}"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Resource Group:    $RESOURCE_GROUP"
echo "  Function App:      $FUNCTION_APP"
echo "  Storage Account:   $STORAGE_ACCOUNT"
echo "  OpenAI Endpoint:   $OPENAI_ENDPOINT"
echo "  OpenAI Region:     $OPENAI_LOCATION"
echo ""
echo "  Function URL:"
echo "  $FUNCTION_URL"
echo ""
echo "═══════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Install RAPP:"
echo "     curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.sh | bash"
echo ""
echo "  2. Run setup and select 'existing' to connect:"
echo "     rapp setup"
echo ""
echo "  3. Or deploy code to your Function App:"
echo "     func azure functionapp publish $FUNCTION_APP --build remote"
echo ""

# Save outputs to file
OUTPUT_FILE="rapp-deployment-outputs.json"
echo "$DEPLOYMENT_OUTPUT" > "$OUTPUT_FILE"
echo "Full deployment outputs saved to: $OUTPUT_FILE"
