# RAPP Agent Registry Constitution — AI BAST Agents Library

> The governing document for the AI BAST Agents Library. Read this before submitting or installing agents.

> ⚠️ **IMPORTANT:** This is an experimental project managed by a v-team from the Artificial Intelligence Business Applications Specialist Team (AIBAST), not an officially supported Microsoft product. Agent templates are starting points that must be customized before production use.

---

## Article I — Purpose

This repository is the **agent registry** for the AIBAST (Artificial Intelligence Business Applications Specialist Team) ecosystem. It is the place where AI agent templates are published, discovered, and installed for use with the RAPP (Rapid Agent Prototype Pattern) platform.

**One principle above all: Single File Agent.** Every agent is one `.py` file. The manifest lives inside it. The docstring is the documentation. There is nothing else.

---

## Article II — The Single File Principle

This is non-negotiable. It is the foundation of RAPP and the reason this ecosystem works.

### An agent is ONE file.

```
agents/@aibast-agents-library/vertical_stacks/stack_name/agent.py
```

### Inside that file:

1. **A docstring** — serves as the README
2. **A `__manifest__` dict** — serves as the package metadata
3. **A class inheriting `BasicAgent`** — serves as the agent
4. **A `perform()` method** — serves as the entry point

### There is no:

- `manifest.json` — the manifest is `__manifest__` inside the `.py`
- `README.md` per agent — the docstring is the readme
- `requirements.txt` — agents use what the platform provides
- Multi-file agents — if it can't fit in one file, split it into two agents

**Why:** A single file can be fetched with one HTTP GET, installed with one file write, read by an LLM in one context window, and understood by a human in one sitting. This is the competitive advantage.

---

## Article III — Namespace Ownership

### Publishers

Every agent lives under a publisher namespace: `@publisher/agent-slug`

- **`@aibast-agents-library`** = the primary publisher for this repo
- **`@yourname`** = your GitHub username for community contributions
- **`@rapp`** = reserved for official base packages

### Rules

1. **Your namespace is yours** — no one else can publish under it
2. **Slugs are kebab-case** — `my-cool-agent`, not `MyCoolAgent`
3. **No squatting** — namespaces that sit empty for 6+ months may be reclaimed
4. **No impersonation** — `@microsoft/` requires proof of org membership

---

## Article IV — The Manifest

Every agent file must contain a `__manifest__` dict. The registry builder extracts it via AST parsing — no imports, no execution.

```python
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/my-agent",
    "version": "1.0.0",
    "display_name": "My Agent",
    "description": "What this agent does in one sentence.",
    "author": "AIBAST",
    "tags": ["category", "keyword1", "keyword2"],
    "category": "integrations",
    "quality_tier": "community",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}
```

### Required Fields

| Field | Rules |
|-------|-------|
| `schema` | Always `"rapp-agent/1.0"` |
| `name` | `@publisher/slug` — must match file path |
| `version` | Semver: `MAJOR.MINOR.PATCH` |
| `display_name` | Human-readable name |
| `description` | One sentence. Searchable. |
| `author` | Your name or team name |
| `tags` | List of lowercase keywords for search |
| `category` | One of the defined categories |

---

## Article V — Quality Tiers

| Tier | Who Sets It | Meaning |
|------|-------------|---------|
| `community` | Automatic on submission | Passes `build_registry.py` validation. Not reviewed. |
| `verified` | Repo maintainer | Reviewed, tested, follows standards, no security issues. |
| `official` | Core team | Maintained by core team. Guaranteed compatibility. |

---

## Article VI — Categories

| Category | For agents that... |
|----------|-------------------|
| `core` | Provide fundamental capabilities — memory, orchestration |
| `pipeline` | Build, generate, transpile, or deploy other agents |
| `integrations` | Connect to external systems — Dynamics 365, SharePoint |
| `productivity` | Create content or automate tasks |
| `devtools` | Help developers — base classes, testing, scaffolding |
| Industry verticals | `b2b_sales`, `healthcare`, `manufacturing`, etc. |

---

## Article VII — Security & Trust

### Agents MUST NOT:

- Contain secrets, API keys, tokens, or credentials
- Include customer data, PII, or proprietary business logic
- Make network calls in `__init__()` — keep constructors fast
- Execute arbitrary code on import — only on explicit `perform()` calls
- Obfuscate code — all logic must be readable

### Agents MUST:

- Declare all required environment variables in `requires_env`
- Handle missing env vars gracefully (return error message, don't crash)
- Use `os.environ.get()` for configuration — never hardcode endpoints
- Be fully readable — no minification, no encoded payloads

---

## Article VIII — Compatibility

All agents in this registry target:

- **Python**: 3.11+
- **Runtime**: RAPP Brainstem / RAPP on Azure
- **Base class**: BasicAgent
- **AI Model**: Azure OpenAI or GitHub Copilot (agents should not hardcode model names)

---

## Article IX — Amendments

This constitution can be amended by opening a PR that modifies `CONSTITUTION.md`. The spirit of this document is **simplicity**. Single file. Single principle. Single source of truth.

---

*Ratified on initial repo creation. The single file is the law.*
