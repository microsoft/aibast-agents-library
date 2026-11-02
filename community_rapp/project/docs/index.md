# CommunityRAPP Documentation

RAPP Hippocampus — the memory center for your AI agents.

## Guides

| Guide | Description |
|-------|-------------|
| [Getting Started](GETTING_STARTED.md) | Create your first project and run it locally |
| [Local Development](LOCAL_DEVELOPMENT.md) | Dev setup, GitHub Copilot auth, local testing |
| [Agent Development](AGENT_DEVELOPMENT.md) | Build custom agents with the BasicAgent pattern |
| [API Reference](API_REFERENCE.md) | Endpoints, request/response formats, auth |
| [Architecture](ARCHITECTURE.md) | System design, memory layers, request flow |
| [Deployment](DEPLOYMENT.md) | Deploy to Azure Functions |
| [Power Platform Integration](POWER_PLATFORM_INTEGRATION.md) | Connect to Teams and M365 Copilot |
| [Security](SECURITY.md) | Entra ID, RBAC, network security |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues and fixes |
| [Brainstem Guidance](BRAINSTEM_GUIDANCE.md) | Bridge from RAPP Brainstem (T1) to Hippocampus (T2) |

## Interactive

- [Get Started](../onboard.html) — one-page onboarding guide (share this!)
- [Chat UI](../index.html) — talk to your running instance
- [Business Mode](../business.html) — side-by-side multi-instance chat
- [Hatchery Flow](hatchery-flow.html) — visual diagram of the T1 to T3 journey

## Quick Links

- [GitHub Repo](https://github.com/microsoft/aibast-agents-library)
- [Report an Issue](https://github.com/microsoft/aibast-agents-library/issues)
- [RAPP Brainstem (Tier 1)](https://github.com/microsoft/aibast-agents-library)
- [CONSTITUTION.md](../CONSTITUTION.md) — governance rules
- [CONTRIBUTING.md](../CONTRIBUTING.md) — how to contribute

## Three-Tier Architecture

```
Brainstem (Tier 1)     ->  Hippocampus (Tier 2)    ->  Nervous System (Tier 3)
Local Flask server         Azure Functions runtime      Copilot Studio + Teams
GitHub Copilot LLM         Azure OpenAI                 M365 Copilot
Stateless agents           Persistent memory            Enterprise channels
```

Start small, layer up when ready. See [CONSTITUTION.md](../CONSTITUTION.md) Article XIII.
