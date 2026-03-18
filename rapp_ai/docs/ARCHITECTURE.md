# System Architecture

Complete technical architecture documentation for CommunityRAPP.

## Table of Contents

- [Overview](#overview)
- [System Layers](#system-layers)
- [Request Flow](#request-flow)
- [Component Details](#component-details)
- [Data Models](#data-models)
- [Agent System](#agent-system)
- [Memory Management](#memory-management)
- [Deployment Architectures](#deployment-architectures)
- [Scalability & Performance](#scalability--performance)
- [Security Architecture](#security-architecture)

## Overview

CommunityRAPP is built on a **6-layer architecture** providing enterprise-grade AI assistance with persistent memory, modular agents, and multi-channel deployment.

### Design Principles

1. **Modularity** - Pluggable agents, extensible architecture
2. **Scalability** - Serverless compute, horizontal scaling
3. **Security** - Zero-trust, encrypted data, audit logging
4. **Flexibility** - Multiple deployment modes, customizable
5. **Reliability** - Error handling, retry logic, fault tolerance

### Technology Stack

```
┌─────────────────────────────────────────────────────┐
│                  Frontend Layer                      │
│  HTML5 │ JavaScript │ Markdown │ Syntax Highlighting │
├─────────────────────────────────────────────────────┤
│               Conversation Layer                     │
│  Microsoft Copilot Studio │ Teams Bot Framework     │
├─────────────────────────────────────────────────────┤
│              Integration Layer                       │
│  Power Automate │ Azure AD │ Microsoft Graph API   │
├─────────────────────────────────────────────────────┤
│              Processing Layer                        │
│  Azure Functions (Python 3.11) │ Function Runtime  │
├─────────────────────────────────────────────────────┤
│                 AI Layer                            │
│  Azure OpenAI Service │ GPT-4o │ Function Calling  │
├─────────────────────────────────────────────────────┤
│                Data Layer                           │
│  Azure File Storage │ Conversation Memory          │
└─────────────────────────────────────────────────────┘
```

## System Layers

### Layer 1: User Interface

Multiple access points for users:

**Web Interface (`client/index.html`):**
- Direct browser access
- No authentication by default
- Real-time chat UI with markdown rendering
- Code block syntax highlighting
- Voice synthesis support
- Mobile-responsive design

**Microsoft Teams:**
- Native Teams chat experience
- SSO via Azure AD
- Rich adaptive cards
- File attachment support
- Channel and personal chat modes

**Microsoft 365 Copilot:**
- Declarative agent in M365 chat
- Contextual assistance across M365 apps
- Conversation starters
- Skill integration

**Direct API:**
- REST endpoint for custom integrations
- JSON request/response
- Function key authentication
- CORS enabled

### Layer 2: Conversation Management

**Copilot Studio (Power Platform Mode):**
- Natural language understanding (NLU)
- Intent recognition
- Entity extraction
- Dialog flow management
- Multi-turn conversation handling
- Topic routing
- Fallback handling

**Direct to Function (Standalone Mode):**
- Conversation history managed in request
- No NLU layer (relies on GPT-4 understanding)
- Direct JSON communication

### Layer 3: Integration & Orchestration

**Power Automate (Power Platform Mode):**

```
┌─────────────────────────────────────────────────┐
│        Power Automate Flow Architecture         │
├─────────────────────────────────────────────────┤
│  1. Trigger: Copilot Studio calls flow         │
│     ↓                                           │
│  2. Action: Get Office 365 user profile        │
│     ↓                                           │
│  3. Action: Compose request body               │
│     ↓                                           │
│  4. Action: HTTP POST to Azure Function        │
│     ↓                                           │
│  5. Action: Parse JSON response                │
│     ↓                                           │
│  6. Action: Return to Copilot Studio           │
└─────────────────────────────────────────────────┘
```

**Benefits:**
- User context enrichment (automatic)
- Error handling and retry logic
- Data transformation
- Logging and monitoring
- Centralized integration point

### Layer 4: Processing Engine

**Azure Function App (`function_app.py`):**

Core processing engine handling:
- Request validation and sanitization
- Agent loading and initialization
- Memory retrieval (user + shared)
- OpenAI API calls with function calling
- Agent execution and orchestration
- Response formatting
- Error handling and logging

**Key Components:**

1. **`businessinsightbot_function`** - HTTP trigger endpoint
2. **`Assistant` class** - Main orchestration logic
3. **Agent loader** - Dynamic agent discovery
4. **Memory manager** - Context persistence
5. **Response formatter** - Dual response (formatted + voice)

### Layer 5: Agent System

**Agent Architecture:**

```python
class BasicAgent:
    """Base class for all agents"""
    def __init__(self, name, metadata):
        self.name = name
        self.metadata = metadata  # OpenAI function schema

    def perform(self, **kwargs):
        """Execute agent logic"""
        pass
```

**Built-in Agents:**

| Agent | Purpose | File |
|-------|---------|------|
| **ContextMemoryAgent** | Retrieve conversation history | `context_memory_agent.py` |
| **ManageMemoryAgent** | Store facts and preferences | `manage_memory_agent.py` |
| **EmailDraftingAgent** | Draft professional emails | `email_drafting_agent.py` |
| **GitConflictResolverAgent** | Resolve Git merge conflicts | `git_conflict_resolver_agent.py` |

**Agent Discovery:**
- Local agents: `/agents/*.py`
- Azure storage agents: `agents/` and `multi_agents/` file shares
- Dynamic loading at function startup
- Automatic schema generation for OpenAI

### Layer 6: Data & AI

**Azure OpenAI Service:**
- Model: GPT-4o (or configured deployment)
- API version: 2025-01-01-preview
- Features: Function calling, streaming (optional)
- Context window: 128K tokens
- Output: 4K tokens max

**Azure File Storage:**

```
Storage Account
├── agents/              # Custom agent Python files
├── multi_agents/        # Multi-agent coordination files
├── memory/
│   ├── shared/          # Shared context (all users)
│   └── users/
│       ├── {guid1}/     # User-specific context
│       └── {guid2}/     # User-specific context
└── logs/                # Application logs (optional)
```

**Memory Structure:**
- **Shared memory**: Facts, common knowledge, system info
- **User memory**: User preferences, conversation history, personal context
- **Format**: Plain text, JSON, or structured data
- **Retention**: Configurable (default: unlimited)

## Request Flow

### Standalone Mode Flow

```
1. HTTP Request
   ↓
   POST http://localhost:7071/api/businessinsightbot_function
   Headers:
     Content-Type: application/json
     x-functions-key: <optional>
   Body:
     {
       "user_input": "What's the weather?",
       "conversation_history": [
         {"role": "user", "content": "Hello"},
         {"role": "assistant", "content": "Hi! How can I help?"}
       ],
       "user_guid": "abc-123" (optional)
     }

2. Function App Processing
   ↓
   a. Validate request
   b. Extract user_guid (or use default)
   c. Load agents from local + Azure storage
   d. Initialize memory (shared + user-specific)

3. Agent Selection
   ↓
   a. Prepare messages with system prompt
   b. Include memory context
   c. Add conversation history
   d. Add user's new message

4. Azure OpenAI Call
   ↓
   a. Send to GPT-4 with function definitions
   b. Model decides: direct response OR call agent function

5a. Direct Response Path
   ↓
   Return response immediately

5b. Agent Function Call Path
   ↓
   a. Parse function name and arguments
   b. Execute corresponding agent.perform()
   c. Add function result to conversation
   d. Make follow-up OpenAI call for final response

6. Response Formatting
   ↓
   a. Split response: formatted || voice
   b. Prepare JSON response
   c. Add CORS headers

7. HTTP Response
   ↓
   {
     "assistant_response": "Formatted markdown response...",
     "voice_response": "Concise voice response",
     "agent_logs": "Execution details...",
     "user_guid": "abc-123"
   }
```

### Power Platform Mode Flow

```
1. User Message in Teams/M365
   ↓
2. Copilot Studio
   ↓ (processes natural language)
3. Power Automate Flow Trigger
   ↓
4. Get Office 365 User Profile
   ↓ (automatic SSO)
5. Compose Request Body
   {
     "user_input": "message",
     "conversation_history": [...],
     "user_guid": "office365-user-id",
     "user_context": {
       "email": "user@company.com",
       "name": "John Doe",
       "department": "Engineering",
       "jobTitle": "Senior Engineer"
     }
   }
   ↓
6. HTTP POST to Azure Function
   (same flow as standalone from here)
   ↓
7-11. Processing (as above)
   ↓
12. Return to Power Automate
   ↓
13. Format for Copilot Studio
   ↓
14. Display in Teams/M365
```

## Component Details

### function_app.py

**Main entry point:** `businessinsightbot_function(req: func.HttpRequest)`

```python
@app.route(route="businessinsightbot_function", methods=["POST", "OPTIONS"])
def businessinsightbot_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered Azure Function for AI assistant.

    Request body:
    {
      "user_input": str,
      "conversation_history": List[dict],
      "user_guid": str (optional),
      "user_context": dict (optional)
    }

    Returns:
    {
      "assistant_response": str,
      "voice_response": str,
      "agent_logs": str,
      "user_guid": str
    }
    """
    # 1. Handle OPTIONS (CORS preflight)
    if req.method == "OPTIONS":
        return build_cors_response(func.HttpResponse(status_code=200))

    # 2. Parse request
    try:
        req_body = req.get_json()
        user_input = req_body.get('user_input', '')
        conversation_history = req_body.get('conversation_history', [])
        user_guid = req_body.get('user_guid', DEFAULT_GUID)
        user_context = req_body.get('user_context', None)
    except ValueError:
        return build_cors_response(
            func.HttpResponse("Invalid JSON", status_code=400)
        )

    # 3. Load agents
    agents = load_agents_from_local_and_azure()

    # 4. Initialize assistant
    assistant = Assistant(
        agents=agents,
        user_guid=user_guid,
        user_context=user_context
    )

    # 5. Process request
    response = assistant.process(user_input, conversation_history)

    # 6. Return response
    return build_cors_response(
        func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )
    )
```

**Assistant Class:**

```python
class Assistant:
    def __init__(self, agents, user_guid, user_context=None):
        self.agents = agents
        self.user_guid = user_guid
        self.user_context = user_context
        self.openai_client = AzureOpenAI(...)
        self.storage = AzureFileStorageManager()

    def process(self, user_input, conversation_history):
        # 1. Initialize memory
        shared_memory = self.load_shared_memory()
        user_memory = self.load_user_memory(self.user_guid)

        # 2. Prepare system prompt
        system_prompt = self.build_system_prompt(
            shared_memory, user_memory, self.user_context
        )

        # 3. Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history,
            {"role": "user", "content": user_input}
        ]

        # 4. Call OpenAI with functions
        response = self.openai_client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            functions=[agent.metadata for agent in self.agents],
            function_call="auto"
        )

        # 5. Handle function calls
        if response.choices[0].message.function_call:
            function_result = self.execute_function(
                response.choices[0].message.function_call
            )

            # Follow-up call with function result
            messages.append(response.choices[0].message)
            messages.append({
                "role": "function",
                "name": function_name,
                "content": function_result
            })

            final_response = self.openai_client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=messages
            )

            assistant_message = final_response.choices[0].message.content
        else:
            assistant_message = response.choices[0].message.content

        # 6. Format response
        formatted, voice = self.split_response(assistant_message)

        return {
            "assistant_response": formatted,
            "voice_response": voice,
            "agent_logs": self.get_logs(),
            "user_guid": self.user_guid
        }
```

### Agent Loading

**Dynamic agent discovery:**

```python
def load_agents():
    agents = []

    # 1. Load from local agents/ folder
    local_path = os.path.join(os.path.dirname(__file__), 'agents')
    for file in os.listdir(local_path):
        if file.endswith('_agent.py'):
            module = importlib.import_module(f'agents.{file[:-3]}')
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasicAgent) and obj != BasicAgent:
                    agents.append(obj())

    # 2. Load from Azure storage
    storage = AzureFileStorageManager()

    # Download agents from 'agents' share
    agent_files = storage.list_files('agents')
    for agent_file in agent_files:
        content = storage.read_file('agents', agent_file)
        # Write to /tmp/agents/
        temp_path = f'/tmp/agents/{agent_file}'
        with open(temp_path, 'w') as f:
            f.write(content)
        # Import dynamically
        spec = importlib.util.spec_from_file_location("temp_agent", temp_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Find agent classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BasicAgent) and obj != BasicAgent:
                agents.append(obj())

    return agents
```

### Memory Management

**Memory initialization:**

```python
def initialize_memory(user_guid, storage_manager):
    """
    Load shared and user-specific memory.

    Returns:
        tuple: (shared_memory, user_memory)
    """
    # Load shared memory (available to all users)
    shared_memory = storage_manager.read_file('memory/shared', 'context.txt')
    if not shared_memory:
        shared_memory = "No shared context available."

    # Load user-specific memory
    user_memory_file = f'{user_guid}_context.txt'
    user_memory = storage_manager.read_file('memory/users', user_memory_file)
    if not user_memory:
        user_memory = "No user-specific context available."

    return shared_memory, user_memory
```

**Memory storage:**

```python
class ManageMemoryAgent(BasicAgent):
    def perform(self, memory_type="user", content="", user_guid="", **kwargs):
        """
        Store content to memory.

        Args:
            memory_type (str): 'shared' or 'user'
            content (str): Content to store
            user_guid (str): User identifier
        """
        storage = AzureFileStorageManager()

        if memory_type == "shared":
            # Append to shared memory
            existing = storage.read_file('memory/shared', 'context.txt') or ""
            updated = existing + "\n" + content
            storage.write_file('memory/shared', 'context.txt', updated)
            return "Stored to shared memory"

        elif memory_type == "user":
            # Append to user memory
            file_name = f'{user_guid}_context.txt'
            existing = storage.read_file('memory/users', file_name) or ""
            updated = existing + "\n" + content
            storage.write_file('memory/users', file_name, updated)
            return f"Stored to memory for user {user_guid}"
```

**Memory trimming:**

To prevent memory overflow:

```python
def trim_conversation_history(history, max_messages=20):
    """
    Keep only the last N messages to prevent token overflow.

    Args:
        history (list): Conversation history
        max_messages (int): Maximum messages to keep

    Returns:
        list: Trimmed history
    """
    if len(history) > max_messages:
        return history[-max_messages:]
    return history
```

## Data Models

### Request Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "user_input": {
      "type": "string",
      "description": "User's message/query",
      "minLength": 1
    },
    "conversation_history": {
      "type": "array",
      "description": "Previous conversation messages",
      "items": {
        "type": "object",
        "properties": {
          "role": {
            "type": "string",
            "enum": ["user", "assistant", "system", "function"]
          },
          "content": {
            "type": "string"
          },
          "name": {
            "type": "string",
            "description": "Function name (for function role)"
          }
        },
        "required": ["role", "content"]
      },
      "default": []
    },
    "user_guid": {
      "type": "string",
      "description": "Unique user identifier",
      "default": "c0p110t0-aaaa-bbbb-cccc-123456789abc"
    },
    "user_context": {
      "type": "object",
      "description": "Office 365 user profile (optional)",
      "properties": {
        "email": {"type": "string"},
        "name": {"type": "string"},
        "department": {"type": "string"},
        "jobTitle": {"type": "string"}
      }
    }
  },
  "required": ["user_input"]
}
```

### Response Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "assistant_response": {
      "type": "string",
      "description": "Formatted markdown response for display"
    },
    "voice_response": {
      "type": "string",
      "description": "Concise response for voice synthesis"
    },
    "agent_logs": {
      "type": "string",
      "description": "Execution details and agent activity"
    },
    "user_guid": {
      "type": "string",
      "description": "User identifier used in this session"
    }
  },
  "required": ["assistant_response", "voice_response", "user_guid"]
}
```

### Agent Metadata Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Agent function name"
    },
    "description": {
      "type": "string",
      "description": "What the agent does"
    },
    "parameters": {
      "type": "object",
      "description": "JSON Schema for parameters",
      "properties": {
        "type": {"const": "object"},
        "properties": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "type": {"type": "string"},
              "description": {"type": "string"}
            }
          }
        },
        "required": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    }
  },
  "required": ["name", "description", "parameters"]
}
```

## Agent System

### Agent Lifecycle

```
1. Initialization (function startup)
   ↓
   Load agents from local folder + Azure storage
   ↓
2. Registration
   ↓
   Register metadata with OpenAI function calling
   ↓
3. Execution (per request)
   ↓
   a. OpenAI decides to call agent
   b. Parse function call arguments
   c. Execute agent.perform(**kwargs)
   d. Return result string
   ↓
4. Result Processing
   ↓
   Add function result to conversation
   Make follow-up OpenAI call for final response
```

### Agent Communication

**Agent-to-Agent:**
- Not directly supported (agents don't call each other)
- Coordination via multi-agent orchestration pattern:

```python
class OrchestratorAgent(BasicAgent):
    def perform(self, task="", **kwargs):
        # Execute multiple agents in sequence
        results = []

        # Step 1: Gather context
        context_agent = ContextMemoryAgent()
        context = context_agent.perform()
        results.append(context)

        # Step 2: Process with specialized agent
        email_agent = EmailDraftingAgent()
        draft = email_agent.perform(
            context=context,
            task=task
        )
        results.append(draft)

        # Step 3: Store result
        memory_agent = ManageMemoryAgent()
        memory_agent.perform(
            memory_type="user",
            content=f"Email draft: {draft}",
            user_guid=kwargs.get('user_guid')
        )

        return "\n\n".join(results)
```

## Memory Management

### Memory Types

**1. Shared Memory:**
- Accessible by all users
- Stores: System info, common knowledge, FAQs
- Location: `memory/shared/context.txt`
- Update: Admin or specialized agents

**2. User Memory:**
- Per-user storage
- Stores: Preferences, conversation history, personal data
- Location: `memory/users/{user_guid}_context.txt`
- Update: User-triggered (via ManageMemoryAgent)

**3. Session Memory:**
- Conversation history in request/response cycle
- Not persisted (unless explicitly stored)
- Managed: Client-side or Power Automate

### Memory Strategies

**Append-Only:**
```python
existing_memory = storage.read_file('memory/users', file_name)
new_memory = existing_memory + "\n" + new_content
storage.write_file('memory/users', file_name, new_memory)
```

**Key-Value:**
```python
import json

existing = storage.read_file('memory/users', file_name) or "{}"
memory_dict = json.loads(existing)
memory_dict[key] = value
storage.write_file('memory/users', file_name, json.dumps(memory_dict))
```

**Timestamped:**
```python
from datetime import datetime

entry = f"[{datetime.now().isoformat()}] {content}"
existing = storage.read_file('memory/users', file_name) or ""
updated = existing + "\n" + entry
storage.write_file('memory/users', file_name, updated)
```

## Deployment Architectures

### Standalone Deployment

```
┌──────────────┐
│  Web Client  │
│ (HTML/JS)    │
└──────┬───────┘
       │ HTTPS
       ▼
┌──────────────────┐
│ Azure Function   │
│ (Python 3.11)    │
└──────┬───────────┘
       │
       ├─────► Azure OpenAI (GPT-4)
       └─────► Azure Storage (Memory)
```

### Power Platform Deployment

```
┌─────────────┐     ┌──────────────┐
│   Teams     │────▶│   Copilot    │
│             │     │   Studio     │
└─────────────┘     └──────┬───────┘
                           │
┌─────────────┐     ┌──────▼───────┐
│  M365       │────▶│    Power     │
│  Copilot    │     │   Automate   │
└─────────────┘     └──────┬───────┘
                           │ HTTPS (with user context)
                           ▼
                    ┌──────────────────┐
                    │ Azure Function   │
                    │ (Python 3.11)    │
                    └──────┬───────────┘
                           │
                           ├─────► Azure OpenAI (GPT-4)
                           └─────► Azure Storage (Memory)
```

### Hybrid Deployment

```
┌──────────────┐     ┌──────────────┐
│  Web Client  │     │  Teams       │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │ HTTPS              │ via Power Platform
       │                    │
       ▼                    ▼
┌────────────────────────────────────┐
│      Azure Function App            │
│  ┌─────────────────────────────┐  │
│  │  businessinsightbot_function│  │
│  └─────────────────────────────┘  │
│                                    │
│  Routes based on:                  │
│  • Presence of user_context        │
│  • Source headers                  │
└──────┬─────────────────────────────┘
       │
       ├─────► Azure OpenAI (GPT-4)
       ├─────► Azure Storage (Memory)
       └─────► Application Insights (Monitoring)
```

## Scalability & Performance

### Scaling Strategies

**Vertical Scaling:**
- Function App plan: Consumption → Premium → Dedicated
- Increase memory allocation per function
- Enable "Always On" for Premium/Dedicated plans

**Horizontal Scaling:**
- Automatic with Consumption plan (up to 200 instances)
- Configurable max instances in Premium/Dedicated

**Optimization Techniques:**

1. **Connection Pooling:**
```python
from azure.storage.fileshare import ShareServiceClient

# Reuse client across invocations
_share_service_client = None

def get_share_service_client():
    global _share_service_client
    if _share_service_client is None:
        _share_service_client = ShareServiceClient.from_connection_string(
            CONNECTION_STRING
        )
    return _share_service_client
```

2. **Response Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_agent_metadata(agent_name):
    """Cache agent metadata to avoid repeated file reads."""
    # Load and return agent metadata
    pass
```

3. **Async Agent Execution:**
```python
import asyncio

async def execute_agents_async(agents, user_input):
    tasks = [asyncio.create_task(agent.perform_async(user_input))
             for agent in agents]
    results = await asyncio.gather(*tasks)
    return results
```

### Performance Metrics

**Target SLAs:**
- Cold start: < 3 seconds
- Warm request: < 1 second (excluding OpenAI latency)
- OpenAI call: 2-10 seconds (depends on response length)
- Total end-to-end: < 15 seconds

**Monitoring:**
- Application Insights: Request duration, failure rate
- Azure Monitor: Function execution count, memory usage
- Custom metrics: Agent execution time, memory operations

## Security Architecture

### Authentication & Authorization

**Standalone Mode:**
- Function key required (`x-functions-key` header)
- Optional: Azure AD authentication

**Power Platform Mode:**
- Azure AD SSO (automatic via Teams/M365)
- Function key in Power Automate (secured)

### Data Encryption

**In Transit:**
- All HTTPS (TLS 1.2+)
- Function App enforces HTTPS

**At Rest:**
- Azure Storage encryption (256-bit AES)
- Encryption keys managed by Azure (or customer-managed)

### Network Security

**IP Restrictions:**
```bash
az functionapp config access-restriction add \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --rule-name AllowPowerPlatform \
  --priority 100 \
  --ip-address POWER_PLATFORM_IP_RANGE
```

**Private Endpoints:**
- VNet integration for Function App
- Private endpoint for Storage Account
- No public internet exposure

### Secrets Management

**Azure Key Vault Integration:**
```json
{
  "Values": {
    "AZURE_OPENAI_API_KEY": "@Microsoft.KeyVault(SecretUri=https://YOUR_VAULT.vault.azure.net/secrets/OpenAI-API-Key/)",
    "AzureWebJobsStorage": "@Microsoft.KeyVault(SecretUri=https://YOUR_VAULT.vault.azure.net/secrets/Storage-Connection/)"
  }
}
```

## Next Steps

- **[Agent Development Guide](AGENT_DEVELOPMENT.md)** - Build custom agents
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment
- **[Security Best Practices](SECURITY.md)** - Secure your system
- **[API Reference](API_REFERENCE.md)** - Complete API docs

---

**Questions?** Open an issue or join the [discussion](https://github.com/kody-w/CommunityRAPP/discussions).
