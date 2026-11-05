---
title: One Concept Across the Stack
section: ms-rapp-1
status: published
hook: How does one Step file show up in Copilot Studio, Microsoft 365 Copilot, Foundry, the Agent Framework and the Agents SDK?
source: "docs/ms-rapp1/; tools/build_ms_rapp1.py; Microsoft Learn: Copilot Studio REST API tools and MCP, Microsoft 365 Copilot API and MCP plugins, Foundry tool catalog, Agent Framework tools (checked 2026-11-01)"
---

# One Concept Across the Stack

The Microsoft agent stack has many surfaces, and each has its own word for "a thing the model can call": action, tool, plugin, connector, function, skill.
ms-rapp/1 reduces them to one concept: **a Step is a function with a schema**. Every surface below already accepts that shape, so one Step file reaches all of them.

## The answer in brief

- A Step's `metadata` is a function schema: a name, a description, a parameters object.
- That one schema can be written out three ways: a **function tool**, an **OpenAPI operation**, or an **MCP tool**.
- Every Microsoft agent surface accepts at least one of the three. None needs the Step to change.

## The three projections

| Projection | Made from | Who accepts it |
|---|---|---|
| Function tool | `metadata` as is (`BasicAgent.to_tool()`) | Brainstem, Foundry function calling, Agent Framework function tools, Agents SDK code |
| OpenAPI operation | `docs/ms-rapp1/openapi.json`, one operation per Step | Copilot Studio REST API tools, Power Platform custom connectors, Foundry OpenAPI tools, Microsoft 365 Copilot API plugins |
| MCP tool | `name`, `description`, and `parameters` as the input schema | Copilot Studio MCP, Microsoft 365 Copilot MCP plugins, Foundry MCP, Agent Framework MCP |

The function tool and the OpenAPI file are built and tested in this repository. The MCP projection is the same three fields under MCP's names; it is described here and not yet built.

## Surface by surface

| Surface | Its word | How a Step arrives |
|---|---|---|
| Brainstem | agent | the file itself, in `agents/` |
| RAPP Runtime | Step | the file itself, in the Step Catalog |
| Copilot Studio | tool (REST API or MCP) | the OpenAPI file; Copilot Studio converts version 3 files to version 2 |
| Power Platform | custom connector | the OpenAPI file |
| Microsoft 365 Copilot | plugin (API or MCP) | the OpenAPI file, or MCP |
| Microsoft Foundry | tool (OpenAPI, function, MCP) | see [[Microsoft Foundry]] |
| Microsoft Agent Framework | function tool, MCP tool | `metadata` as a function, or MCP |
| Microsoft 365 Agents SDK | your agent's code | the agent calls the Step API, or runs `perform` in process |

## Why one concept is enough

Each surface adds hosting, channels, sign-in and governance around the same core: the model reads a schema and calls a function.
Keep the function in one file with one schema and the surfaces become delivery choices, not rewrites.
Change the Step once and every projection is rebuilt from it; `tools/build_ms_rapp1.py --check` fails if the OpenAPI file falls behind.

## Not yet verified

These mappings follow the published shape of each surface, read from Microsoft Learn on 2026-11-01. The generated OpenAPI file has not yet been imported into Copilot Studio, Power Platform, Microsoft 365 Copilot or Foundry, and the MCP projection is not built. Several of these features are in preview.

See also [[Steps]], [[RAPP Runtime]] and [[ms-rapp-1 Overview]].
