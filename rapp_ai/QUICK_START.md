# Quick Start Guide - Local Development

## Prerequisites

**Private Beta Access Required:** CommunityRAPP is currently in private beta. You must be invited to access the main repository. To request access, visit the public installer repo and follow the instructions.

## TL;DR - Start Developing Now

### Step 1: Use the Public Installer

```bash
# Clone the public installer repo
git clone https://github.com/kody-w/rapp-installer.git
cd rapp-installer

# Run the installer (guides you through setup)
./install.sh  # Mac/Linux
# or
.\install.ps1  # Windows
```

The installer will:
- Check if you have access to the private CommunityRAPP repo
- Guide you through requesting access if needed
- Set up your development environment
- Configure dependencies automatically

### Step 2: Once You Have Access

After being invited to the private beta:

```bash
# Clone the private CommunityRAPP repo
git clone https://github.com/kody-w/CommunityRAPP.git
cd CommunityRAPP

# Install dependencies
pip install -r requirements.txt

# Run it
./run.sh  # Mac/Linux
# or
.\run.ps1  # Windows

# Test it
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Hello", "conversation_history": []}'
```

**That's it!** No Azure credentials needed. Storage automatically uses `.local_storage/` directory.

---

## Repository Structure

| Repository | Access | Purpose |
|------------|--------|---------|
| [rapp-installer](https://github.com/kody-w/rapp-installer) | Public | Installer, setup scripts, access request |
| CommunityRAPP | Private Beta | Core RAPP platform and agents |

---

## What Just Happened?

The system detected you're running locally without Azure credentials and automatically:

1. ✅ Created `.local_storage/` directory in your project
2. ✅ Initialized shared memory storage
3. ✅ Loaded all agents from `agents/` folder
4. ✅ Started the Azure Functions runtime on `localhost:7071`

Everything works exactly like it would in Azure - just faster and without needing credentials.

---

## Common Tasks

### Adding a Custom Agent

```bash
# Create agent file
cat > agents/my_agent.py << 'EOF'
from agents.basic_agent import BasicAgent

class MyAgent(BasicAgent):
    def __init__(self):
        self.name = 'MyAgent'
        self.metadata = {
            "name": self.name,
            "description": "My custom agent",
            "parameters": {"type": "object", "properties": {}}
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        return "Hello from my custom agent!"
EOF

# Restart the function app
# Agent is automatically loaded
```

### Viewing Stored Data

```bash
# All data is in .local_storage/
ls -la .local_storage/

# View shared memory
cat .local_storage/shared_memories/memory.json

# View user-specific memory
cat .local_storage/memory/c0p110t0-aaaa-bbbb-cccc-123456789abc/user_memory.json
```

### Testing with Different User GUIDs

```bash
# Send GUID as first message to load user-specific memory
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{"user_input": "12345678-1234-1234-1234-123456789abc", "conversation_history": []}'

# Subsequent messages use that user's context
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Remember my favorite color is blue", "conversation_history": []}'
```

### Cleaning Up Test Data

```bash
# Remove all local storage
rm -rf .local_storage/

# Restart function app - fresh state
./run.sh
```

---

## What About Azure Storage?

### Option 1: Pure Local Development (Recommended)

Use local storage (default) - fast, no credentials needed:

```bash
# Already works! Nothing to configure.
./run.sh
```

### Option 2: Connect to Azure Storage

If you want to test Azure File Storage integration locally:

1. **Get Azure credentials** (from deployment or Azure Portal)
2. **Create `local.settings.json`:**

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;...",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_API_KEY": "your-key",
    "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o",
    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
    "AZURE_STORAGE_ACCOUNT_NAME": "your-storage-account",
    "AZURE_FILES_SHARE_NAME": "your-share-name"
  }
}
```

3. **Restart function app** - automatically uses Azure storage

---

## Troubleshooting

### "Module not found" Error

```bash
# Make sure you're in the project directory
cd /path/to/CommunityRAPP

# Activate virtual environment if you have one
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Kill existing function app
pkill -f "func host start"

# Or use a different port
func start --port 7072
```

### Permission Denied on .local_storage

```bash
# Fix permissions
chmod -R u+w .local_storage/
```

### "No module named 'azure'"

```bash
# Install Azure SDK
pip install azure-functions azure-storage-file-share azure-identity
```

---

## Next Steps

### Learn More

- **Full Documentation:** See `docs/LOCAL_DEVELOPMENT.md`
- **Architecture:** See `STORAGE_SOLUTION.md`
- **Agent Development:** See `docs/AGENT_DEVELOPMENT.md`
- **Troubleshooting:** See `docs/TROUBLESHOOTING.md`

### Deploy to Azure

When you're ready to deploy:

```bash
# Run deployment script
./deploy.sh

# Follow prompts to create Azure resources
# Script automatically generates setup scripts with your credentials
```

### Test the Web UI

```bash
# Open index.html in your browser
open index.html  # Mac
start index.html  # Windows
xdg-open index.html  # Linux

# Points to localhost:7071 by default
# Chat interface with voice synthesis
```

---

## Key Concepts

### Environment Detection

The system automatically detects:

- **Azure Environment** -> Uses Azure File Storage
- **Local with Azure Config** -> Uses Azure File Storage
- **Local without Config** -> Uses local file storage

You never need to change code or configuration.

### Storage Locations

**Local Development:**
```
.local_storage/
├── shared_memories/
├── memory/{guid}/
├── agents/
├── demos/
└── agent_config/
```

**Azure Deployment:**
```
Azure Files Share
├── shared_memories/
├── memory/{guid}/
├── agents/
├── demos/
└── agent_config/
```

Same structure, different backend.

### Agent Loading

Agents are loaded from:
1. `agents/` folder (built-in agents)
2. Local storage or Azure Files (custom agents)

Custom agents can be added via:
- GitHub library (using GitHubAgentLibraryManager)
- Direct file upload (to local storage or Azure Files)
- Manual file creation (in `agents/` folder)

---

## Pro Tips

### Fast Iteration

```bash
# Make changes to agents/
# Function app auto-reloads on file changes
# No need to restart!
```

### Debug Logging

```python
# Add logging to your agents
import logging

class MyAgent(BasicAgent):
    def perform(self, **kwargs):
        logging.info(f"MyAgent called with: {kwargs}")
        result = "some result"
        logging.info(f"MyAgent returning: {result}")
        return result
```

### Test Data

```python
# Pre-populate shared memory for testing
import json

shared_data = {
    "memories": [
        {
            "id": "mem_001",
            "type": "fact",
            "content": "Test memory",
            "timestamp": "2025-01-15T10:00:00Z"
        }
    ]
}

with open('.local_storage/shared_memories/memory.json', 'w') as f:
    json.dump(shared_data, f, indent=4)
```

### Clean Slate

```bash
# Start fresh anytime
rm -rf .local_storage/
./run.sh
```

---

## Getting Help

### Need Access or Support?

- **Access issues:** Visit [rapp-installer](https://github.com/kody-w/rapp-installer) to request private beta access
- **Bug reports:** Open an issue in the installer repo (for public issues) or CommunityRAPP (for beta members)
- **Feature requests:** Submit via GitHub issues

### Run the Test Suite

```bash
python3 test_local_storage.py
```

Verifies:
- ✅ Environment detection
- ✅ Storage initialization
- ✅ Memory operations
- ✅ File operations
- ✅ Directory structure

### Check Logs

Function app logs show:
```
INFO: Using local file storage for development
INFO: Initialized local storage at: /path/to/.local_storage
```

Or for Azure:
```
INFO: Using Azure File Storage
INFO: Initialized token auth for storage account: your-account
```

### Common Questions

**Q: Do I need Azure credentials to develop locally?**
A: No! System automatically uses local storage.

**Q: Will my local changes affect Azure deployment?**
A: No, local storage is completely isolated.

**Q: Can I test Azure storage locally?**
A: Yes, configure `local.settings.json` with Azure credentials.

**Q: How do I deploy to Azure?**
A: Run `./deploy.sh` when ready.

**Q: Is local storage production-ready?**
A: No, it's for development only. Azure deployments automatically use Azure Files.

---

## Summary

**Local Development:**
- ✅ Zero configuration required
- ✅ Works offline
- ✅ Fast iteration (no network latency)
- ✅ Easy debugging (files visible)
- ✅ No credentials needed

**Azure Deployment:**
- ✅ Automatic detection
- ✅ Production-ready storage
- ✅ Shared across instances
- ✅ Persistent and reliable

**Same codebase, different environments - it just works!**

---

## Requesting Private Beta Access

CommunityRAPP is in private beta. To request access:

1. **Visit the public installer repo:** [github.com/kody-w/rapp-installer](https://github.com/kody-w/rapp-installer)
2. **Run the installer** - it will check your access and provide instructions
3. **Submit an access request** via the installer or GitHub issue
4. **Wait for invitation** - you'll receive a GitHub invitation once approved

**What's included in the private beta:**
- Full RAPP (Rapid AI Agent Production Pipeline) platform
- 14-step agent building methodology
- Transcript-to-agent automation
- Quality gates and deployment tools
- Microsoft 365 and Power Platform integration

---

**Ready to build AI agents? Start with the [installer](https://github.com/kody-w/rapp-installer)!**
