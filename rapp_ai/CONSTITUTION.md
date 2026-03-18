# CommunityRAPP Constitution

> The governing document for this repository. Read this before contributing.

---

## Article I — Purpose

CommunityRAPP is the **Azure Functions backend** for the RAPP (Rapid Agent Prototyping Platform) ecosystem. It is the engine that powers agent creation, execution, and orchestration.

**This repo does ONE thing well:** it takes a transcript, discovery call, or user request and turns it into a production-ready AI agent deployed on Azure — with memory, multi-user support, and Microsoft 365 integration.

**This is a community tool.** Every file tracked in this repo must serve any user deploying their own instance — not just one project or customer.

---

## Article II — Scope

### What Belongs Here

| Category | Examples |
|----------|---------|
| **Core Runtime** | `function_app.py`, `host.json`, `requirements.txt` |
| **Agents** | Business agents that inherit from `BasicAgent` and do real work |
| **Utilities** | Storage, environment, results, Copilot Studio (API, templates, triggers) |
| **Documentation** | Architecture, API reference, deployment, Copilot Studio guides |
| **Tests** | Unit tests, integration tests, plumbing tests, live API tests |
| **Demos** | Scripted demo JSON files for the ScriptedDemoAgent |
| **Deployment** | ARM templates, `.funcignore`, CI/CD workflows, deployment configs |
| **RAPP Pipeline** | The 14-step methodology: discovery → MVP → code → quality gates → deploy |
| **Power Platform Harness** | `MSFTAIBASMultiAgentCopilot_*.zip` — the Copilot Studio solution that connects RAPP to Teams/M365 Copilot |

### What Does NOT Belong Here

| Category | Why | Where Instead |
|----------|-----|---------------|
| Customer-specific agents or demos | Ties the repo to one engagement | Your local workspace or private fork |
| Transpiled output (`transpiled/`) | Generated artifacts — rebuild from source agents | Gitignored; lives locally |
| Project-specific solution ZIPs | Binary artifacts tied to one deployment | GitHub Releases or private storage |
| RAPP project workspaces (`.rapp/`, `rapp_projects/`) | Personal experiment data, archives | Gitignored; lives locally |
| Customer-specific HTML (`index-*.html`) | One-off UIs for specific customers | Your local workspace |
| Credentials or PII | Security risk | `local.settings.json` (gitignored) |

---

## Article III — Directory Structure

```
CommunityRAPP/
├── agents/              # Production agents (BasicAgent subclasses)
├── demos/               # Demo script JSON files
│   └── tools/           # Demo capture scripts, HTML tools, bookmarklets
├── docs/                # Documentation, architecture diagrams, PPT templates
├── tests/               # Test suite
├── utils/               # Core utilities
│   ├── copilot_studio/  # Templates, triggers, deploy config
│   └── triggers/        # Trigger engine (router, registry, models)
├── .claude/             # Claude Code configuration
├── .github/             # GitHub workflows, Copilot instructions
├── function_app.py      # Main Azure Function entry point
├── host.json            # Azure Functions host configuration
├── requirements.txt     # Python dependencies
├── azuredeploy.json     # ARM deployment template
├── index.html           # Web chat interface
├── MSFTAIBASMultiAgentCopilot_*.zip  # Copilot Studio harness (community asset)
├── CHANGELOG.md         # Version history
├── CLAUDE.md            # Claude Code guidance
├── CONSTITUTION.md      # This file
├── README.md            # Project readme
└── QUICK_START.md       # Quick start guide
```

**Gitignored (local-only, never tracked):**
- `.rapp/` — RAPP ecosystem workspace, archives, experiments
- `transpiled/` — Generated Copilot Studio artifacts
- `rapp_projects/` — Project working directories
- `*.zip` (except `MSFTAIBASMultiAgentCopilot_*.zip`) — Project-specific solution packages
- `index-*.html` — Customer-specific web UIs
- `local.settings.json` — Credentials and config

---

## Article IV — Agent Standards

### Every agent MUST:

1. **Inherit from `BasicAgent`** (`agents/basic_agent.py`)
2. **Define `name`** — a clear, descriptive string
3. **Define `metadata`** — valid JSON schema for OpenAI function calling
4. **Implement `perform(**kwargs)`** — the agent's core logic
5. **Return a string** — the result passed back to the conversation
6. **Be a single file** — one agent per `.py` file in `agents/`
7. **Be generic** — no hardcoded customer names, endpoints, or credentials

### Every agent SHOULD:

- Handle errors gracefully (return error messages, don't crash)
- Use `logging.info()` and `logging.error()` for observability
- Import storage via `utils.storage_factory.get_storage_manager()`
- Work both locally and in Azure without code changes

### Agents MUST NOT:

- Require packages not in `requirements.txt` (auto-install is a fallback, not a strategy)
- Store secrets in code — use environment variables
- Break the `|||VOICE|||` response delimiter contract
- Reference specific customers, deployments, or endpoints

---

## Article V — Community-First Principle

Every file in this repo must pass the **"thousand strangers" test:**

> *If a thousand developers cloned this repo tomorrow, would this file help them — or confuse them?*

### Rules:

1. **No hardcoded resource names** — use `YOUR_*` placeholders in docs, environment variables in code
2. **No customer-specific content** — agents, demos, and UIs must be generic or serve as reusable examples
3. **No binary artifacts** except the Copilot Studio harness (`MSFTAIBASMultiAgentCopilot_*.zip`) which is a community asset needed for Power Platform integration
4. **Generated output is gitignored** — `transpiled/`, `rapp_projects/`, `.rapp/` live locally
5. **Templates over instances** — provide `local.settings.template.json`, not `local.settings.json`

---

## Article VI — Contributing

### Before You Commit

Ask yourself:
1. Does this change serve the RAPP pipeline or agent runtime? → ✅ Proceed
2. Does this add RAPPverse, RAPPbook, or social features? → ❌ Wrong repo
3. Does this add a new agent? → ✅ Follow Article IV standards
4. Does this add a new top-level directory? → 🤔 Probably wrong — discuss first
5. Does this include customer-specific content? → ❌ Strip it or gitignore it

### Pull Request Standards

- **One concern per PR** — don't bundle unrelated changes
- **Tests pass** — `python tests/run_tests.py` must succeed
- **No secrets** — never commit `local.settings.json` or API keys
- **No project-specific content** — no customer names, resource IDs, or endpoint URLs
- **CLAUDE.md updated** — if you change architecture, update the guidance

### Branch Naming

```
feature/agent-name        # New agent
fix/issue-description     # Bug fix
docs/topic                # Documentation
refactor/component        # Code improvement
```

---

## Article VII — Deployment Contract

The production deployment target is **Azure Functions (Flex Consumption)** with:

- **Python 3.11** (required — 3.13+ breaks Azure Functions v4)
- **Entra ID authentication** (preferred) or key-based (legacy via `USE_IDENTITY_BASED_STORAGE`)
- **Remote build** (`func azure functionapp publish --build remote`)
- **HTTP triggers**: `businessinsightbot_function` (main) + `copilot_studio_trigger` (Copilot Studio)

The main API contract:

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

**Do not change this contract without updating all consumers.**

---

## Article VIII — Memory & Storage

- **Shared memory**: accessible to all users
- **User memory**: scoped by GUID, isolated per user
- **Storage backend**: Azure File Storage (cloud) or `.local_storage/` (local dev)
- **Auth modes**: Identity-based (Managed Identity, recommended) or key-based (legacy)
- **Feature flag**: `USE_IDENTITY_BASED_STORAGE=true` for identity-based storage access
- **Factory pattern**: `get_storage_manager()` auto-detects environment

The default GUID (`c0p110t0-aaaa-bbbb-cccc-123456789abc`) is **intentionally invalid** — it's a guardrail against accidental database insertion. See CLAUDE.md for details.

---

## Article IX — What "Clean" Means

This repo follows the standards:

1. **Root is scannable** — you can understand the project from `ls`
2. **No orphan files** — every file has a clear purpose and home
3. **No ecosystem sprawl** — RAPP ecosystem components live in their own repos
4. **No project baggage** — customer data, experiments, and generated output stay local
5. **Agents are agents** — they follow `BasicAgent`, they do one thing
6. **Docs match reality** — if code changes, docs change
7. **Gitignore is the gatekeeper** — anything project-specific is blocked at the gate, not cleaned up later

---

## Article X — Community Contributions

This repo welcomes contributions from community forks. When integrating external contributions:

1. **Attribution required** — use `Co-authored-by:` trailers in commits
2. **No customer data** — strip customer directories, PII, and credentials
3. **No customer-specific transpiled agents** — only generic templates and structure
4. **Demo captures with customer data** — excluded (screenshots, recordings)
5. **Generic examples welcome** — agent names as examples in code are fine
6. **Document what was included and excluded** — in the commit message and CHANGELOG

### Contributors

| Contributor | Fork | Contributions |
|-------------|------|---------------|
| **Bill Whalen** | [CommunityRAPP-BillWhalen](https://github.com/billwhalenmsft/CommunityRAPP-BillWhalen) | Agent transpiler, Copilot Studio integration, performance optimizations, trigger system, MCS templates, architecture diagrams |

---

## Article XI — Data Protection

### Never commit:

- `local.settings.json` or any file containing API keys/connection strings
- Customer-specific directories (e.g., `customers/masterchief/`, `customers/cortana/`)
- Demo captures containing customer conversations or screenshots
- Customer-specific transpiled agents or deployment configs
- Project-specific solution ZIPs (only `MSFTAIBASMultiAgentCopilot_*.zip` is allowed)
- Any personally identifiable information (PII)
- Hardcoded Azure resource names, subscription IDs, or endpoint URLs

### Safe to include:

- Agent/project names used as code examples (e.g., `microsoftzune` as a demo identifier)
- Generic templates that reference `YOUR_*` placeholder names
- Architecture diagrams with anonymized data flows
- Publicly available API patterns and integrations
- The Copilot Studio harness ZIP (community asset for Power Platform integration)

---

## Article XII — Copilot Studio Transpilation Fidelity

When transpiling Python agents (`.py`) to Copilot Studio native solutions, **all metadata MUST be sourced directly from the original `.py` agent files** — never invented, abbreviated, or left empty. This ensures no fidelity is lost between the Python agent and its Copilot Studio counterpart.

### Required Mappings (Python → Copilot Studio)

| Python Agent Field | Copilot Studio Target | Notes |
|---|---|---|
| `self.metadata["description"]` | `bot.xml` `<description>` tag AND `botcomponent.xml` `<description>` tag | This is what the orchestrator sees when adding sub-agents. **If empty, the orchestrator cannot pick the agent.** |
| `self.metadata["description"]` | GPT component `displayName` | Short name shown in UI |
| System prompt / docstring / `self.metadata` | GPT component `instructions` field in `data` file | Full detailed instructions — must match the depth of the `.py` agent's behavior |
| `self.metadata["parameters"]["properties"]` | Topic trigger phrases + question nodes | Each parameter becomes a data collection step |
| `self.metadata["parameters"]["properties"]["action"]["enum"]` | Individual topics (one per action) | Each action in `perform()` maps to a topic |
| Class docstring | Agent description in solution manifest | High-level purpose |

### Rules

1. **Never leave description empty.** The orchestrator requires a description to route to sub-agents. Pull it verbatim from `self.metadata["description"]` in the `.py` file.
2. **Never abbreviate instructions.** The GPT `instructions` in the `data` file must be as detailed as the Python agent's actual behavior — including all parameters, response formats, error handling, and edge cases.
3. **Never invent capabilities.** If the `.py` agent doesn't do something, the Copilot Studio version must not claim to either.
4. **`isAgentConnectable` must be `true`** for any agent intended to be used as a sub-agent by an orchestrator.
5. **Test the import.** Every solution ZIP must be verified by actually importing into a Copilot Studio environment — not just by checking file structure.

---

## Article XIII — Amendments

This constitution can be amended by:

1. Opening a PR that modifies `CONSTITUTION.md`
2. Explaining why the change is needed in the PR description
3. Getting approval from a repo maintainer

The spirit of this document is **focus**. If an amendment would broaden scope beyond "Azure Functions backend for RAPP agent pipeline," it should be a new repo instead.

---

*Ratified on initial repo cleanup. Revised for community-first principles.*
