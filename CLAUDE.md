# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the AI BAST (Business Applications Solution Technologies) Specialist Team AI Agents Library — a Microsoft project for building and deploying AI agent automation capabilities integrated with Microsoft 365, Teams, and Copilot Studio.

> ⚠️ This is an experimental project managed by a v-team from the Artificial Intelligence Business Applications Specialist Team (AIBAST), not an officially supported Microsoft product.

The framework implements the **Rapid Agent Prototype Pattern (RAPP)** — a 14-step process from customer discovery through production deployment, with a focus on rapid MVP validation and iterative customer feedback.

## Architecture

The system uses a three-tier architecture:

1. **Tier 1 — The Brainstem (Local)**: Flask server + GitHub Copilot for local agent development
2. **Tier 2 — The Spinal Cord (RAPP on Azure)**: Azure Function App + Azure OpenAI + Azure File Storage for cloud deployment
3. **Tier 3 — The Nervous System (Copilot Studio)**: Teams + M365 Copilot via Power Platform solution import or native YAML authoring with [Skills for Copilot Studio](https://github.com/microsoft/skills-for-copilot-studio)

**Key Design Principles**:
- Agents are single `.py` files with embedded `__manifest__` dicts — no separate manifests
- Agents are hot-loaded (no redeployment needed for updates)
- Stateless function design enables horizontal scaling
- Universal memory allows context persistence across interfaces

## Build & Validate

```bash
# Build the agent registry (auto-generates registry.json from __manifest__ dicts)
python build_registry.py

# Run all tests
pytest

# Run specific test files
pytest tests/test_registry_build.py
pytest tests/test_agent_contract.py
```

The `build_registry.py` script uses AST parsing to extract `__manifest__` dicts from all agent `.py` files — no imports or execution. `registry.json` is auto-generated and should never be hand-edited. CI rebuilds it on every push via `.github/workflows/build-registry.yml`.

## RAPP Brainstem (Local Development)

The brainstem kernel (`rapp_brainstem/brainstem.py`) is a **frozen kernel** vendored verbatim from the [rapp-installer grail](https://github.com/kody-w/rapp-installer/tree/main/rapp_brainstem) — currently **v0.6.0** (`rapp_brainstem/VERSION`). Never hand-edit it; re-vendor from the grail and bump the pin in `rapp_brainstem/test_kernel_version.py`.

```bash
cd rapp_brainstem
pip install -r requirements.txt
python brainstem.py  # starts on localhost:7071
```

Or use the one-liner installer:
```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.sh | bash
```

## Agent Development

Agents are Python files that:
- Follow the single-file principle (see `CONSTITUTION.md`)
- Contain a `__manifest__` dict with metadata (schema, name, version, display_name, description, author, tags, category)
- Inherit from `BasicAgent` (defined in `agents/@aibast-agents-library/templates/basic_agent.py`)
- Implement `perform(**kwargs)` that returns a `str`
- Are stored in `agents/@aibast-agents-library/{vertical}_stacks/{stack_name}/`

### Agent Conventions
- `perform()` always returns `str`
- No network calls in `__init__()` — keep constructors fast
- Secrets via env vars — use `os.environ.get()`, declare in `requires_env`
- Handle missing env vars gracefully (return error message, don't crash)
- Semver versioning in `__manifest__`

## Documentation

- `docs/rapp-guide.html` — Comprehensive RAPP 14-step production guide
- `CONSTITUTION.md` — Governing document for agent standards
- `CONTRIBUTING.md` — How to contribute agents
- `skill.md` — Machine-readable AI interface for agent discovery

## License

This project uses the MIT License (Copyright 2026 Microsoft).
