# Copilot Instructions — AI BAST Agents Library

## Architecture

This is the **AI BAST Agents Library** — an agent registry and local-first AI agent platform for the RAPP ecosystem. It contains industry vertical agent templates and a local brainstem server.

### Core principle: Single File Agent

Every agent is **one `.py` file** — no separate manifest, no README, no subdirectory per agent. The `__manifest__` dict embedded in the file IS the package metadata. The docstring IS the documentation. See `CONSTITUTION.md` for the full rationale.

### Key files

- `build_registry.py` — AST-parses all `.py` files under `agents/`, extracts `__manifest__` dicts, validates them, and writes `registry.json`. No imports or code execution.
- `registry.json` — **Auto-generated. Never hand-edit.** CI overwrites it on every push to `main`.
- `skill.md` — Machine-readable interface for AI agents to discover/install agents programmatically.
- `CONSTITUTION.md` — Governing document. Defines the single-file principle, namespace rules, quality tiers, security requirements, and categories.
- `rapp_brainstem/` — Local-first Flask server powered by GitHub Copilot.

### Agent structure

```
agents/@aibast-agents-library/vertical_stacks/stack_name/agent.py
```

Each agent file contains:
1. A docstring (serves as README)
2. A `__manifest__` dict (serves as package metadata)
3. A class inheriting `BasicAgent`
4. A `perform(**kwargs)` method that returns a `str`

### Categories

`core` | `pipeline` | `integrations` | `productivity` | `devtools` | industry verticals (b2b_sales, healthcare, manufacturing, etc.)

### Quality tiers

`community` → `verified` → `official` (promotion by maintainers)

## Build & Validate

```bash
# Validate all manifests and rebuild registry.json
python build_registry.py
```

This is the only build step. CI runs it on every push via `.github/workflows/build-registry.yml`.

## Testing

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_registry_build.py
pytest tests/test_agent_contract.py
```

Tests are parametrized over all agent files under `agents/@aibast-agents-library/`. The `conftest.py` discovers agents, imports each via `importlib`, finds the `BasicAgent` subclass, and yields `(module, class, path)` tuples.

## RAPP Brainstem

The local-first AI agent server lives in `rapp_brainstem/`:

```bash
cd rapp_brainstem
pip install -r requirements.txt
python brainstem.py  # starts on localhost:7071
```

Or use the one-liner installer:
```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.sh | bash
```

## Agent `__manifest__` schema

Required fields: `schema`, `name`, `version`, `display_name`, `description`, `author`, `tags`, `category`.

Optional: `quality_tier` (default `community`), `requires_env` (list of env var names), `dependencies` (list of `@publisher/slug`).

```python
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/my-agent",
    "version": "1.0.0",
    "display_name": "My Agent",
    "description": "One sentence.",
    "author": "AIBAST",
    "tags": ["keyword1", "keyword2"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}
```

## Conventions

- **Agents return strings** — `perform()` always returns `str`.
- **No network calls in `__init__()`** — constructors must be fast.
- **Secrets via env vars** — use `os.environ.get()`, declare in `requires_env`.
- **Handle missing env vars gracefully** — return error message, don't crash.
- **`display_name` must match `self.name`** in the agent class.
- **Semver versioning** — bump version in `__manifest__` on updates.

## Python

- **Version**: 3.11+ (required for Azure Functions v4)
- **AI model**: Azure OpenAI or GitHub Copilot — agents should not hardcode model names.
