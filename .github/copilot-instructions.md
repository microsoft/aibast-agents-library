# Copilot Instructions — RAPP Brainstem

## Architecture

RAPP Brainstem is a progressive AI agent platform using a biological metaphor (see `CONSTITUTION.md` for architectural principles):

1. **Brainstem** (`rapp_brainstem/`) — The core. A local-first Flask server (Python 3.11) using GitHub Copilot's API for LLM inference. No API keys needed — just `gh auth login`. This is where all development happens.
2. **Spinal Cord** (`azuredeploy.json`, `deploy.sh`) — Azure deployment. ARM template creates Function App, Azure OpenAI, Storage, App Insights. All Entra ID auth.
3. **Nervous System** (`MSFTAIBASMultiAgentCopilot_*.zip`) — Power Platform solution for Copilot Studio. Connects the Azure Function to Teams and M365 Copilot.

Everything else in the repo root (install scripts, index.html, docs/) is onboarding infrastructure. `community_rapp/` contains public skill gateways for private backend repos.

### Brainstem internals

`brainstem.py` is the single-file server containing auth, agent orchestration, the tool-calling loop, and all HTTP endpoints.

**Tool-calling loop** (`/chat`): Builds messages from soul + memory + conversation history, then runs up to **3 rounds** of LLM calls. Each round checks for `tool_calls` in the response, executes matching agents via `run_tool_calls()`, appends tool results, and loops. Falls back to `gpt-4o` if the configured model fails.

**Agent auto-discovery**: `load_agents()` globs `*_agent.py` in `AGENTS_PATH`, dynamically imports each file, finds classes with a `perform` method (excluding `BasicAgent` itself), and instantiates them. Each agent's `to_tool()` generates its OpenAI function-calling schema.

**Import shims**: `_register_shims()` injects fake `sys.modules` so agents written for the cloud (CommunityRAPP) work locally:
- `utils.azure_file_storage` → `local_storage.AzureFileStorageManager`
- `utils.dynamics_storage` → same local shim (aliased as `DynamicsStorageManager`)
- `utils.storage_factory` → returns a `LocalStorageManager` instance
- `agents.basic_agent` → the local `basic_agent.py`

**Auto-pip-install**: When loading an agent hits `ModuleNotFoundError`, `_extract_package_name()` maps import names to pip packages via `_PIP_MAP` (e.g., `bs4` → `beautifulsoup4`, `PIL` → `Pillow`), auto-installs, and retries once.

**Memory agents**: `ManageMemory` and `ContextMemory` get special treatment — the LLM-invented `user_guid` arg is stripped before calling `perform()`. The `/chat` handler auto-injects `<memory>` context from `ContextMemory` into the system prompt if that agent is loaded.

**Auth chain** (in priority order):
1. `GITHUB_TOKEN` env var
2. `.copilot_token` file (JSON with `access_token` + `refresh_token` + `saved_at`)
3. `gh auth token` CLI (skips `gho_` tokens — they lack Copilot access)
4. Device code OAuth flow via `/login` endpoint

Copilot API tokens are exchanged from the GitHub token, cached in memory (with 60s expiry buffer) and on disk. A `refresh_token` flow allows automatic re-auth without user interaction.

**Model compatibility**: `_NO_TOOL_CHOICE_MODELS` auto-detects models with `o1` in their ID — these don't support the `tool_choice` parameter. Claude models work but return multi-choice responses (text and tool_calls in separate choices); `call_copilot()` merges these into a single choice automatically.

## Running & Testing

```bash
# Start the brainstem server (creates venv at ~/.brainstem/venv if needed)
cd rapp_brainstem && ./start.sh    # port 7071

# Run tests
cd rapp_brainstem && python3 -m pytest test_local_agents.py -v

# Run a single test
python3 -m pytest test_local_agents.py::TestLocalStorage::test_write_and_read -v

# Run a single test class
python3 -m pytest test_local_agents.py::TestShimRegistration -v

# Health check
curl -s localhost:7071/health | python3 -m json.tool
```

No linter or type-checker is configured.

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serves `index.html` (chat UI) |
| `/chat` | POST | `{"user_input": "...", "conversation_history": [], "session_id": "..."}` |
| `/health` | GET | Status, model, loaded agents, token state |
| `/login` | POST | Start GitHub device code OAuth flow |
| `/login/poll` | POST | Poll for completed device code auth |
| `/login/status` | GET | Check current auth state |
| `/models` | GET | List available models |
| `/models/set` | POST | Change the active model |
| `/agents` | GET | List agent files with loaded agent names |
| `/agents/import` | POST | Upload an agent `.py` file |
| `/agents/export/<filename>` | GET | Download an agent `.py` file |
| `/agents/<filename>` | DELETE | Remove an agent `.py` file |
| `/voice` | GET | Voice mode status |
| `/voice/toggle` | POST | Toggle voice mode |
| `/voice/config` | GET | Read voice config from encrypted `voice.zip` |
| `/voice/config` | POST | Save voice config to encrypted `voice.zip` |
| `/voice/export` | POST | Export `voice.zip` for download |
| `/voice/import` | POST | Import `voice.zip` from upload |
| `/version` | GET | Server version (reads `VERSION` file) |
| `/debug/auth` | GET | Auth diagnostics |

## Writing Agents

Agents extend `BasicAgent` (`agents/basic_agent.py`) with `name`, `metadata` (OpenAI function schema), and `perform()`:

```python
from basic_agent import BasicAgent

class MyAgent(BasicAgent):
    def __init__(self):
        self.name = "MyAgent"
        self.metadata = {
            "name": self.name,
            "description": "Description the LLM reads to decide when to call this.",
            "parameters": {
                "type": "object",
                "properties": {"param1": {"type": "string", "description": "..."}},
                "required": ["param1"]
            }
        }
        super().__init__()

    def perform(self, param1="", **kwargs):
        return f"Result: {param1}"
```

- File must be named `*_agent.py` in the agents directory (subdirectories like `experimental/` are not auto-discovered)
- `perform()` must accept `**kwargs` — the LLM may pass unexpected args
- `to_tool()` on `BasicAgent` converts `metadata` to OpenAI function-calling format
- Agents importing `AzureFileStorageManager` get the local shim automatically
- For storage, use `from utils.azure_file_storage import AzureFileStorageManager` — the shim handles local vs cloud
- Return a string from `perform()` — this becomes the tool result the LLM sees

## Key Conventions

- **Python 3.11** target runtime; venv at `~/.brainstem/venv`
- **No API keys** for local dev — GitHub Copilot token exchange handles auth
- **Config via `.env`** — `GITHUB_TOKEN`, `GITHUB_MODEL`, `SOUL_PATH`, `AGENTS_PATH`, `PORT`, `VOICE_ZIP_PASSWORD` (see `.env.example`)
- **Local-first storage**: `local_storage.py` stores to `.brainstem_data/` on disk, mirroring the CommunityRAPP Azure File Storage layout (`shared_memories/memory.json` for shared, `memory/{guid}/user_memory.json` for per-user)
- **Soul file** (`soul.md`): System prompt loaded as the first message in every conversation. Users customize by editing it or pointing `SOUL_PATH` to their own
- **Skill-based onboarding**: `skill.md` uses the Moltbook pattern — YAML frontmatter, autonomous execution steps, ⏸️ pause points for user input, state saved to `~/.config/brainstem/state.json`
- **Single-file server**: All server logic lives in `brainstem.py` — auth, routing, LLM calls, agent orchestration. Keep it that way.
