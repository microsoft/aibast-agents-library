# Changelog

All notable changes to CommunityRAPP are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Dates are UTC.

---

## [Unreleased]

## [2.1.0] — 2026-03-10

### 🏗️ Repository Cleanup

#### Archived
- `rappbook/` directory (posts, index, data) → `.rapp/ARCHIVED/RappbookSystem/`
- 10 GitHub Actions workflows (rappbook-auto-merge, content-generation, content-crawler, dimension-sync, rappzoo-auto-merge, rebuild-index, autonomous-ticker, data-warehouse, federated-warehouse, git-scrape)
- GitHub scripts (generate-post.js, update-index.js) and rappbook copilot instructions

#### Reorganized
- **Copilot Studio consolidation**: Moved `templates/mcs/`, `transpiled/`, `triggers/`, `copilot_studio_deployment_config.json`, and 3 Copilot Studio docs into `utils/copilot_studio/` — one location for all Copilot Studio infrastructure
- **Demo organization**: Moved HTML tools, Python scripts, and bookmarklets from `demos/` root into `demos/tools/` — `demos/` root now contains only JSON demo data

#### Removed
- `.github/agents/my-agent.agent.md` (empty scaffold)
- `docs/ZURNELKAY_CI_SYSTEM.md` (customer-specific)
- `docs/contract_analysis_e2e_test_script.md` (customer-specific)
- `docs/deploy.html` (redundant with azuredeploy.json)
- `functions.json` (unnecessary with Python v2 decorator model)

#### Fixed
- `tests/test_rapp_pipeline.py` — rewrote to import from actual `agents.rapp_agent.RAPPAgent` instead of nonexistent separate agent modules (12 tests, all passing)
- Updated code paths in `utils/mcs_generator.py`, `agents/copilot_studio_transpiler_agent.py`, `agents/agent_generator_agent.py`, `utils/triggers/trigger_registry.py` for new `utils/copilot_studio/` locations

#### Updated
- `README.md` — added architecture diagram, "Build Your Own Agent" quick start, expanded RAPP Pipeline section
- `CONSTITUTION.md` — updated directory structure and scope table
- `README.md` directories table reflects new structure

---

## [2.0.0] — 2026-02-27

### 🏗️ Repository Restructure

**The Great Cleanup** — Focused this repo solely on the CommunityRAPP Azure Functions backend and RAPP pipeline. Archived all RAPPverse/RAPPbook ecosystem code to `.rapp/`.

#### Added
- `CONSTITUTION.md` — Governing document defining repo scope, agent standards, and contribution guidelines
- `CHANGELOG.md` — This file
- `.rapp/` directory — RAPP ecosystem dotdir (like `.claude/` and `.copilot/`) housing archived code

#### Archived to `.rapp/`
- **Directories**: `rappbook/`, `rappshow/`, `rappzoo/`, `rapptools/`, `world-tick-agent/`, `channels/`, `gateway/`, `factory/`, `experimental/`, `cli/`, `api-demo/`, `docker/`, `data/`, `scripts/`, `skills/`
- **Agents**: rappbook, rappverse, rappzoo_ticker, moltbook, dimension_swarm, unified_evolver, moderator_swarm, content_remediation, engagement_daemon, autonomous_daemon, copilot_orchestrator, content-swarm, and others
- **Utils**: content_validator, expanded_submolts, lore_context, npc_voices, content_generator, ai_moderator, llm_factory, llm_provider, providers
- **Hidden state**: `.daemon/`, `.engagement/`, `.moderators/`, `.swarm/`
- **Misc files**: 10+ orphan HTML files, duplicate config files, noise artifacts

#### Removed from root (not deleted)
- All RAPPverse-specific references from `CLAUDE.md`
- `experimental/` from `.funcignore` (archived)

---

### 🤝 Bill Whalen Integration

Integrated contributions from [Bill Whalen's CommunityRAPP fork](https://github.com/billwhalenmsft/CommunityRAPP-BillWhalen). Excluded customer directories, PII, and customer-specific transpiled agents.

#### Added — Agents (11)
- `agent_generator_agent.py` — Auto-generates agents from configurations
- `agent_transpiler_agent.py` — Converts agents between platforms (Copilot Studio, M365 Copilot, Azure AI Foundry)
- `architecture_diagram_agent.py` — Generates architecture visualizations
- `copilot_studio_transpiler_agent.py` — Copilot Studio native transpilation
- `demo_script_generator_agent.py` — Automated demo script generation
- `powerpoint_generator_agent.py` — PowerPoint generation (v1)
- `powerpoint_generator_agent_v2.py` — PowerPoint generation (v2, enhanced)
- `project_tracker_agent.py` — Project management and tracking
- `rapp_agent.py` — Core RAPP pipeline agent (discovery, MVP, code gen, quality gates)
- `scripted_demo_agent.py` — Interactive demo automation
- `sharepoint_agent.py` — SharePoint integration

#### Added — Utilities
- `utils/copilot_studio_api.py` — Copilot Studio API integration
- `utils/mcs_generator.py` — MCS (Managed Copilot Studio) solution generation
- `utils/salesforce_client.py` — Salesforce CRM integration
- `utils/triggers/` — Event-driven trigger system (models, registry, router)

#### Added — Infrastructure
- `templates/mcs/` — Copilot Studio MCS templates (agent, bot definition, topics)
- `transpiled/` — Output structure for transpiled agents
- `triggers/` — Event trigger definitions (Dataverse, Salesforce, daily CI)
- `copilot_studio_deployment_config.json` — Deployment configuration

#### Added — Documentation
- `docs/FEATURE_BACKLOG.md` — Feature backlog and roadmap
- `docs/SALESFORCE_SETUP_GUIDE.md` — Salesforce integration setup
- `docs/TRANSPILER_GPT_FIX.md` — Transpiler troubleshooting
- `docs/ZURNELKAY_CI_SYSTEM.md` — CI system architecture
- `docs/copilot_studio_api_guide.md` — Copilot Studio API guide
- `docs/copilot_studio_testing_guide.md` — Copilot Studio testing guide
- `docs/arch_diagrams/` — RAPP architecture diagrams (PNG, SVG, Mermaid)
- `docs/ppt/` — PowerPoint templates (Base, Zava, Blue)

#### Added — Tests
- `tests/test_deploy_plumbing.py` — Deployment plumbing tests
- `tests/test_fix_agents.py` — Agent fix verification tests
- `tests/test_cleanup_duplicates.py` — Duplicate cleanup tests
- `tests/test_transpile_plumbing.py` — Transpiler plumbing tests

#### Added — Demos (8)
- Agent generator, transpiler, Copilot Studio transpiler demo JSONs
- `hacker_news_agent.json`, `social_media_manager_agent.json`
- Demo tooling: `create_demo_cases.py`, `run_scripted_demo_option3.py`, `update_case_ages.py`

#### Changed — Core (Performance & Resilience)
- **`function_app.py`**: Singleton OpenAI client with TTL refresh, agent caching with 5-min TTL, request timeout handling (408 responses), Copilot Studio trigger endpoint, vision/image support, improved auth error recovery
- **`host.json`**: Added `functionTimeout` (5 min), structured logging config, HTTP scaling (`maxConcurrentRequests: 100`), HSTS, health monitoring
- **`requirements.txt`**: Fixed pydantic to v2+ (required by openai library)
- **`utils/azure_file_storage.py`**: Flexible authentication — identity-based (Managed Identity) + key-based (connection string) with `USE_IDENTITY_BASED_STORAGE` feature flag
- **`utils/environment.py`**: Added `use_identity_based_storage()` feature flag function
- **`utils/rapp_report_generator.py`**: Minor formatting fix (arrow characters)

#### Changed — Documentation (11 updated)
- AGENT_DEVELOPMENT, API_REFERENCE, ARCHITECTURE, DEPLOYMENT, GETTING_STARTED, LOCAL_DEVELOPMENT, POWER_PLATFORM_INTEGRATION, SECURITY, SHAREPOINT_AGENT_SETUP, TROUBLESHOOTING, index.md

#### Excluded (from Bill's fork)
- `customers/` directory (carrier, vermeer, zurnelkay, lennox) — customer PII
- Customer-specific transpiled agents in `transpiled/copilot_studio_native/`
- `demos/demo_captures/` — screenshots with customer data
- `docs/CARRIER_MVP_USE_CASE_1_PLAN.md` — customer-specific
- `docs/Lennox/` — customer-specific
- `docs/vermeer_machine_walkaround_architecture.md` — customer-specific
- `BACKUPlocal.settings.template.json` — Bill's local config

---

## [1.0.0] — Pre-cleanup

The original CommunityRAPP repository containing the full RAPP ecosystem: Azure Functions backend, RAPPbook social feed, RAPPverse metaverse, RAPPzoo marketplace, content swarms, NPC systems, dimension factories, and more. This version is preserved in the `.rapp/` archive directory.

---

*Maintained by the CommunityRAPP community. See CONSTITUTION.md for contribution guidelines.*
