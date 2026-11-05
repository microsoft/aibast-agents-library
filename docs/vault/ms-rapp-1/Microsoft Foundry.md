---
title: Microsoft Foundry
section: ms-rapp-1
status: published
hook: How is ms-rapp/1 used in Microsoft Foundry, and what does a Foundry agent see?
source: "docs/ms-rapp1/openapi.json; tools/build_ms_rapp1.py; Microsoft Learn: Foundry Agent Service tool catalog, function calling, and agent tracing (checked 2026-11-01)"
---

# Microsoft Foundry

ms-rapp/1 meets Microsoft Foundry at one point: the **Step Catalog becomes an OpenAPI tool**.
A Foundry agent then calls Steps the same way a Brainstem calls agents, with no custom code.

## The answer in brief

- `tools/build_ms_rapp1.py --write` renders `docs/ms-rapp1/openapi.json`: one operation per Step.
- Add that file to a Foundry agent as an **OpenAPI tool**, pointed at your RAPP Runtime host.
- Put it in a **toolbox** to share the same Steps across many agents.
- Read each run in Foundry **tracing**, which records every tool call.

This page describes a pattern. It is separate from the library's solution templates, which use Copilot Studio, Microsoft 365 and Power Platform.

## Mapping

| ms-rapp/1 | Microsoft Foundry | Note |
|---|---|---|
| Step | an operation in an OpenAPI tool | the operation's request body is the Step's `metadata.parameters` |
| Step Catalog | one OpenAPI tool, optionally in a toolbox | OpenAPI tools can be shared through toolboxes |
| Step (in-process) | a function tool | the Step's `metadata` is already a function schema; your app runs `perform` |
| Step API host | the server URL in the OpenAPI file | your RAPP Runtime deployment |
| Run Receipt | agent tracing | built on OpenTelemetry and Application Insights; content recording is off by default |
| Step Policy | agent instructions and content filters | the Step's own checks still run in RAPP Runtime |
| Change Control | a new OpenAPI file version | rebuild the file when the catalog changes; `--check` fails if it is stale |

## Two ways to connect

**OpenAPI tool (recommended).** The Step runs in RAPP Runtime. Foundry calls the Step API over HTTPS. One file describes the whole catalog, and toolboxes can share it.

**Function tool.** Your application registers the Step's `metadata` as a function and runs `perform` itself when the model calls it. Use this when the Step must run inside your own process. Function tools run on the client side, so they cannot go in a toolbox.

## What stays the same

The Step file does not change between hosts. The same `action_items_agent.py` loads in a Brainstem, runs in RAPP Runtime, and is described to Foundry by the generated OpenAPI file.

## Not yet verified

The generated file has not been loaded into a live Foundry project. Foundry features named here were read from Microsoft Learn on 2026-11-01; some, such as toolboxes, may be in preview. Check the current documentation before relying on them.

See also [[ms-rapp-1 Overview]], [[Steps]] and [[RAPP Runtime]].
