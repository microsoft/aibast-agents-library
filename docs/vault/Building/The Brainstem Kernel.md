---
title: The Brainstem Kernel
section: Building
status: published
hook: What is the Brainstem kernel this library ships, and what does it guarantee to every agent and host?
source: "rapp_brainstem/CLAUDE.md; rapp_brainstem/brainstem.py; rapp/GRAIL-SPECIES.json; docs/GRAIL-SPECIES.md; CLAUDE.md; SPEC.md §8, §11.1"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# The Brainstem Kernel

The **Brainstem** is the local AI server at the center of this library.
It is a single-file Flask app that talks to the GitHub Copilot API and runs your agents as tools.
The AIBAST Agents Library ships the **Grail** Brainstem kernel pinned by its species contract. Every difference from the pin is recorded in `rapp/KERNEL-DRIFT.md`, and the catalog is built around it.

## The answer in brief

- One file, `rapp_brainstem/brainstem.py`, holds auth, routing, streaming, diagnostics, model calls, and agent orchestration.
- It runs on port `7071` and needs only a GitHub account with Copilot access. No API keys.
- Its public shape — routes, `BasicAgent`, discovery, shims, port, `/chat` response field, install layout — is pinned in `rapp/GRAIL-SPECIES.json`.
- The pin records kernel version `0.6.16`, generated from Grail commit `49db80c8`.

## What it does

Each `POST /chat` request:

1. loads `soul.md` as the system prompt;
2. discovers agents from `agents/*_agent.py`;
3. calls the Copilot API with the agents as tools;
4. runs tool calls through each agent's `perform()`, up to three rounds;
5. returns JSON, or server-sent events on `POST /chat/stream`.

Authentication tries, in order: `GITHUB_TOKEN`, the `.copilot_token` file, `gh auth token`, then device-code sign-in via `/login`.
Copilot API tokens are short-lived and refresh automatically.

## The pinned surface

The species contract lists every route the Grail exposes. A sample:

```json
"POST /chat",
"POST /chat/stream",
"GET /health",
"GET /agents",
"POST /agents/import",
"GET /version"
```

It also pins:

- `"default_port": 7071`
- `"chat_response_field": "response"`
- the `BasicAgent` methods `__init__`, `perform`, `system_context`, `to_tool` (see [[The Agent Contract]])
- import shims such as `agents.basic_agent` and `utils.azure_file_storage`
- the install layout under `$HOME/.brainstem`: `venv`, `src/rapp_brainstem`, and its flat `agents` directory

## Health

`GET /health` reports `status`, `version`, `model`, the loaded `agents`, any quarantined agent files, and Copilot sign-in state.
It never exchanges tokens; that happens lazily on the first `/chat`.

```bash
curl -s localhost:7071/health | python3 -m json.tool
```

The library adds one small route, `GET /health/public`, returning only `status` and `version`. Its CORS is limited to the library's two Pages origins, so the static catalog can show whether a local Brainstem is ready. It is recorded in the drift ledger as an upstream candidate.

## Configuration

Settings come from `.env` in `rapp_brainstem/`: `GITHUB_TOKEN`, `GITHUB_MODEL` (default `auto`), `SOUL_PATH`, `AGENTS_PATH`, `PORT`, `BRAINSTEM_LAN_MODE`, `BRAINSTEM_ALLOWED_HOSTS`, and `VOICE_ZIP_PASSWORD`.
The target is Python 3.11 with a virtual environment at `~/.brainstem/venv`.

## How rapp/1 frames the kernel

The upstream rapp/1 specification names the Grail as the reference for the synchronous wire: an endpoint conforms when it answers the Grail conformance scenarios the way the pinned Grail does (see [[The Wire]]).
§11.1 then treats the Grail kernel as an immutable anchor identified by `grail_id`:

- different kernel bytes are a different Grail;
- new behavior lives outside the kernel;
- a changed or unmeasured kernel byte is `kernel-drift` and fails closed.

This library follows that model. Its catalog, pages, and Azure and Power Platform tiers live outside the kernel (see [[Distros and Pinning]]). The vendored `brainstem.py` does carry a few **ledgered edits**: one upstream-candidate route (`GET /health/public`) plus permanent identity and catalog-pin rewrites (the support link and `RAR_REVISION`), all listed in `rapp/KERNEL-DRIFT.md`.

## Running it

```bash
cd rapp_brainstem && ./start.sh
cd rapp_brainstem && python -m pytest tests -v
```

## Related

- [[The Agent Contract]]
- [[Distros and Pinning]]
- [[The Wire]]
- [[Conformance and Drift]]
- [[Step 07 Deploy Prototype]]
- [[Sources and Provenance]]
