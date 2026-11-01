---
title: ms-rapp-1 Overview
section: ms-rapp-1
status: published
hook: What is ms-rapp/1, and how does it stay backward compatible with rapp/1 and the Brainstem?
source: "This vault's rapp/1 notes at the pinned commit; docs/ms-rapp1/; tools/build_ms_rapp1.py; tests/test_ms_rapp1.py"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# ms-rapp-1 Overview

**ms-rapp/1** is the enterprise profile of rapp/1.
It keeps every rapp/1 rule unchanged and adds one extension, **RAPP Runtime**, for running AI steps inside an enterprise review boundary.
If you know the Brainstem, you already know the pattern: one fixed engine, one endpoint, a folder of single-file capabilities.

## The answer in brief

- **rapp/1 is the base, unchanged.** This vault's Protocol and Building notes, pinned to one upstream commit, are the rules ms-rapp/1 inherits.
- **Anything that runs on the Brainstem runs here.** A Step is a rapp/1 agent: same base class, same metadata, same `perform`.
- **The extension is additive.** Steps carry two extra fields that a rapp/1 host ignores.
- **Compatibility is tested, not promised.** `tests/test_ms_rapp1.py` loads each example Step as a plain agent and fails if the profile drifts.

## Three levels

| Level | What conforms | What it adds |
|---|---|---|
| 1. rapp/1 | Any agent that follows [[The Agent Contract]] | Nothing. This is the Brainstem's own contract. |
| 2. RAPP Runtime | A Step: a rapp/1 agent with `ROUTE` and `RESULT_SCHEMA` | The Step API, the Step Catalog, Run Receipts. See [[RAPP Runtime]] and [[Steps]]. |
| 3. Microsoft Foundry | A Step Catalog published as an OpenAPI tool | Foundry agents call Steps with no custom code. See [[Microsoft Foundry]]. |

Each level includes the one before it. A file that conforms at level 3 still loads in a Brainstem at level 1.

## Rules that never change

1. **Never break the agent contract.** `BasicAgent`, `metadata`, `perform(**kwargs)` and the `*_agent.py` file name stay exactly as rapp/1 defines them.
2. **Never break the wire.** A host that offers `/chat` keeps the request and response described in [[The Wire]].
3. **Additions are named, never silent.** Everything ms-rapp/1 adds is listed in these notes and marked as an extension.
4. **Rename with an alias.** When an enterprise name differs from a rapp/1 name, both work. See [[RAPP Runtime]] for the name map.

## How it was built

ms-rapp/1 follows the distribution pattern in [[Distros and Pinning]]: the upstream rules come in at a pinned commit, and enterprise additions are layered on top and labeled.
Drift is caught the same way as in [[Conformance and Drift]]: a build check and a test, run on every change.
