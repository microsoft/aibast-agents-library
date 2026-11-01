---
title: Steps
section: ms-rapp-1
status: published
hook: What does a Step file look like, and why does it load unchanged in a Brainstem?
source: "docs/ms-rapp1/steps/action_items_agent.py; tools/build_ms_rapp1.py; rapp_brainstem/agents/basic_agent.py"
---

# Steps

A **Step** is a rapp/1 agent with two extra fields.
Drop it into a Brainstem's `agents/` folder and it loads like any other agent. RAPP Runtime serves the same file through the Step API.

## The answer in brief

- A Step extends `BasicAgent`, sets `name` and `metadata`, and implements `perform(**kwargs)`, exactly as in [[The Agent Contract]].
- It adds `ROUTE` (its Step API path) and `RESULT_SCHEMA` (the shape of its result).
- A rapp/1 host ignores the two extra fields. That is the whole compatibility story.

## The contract

| Field | rapp/1 | ms-rapp/1 adds | Rule |
|---|---|---|---|
| file name | `*_agent.py` | | so a Brainstem discovers it |
| class | one `BasicAgent` subclass | | |
| `metadata` | name, description, parameters | | `parameters` is an object schema; it is the Step API request body |
| `perform(**kwargs)` | returns a string | | for a Step, a JSON string matching `RESULT_SCHEMA` |
| `ROUTE` | | yes | 1 to 40 lowercase letters, digits or hyphens |
| `RESULT_SCHEMA` | | yes | a JSON schema object |

`tools/build_ms_rapp1.py --check` enforces these rules on every Step in `docs/ms-rapp1/steps/`.

## The example

`docs/ms-rapp1/steps/action_items_agent.py` lists the action items in meeting notes. It is deterministic, so the tests run it without a model.

```python
ROUTE = "action-items"
RESULT_SCHEMA = {"type": "object", "properties": {"items": {...}}, "required": ["items"]}

class ActionItemsAgent(BasicAgent):
    def __init__(self):
        self.name = "ActionItems"
        self.metadata = {"name": self.name, "description": "...",
                         "parameters": {"type": "object", "properties": {"notes": {"type": "string"}},
                                        "required": ["notes"]}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        ...
        return json.dumps({"items": items})
```

Given the notes `Action: Dana: send the pricing sheet` and `TODO: book the follow-up`, it returns one item owned by Dana and one marked Unassigned.

## Writing a good Step

- **One fixed task.** A Step that does two things is two Steps.
- **Structured in, structured out.** The parameters and the result schema are the review surface.
- **No new systems.** A Step that reaches a new outside service or data store is a new data flow and goes back to review. See [[Run Receipts and Change Control]].

See also [[RAPP Runtime]] and [[Microsoft Foundry]].
