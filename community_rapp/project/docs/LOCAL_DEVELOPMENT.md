# Local Development Guide

## Overview

The CommunityRAPP system supports **environment-aware storage** that automatically adapts between Azure File Storage (for production) and local file system storage (for development).

This allows you to:
- Develop without Azure credentials
- Test with local file storage
- Automatically switch to Azure storage when deployed
- Maintain the same code for both environments

## How It Works

### Automatic Environment Detection

The system automatically detects whether it's running in:
1. **Azure Environment** - Uses Azure File Storage
2. **Local Development with Azure Configured** - Uses Azure File Storage
3. **Local Development without Azure** - Uses local file system fallback

### Storage Manager Factory

All components use `get_storage_manager()` from `utils/storage_factory.py`:

```python
from utils.storage_factory import get_storage_manager

# Automatically returns the appropriate storage manager
storage = get_storage_manager()
```

### Local Storage Location

When using local fallback, files are stored in:
```
.local_storage/
├── shared_memories/
│   └── memory.json
├── memory/
│   └── {user-guid}/
│       └── user_memory.json
├── agents/
│   └── custom_agent.py
├── demos/
│   └── demo_script.json
└── agent_config/
    └── {user-guid}/
        └── enabled_agents.json
```

This directory is automatically created and is excluded from git via `.gitignore`.

## Development Scenarios

### Scenario 1: Pure Local Development

**Setup:**
- No Azure credentials configured
- No `local.settings.json`

**Behavior:**
- System automatically uses `.local_storage/` directory
- All agents, memories, and configs stored locally
- Full functionality without cloud dependencies

**Getting Started:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the function app
./run.sh  # Mac/Linux
# or
.\run.ps1  # Windows

# 3. Files are automatically created in .local_storage/
```

### Scenario 2: Local Development with Azure Storage

**Setup:**
- Azure credentials configured in `local.settings.json`
- Valid Azure Storage connection string

**Behavior:**
- System uses Azure File Storage even when running locally
- Useful for testing Azure integration
- Shares state with deployed function app

**Configuration:**
```json
{
  "Values": {
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=...",
    "AZURE_STORAGE_ACCOUNT_NAME": "your-storage-account",
    "AZURE_FILES_SHARE_NAME": "your-share-name"
  }
}
```

### Scenario 3: Azure Deployment

**Setup:**
- Function app deployed to Azure
- Environment variables configured

**Behavior:**
- System automatically uses Azure File Storage
- Detects Azure environment via `WEBSITE_INSTANCE_ID`
- Production-ready with persistent storage

## Environment Detection Details

### Detection Logic

The system checks these environment variables (in order):

1. **WEBSITE_INSTANCE_ID** - Set by Azure App Service and Functions
2. **FUNCTIONS_WORKER_RUNTIME** - Set by Azure Functions runtime
3. **WEBSITE_SITE_NAME** - Azure App Service site name

If any are present → **Azure Environment**

If none present, checks for Azure storage configuration:
- `AZURE_STORAGE_ACCOUNT_NAME`
- `AZURE_FILES_SHARE_NAME`
- `AzureWebJobsStorage` (with AccountKey) OR Token auth credentials

If fully configured → **Uses Azure Storage**
If not configured → **Uses Local Fallback**

### Manual Override

You can force local storage even with Azure credentials by setting:

```bash
export FORCE_LOCAL_STORAGE=true
```

Or in `local.settings.json`:
```json
{
  "Values": {
    "FORCE_LOCAL_STORAGE": "true"
  }
}
```

## Storage Interface

Both storage managers (`AzureFileStorageManager` and `LocalFileStorageManager`) implement the same interface:

### Memory Operations
```python
storage = get_storage_manager()

# Set memory context
storage.set_memory_context(user_guid)  # User-specific
storage.set_memory_context(None)       # Shared memory

# Read/Write JSON memory
data = storage.read_json()
storage.write_json({"key": "value"})
```

### File Operations
```python
# Write file
storage.write_file('agents', 'my_agent.py', agent_code)

# Read file
content = storage.read_file('agents', 'my_agent.py')

# List files
files = storage.list_files('agents')
for file in files:
    print(file.name)

# Check existence
exists = storage.file_exists('agents', 'my_agent.py')

# Delete file
storage.delete_file('agents', 'my_agent.py')

# Get properties
props = storage.get_file_properties('agents', 'my_agent.py')
print(props['size'], props['last_modified'])
```

### Directory Operations
```python
# Create directory
storage.ensure_directory_exists('custom_agents')
```

## Testing with Local Storage

### Adding Test Agents

```bash
# Create agent file
cat > .local_storage/agents/test_agent.py << 'EOF'
from agents.basic_agent import BasicAgent

class TestAgent(BasicAgent):
    def __init__(self):
        self.name = 'Test'
        self.metadata = {
            "name": self.name,
            "description": "Test agent",
            "parameters": {"type": "object", "properties": {}}
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        return "Test successful!"
EOF

# Restart function app to load new agent
```

### Adding Test Memories

```python
import json

# Shared memory
shared = {
    "memories": [
        {
            "id": "mem_001",
            "type": "fact",
            "content": "The company was founded in 2020",
            "timestamp": "2025-01-15T10:00:00Z"
        }
    ]
}

with open('.local_storage/shared_memories/memory.json', 'w') as f:
    json.dump(shared, f, indent=4)
```

### User-Specific Configuration

```bash
# Enable specific agents for a user GUID
mkdir -p .local_storage/agent_config/c0p110t0-aaaa-bbbb-cccc-123456789abc
cat > .local_storage/agent_config/c0p110t0-aaaa-bbbb-cccc-123456789abc/enabled_agents.json << 'EOF'
[
  "context_memory_agent.py",
  "manage_memory_agent.py",
  "test_agent.py"
]
EOF
```

## Troubleshooting

### Issue: "Module not found" errors

**Cause:** Storage factory not imported correctly

**Solution:**
```python
# Wrong
from utils.azure_file_storage import AzureFileStorageManager
storage = AzureFileStorageManager()

# Correct
from utils.storage_factory import get_storage_manager
storage = get_storage_manager()
```

### Issue: Local storage not working

**Cause:** Directory permissions or path issues

**Solution:**
```bash
# Check directory exists and is writable
ls -la .local_storage/
chmod -R u+w .local_storage/
```

### Issue: Azure credentials failing

**Cause:** Token-based auth issues with key-based auth disabled

**Solution:**
- System automatically falls back to local storage
- Check logs for "Falling back to local file storage"
- Configure proper Entra ID credentials or use connection string

### Issue: Data not persisting between runs

**For Local Development:**
- Check `.local_storage/` exists and has correct permissions
- Verify file writes succeed (check logs)

**For Azure Deployment:**
- Verify Azure storage credentials are correct
- Check file share exists and is accessible
- Review Application Insights logs

## Migration Between Environments

### Local to Azure

When moving from local development to Azure:

1. **Export local data** (if needed):
```bash
# Backup local storage
tar -czf local-backup.tar.gz .local_storage/
```

2. **Deploy to Azure:**
```bash
./deploy.sh  # Deployment script
```

3. **Upload data to Azure** (optional):
```python
from utils.storage_factory import get_storage_manager

# In Azure environment
storage = get_storage_manager()

# Upload agents
with open('my_agent.py', 'r') as f:
    storage.write_file('agents', 'my_agent.py', f.read())
```

### Azure to Local

To test Azure data locally:

1. **Download from Azure:**
```python
from utils.azure_file_storage import AzureFileStorageManager
import os

# Configure Azure credentials
os.environ['AzureWebJobsStorage'] = 'your-connection-string'

azure_storage = AzureFileStorageManager()

# Download agents
files = azure_storage.list_files('agents')
for file in files:
    content = azure_storage.read_file('agents', file.name)
    with open(f'.local_storage/agents/{file.name}', 'w') as f:
        f.write(content)
```

2. **Switch to local storage:**
```bash
# Remove or rename local.settings.json
mv local.settings.json local.settings.json.backup

# Restart function app
./run.sh
```

## Best Practices

### Development Workflow

1. **Start with local storage** - Fastest development cycle
2. **Test with local files** - Easy to inspect and modify
3. **Validate with Azure storage** - Before deploying to production
4. **Deploy to Azure** - Production environment

### Code Practices

```python
# Always use the factory
from utils.storage_factory import get_storage_manager

# Never hardcode storage types
# Bad:
storage = AzureFileStorageManager()

# Good:
storage = get_storage_manager()
```

### Error Handling

```python
try:
    storage = get_storage_manager()
    data = storage.read_json()
except Exception as e:
    logging.error(f"Storage error: {e}")
    # Handle gracefully
```

### Logging

The system logs which storage backend is in use:
```
INFO: Using local file storage for development
# or
INFO: Using Azure File Storage
```

Check logs to verify expected behavior.

## Advanced: Custom Storage Backend

You can create your own storage backend by implementing the same interface:

```python
class CustomStorageManager:
    def __init__(self):
        # Your initialization
        pass

    def set_memory_context(self, guid):
        # Implement
        pass

    def read_json(self):
        # Implement
        pass

    def write_json(self, data):
        # Implement
        pass

    # ... implement all other methods

# Use in storage_factory.py
def get_storage_manager():
    if custom_condition:
        return CustomStorageManager()
    # ... existing logic
```

## Summary

The environment-aware storage system provides:

- **Zero-config local development** - Works out of the box
- **Seamless Azure integration** - Automatic detection and switching
- **Consistent interface** - Same code for all environments
- **Graceful fallbacks** - Never fails due to auth issues
- **Developer-friendly** - Easy to test and debug locally

Start developing immediately without Azure credentials, then deploy to Azure when ready - all with the same codebase.
