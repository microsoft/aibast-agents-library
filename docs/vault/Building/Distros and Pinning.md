---
title: Distros and Pinning
section: Building
status: published
hook: How does this library ship the Brainstem kernel pinned by a species contract and drift-ledgered, with every difference recorded in `rapp/KERNEL-DRIFT.md`, and its own catalog around it?
source: "rapp/GRAIL-SPECIES.json; rapp/KERNEL-DRIFT.md; docs/GRAIL-SPECIES.md; docs/RELEASE-PROCESS.md; CLAUDE.md; SPEC.md §11.1"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Distros and Pinning

The AIBAST Agents Library is a **distribution** of the Brainstem.
It ships the Grail kernel **pinned** to one exact source commit, with every difference recorded in a drift ledger, and adds its own agent catalog, pages, and cloud tiers around it.
Kernel updates arrive one way, through reviewed kernel-sync pull requests.

## The answer in brief

- **Pin**: `rapp/GRAIL-SPECIES.json` records the kernel's shape and the exact Grail commit it came from.
- **Contract**: a species test fails CI if the shipped kernel stops matching that shape.
- **Ledger**: `rapp/KERNEL-DRIFT.md` names every shipped file that differs from the pin, and why.
- **Catalog**: the library's own agents, registry, and pages sit outside the kernel.

## The pin

The species contract records where the kernel came from:

```json
"source": {
  "ref": "main",
  "commit": "49db80c8c6b6caa7647369beaf477d374a8f293c",
  "fetched_at": "2026-09-04T12:57:59+00:00",
  "files": 31
}
```

It also records `"kernel_version": "0.6.16"`, every route, the `BasicAgent` methods, the discovery rule, the import shims, the default port, the `/chat` response field, and the install layout.

## The species test

`tests/test_grail_species.py` compares the shipped kernel with the pinned shape. It fails when the kernel drops or changes:

- a Flask route the Grail exposes;
- a `BasicAgent` method or its signature;
- the discovery rule (`*_agent.py`, flat, no subdirectories);
- an import shim;
- the default port (`7071`) or the `/chat` response field (`response`);
- an install-layout constant.

```bash
python -m unittest -v tests/test_grail_species.py
GRAIL_SPECIES_LIVE=1 python -m unittest tests/test_grail_species.py
```

Live mode also compares against the current Grail. Items the Grail has and the library lacks are reported as "pending kernel sync"; only a broken shared item fails.

## The drift ledger

Every shipped file that differs from the pinned Grail commit appears in `rapp/KERNEL-DRIFT.md` with a disposition:

- **permanent** — identity rewrites such as repository and support links, the Microsoft persona in `soul.md`, and the catalog pin in the chat's registry panel;
- **upstream candidate** — fixes that belong to every Brainstem user, such as installer overrides and `GET /health/public`, waiting to return through a kernel sync;
- **distribution content** — files only this library ships, such as its learn-new-agent agent and tests.

`python scripts/grail_species.py drift <grail-dir> --ledger rapp/KERNEL-DRIFT.md` fails when a differing path is missing from the ledger.

## One layout, either installer

A Grail install and a library install share one layout: `~/.brainstem`, its `venv/`, `src/rapp_brainstem/`, and the flat `agents/` directory.
Because the contract keeps those identical, either installer can run over the other and the result is still one working Brainstem with the user's agents intact.

## What the library owns

These surfaces belong to the library and are kept through every kernel sync:

- `agents/@aibast-agents-library/`, `registry.json`, `build_registry.py`;
- `index.html`, `docs/installer.html`, `why.html`, `metrics.html`, and `state/`;
- `rapp_ai/`, the Azure Functions tier;
- `README.md`, `docs/rapp-guide.html`, `.github/`, and `tools/`.

## How a kernel update lands

1. A kernel-sync pull request brings the new Grail into the staging ring.
2. The same change regenerates `rapp/GRAIL-SPECIES.json` and refreshes `rapp/KERNEL-DRIFT.md`.
3. Preflight, the Pages deploy, and the clean-runner one-liner smoke must pass.
4. `tools/promotion_check.sh` must report GREEN.
5. One pull request from staging to `microsoft:main`, opened and merged by a human.

A fix that belongs to every Brainstem user goes to the Grail first and comes back through this path.

## How rapp/1 supports this model

The upstream rapp/1 specification (§11.1) treats the Grail as an immutable kernel identified by `grail_id`:

- new behavior must live outside the kernel;
- different kernel bytes are a different Grail, never a retag of the old one;
- if needed behavior cannot be built outside the pin, the implementation reports an incompatibility rather than editing the kernel.

The library's pin, species test, and ledger put that discipline into daily practice.
For release-level byte pinning, see [[RAPP CICD]].

## Related

- [[The Brainstem Kernel]]
- [[The Agent Contract]]
- [[Conformance and Drift]]
- [[RAPP CICD]]
- [[Versioning and Evolution]]
- [[Sources and Provenance]]
