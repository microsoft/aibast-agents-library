---
title: Step 05 Generate Agent Code
section: Production Guide
status: published
hook: How the locked MVP becomes Python agent files that follow the BasicAgent pattern.
source: "docs/rapp-guide.html#step5; SPEC.md §8, §9.2, §11.1"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Step 05 Generate Agent Code

This step turns the locked MVP into **agent code**: single Python files the Brainstem or Azure Function can load.
Usually one well-scoped agent is enough. Split into several agents only when the use case truly spans separate roles.

Guide section: [Step 5 in the production guide](../rapp-guide.html#step5)

## At a glance

- **Type:** Manual, with AI-assisted generation
- **Duration:** minutes to scaffold; writing the business logic is still the real work
- **Owner:** Technical Team
- **Input:** the approved poke and project JSON from [[Step 04 Customer Validation]]
- **Output:** `[agent_name]_agent.py` files, tested locally

## Then and now

When the guide was first written, each agent took 2-3 weeks by hand.
Today a scaffolded agent is generated, smoke-tested and hot-loaded in about fifteen seconds. A hand-written one is live the moment the file is saved.
The library has 72 published patterns. 70 of them use one single-file agent with several deterministic operations.

## The process

1. Review the approved poke and project JSON.
2. Identify the capabilities the MVP needs.
3. Start from an existing agent template.
4. Write each agent in the **BasicAgent pattern**.
5. Save each as `[agent_name]_agent.py`.
6. Test locally before [[Step 06 Code Quality Review]].

The **RAPP Agent Generator** (with a manual fallback prompt in the guide) drafts the code from the MVP description.

## The rules every agent follows

From the generator prompt:

1. Inherit from `BasicAgent`.
2. Class name in PascalCase, e.g. `ContractGenerationAgent`.
3. `self.name` in PascalCase with **no spaces**.
4. `perform()` **always returns a string** — never a dict or `None`.
5. Errors return descriptive strings; never raise.
6. Include complete JSON Schema `metadata` so the agent documents itself.
7. One capability per agent. Published agents run roughly 180-960 lines, median about 400.

## The template

```python
from agents.basic_agent import BasicAgent
import logging
import json

class YourAgentNameAgent(BasicAgent):
    def __init__(self):
        self.name = "YourAgentName"  # NO SPACES!
        self.metadata = {
            "name": self.name,
            "description": "Clear description of when to call this agent and what it does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string|integer|array|etc",
                        "description": "What this parameter is for"
                    }
                },
                "required": ["param1"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        """
        What this method does.
        Returns: String describing the result
        """
        param1 = kwargs.get('param1')
        if not param1:
            return "Error: param1 is required"
        try:
            result = "Success: description of what happened"
            return result
        except Exception as e:
            return f"Error in {self.name}: {str(e)}"
```

The `metadata` is what the model reads to decide **when** to call the agent and with which parameters.

## How rapp/1 underpins this step

This is where the protocol becomes concrete.

- **New capability is a new agent, not a new endpoint.** The upstream RAPP/1 specification (§8) says new capability is "a new agent behind `/chat`, never a sibling REST route". Writing an agent file is exactly that. See [[The Wire]] and [[The Agent Contract]].
- **The kernel stays unchanged.** New implementation behavior must live outside the pinned Grail kernel (§11.1). Agents are dropped into the agents folder; the kernel file is not edited. See [[The Brainstem Kernel]].
- **One agent file can travel as a rapplication.** The `rapplication` egg variant (§9.2) is a ZIP that must include `rappid.json` and exactly one `agent.py` at the root. See [[The Egg]] and [[Identity and the Rappid]].

## Related

- [[The Agent Contract]]
- [[Step 04 Customer Validation]]
- [[Step 06 Code Quality Review]]
- [[The Wire]]
- [[The Egg]]
- [[The Brainstem Kernel]]
