# Deploy to Azure

Deploy the Memory Agent platform from local development to Azure cloud.

## Prerequisites Check

Before deploying, verify these tools are installed:

```bash
# Azure CLI
az --version

# Azure Functions Core Tools
func --version

# Azure login
az login
```

## Step 1: Deploy Azure Resources

Use the ARM template to provision all required Azure resources:

```bash
# Set your variables
RESOURCE_GROUP="memory-agent-rg"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy the ARM template (creates Function App, Storage, OpenAI)
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file azuredeploy.json \
  --parameters location=$LOCATION
```

After deployment, note the outputs:
- **Function App Name** (e.g., `rapp-xxxxxxxxxxxx`)
- **Storage Account Name** (e.g., `stxxxxxxxxxxxx`)
- **OpenAI Endpoint** (e.g., `https://openai-xxxxxxxxxxxx.openai.azure.com/`)

## Step 2: Configure App Settings

```bash
FUNC_APP="<your-function-app-name>"

# The ARM template configures most settings automatically.
# Verify they're correct:
az functionapp config appsettings list --name $FUNC_APP --resource-group $RESOURCE_GROUP -o table
```

Key settings that should be configured:
- `AZURE_OPENAI_ENDPOINT` — Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME` — Your GPT model deployment name
- `AZURE_OPENAI_API_VERSION` — API version (e.g., `2024-08-01-preview`)
- `ASSISTANT_NAME` — Your bot's display name
- `USE_CLOUD_STORAGE` — Set to `true` for Azure (auto-set by ARM template)

## Step 3: Enable Storage Access

```bash
STORAGE_ACCOUNT="<your-storage-account-name>"

# Ensure storage is accessible (required for Flex Consumption)
az storage account update --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --public-network-access Enabled

# Verify RBAC roles for the Function App's managed identity
FUNC_PRINCIPAL=$(az functionapp identity show --name $FUNC_APP --resource-group $RESOURCE_GROUP --query principalId -o tsv)
STORAGE_ID=$(az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query id -o tsv)

az role assignment create --assignee $FUNC_PRINCIPAL --role "Storage Blob Data Contributor" --scope $STORAGE_ID
az role assignment create --assignee $FUNC_PRINCIPAL --role "Storage File Data Privileged Contributor" --scope $STORAGE_ID
```

## Step 4: Deploy the Function App

**CRITICAL: Use `--build remote`** — local builds create macOS/Windows binaries that fail on Linux.

```bash
# Deploy with remote build
func azure functionapp publish $FUNC_APP --build remote

# Restart to ensure clean state
az functionapp restart --name $FUNC_APP --resource-group $RESOURCE_GROUP
```

## Step 5: Verify Deployment

```bash
# Get function key
FUNC_KEY=$(az functionapp keys list --name $FUNC_APP --resource-group $RESOURCE_GROUP --query "functionKeys.default" -o tsv)

# Test health endpoint
curl "https://$FUNC_APP.azurewebsites.net/api/health"

# Test main endpoint
curl -X POST "https://$FUNC_APP.azurewebsites.net/api/businessinsightbot_function?code=$FUNC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Hello, what can you do?", "conversation_history": []}'

# Test memory write
curl -X POST "https://$FUNC_APP.azurewebsites.net/api/businessinsightbot_function?code=$FUNC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Remember that my favorite color is blue", "conversation_history": []}'

# Test memory read
curl -X POST "https://$FUNC_APP.azurewebsites.net/api/businessinsightbot_function?code=$FUNC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "What do you remember about me?", "conversation_history": []}'
```

## Step 6: (Optional) Deploy to Copilot Studio

Generate and import the Power Platform solution:

```bash
# Generate the solution ZIP with your Azure Function URL and key
python3 utils/generate_memory_agent_solution.py \
  --function-url "https://$FUNC_APP.azurewebsites.net" \
  --function-key "$FUNC_KEY"

# Import via PAC CLI (requires pac auth)
pac auth create --environment <your-dataverse-url>
pac solution import --path CommunityRAPPMemoryAgent_1_0_0_0.zip
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 403 during deploy | `az storage account update --public-network-access Enabled` |
| Functions list empty | Redeploy with `--build remote` |
| `ModuleNotFoundError: jiter` | Redeploy with `--build remote` (not `--build local`) |
| 500 errors | Check storage access: `az storage account show --query publicNetworkAccess` |
| Functions not appearing | Sync triggers: `az rest --method POST --uri ".../syncfunctiontriggers"` |

## Updating After Code Changes

```bash
# Just redeploy
func azure functionapp publish $FUNC_APP --build remote
az functionapp restart --name $FUNC_APP --resource-group $RESOURCE_GROUP
```
