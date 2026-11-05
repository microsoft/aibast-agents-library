---
title: The Agent Contract
section: Building
status: published
hook: What exactly must a Brainstem agent file look like, and how does it reach the user through POST /chat?
source: "rapp_brainstem/agents/basic_agent.py; rapp_brainstem/brainstem.py (load_agents, /chat, /health); rapp_brainstem/CLAUDE.md; rapp/GRAIL-SPECIES.json; SPEC.md §8"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# The Agent Contract

An **agent** is one Python file that gives the Brainstem one new skill.
The file follows a small, fixed **contract**: a class built on `BasicAgent`, a description of its inputs, and a `perform` method.
Every new capability is a new agent behind `POST /chat`, never a new web address.

## The answer in brief

- File name ends in `_agent.py` and sits directly in `agents/`.
- The class extends `BasicAgent`.
- `metadata` is an OpenAI function schema: name, description, parameters.
- `perform(**kwargs)` does the work and returns text.
- The model decides when to call it, through `POST /chat`.

## Discovery

The Brainstem finds agents with one rule, recorded in the species contract `rapp/GRAIL-SPECIES.json`:

```json
"discovery": {
  "glob": "*_agent.py",
  "flat": true,
  "subdirectories_excluded": true,
  "listing_globs": [
    "*.py",
    "*_agent.py"
  ]
}
```

- Only the flat `agents/` directory is scanned. `agents/experimental/` is intentionally excluded.
- Agents reload from disk on every request. Edit the file and test again; no restart is needed.
- If two files register the same agent name, the later file is quarantined and reported by `GET /health`.

## The base class

Every agent extends `BasicAgent` from `agents/basic_agent.py`. Its four methods are part of the pinned contract:

| Method | Role |
|---|---|
| `__init__(self, name, metadata)` | sets the agent's name and function schema |
| `perform(self, **kwargs)` | runs the agent; arguments come from the model's tool call |
| `system_context(self)` | optional text added to the system prompt each turn |
| `to_tool(self)` | turns `metadata` into an OpenAI function-calling tool definition |

The default `metadata` shape shows the expected fields:

```python
self.metadata = {
    "name": self.name,
    "description": "Base agent -- override this.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}
```

## How a request flows

For `POST /chat` the Brainstem:

1. loads `soul.md`, the system prompt;
2. discovers agents from `agents/`;
3. builds tool definitions from each agent's `metadata`;
4. calls the model with the conversation and the tools;
5. runs `perform()` for each tool call, looping up to three rounds;
6. returns the final answer and `agent_logs`.

Agents written for the cloud tier can import `utils.azure_file_storage`. The Brainstem maps it to a local JSON store through a `sys.modules` shim, so the same file runs in both places.

## The wire the agent sits behind

The upstream rapp/1 specification fixes the synchronous wire (see [[The Wire]]):

- Request: a JSON object with `user_input` (required), optional `conversation_history`, optional `session_id`. Unknown members are ignored.
- Success: HTTP 200 with at least `response`, `agent_logs`, and `session_id`.
- Malformed request: HTTP 400 with exactly `{"error": string}`.
- `GET /health` is the liveness probe; it carries no RAPP semantics.

A minimal call:

```bash
curl -s localhost:7071/chat -H 'Content-Type: application/json' \
  -d '{"user_input": "What can you do?"}'
```

The answer is in the `response` field. The species contract pins this as `"chat_response_field": "response"`.

## Why the contract stays small

The rapp/1 specification says new capability is a new agent behind `/chat`, never a sibling REST route.
That keeps one stable surface for every host: the local Brainstem, the Azure tier, and Copilot Studio.
It is also why this library's catalog ships agents and stacks, not server changes (see [[Distros and Pinning]]).

## Related

- [[The Brainstem Kernel]]
- [[The Wire]]
- [[Distros and Pinning]]
- [[Step 05 Generate Agent Code]]
- [[Step 06 Code Quality Review]]
- [[Sources and Provenance]]
