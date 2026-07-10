# CommunityRAPP — Public Skill Interface

> **CommunityRAPP (RAPP Hippocampus) is open source.**
> Repo: [github.com/kody-w/CommunityRAPP](https://github.com/kody-w/CommunityRAPP)
> Onboarding: [kody-w.github.io/CommunityRAPP/onboard.html](https://kody-w.github.io/CommunityRAPP/onboard.html)

---

## Identity

```
repo: kody-w/CommunityRAPP (public)
public_gateway: microsoft/aibast-agents-library (this repo)
type: azure-functions-backend
purpose: Local-first AI agent platform with persistent memory
tier: Hippocampus (Tier 2) — between Brainstem (T1) and Nervous System (T3)
```

---

## What CommunityRAPP Is

The **Azure Functions backend** for the RAPP ecosystem. It provides persistent memory, auto-discovered agents, and a path from local development to Azure deployment to Copilot Studio / Teams / M365 Copilot.

**Local-first:** Runs on your machine with local file storage. No Azure account or API keys needed to start. GitHub Copilot device-code auth is built into the chat UI.

---

## One-Liner Install

**Mac / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/community_rapp/install.sh | bash
```

**Windows:**
```powershell
irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/community_rapp/install.ps1 | iex
```

Creates `~/rapp-projects/{name}/` with its own venv, dependencies, and start script.

---

## Architecture

```
User (Chat UI / Teams / M365 Copilot)
  -> Azure Function (or local func start)
    -> OpenAI function calling (agent routing)
      -> Agent performs action (memory, custom logic)
        -> Response with |||VOICE||| delimiter
```

### HTTP Triggers

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Health check (supports `?deep=true`) |
| `POST /api/businessinsightbot_function` | Main conversation endpoint |
| `POST /api/trigger/copilot-studio` | Direct agent invocation |

### API Contract

```json
// Request
POST /api/businessinsightbot_function
{
  "user_input": "string",
  "conversation_history": [],
  "user_guid": "optional-guid"
}

// Response
{
  "assistant_response": "formatted markdown |||VOICE||| concise voice text",
  "voice_response": "concise voice text",
  "agent_logs": "what agents did",
  "user_guid": "the-user-guid"
}
```

---

## Key Components

### Built-in Agents

| Agent | Purpose |
|-------|---------|
| `ContextMemory` | Recalls stored memories (keyword search, pagination, full recall) |
| `ManageMemory` | Stores memories (facts, preferences, insights, tasks) |

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `agents/` | Production agents (auto-loaded on startup) |
| `utils/` | Storage, auth, environment detection |
| `hatchery/` | Brainstem bridge agent (hosted for download, not part of runtime) |
| `docs/` | Full documentation suite |
| `tests/` | Test suite (mocked, no API keys needed) |

---

## Performance Features

- **Singleton OpenAI client** with 30-min TTL refresh
- **Agent caching** with 5-min TTL
- **Device-code auth** for GitHub Copilot (no manual env vars)
- **Dual storage** — local files or Azure File Storage
- **Entra ID auth** (Managed Identity) or key-based

---

## Compatibility

- **Python**: 3.11-3.12 (3.13+ breaks Azure Functions v4)
- **Runtime**: Azure Functions (local or Flex Consumption)
- **AI Model**: GitHub Copilot (local) or Azure OpenAI (cloud)
- **Auth**: Entra ID (Managed Identity) or key-based

---

## Version

```
last_updated: 2026-03-25
```
