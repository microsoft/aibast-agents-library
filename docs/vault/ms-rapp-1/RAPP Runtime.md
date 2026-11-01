---
title: RAPP Runtime
section: ms-rapp-1
status: published
hook: What is RAPP Runtime, and how does each of its pieces map to the Brainstem?
source: "docs/ms-rapp1/; the Brainstem kernel in rapp_brainstem/; tools/build_ms_rapp1.py"
---

# RAPP Runtime

**RAPP Runtime** is the ms-rapp/1 engine that runs AI steps.
It has the Brainstem's shape, named in terms enterprise engineers and reviewers already use.

## The answer in brief

- One fixed engine runs every Step. It does not change per use case.
- One signed-in endpoint, the **Step API**, serves every Step. A new capability never adds an endpoint.
- The **Step Catalog** is a folder of reviewed Step files, loaded when they are called.
- Every run leaves a **Run Receipt** for audit.

## Name map

| RAPP Runtime | Brainstem | What it is |
|---|---|---|
| RAPP Runtime | Brainstem kernel | The fixed engine. See [[The Brainstem Kernel]]. |
| Step API | `POST /chat` | `POST /api/lens/<route>`: one endpoint for every Step. |
| Step | `agent.py` | One file, one business task, one checked result. See [[Steps]]. |
| Step Catalog | `agents/` | The approved set of Steps: only reviewed, deployed files. |
| Live catalog | agents reload every request | A merged and deployed Step is used on the next call. |
| Step Policy | `soul.md` | Fixed instructions. The model passes values; the Step checks them. |
| Result | `response` | The checked output, returned as `frame`. |
| Run Receipt | agent logs | Which Step, which model, how many attempts, what usage. |
| Change Control | a pull request into `agents/` | A Step arrives only by reviewed pull request and deploy, never from a browser. |

The code names (`lens`, `/api/lens/<route>`) stay as they are. The enterprise names are documentation names, so no published caller breaks.

## Where the shape differs, on purpose

| | Brainstem `/chat` | Step API |
|---|---|---|
| Input | `{user_input, conversation_history, session_id}` | the Step's own `metadata.parameters` |
| Output | `{response, session_id, ...}` | `{frame}`, matching the Step's `RESULT_SCHEMA` |
| Who picks the agent | the model | the caller, by route |

A Step is a fixed task with structured input. That keeps each Step reviewable on its own, which is what an enterprise release review assesses.
A free-text `/chat` on RAPP Runtime is allowed by the profile, but it accepts open text, so it should go through its own review before release.

See also [[ms-rapp-1 Overview]] and [[Run Receipts and Change Control]].
