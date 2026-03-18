# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Governance

**Read `CONSTITUTION.md` first.** It defines what belongs in this repo and what doesn't.

## Project Overview

CommunityRAPP is a **base memory agent platform** built on Azure Functions with Azure OpenAI integration. Think of it as a "brainstem" — a minimal, extensible runtime that gives any AI agent persistent memory across conversations.

The platform provides:
- Two built-in agents: **ContextMemory** (read) and **ManageMemory** (write)
- Dual-layer memory: shared (all users) + user-specific (per GUID)
- Three HTTP endpoints: health check, main conversation, and Copilot Studio integration
- A pattern for adding custom agents by dropping files into `agents/`

> **Disclaimer:** This is an experimental research project managed by a v-team, not an officially supported Microsoft product. The Copilot Studio YAML schema may change without notice. Always review and validate generated output before pushing to your environment — AI-generated output may contain errors or unsupported patterns.

## Development Commands

### Running Locally

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the function app
func start
```

The local endpoints will be available at:
- `http://localhost:7071/api/health` — Health check
- `http://localhost:7071/api/businessinsightbot_function` — Main conversation
- `http://localhost:7071/api/trigger/copilot-studio` — Copilot Studio direct invocation

### Testing the API

```bash
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Hello", "conversation_history": []}'
```

### Environment Setup

- **Python 3.11 required** (3.13+ breaks Azure Functions v4)
- **Dependencies:** `pip install -r requirements.txt`
- **Configuration:** Copy `local.settings.template.json` to `local.settings.json` and fill in values
- **Azure auth:** Run `az login` for local development with cloud storage

### Running Tests

```bash
# Run all 34 unit tests (mocked, no API keys needed)
python -m pytest tests/test_memory_agents.py -v

# Or use the test runner
python tests/run_tests.py
```

## Architecture

### The Brainstem Concept

This platform is the foundational layer — the "brainstem" — that other agent systems build on. It handles:
1. **Memory persistence** — storing and recalling facts, preferences, insights, and tasks
2. **User isolation** — separate memory contexts per user GUID
3. **Agent orchestration** — OpenAI function calling to route to the right agent
4. **Response formatting** — dual output (markdown + voice) via `|||VOICE|||` delimiter

### HTTP Endpoints

| Route | Auth | Methods | Purpose |
|-------|------|---------|---------|
| `/api/health` | Anonymous | GET | Health check (supports `?deep=true`) |
| `/api/businessinsightbot_function` | Function key | POST/OPTIONS | Main conversation endpoint |
| `/api/trigger/copilot-studio` | Function key | POST | Direct agent invocation from Copilot Studio |

### Core Components

**`function_app.py`** (~1031 lines) — Main entry point:
- `Assistant` class orchestrates conversations with OpenAI
- Singleton caches: OpenAI client (30-min TTL), agent cache (5-min TTL)
- GUID-based user context with default: `c0p110t0-aaaa-bbbb-cccc-123456789abc`
- Supports both tools API (gpt-4o) and legacy functions API (gpt-4-turbo)
- Retry logic (max 3 attempts, 2s delay) for OpenAI calls

**`agents/`** — Agent implementations:
- `basic_agent.py` — Base class with `name`, `metadata`, `perform(**kwargs)`
- `context_memory_agent.py` — **ContextMemory**: Recalls stored memories with keyword filtering, pagination, full recall mode
- `manage_memory_agent.py` — **ManageMemory**: Stores memories with type (fact/preference/insight/task), importance (1-5), tags

**`utils/`** — Platform utilities:
- `storage_factory.py` — Singleton factory with 30-min TTL; returns Azure or Local storage manager
- `azure_file_storage.py` — `AzureFileStorageManager` using Entra ID (ChainedTokenCredential)
- `local_file_storage.py` — `LocalFileStorageManager` using `.local_storage/` directory
- `environment.py` — Detection helpers: `is_running_in_azure()`, `should_use_azure_storage()`
- `result.py` — `Result`/`Success`/`Failure` types with `AgentLoadError` and `APIError`
- `agent_manager.py` — Singleton agent registry with `discover_agents()` auto-loading
- `generate_memory_agent_solution.py` — Generates Power Platform solution ZIPs for Copilot Studio

### Request Flow

1. HTTP POST → endpoint with `{ user_input, conversation_history, user_guid? }`
2. Load agents from local `agents/` folder (cached 5 min)
3. Create `Assistant` with user GUID (from request body, prompt, or default)
4. Initialize memory contexts (shared + user-specific)
5. Call Azure OpenAI with agent function definitions
6. If tool called → execute agent → feed result back → get final response
7. Parse response at `|||VOICE|||` delimiter into formatted + voice parts
8. Return: `{ assistant_response, voice_response, agent_logs, user_guid }`

### Response Format

Responses use the `|||VOICE|||` delimiter:
- **Before delimiter:** Full markdown-formatted response (headings, code blocks, lists)
- **After delimiter:** 1-2 sentence conversational summary for speech synthesis
- If no delimiter present, voice response is auto-generated from first sentence

### Memory Storage Layout

```
Shared Memory (all users):    {storage}/shared_memories/memory.json
User-Specific Memory:         {storage}/{user_guid}/memory.json
```

Where `{storage}` is Azure File Share (cloud) or `.local_storage/` (local dev).

### Key Design Patterns

- **String safety:** `ensure_string_content()` and `ensure_string_function_args()` sanitize all values
- **CORS:** `build_cors_response()` adds headers to every response; OPTIONS preflight supported
- **Graceful degradation:** Agent load failures are logged but don't crash; memory init failures handled
- **Intentionally invalid default GUID:** `c0p110t0-aaaa-bbbb-cccc-123456789abc` contains non-hex chars ('p','l') — this is a security feature that prevents accidental DB insertion in UUID columns

## Configuration

### Environment Variables (`local.settings.json`)

See `local.settings.template.json` for the full template. Key variables:

| Variable | Purpose |
|----------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment (e.g., `gpt-4o`) |
| `AZURE_OPENAI_API_VERSION` | API version (e.g., `2024-08-01-preview`) |
| `AZURE_OPENAI_API_KEY` | API key (optional if using Entra ID) |
| `ASSISTANT_NAME` | Bot display name |
| `CHARACTERISTIC_DESCRIPTION` | Bot personality description |
| `USE_CLOUD_STORAGE` | `true` for Azure File Storage, `false` for local |
| `USE_IDENTITY_BASED_STORAGE` | `true` for Entra ID auth to storage |
| `AzureWebJobsStorage` | Azure Storage connection string |

### Authentication

Uses **Entra ID (token-based)** authentication:
- `ChainedTokenCredential`: ManagedIdentity (Azure) → AzureCliCredential (local)
- Required RBAC roles on Function App's managed identity:
  - Storage: `Storage Blob Data Contributor`, `Storage File Data Privileged Contributor`
  - OpenAI: `Cognitive Services OpenAI User`

For local dev: `az login` is required.

## Adding Custom Agents

Create a new file in `agents/` (e.g., `my_agent.py`):

```python
from agents.basic_agent import BasicAgent

class MyAgent(BasicAgent):
    def __init__(self):
        self.name = 'MyAgent'
        self.metadata = {
            "name": self.name,
            "description": "What this agent does",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Input parameter"
                    }
                },
                "required": ["input"]
            }
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        input_data = kwargs.get('input', '')
        return f"Processed: {input_data}"
```

Agents are auto-discovered on startup. Files matching `*_agent.py` in `agents/` are loaded.

## Deploy to Azure

Use the Copilot deploy skill (`.github/copilot/skills/deploy-to-azure.md`) or deploy manually:

```bash
# ARM template provisions: Function App, OpenAI, Storage, App Insights
az deployment group create --resource-group YOUR_RG --template-file azuredeploy.json

# Deploy code (MUST use --build remote for Linux compatibility)
func azure functionapp publish YOUR_FUNCTION_APP --build remote
```

Key deployment notes:
- Storage `publicNetworkAccess` must stay **enabled** (Flex Consumption requires it)
- Use `--build remote`, never `--build local` (avoids macOS binary issues like `jiter`)
- After deploy, sync triggers if functions don't appear

## Deploy to Copilot Studio

Generate a Power Platform solution ZIP to connect this platform to Teams/M365 Copilot:

```bash
python utils/generate_memory_agent_solution.py \
  --function-url https://YOUR_APP.azurewebsites.net \
  --function-key YOUR_FUNCTION_KEY \
  --output CommunityRAPPMemoryAgent_1_0_0_0.zip
```

Import the resulting ZIP into Power Platform at [make.powerapps.com](https://make.powerapps.com) → Solutions → Import.

## Important Notes

- **Never commit `local.settings.json`** — contains secrets; use the template
- **Python 3.11 required** — 3.13+ breaks Azure Functions v4
- **Response format** must include `|||VOICE|||` delimiter for proper voice/formatted splitting
- **Default GUID is intentionally invalid** — security guardrail, not a bug
- **Memory trimming** — conversation history limited to last 20 messages
- **Singleton TTLs** — OpenAI client: 30 min, agent cache: 5 min, storage manager: 30 min
- **Tests are fully mocked** — no API keys or Azure access needed to run the test suite
