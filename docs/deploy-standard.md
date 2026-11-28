# The deploy standard

One way to take a library solution to where a person works, whichever AI does the work.
It is three small things: six verbs, one data form, one test.

Status: staging. Two targets answer the verbs today. This is an experimental project, not an
officially supported Microsoft product.

## 1. Six verbs

Every target answers the same six. Nothing changes until `deploy` or `undo` is confirmed.

| Verb | What it does | Changes anything |
|---|---|---|
| `check` | Is the target there and signed in | No |
| `look` | What the person already has, and what to recommend | No |
| `probe` | Prove it reads real data or answers its first question | No |
| `plan` | Say what will happen | No |
| `deploy` | Do it, after a yes | Yes |
| `undo` | Take it back, after a yes | Yes |

Every verb returns JSON with `ok` and a one-line `summary` in plain words.

| Target | File |
|---|---|
| Copilot Studio | `agents/@aibast-agents-library/templates/copilot_studio_deploy_agent.py` |
| The person's own Brainstem | `brainstem_deploy_agent.py` (agent `BrainstemDeploy`; `tools/brainstem_target.py` still works) |

## 2. One data form: the fit guide

A solution deploys with sample data unless it has a fit guide. The fit guide is the `fit` key in
`solutions/<slug>/deployment.json`. It is data, so a person or an AI can write it.

| Field | Meaning |
|---|---|
| `schema` | `aibast-fit-guide/1.0` |
| `needs` | What the agent needs, in business words |
| `defaults` | The numbers its rules use |
| `systems[]` | One mapping for each system the library knows |

Each mapping:

| Field | Meaning |
|---|---|
| `system` | The system's everyday name |
| `connector`, `operation_id` | The standard connector and its one read operation |
| `fixed_inputs`, `query_input` | Inputs that never change, and the input that takes the query |
| `rule` | One sentence for how the agent decides. The agent says it in every answer |
| `preview` | One small count that proves the data is there |
| `expect_says` | The sentence the person hears, filled from the preview |
| `test_question` | A first question to ask |
| `operations` | For each operation: when to use it, and its queries |

Rules the checker enforces:

- Read operations only.
- Counts and sums come from a query, never from the model.
- Operation names are the solution's own.
- The agent runs as the signed-in person and carries the disclaimer.

When a solution has no fit guide, `look` returns the form and the AI may write a mapping, prove
it with `probe`, and pass it to `plan` and `deploy`.

## 3. One test

| Check | How | Where it runs |
|---|---|---|
| The form | `python3 tools/check_fit_guides.py` | Every pull request |
| Real data | `probe <solution> --env <environment>` | With the person's sign-in |
| Any AI | Give a fresh AI only "Get <SKILL.md> and do it." It passes with one question and answers that match the source | By hand today |

## What is not standard yet

- One data system is proven (Dynamics 365).
- The any-AI check is run by hand.
- The form's home is this library. It moves nowhere else until it has won on more than one install.

This standard is one part of [the AIBAST pattern](aibast-pattern.md).
