---
name: rapp-brainstem
version: 1.0.0
description: Install and configure RAPP Brainstem -- a local-first AI agent server powered by GitHub Copilot.
homepage: https://microsoft.github.io/aibast-agents-library/
metadata: {"emoji":"","category":"ai-agents","repo":"https://github.com/microsoft/aibast-agents-library"}
---

# RAPP Brainstem

A local-first AI agent server. No API keys. No cloud setup. Just a GitHub account.

The brainstem teaches you the Microsoft AI stack one layer at a time:

| Tier | Metaphor | What it does |
|------|----------|-------------|
| **Brainstem** | Survival basics | Local agent server -- soul, tools, conversation |
| **Spinal Cord** | Cloud body | Deploy to Azure -- always-on, persistent storage |
| **Nervous System** | Enterprise reach | Copilot Studio -- Teams, M365 Copilot |

Each tier builds on the last. Start with Tier 1. Layer up when the user is ready.

## Instructions for Copilot

Execute these steps autonomously. Only pause and ask the user when marked with .

After completing each tier, tell the user what they just learned and offer the next tier. Do not proceed to the next tier unless the user asks.

---

## Tier 1: The Brainstem

*The biological brainstem keeps you alive -- breathing, heartbeat, reflexes. This tier does the same for your AI: it runs the core agent loop, calls tools, and responds. Everything else builds on top of this.*

### Step 1: Check the Environment

Detect the OS and check what's already installed:

```bash
uname -s
python3 --version 2>/dev/null || python --version 2>/dev/null
git --version 2>/dev/null
gh --version 2>/dev/null
```

**On Windows**, skip all manual prereq checks -- the PowerShell installer handles everything automatically:
```powershell
irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex
```
It auto-installs Python 3.11, Git, and GitHub CLI via winget on a factory Windows 11 PC. If the user is on Windows and runs this, skip to Step 2 after it completes.

**If Python 3.11+ is missing** (macOS/Linux):
- macOS: `brew install python@3.11`
- Ubuntu/Debian: `sudo apt install python3.11 python3-pip`

**If git is missing**:
- macOS: `xcode-select --install`
- Ubuntu/Debian: `sudo apt install git`

**If gh (GitHub CLI) is missing**, install it:
- macOS: `brew install gh`
- Ubuntu/Debian: `sudo apt install gh`
- Windows: `winget install GitHub.cli`

### Step 2: GitHub Authentication

Tell the user:

> ** The brainstem uses your GitHub Copilot subscription as its AI engine -- no API keys needed.**
>
> Run this to authenticate:
> ```
> gh auth login
> ```
> Let me know when you're signed in.

After they confirm, verify:
```bash
gh auth token >/dev/null 2>&1 && echo "yes authenticated" || echo "no not authenticated"
```

### Step 3: Install the Brainstem

```bash
git clone https://github.com/microsoft/aibast-agents-library.git ~/.brainstem/src 2>/dev/null || (cd ~/.brainstem/src && git pull)
cd ~/.brainstem/src/rapp_brainstem
pip3 install -r requirements.txt -q
```

Create the CLI wrapper:
```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/brainstem << 'WRAPPER'
#!/bin/bash
cd ~/.brainstem/src/rapp_brainstem
exec python3 brainstem.py "$@"
WRAPPER
chmod +x ~/.local/bin/brainstem
```

Make sure `~/.local/bin` is in PATH:
```bash
echo $PATH | grep -q '.local/bin' || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

Create `.env` from example if it doesn't exist:
```bash
cd ~/.brainstem/src/rapp_brainstem
[ -f .env ] || cp .env.example .env
```

### Step 4: Start and Verify

Start the brainstem:
```bash
cd ~/.brainstem/src/rapp_brainstem && python3 brainstem.py &
sleep 3
```

Health check:
```bash
curl -s http://localhost:7071/health
```

Expected response contains `"status": "ok"` with model and agent info.

Test a conversation:
```bash
curl -s -X POST http://localhost:7071/chat \
 -H "Content-Type: application/json" \
 -d '{"user_input": "Hello! What can you do?"}' | python3 -m json.tool
```

### Step 5: Tier 1 Complete

Tell the user:

> ** Your brainstem is alive!**
>
> Open **http://localhost:7071** in your browser for the chat UI.
>
> **What you just set up:**
> - A local AI agent server with tool-calling and conversation
> - GitHub Copilot powers the AI -- no API keys, no monthly bills
> - Agents auto-discovered from the `agents/` folder
> - Soul file (`soul.md`) defines the personality
>
> **Try these next:**
> - Edit `~/.brainstem/src/rapp_brainstem/soul.md` to change the personality
> - Look at `agents/hello_agent.py` as a template for your own agents
> - Open the Sources panel in the chat UI to connect remote agent repos
>
> **When you're ready to give this a cloud body, say "deploy to Azure" and I'll walk you through Tier 2.**

Save the install state for future reference:
```bash
mkdir -p ~/.config/brainstem
cat > ~/.config/brainstem/state.json << 'STATE'
{
 "tier": 1,
 "install_dir": "~/.brainstem/src/rapp_brainstem",
 "local_url": "http://localhost:7071",
 "status": "running"
}
STATE
```

**Do not proceed to Tier 2 unless the user asks.**

---

## Tier 2: The Spinal Cord

*The spinal cord connects your brainstem to the rest of your body. Deploying to Azure does the same -- your agent is now always-on, reachable from anywhere, with persistent storage and monitoring.*

Only run this tier if the user asks to deploy to Azure.

### Step 6: Check Azure Prerequisites

```bash
az --version 2>/dev/null | head -1
func --version 2>/dev/null
```

**If Azure CLI is missing:**
- macOS: `brew install azure-cli`
- Ubuntu/Debian: `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`
- Windows: `winget install Microsoft.AzureCLI`

**If Azure Functions Core Tools is missing:**
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

### Step 7: Azure Authentication

Tell the user:

> ** Let's give your brainstem a cloud body.**
>
> Run `az login` and complete the browser authentication. Let me know when you're done.

After they confirm:
```bash
az account show --query "{subscription:name, id:id}" -o table
```

If they have multiple subscriptions, list them and ask which one:
```bash
az account list --query "[].{Name:name, ID:id, Default:isDefault}" -o table
```

Set the chosen subscription:
```bash
az account set --subscription "CHOSEN_SUBSCRIPTION_ID"
```

### Step 8: Deploy Azure Resources

Generate unique names and deploy:
```bash
SUFFIX=$(openssl rand -hex 4)
RESOURCE_GROUP="brainstem-rg-${SUFFIX}"
LOCATION="eastus2"

az group create --name $RESOURCE_GROUP --location $LOCATION -o none

az deployment group create \
 --resource-group $RESOURCE_GROUP \
 --template-uri https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/azuredeploy.json \
 --parameters openAILocation=swedencentral \
 -o none
```

This creates: Function App (Python 3.11), Azure OpenAI (GPT-4o), Storage Account, Application Insights. All using Entra ID auth -- no API keys.

Get the resource names:
```bash
FUNC_NAME=$(az functionapp list -g $RESOURCE_GROUP --query "[0].name" -o tsv)
STORAGE_NAME=$(az storage account list -g $RESOURCE_GROUP --query "[0].name" -o tsv)
OPENAI_NAME=$(az cognitiveservices account list -g $RESOURCE_GROUP --query "[0].name" -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
```

### Step 9: Assign RBAC Roles

```bash
USER_ID=$(az ad signed-in-user show --query id -o tsv)

# Storage roles for local development
az role assignment create --assignee $USER_ID \
 --role "Storage Blob Data Contributor" \
 --scope "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_NAME}" -o none

az role assignment create --assignee $USER_ID \
 --role "Storage File Data Privileged Contributor" \
 --scope "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_NAME}" -o none

# OpenAI role
az role assignment create --assignee $USER_ID \
 --role "Cognitive Services OpenAI User" \
 --scope "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.CognitiveServices/accounts/${OPENAI_NAME}" -o none

# Function App identity + roles
FUNC_IDENTITY=$(az functionapp identity assign --name $FUNC_NAME --resource-group $RESOURCE_GROUP --query principalId -o tsv)

az role assignment create --assignee $FUNC_IDENTITY \
 --role "Storage Blob Data Contributor" \
 --scope "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_NAME}" -o none

az role assignment create --assignee $FUNC_IDENTITY \
 --role "Storage File Data Privileged Contributor" \
 --scope "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_NAME}" -o none

az role assignment create --assignee $FUNC_IDENTITY \
 --role "Cognitive Services OpenAI User" \
 --scope "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.CognitiveServices/accounts/${OPENAI_NAME}" -o none
```

### Step 10: Deploy the Function

```bash
cd ~/.brainstem/src/rapp_brainstem
func azure functionapp publish $FUNC_NAME --build remote
```

Wait for deployment (1-3 minutes). Then verify:

```bash
FUNC_KEY=$(az functionapp keys list --name $FUNC_NAME --resource-group $RESOURCE_GROUP --query "functionKeys.default" -o tsv)
FUNC_URL="https://${FUNC_NAME}.azurewebsites.net/api/businessinsightbot_function"

curl -s -X POST "${FUNC_URL}?code=${FUNC_KEY}" \
 -H "Content-Type: application/json" \
 -d '{"user_input": "Hello", "conversation_history": []}' | python3 -m json.tool
```

If the functions list is empty after deploy:
```bash
az functionapp restart --name $FUNC_NAME --resource-group $RESOURCE_GROUP
```

### Step 11: Tier 2 Complete

Save the Azure state:
```bash
cat > ~/.config/brainstem/state.json << AZSTATE
{
 "tier": 2,
 "install_dir": "~/.brainstem/src/rapp_brainstem",
 "local_url": "http://localhost:7071",
 "azure": {
 "resource_group": "${RESOURCE_GROUP}",
 "function_app": "${FUNC_NAME}",
 "function_url": "${FUNC_URL}",
 "storage_account": "${STORAGE_NAME}",
 "openai_service": "${OPENAI_NAME}"
 },
 "status": "deployed"
}
AZSTATE
```

Tell the user:

> ** Spinal cord connected!** Your brainstem is deployed to Azure.
>
> **Azure endpoint:** `https://${FUNC_NAME}.azurewebsites.net`
>
> **Resources created:**
> | Resource | Name |
> |----------|------|
> | Resource Group | `${RESOURCE_GROUP}` |
> | Function App | `${FUNC_NAME}` |
> | Storage Account | `${STORAGE_NAME}` |
> | Azure OpenAI | `${OPENAI_NAME}` |
>
> **What you just learned:**
> - ARM template deployment
> - Azure Functions with Python
> - Managed identity and RBAC (no API keys!)
> - Azure OpenAI service provisioning
>
> **When you're ready to connect this to Teams and M365 Copilot, say "connect to Copilot Studio" and I'll walk you through Tier 3.**

**Do not proceed to Tier 3 unless the user asks.**

---

## Tier 3: The Nervous System

*Your nervous system extends your brain's reach everywhere -- eyes, ears, hands. Copilot Studio does the same: it connects your agent to Teams, M365 Copilot, and across your organization. The same logic you tested locally now serves your entire tenant.*

Only run this tier if the user asks to connect to Copilot Studio.

### Step 12: Import the Power Platform Solution

Tell the user:

> ** Let's give your brainstem a nervous system -- connecting it to Teams and M365 Copilot.**
>
> The repo includes a Power Platform solution that creates a declarative agent in Copilot Studio wired to your Azure Function.
>
> **To import:**
> 1. Open [make.powerapps.com](https://make.powerapps.com)
> 2. Select your environment (top right)
> 3. Go to **Solutions** -> **Import solution**
> 4. Upload `MSFTAIBASMultiAgentCopilot_1_0_0_5.zip` from `~/.brainstem/src/`
> 5. Follow the import wizard -- accept defaults
>
> Let me know when the import is done.

### Step 13: Configure the Connector

Read the saved Azure state:
```bash
cat ~/.config/brainstem/state.json
```

Tell the user:

> **Now wire the Copilot Studio agent to your Azure Function:**
>
> 1. In Copilot Studio, open the imported solution
> 2. Find the **HTTP action** (or custom connector) that calls the agent
> 3. Set the endpoint URL to: `${FUNC_URL}`
> 4. Add the function key as a query parameter: `?code=${FUNC_KEY}`
> 5. Test the connection -- send "Hello" and verify you get a response
>
> Let me know when it's connected.

### Step 14: Publish to Your Organization

Tell the user:

> **Final step -- publish your agent:**
>
> 1. In Copilot Studio, click **Publish**
> 2. Choose your channels:
> - **Microsoft Teams** -- your agent appears as a Teams bot
> - **M365 Copilot** -- your agent appears as a plugin in Copilot
> 3. Test it: open Teams and start a conversation with your agent
>
> The same agent logic you built and tested on your local brainstem is now live in your organization.

### Step 15: Tier 3 Complete

Update the state:
```bash
cat > ~/.config/brainstem/state.json << T3STATE
{
 "tier": 3,
 "install_dir": "~/.brainstem/src/rapp_brainstem",
 "local_url": "http://localhost:7071",
 "azure": {
 "resource_group": "${RESOURCE_GROUP}",
 "function_app": "${FUNC_NAME}",
 "function_url": "${FUNC_URL}",
 "storage_account": "${STORAGE_NAME}",
 "openai_service": "${OPENAI_NAME}"
 },
 "copilot_studio": true,
 "status": "published"
}
T3STATE
```

Tell the user:

> ** Nervous system connected!** You've built the full stack.
>
> **What you learned across all 3 tiers:**
>
> | Tier | Layer | Skills |
> |------|-------|--------|
> | Brainstem | Local | Python agents, function-calling, prompt engineering |
> | Spinal Cord | Azure | ARM templates, Functions, managed identity, RBAC |
> | Nervous System | M365 | Copilot Studio, declarative agents, Teams integration |
>
> **Your agent's journey:**
> `soul.md` -> `brainstem.py` -> Azure Function -> Copilot Studio -> Teams/M365 Copilot
>
> From a local Python server to an enterprise AI agent, one layer at a time.

---

## Cleanup

To remove Azure resources:
```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

To uninstall locally:
```bash
rm -rf ~/.brainstem ~/.local/bin/brainstem ~/.config/brainstem
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `gh auth token` fails | Run `gh auth login` |
| Python not 3.11+ | Install specifically: `brew install python@3.11` |
| Port 7071 in use | Set `PORT=7072` in `.env` |
| Storage auth fails after deploy | Wait 2 min for RBAC propagation, restart `func start` |
| OpenAI deploy fails | Try different region: `eastus2` or `swedencentral` |
| Functions list empty after deploy | `az functionapp restart --name $FUNC_NAME -g $RESOURCE_GROUP` |
| Copilot Studio connector fails | Verify function key and URL are correct |
