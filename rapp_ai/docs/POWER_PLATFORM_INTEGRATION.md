# Power Platform Integration Guide

Deploy CommunityRAPP to Microsoft Teams and Microsoft 365 Copilot using Power Platform.

## 📖 Table of Contents

- [Overview](#overview)
- [Why Power Platform?](#why-power-platform)
- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Step-by-Step Setup](#step-by-step-setup)
- [User Context Integration](#user-context-integration)
- [Advanced Configuration](#advanced-configuration)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Cost Analysis](#cost-analysis)
- [Security Best Practices](#security-best-practices)

## Overview

Power Platform integration enables you to deploy your AI assistant to:
- 💬 **Microsoft Teams** - Personal and team channels
- 🤖 **Microsoft 365 Copilot** - As a declarative agent
- 📱 **Power Apps** - Embedded in custom apps
- 🔄 **Power Automate** - Workflow automation

## Why Power Platform?

### Benefits

| Feature | Standalone Mode | Power Platform Mode |
|---------|----------------|---------------------|
| **Access Point** | REST API, Web UI | Teams, M365 Copilot, Web |
| **User Authentication** | Function key | Azure AD/SSO |
| **User Context** | Manual (GUID) | Automatic (Office 365 profile) |
| **Conversation UI** | Custom HTML | Teams native UI |
| **Analytics** | Application Insights | Power Platform Analytics + App Insights |
| **Deployment** | Azure only | Azure + Microsoft 365 |

### Use Cases

**Perfect for Power Platform when:**
- ✅ Users work primarily in Microsoft Teams
- ✅ Need SSO with Azure AD/Entra ID
- ✅ Want automatic user context (name, email, department)
- ✅ Require M365 Copilot integration
- ✅ Need enterprise governance and compliance

**Stick with Standalone when:**
- ✅ Building custom web/mobile apps
- ✅ Integrating with non-Microsoft systems
- ✅ Need complete UI control
- ✅ Don't have Power Platform licenses

## Prerequisites

### Licenses Required

**Per User:**
- Microsoft 365 E3/E5 **or** Business Premium
- Power Automate Premium ($15/user/month)
- Optional: Microsoft 365 Copilot license ($30/user/month)

**Organization:**
- Power Platform environment with admin access
- Azure subscription (for backend Function App)

### Technical Requirements

**Permissions Needed:**
- Power Platform Environment Admin **or** System Administrator
- Ability to create Power Automate flows
- Copilot Studio access
- Teams app deployment rights (or approval from Teams admin)

**Azure Resources:**
- Deployed CommunityRAPP Function App (see [Getting Started](GETTING_STARTED.md))
- Function URL and access key

### Verify Prerequisites

Check you have everything:

```bash
# Check if you have Power Automate Premium
# 1. Go to https://flow.microsoft.com
# 2. Click "My flows" → "New flow"
# 3. If you see "Automated cloud flow" and premium connectors, you're good!

# Get your Azure Function details
# You'll need these from your deployment:
# - Function URL: https://YOUR-APP.azurewebsites.net/api/businessinsightbot_function
# - Function Key: (from Azure Portal → Function App → Functions → businessinsightbot_function → Function Keys)
```

## Architecture

### Full Stack Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                     │
│  Microsoft Teams  │  M365 Copilot  │  Power Apps  │  Web UI     │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Conversation Layer                            │
│                     Copilot Studio                               │
│  • Natural Language Processing                                   │
│  • Dialog Management                                             │
│  • Intent Recognition                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Integration Layer                             │
│                     Power Automate                               │
│  • User Context Enrichment (Office 365 profile)                 │
│  • Data Transformation                                           │
│  • Error Handling & Retry Logic                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     Processing Layer                             │
│                   Azure Function App                             │
│  • Agent Selection & Routing                                     │
│  • Memory Management                                             │
│  • Azure OpenAI Integration                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                       Agent Layer                                │
│   Memory  │  Email  │  Calendar  │  Custom  │  GitConflict     │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                       Data Layer                                 │
│    Azure Storage    │    Azure OpenAI    │   Microsoft Graph   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

**Request Flow:**
```
1. User sends message in Teams/M365 Copilot
   ↓
2. Copilot Studio processes natural language
   ↓
3. Triggers Power Automate flow
   ↓
4. Power Automate enriches with Office 365 user data
   │ - User name
   │ - Email address
   │ - Department
   │ - Job title
   ↓
5. HTTP POST to Azure Function
   {
     "user_input": "User's message",
     "conversation_history": [...],
     "user_guid": "office365-user-id",
     "user_context": {
       "email": "user@company.com",
       "name": "John Doe",
       "department": "Engineering"
     }
   }
   ↓
6. Azure Function processes request
   │ - Loads user memory
   │ - Routes to appropriate agents
   │ - Calls Azure OpenAI
   ↓
7. Returns response to Power Automate
   ↓
8. Power Automate formats for Copilot Studio
   ↓
9. Copilot Studio displays in Teams/M365 Copilot
```

## Step-by-Step Setup

### Phase 1: Download Power Platform Solution

**Option 1: From GitHub Releases (Recommended)**

1. Visit [CommunityRAPP Releases](https://github.com/kody-w/CommunityRAPP/releases)
2. Download `Copilot365_PowerPlatform_Solution.zip`

**Option 2: Create Manually**

If no solution package is available, follow the manual setup in Phase 2-4.

### Phase 2: Set Up Power Automate Flow

#### Step 1: Create the Flow

1. Go to [Power Automate](https://flow.microsoft.com)
2. Click **+ Create** → **Automated cloud flow**
3. Name it: `Copilot365-Backend-Connector`
4. Skip trigger selection (we'll add it later)
5. Click **Create**

#### Step 2: Add Copilot Studio Trigger

1. Click **+ New step** → Search for "Copilot Studio"
2. Select **When Copilot Studio calls a flow**
3. Add input parameters:
   - **Name**: `user_message` | **Type**: Text
   - **Name**: `conversation_id` | **Type**: Text (optional)

#### Step 3: Get User Profile Information

1. Click **+ New step** → Search for "Office 365 Users"
2. Select **Get my profile (V2)**
3. This automatically gets the current user's profile

#### Step 4: Call Azure Function

1. Click **+ New step** → Search for "HTTP"
2. Select **HTTP** action
3. Configure:
   - **Method**: POST
   - **URI**: `https://YOUR-FUNCTION-APP.azurewebsites.net/api/businessinsightbot_function`
   - **Headers**:
     ```json
     {
       "Content-Type": "application/json",
       "x-functions-key": "YOUR_FUNCTION_KEY_HERE"
     }
     ```
   - **Body**: Click "Add dynamic content" and construct:
     ```json
     {
       "user_input": @{triggerBody()?['user_message']},
       "conversation_history": [],
       "user_guid": "@{outputs('Get_my_profile_(V2)')?['body/id']}",
       "user_context": {
         "email": "@{outputs('Get_my_profile_(V2)')?['body/mail']}",
         "name": "@{outputs('Get_my_profile_(V2)')?['body/displayName']}",
         "department": "@{outputs('Get_my_profile_(V2)')?['body/department']}",
         "jobTitle": "@{outputs('Get_my_profile_(V2)')?['body/jobTitle']}"
       }
     }
     ```

#### Step 5: Parse Response

1. Click **+ New step** → Search for "Parse JSON"
2. Select **Parse JSON**
3. **Content**: `body('HTTP')`
4. **Schema**: Click "Use sample payload" and paste:
   ```json
   {
     "assistant_response": "Hello! How can I help you?",
     "voice_response": "Hello!",
     "agent_logs": "Session initialized",
     "user_guid": "abc-123"
   }
   ```

#### Step 6: Return to Copilot Studio

1. Click **+ New step** → Search for "Copilot Studio"
2. Select **Return value(s) to Copilot Studio**
3. Add outputs:
   - **Name**: `bot_response` | **Value**: `body('Parse_JSON')?['assistant_response']`
   - **Name**: `voice_response` | **Value**: `body('Parse_JSON')?['voice_response']`

#### Step 7: Add Error Handling

1. On the HTTP action, click **...** → **Configure run after**
2. Add parallel branch for error handling:
   - **Condition**: `body('HTTP')?['status']` equals `failed`
   - **Action**: Return error message to Copilot Studio

#### Step 8: Save and Test

1. Click **Save**
2. Click **Test** → **Manually** → **Run flow**
3. Enter test data: `user_message: "Hello"`
4. Verify response is received

### Phase 3: Configure Copilot Studio

#### Step 1: Create Copilot

1. Go to [Copilot Studio](https://copilotstudio.microsoft.com)
2. Click **+ Create** → **New copilot**
3. Choose **Skip to configure**
4. Name: `Copilot 365 Agent`
5. Language: English
6. Click **Create**

#### Step 2: Create Main Topic

1. In Copilot Studio, go to **Topics**
2. Click **+ Add a topic** → **From blank**
3. Name: `Main Assistant Topic`
4. Add trigger phrases:
   ```
   - help me
   - I need assistance
   - can you help
   - I have a question
   - assist me
   ```

#### Step 3: Add Flow Action

1. In the topic authoring canvas, click **+ Add node**
2. Select **Call an action** → **Your flow name** (`Copilot365-Backend-Connector`)
3. Map inputs:
   - `user_message` ← `Activity.Text` (user's message)
4. Map outputs to variables:
   - Create variable: `BotResponse` ← `bot_response`
   - Create variable: `VoiceResponse` ← `voice_response`

#### Step 4: Display Response

1. After the flow action, click **+ Add node**
2. Select **Send a message**
3. Message content: `{x:BotResponse}`

#### Step 5: Create Fallback Topic

1. Go to **Topics** → **System** → **Fallback**
2. Customize message: "I can help you with that. Let me think..."
3. Add same flow action as Main topic
4. Display response

#### Step 6: Test in Copilot Studio

1. Click **Test your copilot** (top right)
2. Type: "Hello, can you help me?"
3. Verify response comes from your Azure Function

### Phase 4: Deploy to Channels

#### Deploy to Microsoft Teams

**Step 1: Publish Copilot**
1. In Copilot Studio, click **Publish** (top right)
2. Click **Publish** to confirm
3. Wait for "Successfully published" message

**Step 2: Configure Teams Channel**
1. Go to **Channels** (left sidebar)
2. Click **Microsoft Teams**
3. Click **Turn on Teams**
4. Choose availability:
   - **Show to everyone** (public)
   - **Show to my teammates** (specific people)
   - **Show to my organization** (all employees)
5. Click **Turn on**

**Step 3: Add to Teams**
1. Click **Open bot** (opens Teams)
2. Chat with your bot in Teams!

**Step 4: Add to Teams App Store**
1. In Copilot Studio, under Teams channel settings
2. Click **Submit for admin approval**
3. Teams admin reviews and approves
4. Bot appears in Teams app store for organization

#### Deploy to Microsoft 365 Copilot

**Step 1: Create Declarative Agent**

1. Create a manifest file (`declarativeAgent.json`):

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.0/schema.json",
  "version": "v1.0",
  "id": "copilot365-agent",
  "name": "Copilot 365 Agent",
  "description": "Enterprise AI assistant with persistent memory and custom agents",
  "instructions": "You are an enterprise AI assistant. Help users with their questions using available agents and tools.",
  "conversation_starters": [
    {
      "title": "Help me get started",
      "text": "What can you help me with?"
    },
    {
      "title": "Draft an email",
      "text": "Help me draft a professional email"
    },
    {
      "title": "Search my documents",
      "text": "Find documents about project planning"
    }
  ],
  "actions": [
    {
      "id": "copilot365-backend",
      "type": "powerPlatform",
      "powerPlatformFlowId": "YOUR_FLOW_ID_HERE"
    }
  ],
  "capabilities": {
    "conversationHistory": true,
    "webSearch": false
  }
}
```

**Step 2: Package as Teams App**

1. Create folder structure:
   ```
   Copilot365Agent/
   ├── manifest.json
   ├── declarativeAgent.json
   ├── color.png (192x192)
   └── outline.png (32x32)
   ```

2. Create `manifest.json`:
   ```json
   {
     "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.16/MicrosoftTeams.schema.json",
     "manifestVersion": "1.16",
     "id": "YOUR-UNIQUE-GUID",
     "version": "1.0.0",
     "developer": {
       "name": "Your Organization",
       "websiteUrl": "https://yourcompany.com",
       "privacyUrl": "https://yourcompany.com/privacy",
       "termsOfUseUrl": "https://yourcompany.com/terms"
     },
     "name": {
       "short": "Copilot 365 Agent",
       "full": "Copilot 365 Enterprise AI Assistant"
     },
     "description": {
       "short": "AI assistant with persistent memory",
       "full": "Enterprise AI assistant built on Azure with GPT-4, featuring persistent memory, custom agents, and Microsoft 365 integration."
     },
     "icons": {
       "color": "color.png",
       "outline": "outline.png"
     },
     "copilotAgents": {
       "declarativeAgents": [
         {
           "id": "copilot365-agent",
           "file": "declarativeAgent.json"
         }
       ]
     }
   }
   ```

3. Zip all files (manifest.json, declarativeAgent.json, and icons)

**Step 3: Deploy to M365 Copilot**

1. Go to [Teams Admin Center](https://admin.teams.microsoft.com)
2. Navigate to **Teams apps** → **Manage apps**
3. Click **Upload new app**
4. Upload your ZIP file
5. Set permissions and availability
6. Click **Publish**

**Step 4: Test in M365 Copilot**

1. Open Microsoft 365 Copilot (microsoft365.com)
2. Click on agents/plugins icon
3. Find "Copilot 365 Agent"
4. Start chatting!

## User Context Integration

### Accessing User Information in Agents

Update your agents to use Office 365 user context:

```python
from agents.basic_agent import BasicAgent

class PersonalizedAgent(BasicAgent):
    def __init__(self):
        self.name = 'Personalized'
        self.metadata = {
            "name": self.name,
            "description": "Provides personalized assistance using user context",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_context": {
                        "type": "object",
                        "description": "Office 365 user profile information",
                        "properties": {
                            "email": {"type": "string"},
                            "name": {"type": "string"},
                            "department": {"type": "string"},
                            "jobTitle": {"type": "string"}
                        }
                    },
                    "query": {
                        "type": "string",
                        "description": "User's request"
                    }
                },
                "required": ["query"]
            }
        }
        super().__init__(self.name, self.metadata)

    def perform(self, user_context=None, query="", **kwargs):
        """
        Perform personalized assistance using user context.

        Args:
            user_context (dict): Office 365 user profile
            query (str): User's request
        """
        if user_context:
            name = user_context.get('name', 'User')
            email = user_context.get('email', 'unknown')
            department = user_context.get('department', 'Unknown')
            job_title = user_context.get('jobTitle', 'Unknown')

            # Personalize response based on department
            if 'Engineering' in department:
                return f"Hi {name}, as an engineer, I can help you with technical documentation, code reviews, and development workflows. What do you need?"
            elif 'Sales' in department:
                return f"Hello {name}, I can assist with CRM data, customer insights, and sales reports. How can I help?"
            else:
                return f"Hello {name} from {department}, how can I assist you today?"
        else:
            return "Hello! How can I assist you?"
```

### Storing User-Specific Data

```python
from utils.azure_file_storage import AzureFileStorageManager

class UserPreferencesAgent(BasicAgent):
    def __init__(self):
        self.name = 'UserPreferences'
        self.storage = AzureFileStorageManager()
        # ... metadata setup ...

    def perform(self, user_guid="", action="get", preference_key="", preference_value="", **kwargs):
        """
        Manage user-specific preferences.

        Args:
            user_guid (str): Office 365 user ID
            action (str): 'get' or 'set'
            preference_key (str): Preference name
            preference_value (str): Preference value (for 'set')
        """
        file_name = f"user_preferences_{user_guid}.json"

        if action == "set":
            # Load existing preferences
            preferences = self.storage.read_file("user_data", file_name)
            if not preferences:
                preferences = {}
            else:
                import json
                preferences = json.loads(preferences)

            # Update preference
            preferences[preference_key] = preference_value

            # Save back
            import json
            self.storage.write_file("user_data", file_name, json.dumps(preferences))

            return f"Preference '{preference_key}' saved successfully."

        elif action == "get":
            preferences = self.storage.read_file("user_data", file_name)
            if preferences:
                import json
                prefs = json.loads(preferences)
                return prefs.get(preference_key, "Preference not found")
            return "No preferences found"
```

## Advanced Configuration

### Multi-Environment Setup

For dev/test/prod environments:

**Development Environment:**
```json
{
  "user_input": "test message",
  "conversation_history": [],
  "user_guid": "dev-test-user",
  "environment": "development",
  "azure_function_url": "https://dev-copilot365.azurewebsites.net/api/businessinsightbot_function"
}
```

**Production Environment:**
```json
{
  "user_input": "production message",
  "conversation_history": [],
  "user_guid": "@{outputs('Get_my_profile_(V2)')?['body/id']}",
  "environment": "production",
  "azure_function_url": "https://prod-copilot365.azurewebsites.net/api/businessinsightbot_function"
}
```

Create separate Power Automate flows for each environment.

### Custom Authentication

For scenarios requiring additional authentication:

1. **Add API Management Layer:**
   - Deploy Azure API Management
   - Add OAuth 2.0 / JWT validation
   - Route to Function App

2. **Update Power Automate:**
   - Change HTTP connector to use APIM endpoint
   - Add authentication header with token

### Conversation History Management

To maintain conversation history across messages:

**In Power Automate:**

1. Add **Initialize variable** action at the start:
   - Name: `conversationHistory`
   - Type: Array
   - Value: `[]`

2. After each response, **Append to array variable**:
   ```json
   {
     "role": "user",
     "content": "@{triggerBody()?['user_message']}"
   }
   ```

3. Include in HTTP request body:
   ```json
   {
     "conversation_history": @{variables('conversationHistory')},
     ...
   }
   ```

### Rate Limiting & Throttling

Protect your backend from abuse:

**In Power Automate:**
1. Add **Scope** action for rate limiting check
2. Check calls per user per hour
3. Return error if exceeded

**In Azure Function:**
```python
from datetime import datetime, timedelta
import json

def check_rate_limit(user_guid, storage_manager):
    """Check if user has exceeded rate limit."""
    rate_limit_file = f"rate_limit_{user_guid}.json"

    # Get current rate limit data
    data = storage_manager.read_file("rate_limits", rate_limit_file)

    if data:
        rate_data = json.loads(data)
        last_reset = datetime.fromisoformat(rate_data['last_reset'])

        # Reset if hour has passed
        if datetime.now() - last_reset > timedelta(hours=1):
            rate_data = {'count': 0, 'last_reset': datetime.now().isoformat()}

        # Check limit
        if rate_data['count'] >= 100:  # 100 requests per hour
            return False, "Rate limit exceeded. Try again later."

        rate_data['count'] += 1
    else:
        rate_data = {'count': 1, 'last_reset': datetime.now().isoformat()}

    # Save updated count
    storage_manager.write_file("rate_limits", rate_limit_file, json.dumps(rate_data))
    return True, ""
```

## Monitoring & Troubleshooting

### Power Automate Monitoring

**View Flow Runs:**
1. Go to [Power Automate](https://flow.microsoft.com)
2. Click **My flows**
3. Select your flow
4. Click **28-day run history**
5. Review succeeded/failed runs

**Debug Failed Runs:**
1. Click a failed run
2. Expand each action to see inputs/outputs
3. Check HTTP response codes
4. Verify function key is correct

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **"Unauthorized" (401)** | Invalid function key | Regenerate key in Azure Portal → Function App → Function Keys |
| **"Bad Request" (400)** | Invalid request body format | Check JSON structure matches expected schema |
| **"Timeout" (500)** | Function execution > 230s | Optimize agents, enable streaming, or increase timeout |
| **User context not passed** | Office 365 connector permissions | Re-authenticate Office 365 Users connector |
| **Copilot doesn't trigger** | Missing trigger phrases | Add more variations in Copilot Studio topics |
| **Response not displaying** | Incorrect variable mapping | Verify output variables match in flow and copilot |
| **Slow responses** | Cold start latency | Enable "Always On" in Function App (requires Basic or higher plan) |

### Enable Detailed Logging

**In Power Automate:**
1. Edit flow
2. Add **Compose** actions to log data:
   ```
   Compose_UserInput: @{triggerBody()?['user_message']}
   Compose_HTTPResponse: @{body('HTTP')}
   ```

**In Azure Function:**

Update `local.settings.json` and Azure configuration:
```json
{
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "LOGGING_LEVEL": "DEBUG"
  }
}
```

Check logs in Azure Portal → Function App → Logs (or Application Insights).

### Performance Optimization

**1. Reduce Cold Starts:**
- Enable "Always On" (Function App → Configuration)
- Use Premium or Dedicated hosting plan

**2. Cache Responses:**
```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(user_input_hash):
    # Return cached response if available
    pass

def generate_response(user_input):
    input_hash = hashlib.md5(user_input.encode()).hexdigest()
    cached = get_cached_response(input_hash)
    if cached:
        return cached
    # Generate new response...
```

**3. Parallel Agent Execution:**
```python
import asyncio

async def execute_agents_parallel(agents, user_input):
    tasks = [agent.perform_async(input=user_input) for agent in agents]
    results = await asyncio.gather(*tasks)
    return results
```

## Cost Analysis

### Detailed Cost Breakdown

**Azure Components:**
| Service | Plan | Cost |
|---------|------|------|
| Function App | Consumption | ~$0 (1M free executions/month) |
| Storage | Standard | ~$5/month |
| Azure OpenAI | Pay-per-use | ~$0.01-0.03 per 1K tokens |
| Application Insights | Basic | ~$2-5/month |

**Power Platform Components:**
| Service | Plan | Cost per User/Month |
|---------|------|---------------------|
| Power Automate | Premium | ~$15 |
| Copilot Studio | Included in Premium | $0 |
| Microsoft 365 Copilot | Optional | ~$30 |

**Total Estimates:**

For **10 users** with **moderate usage** (50 conversations/day):
- Azure backend: ~$10-20/month
- Power Platform: $150/month (10 users × $15)
- OpenAI: ~$50-100/month
- **Total: ~$210-270/month** ($21-27 per user)

For **100 users** with **moderate usage**:
- Azure backend: ~$50-100/month
- Power Platform: $1,500/month (100 users × $15)
- OpenAI: ~$500-800/month
- **Total: ~$2,050-2,400/month** ($20-24 per user)

**Cost Optimization Tips:**
- ✅ Start with pilot group (10-20 users)
- ✅ Use consumption plan for Function App initially
- ✅ Monitor OpenAI token usage and optimize prompts
- ✅ Consider shared flows instead of per-user licensing where possible
- ✅ Leverage Azure Reserved Instances for predictable workloads

## Security Best Practices

### 1. Secure Function Keys

**DO:**
- ✅ Use function-level keys (not master key)
- ✅ Rotate keys every 90 days
- ✅ Store keys in Azure Key Vault
- ✅ Use different keys for dev/test/prod

**DON'T:**
- ❌ Hardcode keys in flows
- ❌ Share keys via email or chat
- ❌ Use same key across environments

**Implementation:**
```powershell
# Rotate function key
az functionapp keys renew \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --key-type functionKeys \
  --key-name default
```

### 2. Data Loss Prevention (DLP)

Enable DLP policies in Power Platform Admin Center:

1. Go to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Data policies**
3. Click **New policy**
4. Name: `Copilot365-DLP`
5. Add connectors to appropriate groups:
   - **Business**: Office 365 Users, HTTP (to your Azure Function only)
   - **Blocked**: Other HTTP connectors, file system connectors
6. Apply to specific environments

### 3. Audit Logging

**Enable in Power Platform:**
1. Admin Center → **Analytics** → **Power Automate**
2. View flow execution logs
3. Export to Log Analytics for long-term retention

**Enable in Azure:**
1. Function App → **Monitoring** → **Diagnostic settings**
2. Send to Log Analytics workspace
3. Query logs:
   ```kusto
   FunctionAppLogs
   | where TimeGenerated > ago(24h)
   | where Message contains "businessinsightbot_function"
   | project TimeGenerated, Message, Level
   ```

### 4. Network Security

**Restrict Function App Access:**
1. Azure Portal → Function App → **Networking**
2. **Access restrictions** → **Add rule**
3. Allow only Power Platform IP ranges (regional)
4. Block all other IPs

**Use Private Endpoints:**
For enhanced security, deploy Function App with private endpoints:
```bash
az functionapp vnet-integration add \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --vnet YOUR_VNET \
  --subnet YOUR_SUBNET
```

### 5. User Consent & Privacy

**In Copilot Studio:**
1. Add welcome topic with privacy notice
2. Explain data collection and usage
3. Provide opt-out mechanism
4. Link to privacy policy

**Example Privacy Message:**
```
👋 Welcome to Copilot 365 Agent!

Before we start, please note:
• Your conversations are processed using Azure OpenAI
• We store conversation history to improve responses
• Your Office 365 profile (name, email) is used for personalization
• All data is encrypted and complies with Microsoft's privacy standards

By using this assistant, you agree to our Privacy Policy: [link]

Ready to get started? Ask me anything!
```

### 6. Compliance & Governance

**Microsoft Purview Integration:**
1. Enable sensitivity labels in Power Platform
2. Apply labels to flows containing sensitive data
3. Configure data retention policies
4. Enable eDiscovery for compliance

**Regular Security Reviews:**
- Monthly: Review access logs and unusual activity
- Quarterly: Audit user permissions and flow owners
- Annually: Complete security assessment and penetration testing

## Next Steps

Now that you have Power Platform integration set up:

1. **Customize Experience**
   - Update Copilot Studio welcome messages
   - Add conversation starters
   - Create specialized topics

2. **Extend Functionality**
   - Build [custom agents](AGENT_DEVELOPMENT.md)
   - Integrate with Microsoft Graph
   - Add more Power Automate flows

3. **Monitor & Optimize**
   - Set up alerts for failures
   - Review usage analytics
   - Optimize token usage

4. **Scale Deployment**
   - Roll out to pilot group
   - Gather feedback
   - Deploy organization-wide

## Additional Resources

- 📚 [Power Platform Documentation](https://learn.microsoft.com/power-platform/)
- 🤖 [Copilot Studio Documentation](https://learn.microsoft.com/microsoft-copilot-studio/)
- 💬 [Power Automate Community](https://powerusers.microsoft.com/t5/Microsoft-Power-Automate/ct-p/MPACommunity)
- 📘 [Azure Functions Best Practices](https://learn.microsoft.com/azure/azure-functions/functions-best-practices)

## Need Help?

- **Issues**: [GitHub Issues](https://github.com/kody-w/CommunityRAPP/issues)
- **Discussions**: [Community Forum](https://github.com/kody-w/CommunityRAPP/discussions)
- **Documentation**: [Back to docs home](index.md)

---

**Ready to build amazing experiences?** 🚀 Start integrating with Power Platform today!
