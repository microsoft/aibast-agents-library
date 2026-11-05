---
title: Step 06 Code Quality Review
section: Production Guide
status: published
hook: What a reviewer checks in generated agent code at Quality Gate 3 before it is deployed.
source: "docs/rapp-guide.html#step6; SPEC.md §8"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Step 06 Code Quality Review

The **code quality review** is **Quality Gate 3**.
An experienced developer reads every generated agent for **security**, **error handling**, **integration** and **metadata quality**.
Only approved code moves to deployment.

Guide section: [Step 6 in the production guide](../rapp-guide.html#step6)

## At a glance

- **Type:** Audit (Quality Gate 3)
- **Duration:** 30-60 minutes for 6-10 agents
- **Owner:** Technical Team Lead with Python and Azure experience
- **Input:** agent files from [[Step 05 Generate Agent Code]]
- **Output:** approved code, issue log, integration notes, green light to deploy

## The review checklist

### 1. Security

- **No hardcoded credentials** — secrets come from environment variables.
- **Input validation** — required parameters are checked before use.
- **Parameterized queries** for any database access.
- **File path sanitization** for any file reads.

### 2. Error handling

- External calls wrapped in `try`/`except`.
- Errors logged with context (agent name, parameters).
- **Always return strings** — never `None`, a dict, or a raised exception.
- One failing agent must not break the others.

### 3. Integration

- Customer API endpoints are correct.
- Field names match the customer's real system.
- Auth method matches their setup (OAuth, API key, certificate).
- Required packages are listed in `requirements.txt`.

### 4. Metadata

- **Clear descriptions** so the model knows when to call the agent.
- The `required` array is accurate.
- Parameter descriptions include example values.
- Fixed options use `enum`.

## Common fixes

**Returns a dict instead of a string.**

```python
# wrong
return {"status": "success", "route": optimized_route}
# fixed
return f"Route generated successfully: {json.dumps(optimized_route)}"
```

The intelligence layer expects strings.

**Missing error context.** Replace `return "Error occurred"` with a logged, specific message that names the inputs.

**Vague description.** Replace `"Handles route planning"` with text that says what the agent does and which user requests should trigger it.

## Gate decision

- **Pass:** all agents reviewed, minor fixes applied → [[Step 07 Deploy Prototype]].
- **Fail:** major logic errors or missing integrations → send feedback to the generator and regenerate.

Review is a conversation with the AI: merge redundant agents, split overloaded ones, adjust details until the files meet the bar.

The guide reports a 94% first-attempt pass rate and 231 executable demo cases.

## Why pass rates are high

- The framework enforces one pattern: `BasicAgent`, JSON Schema metadata, string returns.
- The generator learns from working agents.
- Each agent does one thing, so it is easy to review.

## How rapp/1 underpins this step

The string-return rule matches the wire. On success, `POST /chat` returns a JSON object whose `response` member is a string, with `agent_logs` as a string of one line per agent call (§8). Agents that return strings keep that contract intact. See [[The Wire]] and [[The Agent Contract]].

For the security side of the protocol itself, see [[Security Considerations]].

## Related

- [[Step 05 Generate Agent Code]]
- [[Step 07 Deploy Prototype]]
- [[The Agent Contract]]
- [[The Wire]]
- [[Security Considerations]]
