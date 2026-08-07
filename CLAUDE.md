# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

AIBAST Agents Library is the stable Microsoft downstream for the RAPP (Rapid Agent Prototype Pattern) stack. It combines the local Brainstem server, an industry agent-template catalog, the RAPP production guide, Azure deployment assets, and a Power Platform solution.

Philosophy: "engine, not experience" — this is infrastructure, not a consumer product. See `CONSTITUTION.md` for scope rules and governance.

## Repository Layout

- `rapp_brainstem/` — The core brainstem server (see `rapp_brainstem/CLAUDE.md` for deep internals)
- `agents/@aibast-agents-library/` — AIBAST-owned industry templates and stacks; never replace this tree from Grail
- `registry.json`, `build_registry.py` — generated catalog and its AIBAST-owned builder
- `install.sh`, `install.ps1`, `install.cmd` — One-liner installers (Brainstem path). **These are sacred** — any change must be tested end-to-end on a fresh machine.
- `community_rapp/` — Hippocampus (Tier 2) installer scripts. Parallel path, no dependency on brainstem.
- `rapp_ai/` — AIBAST-owned Azure Functions implementation and documentation
- `azuredeploy.json`, `deploy.sh`, `deploy.ps1` — Azure ARM deployment (Tier 2 cloud)
- `MSFTAIBASMultiAgentCopilot_*.zip` — Power Platform solution for Copilot Studio (Tier 3)
- `index.html` — AIBAST Agents Library landing page served at microsoft.github.io/aibast-agents-library
- `library.html` — browsable agent catalog (search, vertical filter, per-agent and per-stack install commands); reads `registry.json`
- `metrics.html`, `scripts/build_metrics.py`, `state/metrics*.json` — public metrics dashboard and its daily snapshot
- `docs/rapp-guide.html` — Restored 14-step RAPP production methodology
- `docs/` — Quick start, tutorial, production guide, and installer mirrors
- `skill.md` — Moltbook-pattern onboarding skill (YAML frontmatter, autonomous steps, pause points)

## Commands

```bash
# Start brainstem server (creates venv, installs deps, launches on port 7071)
cd rapp_brainstem && ./start.sh

# Direct run (assumes deps installed)
cd rapp_brainstem && python brainstem.py

# Run all Brainstem tests
cd rapp_brainstem && python -m pytest tests -v

# Run a single test
cd rapp_brainstem && python -m pytest tests/test_local_agents.py::TestLocalStorage::test_write_and_read -v

# Validate and regenerate the AIBAST registry
python build_registry.py
python -m pytest tests -v

# Refresh the public metrics snapshot (state/metrics.json)
python scripts/build_metrics.py            # live; GITHUB_TOKEN with admin:read unlocks traffic
python scripts/build_metrics.py --offline  # no network, catalog composition only

# Health check (server must be running)
curl -s localhost:7071/health | python3 -m json.tool

# Test installer (bash)
bash tests/test_installer.sh
```

No linter, formatter, or type checker is configured.

## Architecture: Three Tiers

| Tier | Name | What | Key Files |
|------|------|------|-----------|
| 1 | **Brainstem** (local) | Flask server + GitHub Copilot API | `rapp_brainstem/brainstem.py` |
| 2 | **Spinal Cord** (Azure) | Azure Functions + Azure OpenAI | `azuredeploy.json`, `deploy.sh` |
| 3 | **Nervous System** (M365) | Copilot Studio + Teams | `MSFTAIBASMultiAgentCopilot_*.zip` |

Each tier is self-contained. Users advance when they choose to.

## Brainstem Server (rapp_brainstem/)

**Single-file server**: All logic lives in `brainstem.py` (~3,300 lines) — auth, routing, streaming, diagnostics, LLM calls, and agent orchestration. Keep it that way.

**Request flow (`POST /chat` and `POST /chat/stream`)**: Load soul.md -> discover agents from `agents/*_agent.py` -> call Copilot API with tools -> execute tool calls via agent `.perform()` -> loop up to 3 rounds -> return JSON or server-sent events.

**Agent system**: Files matching `agents/*_agent.py` are auto-discovered (flat directory only, `experimental/` excluded). Each extends `BasicAgent` with `metadata` (OpenAI function schema) and `perform(**kwargs)`. Agents reload from disk every request — no restart needed.

**Auth chain** (priority order): `GITHUB_TOKEN` env var -> `.copilot_token` file -> `gh auth token` CLI -> device code OAuth via `/login`. Copilot API tokens are short-lived with auto-refresh.

**Import shims**: `_register_shims()` injects `sys.modules` so agents written for CommunityRAPP (cloud) work locally — `utils.azure_file_storage` maps to `local_storage.py`.

**Memory agents**: `ManageMemory` and `ContextMemory` get special handling — `user_guid` arg is stripped, and `/chat` auto-injects `<memory>` context if ContextMemory is loaded.

## Branching and Release Model

**`main` is production.** The install one-liners (`curl ... install.sh | bash`) pull from `main`. Users get whatever is on `main`.

**Development happens on feature/fix branches.** Commits accumulate on the working branch (e.g., `3-device-code-auth-gets-stuck-...`). Multiple fixes and features can stack up before merging.

**Promotion path:**
1. Commit to feature branch (where active development happens)
2. When ready to release, merge to `main` with a `release: vX.Y.Z` commit
3. Bump `rapp_brainstem/VERSION` as part of the release commit

**Do not push directly to `main`** except via a merge at release time. The one-liner install is sacred — `main` must always be in a working state.

## Grail Downstream Boundary

Shared Brainstem releases flow from `kody-w/rapp-installer`, but this repository is not a mirror. Preserve these AIBAST-owned surfaces during every sync:

- `agents/@aibast-agents-library/`, `registry.json`, and `build_registry.py`
- `library.html`, `metrics.html`, `scripts/build_metrics.py`, and `state/` (the catalog browse page, the metrics dashboard, and its snapshots)
- `rapp_ai/`
- `README.md`, `index.html`, `CLAUDE.md`, `docs/index.html`, `docs/tutorial.html`, and `docs/rapp-guide.html`
- `.github/`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `.vscode/`, and `tools/`

Only repository-identity references are rewritten mechanically: `kody-w/rapp-installer` becomes `microsoft/aibast-agents-library`, and Brainstem support drafts target `microsoft/aibast-agents-library`. Content repositories such as CommunityRAPP are separate dependencies and must be reviewed rather than globally replaced. Installer mirrors under `docs/install.*` must remain byte-identical to their root counterparts.

## Key Conventions

- **Python 3.11** target; venv at `~/.brainstem/venv`
- **No API keys** for local dev — GitHub Copilot token exchange handles auth
- **Config via `.env`** in `rapp_brainstem/` — `GITHUB_TOKEN`, `GITHUB_MODEL` (default `auto`), `SOUL_PATH`, `AGENTS_PATH`, `PORT`, `BRAINSTEM_LAN_MODE`, `BRAINSTEM_ALLOWED_HOSTS`, and `VOICE_ZIP_PASSWORD`
- Two install paths exist and must never cross-contaminate: brainstem (`install.sh`) and hippocampus (`community_rapp/install.sh`)
- The landing page (`index.html`) and `docs/` are static HTML — no build step
