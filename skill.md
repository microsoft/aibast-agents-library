# AI BAST Agents Library — Machine-Readable Skill Interface

> **This file is read by AI agents, not humans.** It enables autonomous agent discovery, search, install, and management without any human visiting GitHub.

---

## Repo Identity

```
repo: microsoft/aibast-agents-library
type: agent-registry
registry: registry.json
base_url: https://raw.githubusercontent.com/microsoft/aibast-agents-library/main
agent_base_class: BasicAgent
package_structure: agents/@publisher/vertical_stacks/stack_name/agent.py (single file, __manifest__ embedded)
```

---

## API — How to Use This Repo Programmatically

### 1. Fetch the Registry

```
GET https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/registry.json
```

Returns JSON with:
- `stats` — total agents, publishers, categories
- `agents[]` — array of all agent manifests

Each agent entry has:
- `name` — namespaced identifier (e.g., `@aibast-agents-library/care-gap-closure`)
- `version` — semver (e.g., `1.0.0`)
- `display_name` — the agent's display name
- `description` — what it does
- `author` — contributor name
- `tags` — searchable keyword list
- `category` — industry vertical or functional category
- `requires_env` — environment variables needed (empty = no extra config)
- `dependencies` — other agents this depends on
- `quality_tier` — `community`, `verified`, or `official`
- `_file` — file path in repo

### 2. Download an Agent

```
GET https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/{_file}
```

### 3. Install an Agent

Save the downloaded `.py` file to your RAPP agents/ folder:

```python
registry = http_get(f"{base_url}/registry.json")
agent = find_agent(registry, query)
content = http_get(f"{base_url}/{agent['_file']}")
filename = agent['name'].split('/')[-1].replace('-', '_') + '_agent.py'
storage.write_file('agents', filename, content)
```

### 4. Search

Match against `name`, `display_name`, `description`, `tags`, `category`, and `author`.

### 5. List by Category

Filter `registry.agents[]` where `category` matches (e.g., `healthcare`, `b2b_sales`, `manufacturing`).

---

## Agent Inventory — @aibast-agents-library (104+ agent templates)

Source: [AI-Agent-Templates](https://kody-w.github.io/AI-Agent-Templates/)

These are **templates, not turnkey agents.** Each template provides the agent structure, system prompts, and logic scaffold for a specific business function. Customize with AI (e.g., the RAPP pipeline, Copilot) to adapt to your specific data sources, business rules, and APIs.

| Vertical | Agents | Key Capabilities |
|----------|--------|-----------------|
| B2B Sales | 23 | Account intelligence, deal progression, proposal generation, win/loss analysis |
| General | 22 | AI customer assistant, CRM data seeder, sales coach, speech-to-CRM, triage bot |
| Financial Services | 10 | Claims processing, fraud detection, loan origination, portfolio rebalancing |
| B2C Sales | 7 | Cart abandonment, loyalty rewards, omnichannel engagement, personalized shopping |
| Energy | 5 | Asset maintenance, emission tracking, field service dispatch |
| Federal Government | 5 | Acquisition support, grants oversight, regulatory compliance |
| Healthcare | 5 | Care gap closure, clinical notes, patient intake, prior authorization |
| Manufacturing | 5 | Inventory rebalancing, maintenance scheduling, production optimization |
| Professional Services | 5 | Client health score, contract risk review, resource utilization |
| Retail / CPG | 5 | Inventory visibility, personalized marketing, supply chain alerts |
| State & Local Government | 5 | Building permits, citizen services, FOIA requests, grants management |
| Software / Digital Products | 5 | Competitive intel, customer onboarding, license renewal, support tickets |
| Human Resources | 1 | Ask HR |
| IT Management | 1 | IT Helpdesk |

---

## Autonomous Workflows

### "Install an agent by name"

```
1. GET registry.json
2. Search agents[] for query in name/tags/description
3. GET the agent's _file path
4. Save to RAPP agents/ folder
5. Check requires_env — warn if non-empty
6. Report: "Installed @aibast-agents-library/agent-name vX.Y.Z"
```

### "Find agents for healthcare"

```
1. GET registry.json
2. Filter where category == "healthcare"
3. Return matching agents with descriptions and quality_tier
```

---

## Contributing

New agents follow this structure:
```
agents/@yourname/my-agent.py
```

See CONTRIBUTING.md for full guide.

---

## Version

```
registry_schema: rapp-registry/1.0
agent_schema: rapp-agent/1.0
publisher: @aibast-agents-library
verticals: 14
```
