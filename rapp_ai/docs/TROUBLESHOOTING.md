# Troubleshooting Guide

Solutions to common issues when deploying and running CommunityRAPP.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Azure Function Issues](#azure-function-issues)
- [Azure OpenAI Issues](#azure-openai-issues)
- [Power Platform Issues](#power-platform-issues)
- [Performance Issues](#performance-issues)
- [Memory & Storage Issues](#memory--storage-issues)
- [Diagnostic Tools](#diagnostic-tools)

## Installation Issues

### Python 3.11 Not Found (Windows)

**Symptom:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Setup script auto-installs Python 3.11 - wait 2-3 minutes
2. If still fails, manually install from [python.org](https://python.org/downloads/)
3. Ensure "Add Python to PATH" is checked during installation
4. Restart terminal after installation

**Verify installation:**
```powershell
python --version  # Should show Python 3.11.x
```

### Azure Functions Core Tools Not Found

**Symptom:**
```
'func' is not recognized as an internal or external command
```

**Solution:**

**Windows:**
```powershell
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

**Mac:**
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

**Linux:**
```bash
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

### Setup Script Permission Denied (Mac/Linux)

**Symptom:**
```
Permission denied: './setup.sh'
```

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### PowerShell Execution Policy Error (Windows)

**Symptom:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

## Runtime Errors

### "Module not found" Error

**Symptom:**
```
ModuleNotFoundError: No module named 'azure'
```

**Solution:**
```bash
# Activate virtual environment
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port 7071 Already in Use

**Symptom:**
```
Port 7071 is already in use
```

**Solution:**

**Option 1: Kill existing process**

**Windows:**
```powershell
netstat -ano | findstr :7071
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -i :7071
kill -9 <PID>
```

**Option 2: Use different port**
```bash
func start --port 7072
```

### ImportError: Cannot import 'BasicAgent'

**Symptom:**
```
ImportError: cannot import name 'BasicAgent' from 'agents.basic_agent'
```

**Solution:**
1. Verify `agents/basic_agent.py` exists
2. Check Python path includes project directory
3. Ensure `__init__.py` exists in `agents/` folder:

```bash
# Create if missing
touch agents/__init__.py
```

### JSON Decode Error

**Symptom:**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1
```

**Solution:**
- Ensure request body is valid JSON
- Check Content-Type header is `application/json`
- Verify no extra characters in request

**Test with curl:**
```bash
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Hello","conversation_history":[]}'
```

## Azure Function Issues

### Cold Start Timeout

**Symptom:**
Function times out on first request after idle period.

**Solution:**

**Option 1: Enable Always On (Premium/Dedicated plan only)**
```bash
az webapp config set \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --always-on true
```

**Option 2: Use Premium Plan**
```bash
az functionapp plan create \
  --name premium-plan \
  --resource-group YOUR_RESOURCE_GROUP \
  --sku EP1 \
  --is-linux
```

**Option 3: Implement warmup trigger**
Add to `function_app.py`:
```python
@app.schedule(schedule="0 */5 * * * *", arg_name="timer")
def warmup_timer(timer: func.TimerRequest):
    logging.info("Warmup function triggered")
```

### Function Execution Timeout

**Symptom:**
```
Function execution timeout after 230 seconds
```

**Solution:**

**Option 1: Optimize code**
- Cache agent metadata
- Use async/await for I/O operations
- Reduce OpenAI token usage

**Option 2: Increase timeout (Premium/Dedicated only)**

In `host.json`:
```json
{
  "version": "2.0",
  "functionTimeout": "00:10:00"
}
```

**Option 3: Split into multiple functions**
- Separate long-running operations
- Use durable functions for orchestration

### Deployment Fails

**Symptom:**
```
Error: Deployment failed with exit code 1
```

**Solution:**

**Check Python version:**
```bash
func azure functionapp list-functions YOUR_FUNCTION_APP
```

**Ensure Python 3.11:**
```bash
az functionapp config set \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --linux-fx-version "PYTHON|3.11"
```

**Check logs:**
```bash
az functionapp log tail \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP
```

**Common fixes:**
- Delete `.python_packages/` and redeploy
- Ensure `requirements.txt` has correct versions
- Check for circular imports

### "Unauthorized" (401) Error

**Symptom:**
```
HTTP 401: Unauthorized
```

**Solution:**

**Get function key:**
```bash
az functionapp keys list \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --query functionKeys.default
```

**Include in request:**
```bash
curl -X POST "https://YOUR_APP.azurewebsites.net/api/businessinsightbot_function?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Hello","conversation_history":[]}'
```

**Or use header:**
```bash
curl -X POST "https://YOUR_APP.azurewebsites.net/api/businessinsightbot_function" \
  -H "Content-Type: application/json" \
  -H "x-functions-key: YOUR_KEY" \
  -d '{"user_input":"Hello","conversation_history":[]}'
```

## Azure OpenAI Issues

### "Rate limit exceeded" Error

**Symptom:**
```
RateLimitError: Requests to the OpenAI API have exceeded rate limits
```

**Solution:**

**Check quota:**
```bash
az cognitiveservices account show \
  --name YOUR_OPENAI_SERVICE \
  --resource-group YOUR_RESOURCE_GROUP \
  --query properties.capabilities
```

**Request quota increase:**
1. Azure Portal → OpenAI Service → Quotas
2. Select your model deployment
3. Click "Request Quota Increase"
4. Provide justification and usage estimates

**Implement retry logic:**
```python
import time
from openai import RateLimitError

def call_openai_with_retry(client, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise e
```

### "Deployment not found" Error

**Symptom:**
```
DeploymentNotFoundError: The API deployment for this resource does not exist
```

**Solution:**

**List deployments:**
```bash
az cognitiveservices account deployment list \
  --name YOUR_OPENAI_SERVICE \
  --resource-group YOUR_RESOURCE_GROUP
```

**Check deployment name in configuration:**
```bash
az functionapp config appsettings list \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --query "[?name=='AZURE_OPENAI_DEPLOYMENT_NAME'].value" \
  --output tsv
```

**Update if incorrect:**
```bash
az functionapp config appsettings set \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --settings "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o"
```

### "Invalid API key" Error

**Symptom:**
```
AuthenticationError: Invalid API key provided
```

**Solution:**

**Regenerate key:**
```bash
az cognitiveservices account keys regenerate \
  --name YOUR_OPENAI_SERVICE \
  --resource-group YOUR_RESOURCE_GROUP \
  --key-name key1
```

**Get new key:**
```bash
NEW_KEY=$(az cognitiveservices account keys list \
  --name YOUR_OPENAI_SERVICE \
  --resource-group YOUR_RESOURCE_GROUP \
  --query key1 --output tsv)
```

**Update function app:**
```bash
az functionapp config appsettings set \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --settings "AZURE_OPENAI_API_KEY=$NEW_KEY"
```

## Power Platform Issues

### Power Automate Flow Fails

**Symptom:**
Flow shows "Failed" status in run history.

**Solution:**

**Check run history:**
1. Power Automate → My flows
2. Click your flow
3. View "28-day run history"
4. Click failed run to see details

**Common issues:**

**1. HTTP action timeout:**
- Increase timeout in HTTP action (default 100 seconds)
- Optimize function response time

**2. Invalid JSON:**
- Verify body is valid JSON
- Use "Parse JSON" action with correct schema

**3. Function key expired:**
- Regenerate function key
- Update in Power Automate HTTP action

**4. Office 365 Users connector not authenticated:**
- Edit flow
- Re-authenticate "Office 365 Users" connector
- Test connection

### Copilot Studio Not Triggering

**Symptom:**
Bot doesn't respond to messages in Teams.

**Solution:**

**1. Check topic triggers:**
- Copilot Studio → Topics
- Verify trigger phrases match user input
- Add more variations

**2. Test in Copilot Studio:**
- Click "Test your copilot"
- Send test message
- Check which topic triggers (or if fallback triggers)

**3. Verify flow connection:**
- Topic → Call an action
- Ensure correct flow selected
- Check input/output mappings

**4. Republish copilot:**
- Click "Publish" in top right
- Wait for "Successfully published"

### User Context Not Passed

**Symptom:**
Function receives empty `user_context`.

**Solution:**

**1. Check Office 365 Users connector:**
- Power Automate → Connections
- Find "Office 365 Users"
- Test connection
- Re-authenticate if needed

**2. Verify flow action:**
- Edit "Get my profile (V2)" action
- Ensure no errors
- Check outputs contain email, name, etc.

**3. Check HTTP body:**
- In HTTP action, click "Show advanced options"
- Verify body includes:
```json
{
  "user_context": {
    "email": "@{outputs('Get_my_profile_(V2)')?['body/mail']}",
    "name": "@{outputs('Get_my_profile_(V2)')?['body/displayName']}"
  }
}
```

### Teams Bot Not Found

**Symptom:**
Bot doesn't appear in Teams app store.

**Solution:**

**1. Check publication status:**
- Copilot Studio → Channels → Microsoft Teams
- Verify "Turn on Teams" is enabled
- Check availability setting

**2. Admin approval required:**
- Contact Teams administrator
- Request approval for bot
- Check Teams Admin Center → Manage apps

**3. Clear Teams cache:**
- Teams → Settings → Clear cache
- Restart Teams
- Search for bot again

## Performance Issues

### Slow Response Times

**Symptom:**
Responses take >15 seconds.

**Solution:**

**1. Enable Application Insights:**
```bash
az monitor app-insights component create \
  --app YOUR_INSIGHTS \
  --location eastus \
  --resource-group YOUR_RESOURCE_GROUP
```

**2. Check logs for bottlenecks:**
```kusto
requests
| where name == "businessinsightbot_function"
| summarize avg(duration), max(duration) by bin(timestamp, 1h)
```

**3. Optimize agents:**
- Cache external API calls
- Reduce OpenAI token usage
- Use async operations

**4. Upgrade hosting plan:**
```bash
az functionapp plan update \
  --name YOUR_PLAN \
  --resource-group YOUR_RESOURCE_GROUP \
  --sku EP1
```

### High Memory Usage

**Symptom:**
Function app restarts due to memory pressure.

**Solution:**

**1. Check memory usage:**
```kusto
performanceCounters
| where name == "% Processor Time"
| summarize avg(value) by bin(timestamp, 5m)
```

**2. Optimize code:**
- Clear conversation history after N messages
- Avoid loading large files into memory
- Use generators instead of lists

**3. Increase memory allocation:**
```bash
az functionapp plan update \
  --name YOUR_PLAN \
  --resource-group YOUR_RESOURCE_GROUP \
  --sku EP2  # More memory
```

## Memory & Storage Issues

### "File not found" Error

**Symptom:**
```
FileNotFoundError: No such file or directory: 'memory/shared/context.txt'
```

**Solution:**

**1. Check file shares exist:**
```bash
az storage share list \
  --account-name YOUR_STORAGE \
  --output table
```

**2. Create missing shares:**
```bash
az storage share create \
  --name memory \
  --account-name YOUR_STORAGE

az storage share create \
  --name agents \
  --account-name YOUR_STORAGE
```

**3. Initialize memory files:**
```bash
# Create initial context file
echo "System initialized on $(date)" > context.txt

# Upload to Azure
az storage file upload \
  --share-name memory \
  --source context.txt \
  --path shared/context.txt \
  --account-name YOUR_STORAGE
```

### Storage Connection Error

**Symptom:**
```
azure.core.exceptions.ServiceRequestError: Connection error
```

**Solution:**

**1. Check connection string:**
```bash
az storage account show-connection-string \
  --name YOUR_STORAGE \
  --resource-group YOUR_RESOURCE_GROUP
```

**2. Update function app setting:**
```bash
az functionapp config appsettings set \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --settings "AzureWebJobsStorage=<CONNECTION_STRING>"
```

**3. Check firewall rules:**
- Azure Portal → Storage Account → Networking
- Add Function App IP to allowed list
- Or enable "Allow Azure services"

## Diagnostic Tools

### Enable Debug Logging

**In `local.settings.json`:**
```json
{
  "Values": {
    "LOGGING_LEVEL": "DEBUG",
    "PYTHON_ENABLE_DEBUG_LOGGING": "1"
  }
}
```

**In Azure:**
```bash
az functionapp config appsettings set \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --settings "LOGGING_LEVEL=DEBUG"
```

### View Live Logs

**Local:**
```bash
func start --verbose
```

**Azure Portal:**
1. Function App → Functions → businessinsightbot_function
2. Click "Monitor"
3. View "Invocations" and "Logs"

**Azure CLI:**
```bash
az functionapp log tail \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP
```

### Application Insights Queries

**Recent errors:**
```kusto
traces
| where severityLevel >= 3
| where timestamp > ago(1h)
| project timestamp, message, severityLevel
| order by timestamp desc
```

**Agent execution times:**
```kusto
traces
| where message contains "Agent executed"
| extend agent = extract("Agent: (\\w+)", 1, message)
| extend duration = extract("Duration: ([0-9\\.]+)", 1, message)
| summarize avg(todouble(duration)) by agent
```

### Test Individual Components

**Test agent locally:**
```python
# test_agent.py
from agents.my_agent import MyAgent

agent = MyAgent()
result = agent.perform(param1="test")
print(result)
```

**Test OpenAI connection:**
```python
# test_openai.py
from openai import AzureOpenAI
import os

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2025-01-01-preview",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
```

**Test storage connection:**
```python
# test_storage.py
from utils.azure_file_storage import AzureFileStorageManager

storage = AzureFileStorageManager()
result = storage.read_file('memory', 'shared/context.txt')
print(result)
```

## Getting More Help

### Still stuck?

1. **Check GitHub Issues:** [Existing issues](https://github.com/kody-w/CommunityRAPP/issues)
2. **Search Discussions:** [Community forum](https://github.com/kody-w/CommunityRAPP/discussions)
3. **Open New Issue:** [Report a bug](https://github.com/kody-w/CommunityRAPP/issues/new)

### Include in Bug Reports

- Operating system and version
- Python version (`python --version`)
- Azure Functions Core Tools version (`func --version`)
- Error messages (full stack trace)
- Steps to reproduce
- Relevant log snippets

---

**Back to:** [Documentation Home](index.md)
