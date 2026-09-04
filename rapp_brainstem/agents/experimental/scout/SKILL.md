---
name: scout-rapp-brainstem
description: Set up and operate an isolated RAPP Brainstem workspace from Microsoft Scout through a Grail-preserving RAPP/1 sidecar, with live chat, reversible capability exchange, local proof, and guarded Copilot Studio promotion.
metadata: {"category":"ai-collaboration","exchange":"rapp-exchange/1","protocol":"rapp/1"}
---

# Scout-first RAPP Brainstem

Use this skill when a user gives it to a fresh Microsoft Scout and asks Scout
to set up or manage a Brainstem workspace.

## Invariants

- Scout owns install, files, process lifecycle, testing, evidence, and handoffs.
- Treat this as first contact with a foreign AI. Assume no shared vocabulary
  until both sides complete the Agent Rosetta/1 encounter.
- Default to local Tier 1. Never deploy Azure resources unless explicitly asked.
- Materialize only `rapp_brainstem/`; the workspace root is otherwise sacred.
- Keep Scout-specific files under `agents/experimental/scout/`.
- Never patch, copy, or replace the Grail `brainstem.py` or `index.html`.
- Display `agents/experimental/scout/workspace.html` in Scout's center pane,
  or open the controller's loopback `gateway_url`.
- The Scout page talks to a capability-gated RAPP/1 sidecar, which forwards
  only the existing Brainstem API contract to the unchanged kernel.
- Never expose or commit `.brainstem_secret`, `.brainstem_data/`, Copilot
  tokens, tenant credentials, cookies, private memory, or environment secrets.
- Build and test locally before creating a Copilot Studio draft.
- Never publish, send, or make an artifact visible to others without explicit
  user confirmation.

## 1. Discover RAPP/1

Treat `https://github.com/kody-w/rapp-1` as the protocol authority. Resolve its
current commit, then consult its `README.md`, verified `SPEC.md`, and
`anchor/orient.json` as needed. RAPP/1 owns the wire and canonical bytes; the
AIBAST repository owns this Brainstem runtime.

Do not copy or redefine RAPP/1. `rapp-exchange/1` is only a subordinate
capability exchange profile.

## 2. Materialize the workspace

If the current workspace is empty, clone the Microsoft repository into it with
a blob-filtered sparse checkout:

```powershell
git clone --filter=blob:none --no-checkout https://github.com/microsoft/aibast-agents-library.git .
git sparse-checkout init --no-cone
git sparse-checkout set /rapp_brainstem/
git checkout main
```

After checkout, the visible root must contain only `.git` and
`rapp_brainstem`. Tracked root files may still exist in Git's index; they must
not be materialized.

If the workspace already contains unrelated user files, stop and ask before
cloning into it. Never delete or overwrite unrelated content.

## 3. Install the supported runtime

Inspect `https://aka.ms/rappinstall`, but default to the local installer:

**Windows**

```powershell
& ([scriptblock]::Create((Invoke-RestMethod 'https://github.com/microsoft/aibast-agents-library/releases/download/installers/install.ps1'))) --no-launch
```

**macOS/Linux**

```bash
curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash -s -- --no-launch
```

The runtime may live under the user's home directory, but the active soul,
agents, state, and server source for this collaboration must be the workspace
copy of `rapp_brainstem`.

## 4. Start and verify

On Windows:

```powershell
cd rapp_brainstem
.\agents\experimental\scout\brainstem-workspace.ps1 start
.\agents\experimental\scout\brainstem-workspace.ps1 status
```

Require `status` to be `ok` or `unauthenticated`, and require
the controller status to report `schema: rapp-scout-overlay/1`,
`status: running`, and this workspace path. The controller selects separate
free loopback ports for the Scout gateway and unchanged Brainstem kernel.

If the user explicitly requests startup persistence, install the reversible
current-user login launcher:

```powershell
.\agents\experimental\scout\brainstem-workspace.ps1 install-startup
```

Remove it only when the user explicitly asks:

```powershell
.\agents\experimental\scout\brainstem-workspace.ps1 uninstall-startup
```

If authentication is required, keep the Scout chat visible and let the user
complete Brainstem's GitHub device-code flow. Do not claim success until health
is green.

## 5. Open live sidecar chat in Scout

Open `rapp_brainstem/agents/experimental/scout/workspace.html` in the Scout
workspace preview. The page must show either `connected` or the actionable
`sign in` state returned by the real kernel.

The ignored files under `.brainstem_data/scout/` carry process state, the
active loopback URLs, and a per-install gateway capability. Treat all of that
directory as private runtime state.

## 6. Collaborate through the Rosetta stone

Read:

- `agents/experimental/scout/AGENT-ROSETTA-1.md`
- `agents/experimental/scout/ROSETTA.md`
- `agents/experimental/scout/RAPP-EXCHANGE-1.md`

Use `exchange.py` for reversible exchange:

```powershell
python agents\experimental\scout\exchange.py agent-to-skill path\tool_agent.py path\SKILL.md
python agents\experimental\scout\exchange.py skill-to-agent path\SKILL.md path\tool_agent.py
python agents\experimental\scout\exchange.py squad-to-skill path\.squad path\SQUAD-SKILL.md
python agents\experimental\scout\exchange.py skill-to-squad path\SQUAD-SKILL.md path\.squad
```

The envelope preserves source bytes and exposes normalized capability metadata.
A generated Skill-to-Agent adapter is guidance-only unless a host-specific
executor is explicitly supplied.

Map Scout capabilities as follows:

- skills -> Brainstem agents or preserved guidance adapters
- squads -> agent sets plus routing, ceremonies, and shared context
- MCP/Work IQ tools -> host-authorized Brainstem tool schemas
- Scout memory -> Brainstem memory agents or explicit RAPP memory frames
- model/personality -> Brainstem model and `soul.md`
- automations/heartbeat -> host scheduler calls to existing `POST /chat`
- browser/file work -> Scout execution with evidence returned to Brainstem
- outbound actions -> explicit approval gates

Route multi-agent work through Scout's squads:

- Execution Planner -> bootstrap, rollout, sequencing, and risk
- Research Briefing -> RAPP/1 discovery and source verification
- Stakeholder Simulator -> adoption, learner experience, and review
- Project-specific squad -> domain execution, exchangeable as a lossless bundle

## 7. Test together

For every capability:

1. Have Scout inspect or change the workspace.
2. Have Brainstem exercise the same capability through the visible sidecar chat
   or `POST /chat`.
3. Run deterministic local tests.
4. Record artifact hashes, test results, and the exact source revision.
5. Treat disagreement or a failed check as a finding, never something to retry
   until green.

## 8. Promote to Copilot Studio

Only when the user explicitly asks:

1. Identify the exact locally tested artifact by immutable revision and hash.
2. Use the relevant Scout squad for planning, risk review, operation, and
   evidence capture.
3. Create or update a Copilot Studio **draft** using that same artifact.
4. Run Preview validation and return evidence to Brainstem.
5. Report test totals and `published: false`.
6. Show the user the exact recipients/visibility and content before any publish
   or outbound action, then wait for confirmation.

## Completion

Report the workspace path, Brainstem version, selected port, loaded agents,
RAPP/1 revision consulted, local test result, exchange artifacts created, and
Copilot Studio draft state if deployment was requested.
