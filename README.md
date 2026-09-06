# AIBAST Agents Library

> ⚠️ **IMPORTANT:** This is an experimental project managed by a v-team from the Artificial Intelligence Business Applications Specialist Team (AIBAST), not an officially supported Microsoft product.

> **👉 [Get Started at microsoft.github.io/aibast-agents-library](https://microsoft.github.io/aibast-agents-library/)**

Industry agent templates, the RAPP production methodology, and a local-first AI agent server powered by GitHub Copilot. No provider API key or cloud setup is required for core chat beyond a GitHub account with Copilot access.

[Production Guide](https://microsoft.github.io/aibast-agents-library/docs/rapp-guide.html) | [Agent Library](https://microsoft.github.io/aibast-agents-library/library.html) | [Library Metrics](https://microsoft.github.io/aibast-agents-library/metrics.html) | [Brainstem API and configuration](rapp_brainstem/README.md)

## Scout-Optimized Install and Brainstem Use

In Microsoft Scout, ask:

> Install RAPP from https://aka.ms/rappinstall, open Brainstem in my browser,
> and verify that a real chat request works.

Scout owns the shell, browser, health-check, authentication, and verification
steps. The user does not need to operate a terminal. The workflow keeps local
Brainstem GitHub Copilot authentication separate from Microsoft 365
authentication and never treats the local install request as approval to
provision Azure resources.

[Download the Scout skill](skills/scout-optimized-install-and-brainstem-use/SKILL.md)

### Terminal install

```
curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash
```

**Windows (PowerShell — works on factory Windows 11):**
```powershell
irm https://github.com/microsoft/aibast-agents-library/releases/download/installers/install.ps1 | iex
```
Auto-installs Python 3.11, Git, and GitHub CLI via winget if missing.

Then:
```bash
brainstem       # start the server → localhost:7071
```

The browser walks through GitHub device-code sign-in when no compatible credential is already available.

---

## Or: Start with the Cloud Backend (Hippocampus)

Want persistent memory, Azure Functions, and a path to Copilot Studio? Skip the brainstem and go straight to Tier 2:

**Mac / Linux:**
```bash
curl -fsSL https://github.com/microsoft/aibast-agents-library/releases/download/installers/community_rapp-install.sh | bash
```

**Windows:**
```powershell
irm https://github.com/microsoft/aibast-agents-library/releases/download/installers/community_rapp-install.ps1 | iex
```

Creates `~/rapp-projects/my-project/` — isolated project with its own venv, agents, and local storage. Auth happens through the chat UI (GitHub device code flow). No API keys needed to start.

[Onboarding guide](https://kody-w.github.io/CommunityRAPP/onboard.html) | [CommunityRAPP repo](https://github.com/kody-w/CommunityRAPP)

---

## How It Works

The brainstem is a Flask server that connects to GitHub Copilot's API for LLM inference. You define a **soul** (system prompt) and drop in **agents** (Python tools the LLM can call). That's it.

```
~/.brainstem/src/rapp_brainstem/
├── brainstem.py       # the server
├── soul.md            # personality (system prompt)
├── agents/            # auto-discovered tools
│   └── hello_agent.py
├── local_storage.py   # local-first storage shim
└── .env               # config (model, paths, port)
```

### Write an Agent

Any `*_agent.py` file in your agents directory gets auto-discovered and registered as a tool:

```python
from basic_agent import BasicAgent

class WeatherAgent(BasicAgent):
    def __init__(self):
        self.name = "Weather"
        self.metadata = {
            "name": self.name,
            "description": "Gets the weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
        super().__init__()

    def perform(self, city="", **kwargs):
        return f"It's sunny in {city}!"
```

### Browse the AIBAST Agent Library

The [**Agent Library**](https://microsoft.github.io/aibast-agents-library/library.html) is the browsable catalog: search across every industry template, filter by vertical, and copy the install command for one agent or a whole stack. It reads `registry.json`, which `build_registry.py` regenerates from the agent manifests on every push.

The files themselves live under [`agents/@aibast-agents-library/`](agents/@aibast-agents-library/), grouped into `*_stacks/*_stack/` folders — a stack is the set of agents that solves one industry scenario end to end. Review a template, adapt it to your environment, then drag the trusted `*_agent.py` file into the Brainstem chat or place it in the configured agents directory. Agent files are Python code and execute locally, so review them before installation.

[**Workshop achievements**](https://microsoft.github.io/aibast-agents-library/achievements.html) record self-paced milestones locally and let learners explicitly sync canonical badges to a public GitHub-attributed profile. The profile page shows the learner's achievement score.

[**Library metrics**](https://microsoft.github.io/aibast-agents-library/metrics.html) publishes AIBAST-only public downloads, every-file observations, per-agent rating Discussion upvotes, signed-in acquisition Discussion signals, workshop adoption, and opt-in achievement rollups. Each run also generates a shareable weekly/monthly PDF plus email-ready text under `reports/`. `scripts/build_metrics.py` builds the snapshot, and `scripts/build_impact_report.py` turns its dated history into the exportable impact report without converting unavailable coverage to zero.

---

## The Stack: Brainstem → Azure → Copilot Studio

RAPP teaches you the Microsoft AI stack one layer at a time. Start with the brainstem locally, then layer up when you're ready.

### 🧠 Tier 1: The Brainstem (local)

The survival basics. The brainstem runs the core agent loop — soul, tool-calling, conversation. Your GitHub Copilot subscription is the AI engine.

**What you learn:** Python agents, function-calling, prompt engineering, local-first development.

### ☁️ Tier 2: The Spinal Cord (Azure)

Give your brainstem a cloud body. Deploy to Azure so it's always-on with persistent storage, monitoring, and Azure OpenAI.

```bash
# Deploy via script
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/deploy.sh | bash
```

Or click: [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Faibast-agents-library%2Fmain%2Fazuredeploy.json)

Creates: Function App (Python 3.11), Azure OpenAI (GPT-4o), Storage Account, Application Insights. All Entra ID auth — no API keys.

**What you learn:** ARM templates, Azure Functions, managed identity, RBAC, Azure OpenAI.

### 🤖 Tier 3: The Nervous System (Copilot Studio)

Connect your agent to Teams and M365 Copilot. Import the included Power Platform solution (`MSFTAIBASMultiAgentCopilot_*.zip`) into Copilot Studio, point it at your Azure Function, and publish.

The same agent logic you tested locally now answers in Microsoft Teams and M365 Copilot across your organization.

**What you learn:** Copilot Studio, declarative agents, Power Platform solutions, Teams integration, enterprise AI.

---

## Configuration

All config via `.env` (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | auto-detected via `gh` | GitHub PAT or Copilot token |
| `GITHUB_MODEL` | `auto` | Selects the fastest available Claude Haiku, then Sonnet, then `gpt-4o`; a model selected in the UI overrides this value. |
| `SOUL_PATH` | `./soul.md` | Path to your soul file |
| `AGENTS_PATH` | `./agents` | Path to your agents directory |
| `PORT` | `7071` | Server port |
| `BRAINSTEM_LAN_MODE` | `false` | Opt in to LAN binding; non-loopback capability routes require the per-install secret. |
| `BRAINSTEM_ALLOWED_HOSTS` | *(empty)* | Optional comma-separated LAN hostnames. |
| `VOICE_ZIP_PASSWORD` | *(empty)* | Optional password for encrypted Azure Speech or ElevenLabs configuration. |

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | `{"user_input": "...", "conversation_history": [], "session_id": "..."}` |
| `/chat/stream` | POST | Server-sent event stream for chat and agent activity. |
| `/health` | GET | Status, model, loaded agents, token state |
| `/login` | POST | Start GitHub device code OAuth flow |
| `/models` | GET | List available models |
| `/agents` | GET | List installed agent files and loaded tools. |
| `/diagnostics/report` | POST | Prepare a privacy-scrubbed GitHub issue draft for review. |

## Requirements

- **Python 3.11+**
- **Git**
- **GitHub account** with Copilot access

## Updating

```bash
cd ~/.brainstem/src && git pull
```

## Uninstalling

```bash
rm -rf ~/.brainstem ~/.local/bin/brainstem
```

---

## Attribution

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).

MIT License — Copyright (c) 2026 Microsoft.
